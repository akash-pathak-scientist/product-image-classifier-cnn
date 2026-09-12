"""Train ProductCNN on the three-domain product-image dataset.

Usage:
    python -m src.train [--epochs 30] [--batch-size 64]

* stratified splits from data/splits/*.csv
* strong augmentation on train (crop/flip/colour/rotation)
* AdamW + cosine schedule + label smoothing
* early stopping on val accuracy, best checkpoint -> models/best.pt
* training history -> reports/train_history.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms as T

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config as C
from src.model import ARCHS, build_model

# ------------------------------------------------------------------ data ---
def make_train_tf(size: int, mild: bool = False) -> T.Compose:
    scale = (0.75, 1.0) if mild else (0.65, 1.0)
    return T.Compose([
        T.RandomResizedCrop(size, scale=scale,
                            interpolation=T.InterpolationMode.BILINEAR),
        T.RandomHorizontalFlip(),
        T.RandomRotation(8 if mild else 12),
        T.ColorJitter(0.2, 0.2, 0.2),
        T.ToTensor(),
        T.Normalize(C.IMAGENET_MEAN, C.IMAGENET_STD),
    ])


def make_eval_tf(size: int) -> T.Compose:
    return T.Compose([
        T.Resize((size, size), interpolation=T.InterpolationMode.BILINEAR),
        T.ToTensor(),
        T.Normalize(C.IMAGENET_MEAN, C.IMAGENET_STD),
    ])


class ProductDS(Dataset):
    def __init__(self, csv_path: Path, tf: T.Compose):
        import pandas as pd
        self.df = pd.read_csv(csv_path)
        self.tf = tf
        self.root = C.RAW_DIR

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        r = self.df.iloc[i]
        img = Image.open(self.root / r["file"]).convert("RGB")
        return self.tf(img), C.CLASSES.index(r["label"])


def seed_everything(seed: int = 42) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def run_epoch(model, loader, crit, opt, device, train: bool):
    model.train() if train else model.eval()
    loss_sum, correct, n = 0.0, 0, 0
    with torch.set_grad_enabled(train):
        for x, y in loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            out = model(x)
            loss = crit(out, y)
            if train:
                opt.zero_grad(set_to_none=True)
                loss.backward()
                opt.step()
            loss_sum += loss.item() * y.size(0)
            correct += (out.argmax(1) == y).sum().item()
            n += y.size(0)
    return loss_sum / n, correct / n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", choices=list(ARCHS), default="mobilenetv3s")
    ap.add_argument("--epochs", type=int, default=C.EPOCHS)
    ap.add_argument("--batch-size", type=int, default=C.BATCH_SIZE)
    ap.add_argument("--lr", type=float, default=None)
    ap.add_argument("--img-size", type=int, default=None)
    ap.add_argument("--init-from", default=None, help="warm-start checkpoint")
    args = ap.parse_args()
    arch, size = args.arch, args.img_size or ARCHS[args.arch][1]
    lr = args.lr or (7e-4 if arch == "mobilenetv3s" else C.LR)

    seed_everything(C.SEED)
    torch.set_num_threads(max(1, torch.get_num_threads()))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device} | torch {torch.__version__}")

    train_ds = ProductDS(C.SPLIT_DIR / "train.csv", make_train_tf(size))
    val_ds = ProductDS(C.SPLIT_DIR / "val.csv", make_eval_tf(size))
    nw = 1 if device == "cpu" else 2        # keep RAM low on small boxes
    train_ld = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                          num_workers=nw, pin_memory=(device == "cuda"),
                          persistent_workers=False, drop_last=True,
                          prefetch_factor=1 if nw else None)
    val_ld = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                        num_workers=nw, pin_memory=(device == "cuda"),
                        persistent_workers=False,
                        prefetch_factor=1 if nw else None)
    print(f"train {len(train_ds)} | val {len(val_ds)}")

    model = build_model(arch, num_classes=len(C.CLASSES),
                        dropout=C.DROPOUT).to(device)
    if args.init_from:
        ck = torch.load(args.init_from, map_location=device, weights_only=False)
        model.load_state_dict(ck["model"])
        print(f"warm-started from {args.init_from} (val_acc {ck['val_acc']})")
    crit = nn.CrossEntropyLoss(label_smoothing=C.LABEL_SMOOTHING)
    if arch == "mobilenetv3s":                      # gentle on pretrained feats
        head_params = [p for n, p in model.named_parameters()
                       if n.startswith("classifier")]
        feat_params = [p for n, p in model.named_parameters()
                       if not n.startswith("classifier")]
        opt = torch.optim.AdamW(
            [{"params": feat_params, "lr": lr / 5},
             {"params": head_params, "lr": lr}],
            weight_decay=C.WEIGHT_DECAY)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=lr,
                                weight_decay=C.WEIGHT_DECAY)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(
        opt, T_max=args.epochs, eta_min=lr / 15)

    history, best_acc, best_ep, since_best = [], 0.0, -1, 0
    for ep in range(1, args.epochs + 1):
        t0 = time.time()
        tr_loss, tr_acc = run_epoch(model, train_ld, crit, opt, device, True)
        va_loss, va_acc = run_epoch(model, val_ld, crit, opt, device, False)
        sched.step()
        history.append({"epoch": ep, "lr": sched.get_last_lr()[0],
                        "train_loss": tr_loss, "train_acc": tr_acc,
                        "val_loss": va_loss, "val_acc": va_acc,
                        "secs": round(time.time() - t0, 1)})
        print(f"ep {ep:02d} | train loss {tr_loss:.4f} acc {tr_acc:.4f} | "
              f"val loss {va_loss:.4f} acc {va_acc:.4f} | "
              f"{history[-1]['secs']}s", flush=True)

        if va_acc > best_acc:
            best_acc, best_ep, since_best = va_acc, ep, 0
            C.MODELS_DIR.mkdir(exist_ok=True)
            torch.save({
                "model": model.state_dict(),
                "arch": arch,
                "classes": C.CLASSES,
                "img_size": size,
                "mean": C.IMAGENET_MEAN, "std": C.IMAGENET_STD,
                "val_acc": va_acc, "epoch": ep,
            }, C.MODELS_DIR / "best.pt")
        else:
            since_best += 1

        (C.REPORTS_DIR / "train_history.json").write_text(
            json.dumps(history, indent=2))

        stop_reason = None
        if ep - best_ep >= C.HOLD_TARGET_EPOCHS and best_acc >= C.TARGET_VAL_ACC:
            stop_reason = f"target reached (val_acc {best_acc:.4f})"
        elif since_best >= C.EARLY_STOP_PATIENCE:
            stop_reason = "early stopping"
        if stop_reason:
            print(f"stop: {stop_reason}")
            break

    print(f"BEST val_acc={best_acc:.4f} @ epoch {best_ep} -> models/best.pt")


if __name__ == "__main__":
    main()
