"""Stream-sample product metadata from the public McAuley-Lab/Amazon-Reviews-2023
corpus (Hou et al., 2024) without downloading the multi-GB source files.

The corpus stores each domain as a huge JSONL file on the Hugging Face Hub.
We open HTTP range windows at random byte offsets, decode the complete JSON
lines found there, and keep products that have a usable "large" product image.
This gives an unbiased random sample while downloading only a few MB.

Usage:  python -m src.data.sample_metadata
Output: data/metadata.csv  (asin, title, label, subcategory, image_url, src_url)
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import (BASE_URL, CHUNK_BYTES, DATASET_ID, DOMAIN_FILES,
                        OFFSET_SAMPLES, SEED, TARGET_PER_CLASS)

HEADERS = {"User-Agent": "product-image-classifier/1.0 (research sample)"}


def iter_json_lines(url: str, offset: int, chunk_bytes: int):
    """Yield parsed JSON dicts for complete lines inside [offset, offset+chunk)."""
    rng = f"bytes={offset}-{offset + chunk_bytes - 1}"
    with requests.get(url, headers={**HEADERS, "Range": rng},
                      stream=True, timeout=(10, 45)) as r:
        r.raise_for_status()
        pending = b""
        for chunk in r.iter_content(chunk_size=1 << 18):
            if not chunk:
                continue
            pending += chunk
            *lines, pending = pending.split(b"\n")
            for ln in lines:
                ln = ln.strip()
                if ln:
                    try:
                        yield json.loads(ln)
                    except json.JSONDecodeError:
                        continue


def image_urls(rec: dict) -> list[str]:
    urls = []
    for img in rec.get("images") or []:
        if not isinstance(img, dict):
            continue
        u = img.get("large") or img.get("hi_res") or img.get("thumb")
        if u:
            urls.append(u)
    return urls


def sample_domain(dom_cfg: dict, rng: random.Random, quota: int) -> list[dict]:
    url = f"{BASE_URL}/{dom_cfg['file']}"
    size = dom_cfg["size"]
    rows: dict[str, dict] = {}
    scanned = 0
    offsets = sorted(rng.randrange(0, max(size - CHUNK_BYTES, 1))
                     for _ in range(OFFSET_SAMPLES))
    print(f"[{dom_cfg['label']}] offsets: {offsets}")
    for off in offsets:
        if len(rows) >= quota:
            break
        got_here = 0
        for rec in iter_json_lines(url, off, CHUNK_BYTES):
            scanned += 1
            title = (rec.get("title") or "").strip()
            if len(title) < 10 or len(title) > 300:      # junk / placeholder
                continue
            urls = image_urls(rec)
            if not urls:
                continue
            asin = rec.get("parent_asin") or rec.get("asin")
            if not asin or asin in rows:
                continue
            cats = rec.get("categories") or []
            sub = cats[1].strip() if len(cats) > 1 and isinstance(cats[1], str) else (
                  cats[0].strip() if cats and isinstance(cats[0], str) else "")
            rows[str(asin)] = {
                "asin": str(asin),
                "title": title.replace("\n", " ").strip(),
                "label": dom_cfg["label"],
                "subcategory": sub,
                "price": rec.get("price"),
                "image_url": urls[0],
                "fallback_url": urls[1] if len(urls) > 1 else "",
                "src_url": f"https://www.amazon.com/dp/{asin}",
                "source_dataset": DATASET_ID,
            }
            got_here += 1
            if len(rows) >= quota:
                break
        print(f"  offset {off}: +{got_here} (total {len(rows)})")
    print(f"[{dom_cfg['label']}] collected {len(rows)} unique products "
          f"({scanned} lines scanned)")
    return list(rows.values())


def main() -> None:
    rng = random.Random(SEED)
    all_rows: list[dict] = []
    for cfg in DOMAIN_FILES.values():
        all_rows += sample_domain(cfg, rng, TARGET_PER_CLASS)
    df = pd.DataFrame(all_rows)
    out = Path(__file__).resolve().parents[2] / "data" / "metadata.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {len(df)} rows -> {out}")
    print(df["label"].value_counts())


if __name__ == "__main__":
    main()
