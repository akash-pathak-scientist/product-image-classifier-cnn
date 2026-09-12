"""Classify a single product image from the command line.

Usage:
    python -m src.predict path/to/image.jpg
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms as T

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.model import build_model


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load(Path(__file__).resolve().parents[1] / "models" / "best.pt",
                      map_location=device, weights_only=False)
    model = build_model(ckpt.get("arch", "productcnn"),
                        num_classes=len(ckpt["classes"]), pretrained=False)
    model.load_state_dict(ckpt["model"])
    model.eval().to(device)
    tf = T.Compose([
        T.Resize((ckpt["img_size"], ckpt["img_size"])),
        T.ToTensor(), T.Normalize(ckpt["mean"], ckpt["std"]),
    ])
    return model, tf, ckpt["classes"], device


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    model, tf, classes, device = load_model()
    img = Image.open(sys.argv[1]).convert("RGB")
    with torch.no_grad():
        probs = torch.softmax(model(tf(img).unsqueeze(0).to(device)), 1)[0]
    ranked = sorted(zip(classes, probs.tolist()), key=lambda t: -t[1])
    print(f"\nPrediction for {sys.argv[1]}:")
    for name, p in ranked:
        print(f"  {name:<12} {p:.1%}")
    print(f"\n=> {ranked[0][0]} ({ranked[0][1]:.1%} confidence)")


if __name__ == "__main__":
    main()
