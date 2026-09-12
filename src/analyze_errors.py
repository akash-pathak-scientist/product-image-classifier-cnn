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

    # NOTE: the corpus's Amazon-Fashion slice ships without a category tree
    # (categories == [] upstream), so Apparel sub-categories are derived from
    # product titles. Clearly labelled as title-derived wherever shown.
    import re

    APPAREL_KW = [
        ("Dresses", r"\bdress(es)?\b"),
        ("Shirts & Tops", r"t-?shirt|shirt|top|blouse|tank|polo"),
        ("Pants & Jeans", r"\bjeans\b|pants|trousers|joggers|leggings|shorts"),
        ("Shoes", r"shoes|sneakers|boots|sandals|slippers|heels|loafers"),
        ("Jewelry & Watches", r"necklace|earring|bracelet|ring\b|jewel|watch|anklet|pendant"),
        ("Socks & Hosiery", r"\bsocks?\b|hosiery|stockings"),
        ("Hoodies & Sweatshirts", r"hoodie|sweatshirt|pullover|fleece"),
        ("Jackets & Coats", r"jacket|coat|parka|windbreaker|raincoat|vest"),
        ("Hats & Caps", r"\bhat\b|cap\b|beanie|headband|bandana"),
        ("Bags & Wallets", r"\bbag\b|wallet|purse|backpack|handbag|tote|satchel"),
        ("Belts & Accessories", r"\bbelt\b|scarf|gloves|mitten|tie\b|suspenders"),
        ("Swimwear", r"swim|bikini|trunks"),
        ("Underwear & Sleep", r"underwear|bra\b|panties|boxer|pajama|lingerie|nightwear|sleep"),
        ("Costumes & Cosplay", r"costume|cosplay|halloween"),
        ("Wristbands & Straps", r"wristband|wristband|strap|armband"),
    ]

    def apparel_sub(row):
        if not (row["label"] == "Apparel"
                and (pd.isna(row["subcategory"]) or row["subcategory"] == "Unknown")):
            return row["subcategory"]
        t = str(row["title"]).lower()
        for name, pat in APPAREL_KW:
            if re.search(pat, t):
                return f"{name} (title-derived)"
        return "Other apparel (title-derived)"

    df["subcategory"] = df.apply(apparel_sub, axis=1)

    wrong = df[df["correct"] == 0]
    lines = [
        "# Error analysis - which product types confuse the model?",
        "",
        f"Test images: **{len(df)}** | misclassified: **{len(wrong)}** "
        f"({len(wrong)/len(df):.2%})",
        "",
        "> Sub-category names marked *(title-derived)* come from product titles:",
        "the corpus's Amazon-Fashion slice ships without a category tree",
        "(`categories == []` upstream), so Apparel sub-categories are derived",
        "from titles with a transparent keyword rule.",
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
