"""Ensemble evaluation: average softmax probabilities of the 224px and 160px
fine-tuned MobileNetV3-Small checkpoints (each with horizontal-flip TTA).

Writes the same report artefacts as src/evaluate.py into reports/ensemble/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config as C
from src.model import build_model
from src.train import ProductDS, make_eval_tf


def predict_ckpt(ckpt_path: str, files_df, size: int, device: str):
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = build_model(ck.get("arch", "mobilenetv3s"),
                        num_classes=len(ck["classes"]), pretrained=False).to(device)
    model.load_state_dict(ck["model"])
    model.eval()
    ds = ProductDS(C.SPLIT_DIR / "test.csv", make_eval_tf(size))
    loader = DataLoader(ds, batch_size=24, num_workers=1, prefetch_factor=1)
    probs = []
    with torch.no_grad():
        for x, _ in loader:
            out = model(x.to(device)) + model(torch.flip(x, [3]).to(device))
            probs.append(torch.softmax(out / 2, 1).cpu().numpy())
    return np.concatenate(probs), ck


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ds = ProductDS(C.SPLIT_DIR / "test.csv", make_eval_tf(224))
    y_true = ds.df["label"].map(lambda c: C.CLASSES.index(c)).to_numpy()

    p224, ck224 = predict_ckpt(C.MODELS_DIR / "best.pt", ds.df, 224, device)
    p160, ck160 = predict_ckpt(C.MODELS_DIR / "best_160.pt", ds.df, 160, device)

    for name, probs, ck in (("mobilenetv3s_224", p224, ck224),
                            ("mobilenetv3s_160", p160, ck160),
                            ("ensemble_mean", (p224 + p160) / 2, None)):
        y_pred = probs.argmax(1)
        acc = float((y_pred == y_true).mean())
        print(f"{name}: test acc {acc:.4f}")
        if name != "ensemble_mean":
            continue
        out_dir = C.REPORTS_DIR / "ensemble"
        out_dir.mkdir(exist_ok=True)
        cm = confusion_matrix(y_true, y_pred)
        report = classification_report(y_true, y_pred,
                                       target_names=C.CLASSES, digits=4)
        (out_dir / "classification_report.txt").write_text(
            f"Test accuracy (ensemble, flip-TTA): {acc:.4f} (n={len(y_true)})\n\n{report}")
        per_pair = {}
        for i, ti in enumerate(C.CLASSES):
            for j, pj in enumerate(C.CLASSES):
                if i != j:
                    per_pair[f"{ti} -> {pj}"] = {
                        "count": int(cm[i, j]),
                        "rate_within_true": round(float(cm[i, j] / cm[i].sum()), 4),
                    }
        (out_dir / "metrics.json").write_text(json.dumps({
            "test_accuracy": round(acc, 4),
            "tta": "horizontal flip averaging + 224px/160px checkpoint ensemble",
            "members": ["models/best.pt (224px)", "models/best_160.pt (160px)"],
            "val_acc_members": [ck224["val_acc"], ck160["val_acc"]],
            "test_n": int(len(y_true)),
            "confusion_matrix": cm.tolist(),
            "per_pair_errors": per_pair,
            "classes": C.CLASSES,
        }, indent=2))

        fig, ax = plt.subplots(figsize=(5.4, 4.6))
        mat = cm / np.maximum(cm.sum(1, keepdims=True), 1)
        im = ax.imshow(mat, cmap="Blues")
        ax.set_xticks(range(len(C.CLASSES)), C.CLASSES, rotation=20)
        ax.set_yticks(range(len(C.CLASSES)), C.CLASSES)
        ax.set_xlabel("Predicted"); ax.set_ylabel("True")
        ax.set_title(f"Ensemble (row-normalised) — test acc {acc:.2%}")
        for i in range(len(C.CLASSES)):
            for j in range(len(C.CLASSES)):
                col = "white" if mat[i, j] > mat.max() * 0.6 else "black"
                ax.text(j, i, f"{cm[i,j]}\n({mat[i,j]:.1%})", ha="center",
                        va="center", color=col, fontsize=9)
        fig.colorbar(im, ax=ax, fraction=0.046)
        fig.tight_layout()
        fig.savefig(out_dir / "confusion_matrix.png", dpi=150)
        print("ensemble reports written")


if __name__ == "__main__":
    main()
