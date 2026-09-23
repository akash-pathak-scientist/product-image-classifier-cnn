"""Create reproducible stratified train/val/test splits from raw_manifest.csv.

Split: 70% train / 15% val / 15% test, stratified per class, seed=42.
Output: data/splits/{train,val,test}.csv + repo-root splits/ backup
(columns: file,label)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import ROOT, SPLIT_DIR, SPLIT_DIR_ALT, RAW_DIR, RAW_DIR_ALT, resolve_image_path

VAL_FRAC, TEST_FRAC = 0.15, 0.15
SEED = 42


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    df = pd.read_csv(root / "data" / "raw_manifest.csv")[["file", "label"]]
    # fallback-aware image existence check (supports build/raw and data/raw)
    def _exists(rel: str) -> bool:
        return (RAW_DIR / rel).exists() or (RAW_DIR_ALT / rel).exists()
    missing = (~df["file"].apply(_exists)).sum()
    assert missing == 0, (
        f"{missing} image files missing on disk! Checked {RAW_DIR} and {RAW_DIR_ALT}. "
        f"Did you run fetch_images or unzip dataset.zip?"
    )

    train, hold = train_test_split(df, test_size=(VAL_FRAC + TEST_FRAC),
                                   stratify=df["label"], random_state=SEED)
    rel = TEST_FRAC / (VAL_FRAC + TEST_FRAC)
    val, test = train_test_split(hold, test_size=rel, stratify=hold["label"],
                                 random_state=SEED)

    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_DIR_ALT.mkdir(parents=True, exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part = part.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
        part.to_csv(SPLIT_DIR / f"{name}.csv", index=False)
        part.to_csv(SPLIT_DIR_ALT / f"{name}.csv", index=False)
        print(f"{name}: {len(part)}  ({part['label'].value_counts().to_dict()})")
    print(f"total: {len(df)}")
    print(f"splits written to {SPLIT_DIR} and {SPLIT_DIR_ALT} (fallback-aware)")


if __name__ == "__main__":
    main()
