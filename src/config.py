"""Central configuration for the Product-Image Classifier project."""
from pathlib import Path

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = ROOT / "build" / "raw"      # primary: bulky images (snapshot-excluded, .gitignore: build/)
RAW_DIR_ALT = ROOT / "data" / "raw"   # fallback: dataset.zip / notebook extracts here
SPLIT_DIR = DATA_DIR / "splits"       # primary: train.csv / val.csv / test.csv
SPLIT_DIR_ALT = ROOT / "splits"       # fallback: tracked in git (data/splits is gitignored)
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"


def get_splits_dir() -> Path:
    """Return the splits directory that actually contains CSVs (fallback-aware)."""
    if (SPLIT_DIR / "train.csv").exists():
        return SPLIT_DIR
    if (SPLIT_DIR_ALT / "train.csv").exists():
        return SPLIT_DIR_ALT
    return SPLIT_DIR  # default for writing (will be created)


def get_split_path(name: str) -> Path:
    """Resolve a single split CSV (e.g. 'train.csv') with fallback."""
    p = SPLIT_DIR / name
    if p.exists():
        return p
    p2 = SPLIT_DIR_ALT / name
    if p2.exists():
        return p2
    return p


def get_raw_dir() -> Path:
    """Return the image root that actually contains data (fallback-aware)."""
    # prefer whichever has at least one class sub-folder
    for cand in (RAW_DIR, RAW_DIR_ALT):
        if (cand / "Apparel").exists() or (cand / "Electronics").exists() or (cand / "Home").exists():
            return cand
    # if neither has class folders, prefer primary if it exists
    if RAW_DIR.exists() and any(RAW_DIR.iterdir()):
        return RAW_DIR
    if RAW_DIR_ALT.exists() and any(RAW_DIR_ALT.iterdir()):
        return RAW_DIR_ALT
    return RAW_DIR


def resolve_image_path(rel: str | Path) -> Path:
    """Resolve a manifest-relative image path (e.g. 'Apparel/xxx.jpg') with fallback."""
    rel = Path(rel)
    for base in (RAW_DIR, RAW_DIR_ALT):
        p = base / rel
        if p.exists():
            return p
    return RAW_DIR / rel

# ---------------------------------------------------------------- labels ---
# The three coarse catalogue domains (Flipkart-style taxonomy).
CLASSES = ["Apparel", "Electronics", "Home"]

# Source: McAuley-Lab/Amazon-Reviews-2023  (public, streamed over HTTP).
# Each entry maps a domain meta file to our coarse label.
DATASET_ID = "McAuley-Lab/Amazon-Reviews-2023"
BASE_URL = (
    "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/"
    "main/raw/meta_categories"
)
# exact byte sizes of the source files (used for random-offset sampling)
DOMAIN_FILES = {
    "Apparel": {
        "file": "meta_Amazon_Fashion.jsonl",
        "size": 1_422_365_805,
        "label": "Apparel",
    },
    "Electronics": {
        "file": "meta_Electronics.jsonl",
        "size": 5_246_144_413,
        "label": "Electronics",
    },
    "Home": {
        "file": "meta_Home_and_Kitchen.jsonl",
        "size": 11_788_767_944,
        "label": "Home",
    },
}

# --------------------------------------------------------------- sampling --
SEED = 42
TARGET_PER_CLASS = 7000        # metadata rows sampled per class
OFFSET_SAMPLES = 16            # random offsets per domain file
CHUNK_BYTES = 8 * 1024 * 1024  # bytes read per offset window

# ------------------------------------------------------------ image fetch --
FETCH_WORKERS = 24
FETCH_TIMEOUT = (8, 20)
MAX_SIDE = 256                 # stored image long side (training res is smaller)
JPEG_QUALITY = 85

# ------------------------------------------------------------- modelling ---
IMG_SIZE = 112
BATCH_SIZE = 64
EPOCHS = 30
LR = 1.5e-3
WEIGHT_DECAY = 1e-4
LABEL_SMOOTHING = 0.05
DROPOUT = 0.30
EARLY_STOP_PATIENCE = 8       # epochs without val-acc improvement
TARGET_VAL_ACC = 0.88         # stop a bit above the project goal (0.85)
HOLD_TARGET_EPOCHS = 3        # keep training this many epochs after target

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

for _d in (DATA_DIR, RAW_DIR, SPLIT_DIR, MODELS_DIR, REPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
# also ensure fallback dirs exist when needed (no error if they already exist)
for _d in (RAW_DIR_ALT, SPLIT_DIR_ALT):
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
