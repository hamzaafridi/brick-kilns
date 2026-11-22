from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union

from .config import AOI_PATH


def load_aoi(path: Path | None = None):
    path = path or AOI_PATH
    with path.open() as f:
        gj = json.load(f)
    geoms = [shape(ft["geometry"]) for ft in gj["features"]]
    return unary_union(geoms)


def aoi_bbox(aoi=None) -> tuple[float, float, float, float]:
    aoi = aoi or load_aoi()
    minx, miny, maxx, maxy = aoi.bounds
    return (minx, miny, maxx, maxy)


def aoi_feature_collection(path: Path | None = None) -> dict:
    path = path or AOI_PATH
    with path.open() as f:
        return json.load(f)


def bbox_polygon(bbox: tuple[float, float, float, float]):
    return box(*bbox)
