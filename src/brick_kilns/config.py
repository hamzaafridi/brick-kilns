from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
AOI_PATH = DATA / "aoi" / "lahore_pilot.geojson"
GT_DIR = DATA / "ground_truth"
CHIPS_DIR = DATA / "chips"
MODELS_DIR = DATA / "models"
OUTPUTS_DIR = DATA / "outputs"
WEB_DIR = ROOT / "web"
WEB_DATA = WEB_DIR / "data"

PAQI_KML_URL = (
    "https://www.google.com/maps/d/kml"
    "?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&forcekml=1"
)
PAQI_MAP_VIEW = (
    "https://www.google.com/maps/d/viewer"
    "?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&usp=sharing"
)

STAC_URL = "https://earth-search.aws.element84.com/v1"
STAC_COLLECTION = "sentinel-2-l2a"

# SentinelKilnDB-inspired chip params @ 10 m
CHIP_SIZE = 128
CHIP_METERS = CHIP_SIZE * 10
SCAN_STRIDE_PX = 96  # ~30 px overlap relative to 128
MIN_NEG_DISTANCE_M = 800.0

# Prefer winter kiln season
DATETIME_RANGE = "2024-11-01T00:00:00Z/2025-02-28T23:59:59Z"
MAX_CLOUD = 20

RANDOM_SEED = 42
TRAIN_FRACTION = 0.8
SCORE_THRESHOLD = 0.55
MAX_TRAIN_POSITIVES = 100
MAX_TRAIN_NEGATIVES = 200
MAX_SCAN_CHIPS = 800  # keep first full run tractable
