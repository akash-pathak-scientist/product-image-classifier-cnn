"""Post-hoc error analysis: WHICH product types cause each confusion pair?

Joins test_predictions.csv with metadata.csv (subcategory) and produces
reports/error_analysis.md with, for every misclassified pair, the product
subcategories that drive it - this is the evidence behind the README's
"why the model fumbles X vs Y" section.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config as C


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    preds = pd.read_csv(C.REPORTS_DIR / "test_predictions.csv")
    meta = pd.read_csv(root / "data" / "metadata.csv", dtype={"asin": str})

    norm = lambda a: a.lstrip("0") if isinstance(a, str) and a.isdigit() else a
    # file names are <Label>/<asin>.jpg  (asin may have lost leading zeros)
    preds["asin"] = (preds["file"].str.split("/").str[-1]
                     .str.replace(".jpg", "", regex=False).map(norm))
    meta["asin"] = meta["asin"].map(norm)
    df = preds.merge(meta[["asin", "subcategory", "title"]], on="asin", how="left")
    df["subcategory"] = df["subcategory"].fillna("Unknown")

    wrong = df[df["correct"] == 0]
    lines = [
        "# Error analysis - which product types confuse the model?",
        "",
        f"Test images: **{len(df)}** | misclassified: **{len(wrong)}** "
        f"({len(wrong)/len(df):.2%})",
        "",
    ]

    pairs = wrong.groupby(["label", "pred"]).size().sort_values(ascending=False)
    lines.append("## Misclassified volume per pair\n")
    lines.append("| true -> predicted | count | % of that true class in test |")
    lines.append("|---|---|---|")
    support = df.groupby("label").size()
    for (t, p), n in pairs.items():
        lines.append(f"| {t} -> {p} | {n} | {n / support[t]:.1%} |")

    lines.append("\n## Top sub-categories behind each confusion pair\n")
    for (t, p), grp in wrong.groupby(["label", "pred"]):
        lines.append(f"### {t} -> {p}  ({len(grp)} images)\n")
        top = grp["subcategory"].value_counts().head(8)
        for sub, n in top.items():
            ex = grp[grp["subcategory"] == sub]["title"].iloc[0]
            lines.append(f"- **{sub}** - {n} images, e.g. *\"{ex[:90]}\"*")
        lines.append("")

    out = C.REPORTS_DIR / "error_analysis.md"
    out.write_text("\n".join(lines))
    print(f"-> {out}\n")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
