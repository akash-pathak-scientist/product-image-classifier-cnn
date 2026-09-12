"""Central configuration for the Product-Image Classifier project."""
from pathlib import Path

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = ROOT / "build" / "raw"      # bulky images live in build/ (snapshot-excluded)
SPLIT_DIR = DATA_DIR / "splits"       # train.csv / val.csv / test.csv
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"

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
