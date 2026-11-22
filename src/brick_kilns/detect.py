from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from shapely.geometry import Point, mapping
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from .aoi import load_aoi
from .config import (
    MAX_SCAN_CHIPS,
    MODELS_DIR,
    OUTPUTS_DIR,
    SCORE_THRESHOLD,
)
from .features import chip_features
from .ground_truth import load_aoi_points
from .imagery import grid_points, pick_scene_for_point, read_chip_rgbnir, search_scenes


def _nms(points: list[dict], min_dist_m: float = 400.0) -> list[dict]:
    if not points:
        return []
    pts = sorted(points, key=lambda p: -p["score"])
    kept: list[dict] = []
    for p in pts:
        ok = True
        for k in kept:
            dlat = (p["lat"] - k["lat"]) * 111_320.0
            dlon = (p["lon"] - k["lon"]) * 111_320.0 * np.cos(np.deg2rad(p["lat"]))
            if (dlat * dlat + dlon * dlon) ** 0.5 < min_dist_m:
                ok = False
                break
        if ok:
            kept.append(p)
    return kept


def match_to_gt(candidates: list[dict], gt: list[dict], radius_m: float = 500.0) -> dict:
    if not candidates or not gt:
        return {
            "matched_candidates": 0,
            "matched_gt": 0,
            "precision_vs_gt": None,
            "recall_vs_gt": None,
            "gt_count": len(gt),
            "candidate_count": len(candidates),
            "match_radius_m": radius_m,
        }
    gt_xy = np.array([[p["lon"], p["lat"]] for p in gt])
    # Convert approx to meters locally
    lat0 = float(np.mean(gt_xy[:, 1]))
    scale = np.array([111_320.0 * np.cos(np.deg2rad(lat0)), 111_320.0])
    gt_m = gt_xy * scale
    cand_m = np.array([[c["lon"], c["lat"]] for c in candidates]) * scale
    nn = NearestNeighbors(n_neighbors=1, algorithm="ball_tree").fit(gt_m)
    dists, idxs = nn.kneighbors(cand_m)
    matched_cand = int(np.sum(dists[:, 0] <= radius_m))
    matched_gt_ids = set(int(i) for i, d in zip(idxs[:, 0], dists[:, 0]) if d <= radius_m)
    precision = matched_cand / len(candidates)
    recall = len(matched_gt_ids) / len(gt)
    return {
        "matched_candidates": matched_cand,
        "matched_gt": len(matched_gt_ids),
        "precision_vs_gt": float(precision),
        "recall_vs_gt": float(recall),
        "gt_count": len(gt),
        "candidate_count": len(candidates),
        "match_radius_m": radius_m,
    }


def detect(threshold: float = SCORE_THRESHOLD, max_chips: int = MAX_SCAN_CHIPS) -> dict:
    model_path = MODELS_DIR / "kiln_rf.joblib"
    bundle = joblib.load(model_path)
    clf = bundle["model"]

    aoi = load_aoi()
    scenes = search_scenes(limit=60)
    if not scenes:
        raise RuntimeError("No scenes for detection")

    # Stratified scan: denser random sample across AOI for tractable first run
    pts = grid_points(aoi, stride_m=1500, limit=max_chips)
    print(f"Scanning {len(pts)} locations…")

    raw: list[dict] = []
    for i, (lon, lat) in enumerate(tqdm(pts)):
        scene = pick_scene_for_point(scenes, lon, lat)
        if scene is None:
            continue
        chip = read_chip_rgbnir(scene.item, lon, lat)
        if chip is None:
            continue
        feat = chip_features(chip).reshape(1, -1)
        score = float(clf.predict_proba(feat)[0, 1])
        if score >= threshold:
            raw.append(
                {
                    "id": f"cand-{i}",
                    "lon": lon,
                    "lat": lat,
                    "score": score,
                    "scene": scene.id,
                }
            )

    candidates = _nms(raw, min_dist_m=500.0)
    gt = load_aoi_points()
    report = match_to_gt(candidates, gt, radius_m=500.0)
    report["threshold"] = threshold
    report["raw_hits"] = len(raw)
    report["candidates_after_nms"] = len(candidates)

    gj = {
        "type": "FeatureCollection",
        "name": "kiln_candidates",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "id": c["id"],
                    "score": round(c["score"], 4),
                    "scene": c["scene"],
                    "role": "candidate",
                },
                "geometry": mapping(Point(c["lon"], c["lat"])),
            }
            for c in candidates
        ],
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUTS_DIR / "candidates.geojson"
    out_path.write_text(json.dumps(gj, indent=2))
    (OUTPUTS_DIR / "accuracy_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return {"candidates_path": str(out_path), "report": report, "candidates": candidates}
