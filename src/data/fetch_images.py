"""Fetch, validate and normalise the product images listed in data/metadata.csv.

* parallel downloads with retries + fallback URL
* decodes with Pillow (rejects corrupt/HTML responses)
* EXIF-orientation fix, RGB conversion, long side resized to MAX_SIDE
* SHA-1 content dedup (drops re-hosted duplicate photos)
* skips files that already exist (idempotent re-runs)
Output: <RAW_DIR>/<Label>/<asin>.jpg  +  data/raw_manifest.csv
"""
from __future__ import annotations

import hashlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import (FETCH_TIMEOUT, FETCH_WORKERS, JPEG_QUALITY, MAX_SIDE,
                        RAW_DIR)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; product-image-classifier/1.0; research)"}
_tls = threading.local()


def _session() -> requests.Session:
    if not hasattr(_tls, "s"):
        _tls.s = requests.Session()
        _tls.s.headers.update(HEADERS)
    return _tls.s


def process(content: bytes) -> bytes | None:
    """Decode + normalise raw bytes -> JPEG bytes (or None if invalid)."""
    try:
        if len(content) < 1200:
            return None
        img = Image.open(BytesIO(content))
        img = ImageOps.exif_transpose(img).convert("RGB")
        w, h = img.size
        if min(w, h) < 48:
            return None
        if max(w, h) > MAX_SIDE:
            sc = MAX_SIDE / max(w, h)
            img = img.resize((round(w * sc), round(h * sc)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, "JPEG", quality=JPEG_QUALITY)
        return buf.getvalue()
    except Exception:
        return None


def fetch_one(task) -> dict | None:
    asin, label, rel, urls = task
    if (RAW_DIR / rel).exists():                    # already fetched earlier
        data = (RAW_DIR / rel).read_bytes()
        return {"asin": asin, "label": label, "file": rel,
                "sha1": hashlib.sha1(data).hexdigest(), "bytes": len(data)}
    s = _session()
    for u in urls:
        if not isinstance(u, str) or not u:
            continue
        try:
            r = s.get(u, timeout=FETCH_TIMEOUT)
            if r.status_code != 200:
                continue
            data = process(r.content)
            if data is None:
                continue
            (RAW_DIR / rel).parent.mkdir(parents=True, exist_ok=True)
            (RAW_DIR / rel).write_bytes(data)
            return {"asin": asin, "label": label, "file": rel,
                    "sha1": hashlib.sha1(data).hexdigest(),
                    "bytes": len(data)}
        except Exception:
            continue
    return None


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    df = pd.read_csv(root / "data" / "metadata.csv").drop_duplicates(subset="asin")
    print(f"{len(df)} products to fetch", flush=True)

    tasks = [(r.asin, r.label, f"{r.label}/{r.asin}.jpg",
              [r.image_url, r.fallback_url])
             for r in df.itertuples(index=False)]

    results, done, failed = [], 0, 0
    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as ex:
        futs = [ex.submit(fetch_one, t) for t in tasks]
        for fut in as_completed(futs):
            res = fut.result()
            done += 1
            if res:
                results.append(res)
            else:
                failed += 1
            if done % 500 == 0:
                print(f"  {done}/{len(tasks)} done | ok={len(results)} "
                      f"failed={failed}", flush=True)

    out = pd.DataFrame(results)
    dup = out.duplicated(subset="sha1")
    print(f"ok: {len(out)} | dead/invalid: {failed} | "
          f"duplicate-content dropped: {int(dup.sum())}")
    out = out[~dup].sort_values("asin").reset_index(drop=True)
    out.to_csv(root / "data" / "raw_manifest.csv", index=False)
    print(f"manifest -> data/raw_manifest.csv ({len(out)} images)")


if __name__ == "__main__":
    main()
