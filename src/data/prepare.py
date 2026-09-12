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
from src.config import ROOT, SPLIT_DIR

VAL_FRAC, TEST_FRAC = 0.15, 0.15
SEED = 42


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    df = pd.read_csv(root / "data" / "raw_manifest.csv")[["file", "label"]]
    missing = (~df["file"].apply(lambda f: (ROOT / "build" / "raw" / f).exists())).sum()
    assert missing == 0, f"{missing} image files missing on disk!"

    train, hold = train_test_split(df, test_size=(VAL_FRAC + TEST_FRAC),
                                   stratify=df["label"], random_state=SEED)
    rel = TEST_FRAC / (VAL_FRAC + TEST_FRAC)
    val, test = train_test_split(hold, test_size=rel, stratify=hold["label"],
                                 random_state=SEED)

    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    backup = root / "splits"
    backup.mkdir(exist_ok=True)
    for name, part in [("train", train), ("val", val), ("test", test)]:
        part = part.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
        part.to_csv(SPLIT_DIR / f"{name}.csv", index=False)
        part.to_csv(backup / f"{name}.csv", index=False)
        print(f"{name}: {len(part)}  ({part['label'].value_counts().to_dict()})")
    print(f"total: {len(df)}")


if __name__ == "__main__":
    main()
