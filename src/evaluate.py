"""Evaluate the trained model on the held-out test set.

Produces:
* reports/metrics.json            - every number quoted in the README
* reports/classification_report.txt
* reports/confusion_matrix.png    (counts + row-normalised)
* reports/training_curves.png
* reports/examples_misclassified/ - up to 12 real misclassified images
* reports/test_predictions.csv
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import (classification_report, confusion_matrix)
from torch.utils.data import DataLoader
from torchvision import transforms as T

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config as C
from src.model import build_model
from src.train import ProductDS


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load(C.MODELS_DIR / "best.pt", map_location=device, weights_only=False)
    classes = ckpt["classes"]
    mean, std = ckpt["mean"], ckpt["std"]

    tf = T.Compose([
        T.Resize((ckpt["img_size"], ckpt["img_size"]),
                 interpolation=T.InterpolationMode.BILINEAR),
        T.ToTensor(), T.Normalize(mean, std),
    ])
    test_ds = ProductDS(C.SPLIT_DIR / "test.csv", tf)
    loader = DataLoader(test_ds, batch_size=64, shuffle=False, num_workers=1)

    model = build_model(ckpt.get("arch", "productcnn"),
                        num_classes=len(classes), pretrained=False).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    tta = "--no-tta" not in sys.argv          # flip-averaging, disclosed in README
    y_true, y_pred, probs_all = [], [], []
    with torch.no_grad():
        for x, y in loader:
            out = model(x.to(device))
            if tta:
                out = out + model(torch.flip(x, dims=[3]).to(device))
                out = out / 2
            probs_all.append(torch.softmax(out.cpu(), 1).numpy())
            y_pred.extend(out.argmax(1).cpu().tolist())
            y_true.extend(y.tolist())
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    probs = np.concatenate(probs_all)

    acc = float((y_true == y_pred).mean())
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=classes, digits=4)

    print(f"\nTEST ACCURACY: {acc:.4f}  (n={len(y_true)})\n")
    print(report)

    # ------------------------------------------------ classification report --
    (C.REPORTS_DIR / "classification_report.txt").write_text(
        f"Test accuracy: {acc:.4f} (n={len(y_true)})\n\n{report}")

    # ------------------------------------------------------------- metrics ---
    per_pair = {}
    for i, ti in enumerate(classes):
        for j, pj in enumerate(classes):
            if i != j:
                per_pair[f"{ti} -> {pj}"] = {
                    "count": int(cm[i, j]),
                    "rate_within_true": round(float(cm[i, j] / cm[i].sum()), 4),
                }
    metrics = {
        "test_accuracy": round(acc, 4),
        "tta_flip": tta,
        "test_n": int(len(y_true)),
        "val_accuracy_best": ckpt["val_acc"],
        "best_epoch": ckpt["epoch"],
        "classes": classes,
        "per_class_support": {c: int((y_true == i).sum())
                              for i, c in enumerate(classes)},
        "confusion_matrix": cm.tolist(),
        "per_pair_errors": per_pair,
    }
    (C.REPORTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))

    # ------------------------------------------------------ confusion matrix -
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, mat, fmt, title in (
        (axes[0], cm, "d", "Confusion matrix (counts)"),
        (axes[1], cm / np.maximum(cm.sum(1, keepdims=True), 1), ".2%",
         "Confusion matrix (row-normalised)"),
    ):
        im = ax.imshow(mat, cmap="Blues")
        ax.set_xticks(range(len(classes)), classes, rotation=20)
        ax.set_yticks(range(len(classes)), classes)
        ax.set_xlabel("Predicted"); ax.set_ylabel("True")
        ax.set_title(title)
        for i in range(len(classes)):
            for j in range(len(classes)):
                col = "white" if mat[i, j] > mat.max() * 0.6 else "black"
                ax.text(j, i, format(mat[i, j], fmt), ha="center",
                        va="center", color=col, fontsize=11)
    fig.colorbar(im, ax=axes[1], fraction=0.046)
    fig.suptitle(f"ProductCNN - test accuracy {acc:.2%} (n={len(y_true)})")
    fig.tight_layout()
    fig.savefig(C.REPORTS_DIR / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    # ------------------------------------------------------- training curves -
    hist = json.loads((C.REPORTS_DIR / "train_history.json").read_text())
    eps = [h["epoch"] for h in hist]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(eps, [h["train_loss"] for h in hist], label="train")
    axes[0].plot(eps, [h["val_loss"] for h in hist], label="val")
    axes[0].set_title("Loss"); axes[0].set_xlabel("epoch"); axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[1].plot(eps, [h["train_acc"] for h in hist], label="train")
    axes[1].plot(eps, [h["val_acc"] for h in hist], label="val")
    axes[1].axhline(0.85, ls="--", c="red", lw=1)
    axes[1].text(eps[0], 0.852, "project target 85%", color="red", fontsize=8)
    axes[1].set_title("Accuracy"); axes[1].set_xlabel("epoch"); axes[1].legend()
    axes[1].grid(alpha=0.3)
    fig.suptitle("ProductCNN training curves")
    fig.tight_layout()
    fig.savefig(C.REPORTS_DIR / "training_curves.png", dpi=150)
    plt.close(fig)

    # --------------------------------------------- misclassified examples ----
    ex_dir = C.REPORTS_DIR / "examples_misclassified"
    if ex_dir.exists():
        shutil.rmtree(ex_dir)
    ex_dir.mkdir(parents=True)
    test_df = test_ds.df.reset_index(drop=True)
    wrong = np.where(y_true != y_pred)[0]
    conf = probs[np.arange(len(y_pred)), y_pred]
    wrong = wrong[np.argsort(conf[wrong])]          # most confident mistakes first
    picked = 0
    seen = set()
    for idx in wrong:
        t, p = classes[y_true[idx]], classes[y_pred[idx]]
        if (t, p) in seen:                           # cover every pair
            continue
        seen.add((t, p))
        src = C.RAW_DIR / test_df.iloc[idx]["file"]
        dst = ex_dir / f"true-{t.lower()}_pred-{p.lower()}_{Path(test_df.iloc[idx]['file']).stem[:24]}.jpg"
        shutil.copy(src, dst)
        picked += 1
        if picked >= 12:
            break

    # ------------------------------------------------------ predictions csv --
    out = test_df.copy()
    out["pred"] = [classes[i] for i in y_pred]
    out["correct"] = (out["label"] == out["pred"]).astype(int)
    out["confidence"] = conf.round(4)
    out.to_csv(C.REPORTS_DIR / "test_predictions.csv", index=False)

    print(f"saved: metrics.json, confusion_matrix.png, training_curves.png, "
          f"{picked} misclassified examples")


if __name__ == "__main__":
    main()
