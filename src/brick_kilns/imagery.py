from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pystac_client
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from shapely.geometry import Point, box
from shapely.ops import transform as shp_transform

from .aoi import aoi_bbox, load_aoi
from .config import (
    CHIP_METERS,
    CHIP_SIZE,
    DATETIME_RANGE,
    MAX_CLOUD,
    SCAN_STRIDE_PX,
    STAC_COLLECTION,
    STAC_URL,
)

# Quiet noisy GDAL/AWS warnings for anonymous public COGs
warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)


@dataclass
class Scene:
    id: str
    item: object
    bbox: tuple[float, float, float, float]


def search_scenes(
    bbox: tuple[float, float, float, float] | None = None,
    datetime_range: str = DATETIME_RANGE,
    max_cloud: float = MAX_CLOUD,
    limit: int = 40,
) -> list[Scene]:
    bbox = bbox or aoi_bbox()
    catalog = pystac_client.Client.open(STAC_URL)
    search = catalog.search(
        collections=[STAC_COLLECTION],
        bbox=list(bbox),
        datetime=datetime_range,
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=limit,
    )
    scenes: list[Scene] = []
    for item in search.items():
        b = item.bbox
        scenes.append(Scene(id=item.id, item=item, bbox=(b[0], b[1], b[2], b[3])))
    # Prefer low cloud
    scenes.sort(key=lambda s: s.item.properties.get("eo:cloud_cover", 100))
    return scenes


def _asset_href(item, key: str) -> str | None:
    asset = item.assets.get(key)
    if asset is None:
        return None
    return asset.href


def chip_bounds(lon: float, lat: float, meters: float = CHIP_METERS) -> tuple[float, float, float, float]:
    # Approx degrees at Lahore latitude (~31.5N)
    dlat = (meters / 2.0) / 111_320.0
    dlon = (meters / 2.0) / (111_320.0 * np.cos(np.deg2rad(lat)))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def _read_bands(item, lon: float, lat: float, keys: tuple[str, ...], size: int) -> np.ndarray | None:
    hrefs = [_asset_href(item, k) for k in keys]
    if any(h is None for h in hrefs):
        return None

    wgs_bounds = chip_bounds(lon, lat)
    geom = box(*wgs_bounds)
    bands = []
    try:
        with rasterio.Env(AWS_NO_SIGN_REQUEST="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
            with rasterio.open(hrefs[0]) as ds0:
                transformer = Transformer.from_crs("EPSG:4326", ds0.crs, always_xy=True)
                proj_geom = shp_transform(transformer.transform, geom)
                minx, miny, maxx, maxy = proj_geom.bounds
            for href in hrefs:
                with rasterio.open(href) as ds:
                    window = from_bounds(minx, miny, maxx, maxy, transform=ds.transform)
                    data = ds.read(
                        1,
                        window=window,
                        out_shape=(size, size),
                        resampling=Resampling.bilinear,
                        boundless=True,
                        fill_value=0,
                    )
                    bands.append(data.astype(np.float32))
    except Exception:
        return None

    arr = np.stack(bands, axis=-1)
    if np.nanmax(arr) > 1.5:
        arr = arr / 10000.0
    arr = np.clip(arr, 0, 1)
    if float(np.mean(arr[..., :3] == 0)) > 0.6:
        return None
    return arr


def read_chip_rgb(item, lon: float, lat: float, size: int = CHIP_SIZE) -> np.ndarray | None:
    """Return HxWx3 float32 RGB in [0,1] from Sentinel-2 L2A COGs, or None on failure."""
    return _read_bands(item, lon, lat, ("red", "green", "blue"), size)


def read_chip_rgbnir(item, lon: float, lat: float, size: int = CHIP_SIZE) -> np.ndarray | None:
    return _read_bands(item, lon, lat, ("red", "green", "blue", "nir"), size)


def pick_scene_for_point(scenes: list[Scene], lon: float, lat: float):
    pt = Point(lon, lat)
    for s in scenes:
        if box(*s.bbox).contains(pt):
            return s
    return None


def grid_points(
    aoi=None,
    stride_m: float = SCAN_STRIDE_PX * 10,
    limit: int | None = None,
) -> list[tuple[float, float]]:
    aoi = aoi or load_aoi()
    minx, miny, maxx, maxy = aoi.bounds
    # Degree steps
    mid_lat = (miny + maxy) / 2
    dlat = stride_m / 111_320.0
    dlon = stride_m / (111_320.0 * np.cos(np.deg2rad(mid_lat)))
    pts: list[tuple[float, float]] = []
    y = miny + dlat / 2
    while y <= maxy:
        x = minx + dlon / 2
        while x <= maxx:
            if aoi.contains(Point(x, y)):
                pts.append((x, y))
                if limit and len(pts) >= limit:
                    return pts
            x += dlon
        y += dlat
    return pts
