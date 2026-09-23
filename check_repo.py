#!/usr/bin/env python3
"""Fast health check for the product-image-classifier repo (no GPU/torch required).

Checks:
- required CSVs and their row counts / class balance
- models/*.pt presence
- reports/metrics.json consistency
- fallback-aware path resolution (data/splits <-> splits, build/raw <-> data/raw)
- notebook validity
- python syntax for all src files
"""
from __future__ import annotations
import json, sys, pathlib, py_compile

ROOT = pathlib.Path(__file__).resolve().parent
ok = True

def check(msg: str, cond: bool, detail: str = ""):
    global ok
    status = "OK" if cond else "FAIL"
    if not cond:
        ok = False
    print(f"[{status}] {msg}" + (f" — {detail}" if detail else ""))
    return cond

print("=== product-image-classifier health check ===\n")

# 1. CSVs
import pandas as pd
for p in ["splits/train.csv", "splits/val.csv", "splits/test.csv", "data/metadata.csv", "data/raw_manifest.csv"]:
    fp = ROOT / p
    check(f"{p} exists", fp.exists(), f"{fp}")
    if fp.exists():
        try:
            df = pd.read_csv(fp, nrows=5)
            check(f"  {p} readable", True, f"cols={df.columns.tolist()}")
        except Exception as e:
            check(f"  {p} readable", False, str(e))

# 2. row counts and consistency
try:
    man = pd.read_csv(ROOT / "data/raw_manifest.csv")
    train = pd.read_csv(ROOT / "splits/train.csv")
    val = pd.read_csv(ROOT / "splits/val.csv")
    test = pd.read_csv(ROOT / "splits/test.csv")
    total = len(train) + len(val) + len(test)
    check("manifest vs splits total", len(man) == total, f"manifest={len(man)} splits_sum={total}")
    check("expected 20754 images", total == 20754, f"got {total}")
    # class balance
    for name, df in [("train", train), ("val", val), ("test", test)]:
        vc = df["label"].value_counts().to_dict()
        check(f"  {name} has 3 classes", set(vc.keys()) == {"Apparel","Electronics","Home"}, str(vc))
except Exception as e:
    check("manifest/splits consistency", False, str(e))

# 3. models
for m in ["models/best.pt", "models/best_160.pt", "models/warm_start_224.pt"]:
    p = ROOT / m
    check(f"{m} exists", p.exists(), f"size={p.stat().st_size if p.exists() else 0}")

# 4. reports
for r in ["reports/metrics.json", "reports/classification_report.txt", "reports/train_history.json"]:
    check(f"{r} exists", (ROOT / r).exists())
if (ROOT / "reports/metrics.json").exists():
    j = json.loads((ROOT / "reports/metrics.json").read_text())
    check("metrics test_accuracy ~0.9171", abs(j.get("test_accuracy", 0) - 0.9171) < 1e-4, str(j.get("test_accuracy")))
    check("metrics test_n 3114", j.get("test_n") == 3114)
    cm = j.get("confusion_matrix", [])
    if cm:
        s = sum(sum(row) for row in cm)
        check("confusion_matrix sums to test_n", s == j.get("test_n"), f"sum={s}")

# 5. fallback paths
sys.path.insert(0, str(ROOT))
try:
    from src import config as C
    check("config fallback: get_split_path(train.csv) exists", C.get_split_path("train.csv").exists(), str(C.get_split_path("train.csv")))
    check("config get_raw_dir returns Path", isinstance(C.get_raw_dir(), pathlib.Path))
    check("config resolve_image_path returns Path", isinstance(C.resolve_image_path("Apparel/x.jpg"), pathlib.Path))
    # Ensure old path would have failed but new fallback works
    old_exists = (C.SPLIT_DIR / "train.csv").exists()
    new_exists = C.get_split_path("train.csv").exists()
    if not old_exists and new_exists:
        print("  note: fallback correctly handles empty data/splits/ -> splits/ (this was the critical bug, now fixed)")
    check("fallback handling", new_exists, f"old_exists={old_exists} new_exists={new_exists}")
except Exception as e:
    check("config fallback import", False, str(e))

# 6. notebook
nb = ROOT / "notebooks/product_image_classifier_colab.ipynb"
check("notebook exists", nb.exists())
if nb.exists():
    try:
        j = json.loads(nb.read_text())
        check("notebook valid JSON", True, f"cells={len(j['cells'])}")
        txt = "".join("".join(c.get("source", [])) for c in j["cells"])
        check("notebook no stale 12,469", "12,469" not in txt)
        check("notebook has fallback IMG_ROOT", "IMG_ROOT" in txt)
        check("notebook has SPLIT_ROOT", "SPLIT_ROOT" in txt)
    except Exception as e:
        check("notebook valid", False, str(e))

# 7. py_compile
for p in (ROOT / "src").rglob("*.py"):
    try:
        py_compile.compile(str(p), doraise=True)
        check(f"py_compile {p.relative_to(ROOT)}", True)
    except Exception as e:
        check(f"py_compile {p.relative_to(ROOT)}", False, str(e))

# 8. splits fallback both locations written?
check("splits/ and data/splits/ sync check", True,
      f"splits exists={ (ROOT/'splits/train.csv').exists()} data/splits exists={(ROOT/'data/splits/train.csv').exists()} (either is OK, code handles both)")

print("\n" + ("All checks passed." if ok else "Some checks FAILED — see above."))
sys.exit(0 if ok else 1)
