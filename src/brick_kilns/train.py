from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import numpy as np
from shapely.geometry import Point
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    precision_recall_fscore_support,
    roc_auc_score,
)
from tqdm import tqdm

from .aoi import load_aoi
from .config import (
    CHIPS_DIR,
    MAX_TRAIN_NEGATIVES,
    MAX_TRAIN_POSITIVES,
    MIN_NEG_DISTANCE_M,
    MODELS_DIR,
    OUTPUTS_DIR,
    RANDOM_SEED,
    TRAIN_FRACTION,
)
from .features import chip_features
from .ground_truth import load_aoi_points
from .imagery import grid_points, pick_scene_for_point, read_chip_rgbnir, search_scenes


def _far_enough(lon: float, lat: float, positives: list[dict], min_m: float) -> bool:
    for p in positives:
        # rough meters
        dlat = (lat - p["lat"]) * 111_320.0
        dlon = (lon - p["lon"]) * 111_320.0 * np.cos(np.deg2rad(lat))
        if (dlat * dlat + dlon * dlon) ** 0.5 < min_m:
            return False
    return True


def collect_dataset(scenes, positives: list[dict], seed: int = RANDOM_SEED):
    rng = random.Random(seed)
    pos = positives[:]
    rng.shuffle(pos)
    pos = pos[:MAX_TRAIN_POSITIVES]

    X: list[np.ndarray] = []
    y: list[int] = []
    meta: list[dict] = []

    print(f"Collecting up to {len(pos)} positive chips…")
    for p in tqdm(pos):
        scene = pick_scene_for_point(scenes, p["lon"], p["lat"])
        if scene is None:
            continue
        chip = read_chip_rgbnir(scene.item, p["lon"], p["lat"])
        if chip is None:
            continue
        X.append(chip_features(chip))
        y.append(1)
        meta.append({"id": p["id"], "lon": p["lon"], "lat": p["lat"], "label": 1, "scene": scene.id})

    aoi = load_aoi()
    candidates = grid_points(aoi, stride_m=1200, limit=MAX_TRAIN_NEGATIVES * 5)
    rng.shuffle(candidates)
    print(f"Collecting up to {MAX_TRAIN_NEGATIVES} negative chips…")
    neg_count = 0
    for lon, lat in tqdm(candidates):
        if neg_count >= MAX_TRAIN_NEGATIVES:
            break
        if not _far_enough(lon, lat, positives, MIN_NEG_DISTANCE_M):
            continue
        scene = pick_scene_for_point(scenes, lon, lat)
        if scene is None:
            continue
        chip = read_chip_rgbnir(scene.item, lon, lat)
        if chip is None:
            continue
        X.append(chip_features(chip))
        y.append(0)
        meta.append({"id": f"neg-{neg_count}", "lon": lon, "lat": lat, "label": 0, "scene": scene.id})
        neg_count += 1

    return np.asarray(X), np.asarray(y), meta


def train_and_eval() -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CHIPS_DIR.mkdir(parents=True, exist_ok=True)

    positives = load_aoi_points()
    print(f"AOI ground-truth points: {len(positives)}")
    scenes = search_scenes(limit=60)
    print(f"STAC scenes available: {len(scenes)}")
    if not scenes:
        raise RuntimeError("No Sentinel-2 scenes found for AOI/datetime")

    X, y, meta = collect_dataset(scenes, positives)
    if len(X) < 20 or y.sum() < 5 or (len(y) - y.sum()) < 5:
        raise RuntimeError(f"Not enough labeled chips to train (n={len(X)}, pos={int(y.sum())})")

    rng = np.random.default_rng(RANDOM_SEED)
    idx = np.arange(len(X))
    rng.shuffle(idx)
    cut = int(len(idx) * TRAIN_FRACTION)
    train_idx, test_idx = idx[:cut], idx[cut:]
    # Ensure both classes in test
    if len(set(y[test_idx].tolist())) < 2:
        test_idx = idx[-max(10, len(idx) // 5) :]
        train_idx = idx[: -max(10, len(idx) // 5)]

    Xtr, Xte = X[train_idx], X[test_idx]
    ytr, yte = y[train_idx], y[test_idx]

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    clf.fit(Xtr, ytr)
    proba = clf.predict_proba(Xte)[:, 1]
    pred = (proba >= 0.5).astype(int)

    precision, recall, f1, _ = precision_recall_fscore_support(
        yte, pred, average="binary", zero_division=0
    )
    metrics = {
        "n_total": int(len(X)),
        "n_pos": int(y.sum()),
        "n_neg": int(len(y) - y.sum()),
        "n_train": int(len(train_idx)),
        "n_test": int(len(test_idx)),
        "accuracy": float(accuracy_score(yte, pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc_score(yte, proba)) if len(set(yte.tolist())) > 1 else None,
        "average_precision": float(average_precision_score(yte, proba))
        if len(set(yte.tolist())) > 1
        else None,
        "classification_report": classification_report(yte, pred, digits=3),
        "ground_truth_source": "PAQI (Urban Unit unavailable)",
        "imagery": "Sentinel-2 L2A via Earth Search STAC + AWS Open Data COGs",
    }

    model_path = MODELS_DIR / "kiln_rf.joblib"
    joblib.dump({"model": clf, "scenes_hint": [s.id for s in scenes[:10]]}, model_path)
    (OUTPUTS_DIR / "train_metrics.json").write_text(json.dumps(metrics, indent=2))
    (OUTPUTS_DIR / "train_meta.json").write_text(json.dumps(meta, indent=2))
    print(metrics["classification_report"])
    print(f"Saved model → {model_path}")
    return metrics
