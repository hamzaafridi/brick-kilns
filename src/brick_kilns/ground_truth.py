from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from shapely.geometry import Point, mapping

from .aoi import load_aoi
from .config import GT_DIR, PAQI_KML_URL, PAQI_MAP_VIEW


KML_NS = {"k": "http://www.opengis.net/kml/2.2"}


def download_paqi_kml(dest: Path | None = None) -> Path:
    GT_DIR.mkdir(parents=True, exist_ok=True)
    dest = dest or (GT_DIR / "paqi_pakistan.kml")
    r = requests.get(PAQI_KML_URL, timeout=120, headers={"User-Agent": "brick-kilns/0.1"})
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def parse_kml_points(kml_path: Path) -> list[dict]:
    tree = ET.parse(kml_path)
    root = tree.getroot()
    points: list[dict] = []
    for i, pm in enumerate(root.findall(".//k:Placemark", KML_NS)):
        name_el = pm.find("k:name", KML_NS)
        name = (name_el.text or f"Point {i}").strip() if name_el is not None else f"Point {i}"
        coord_el = pm.find(".//k:coordinates", KML_NS)
        if coord_el is None or not coord_el.text:
            continue
        parts = coord_el.text.strip().split(",")
        if len(parts) < 2:
            continue
        lon, lat = float(parts[0]), float(parts[1])
        points.append({"id": f"paqi-{i}", "name": name, "lon": lon, "lat": lat, "source": "paqi"})
    return points


def filter_to_aoi(points: list[dict], aoi=None) -> list[dict]:
    aoi = aoi or load_aoi()
    out = []
    for p in points:
        if aoi.contains(Point(p["lon"], p["lat"])):
            out.append(p)
    return out


def to_geojson(points: list[dict], name: str) -> dict:
    return {
        "type": "FeatureCollection",
        "name": name,
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "id": p["id"],
                    "name": p["name"],
                    "source": p["source"],
                    "role": "ground_truth",
                },
                "geometry": mapping(Point(p["lon"], p["lat"])),
            }
            for p in points
        ],
    }


def write_geojson(gj: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gj, indent=2))
    return path


def ingest_paqi() -> dict:
    """Download PAQI KML, clip to AOI, write GeoJSON. Returns summary stats."""
    kml = download_paqi_kml()
    all_pts = parse_kml_points(kml)
    aoi_pts = filter_to_aoi(all_pts)
    write_geojson(to_geojson(all_pts, "paqi_pakistan"), GT_DIR / "paqi_pakistan.geojson")
    write_geojson(to_geojson(aoi_pts, "paqi_lahore_aoi"), GT_DIR / "paqi_lahore_aoi.geojson")
    meta = {
        "source": "PAQI Google My Maps",
        "map_url": PAQI_MAP_VIEW,
        "kml_url": PAQI_KML_URL,
        "nationwide_count": len(all_pts),
        "aoi_count": len(aoi_pts),
        "note": (
            "Urban Unit census has no public point dump and dashboard was unreachable; "
            "PAQI crowd map used as available ground truth for v1."
        ),
    }
    (GT_DIR / "manifest.json").write_text(json.dumps(meta, indent=2))
    return meta


def load_aoi_points(path: Path | None = None) -> list[dict]:
    path = path or (GT_DIR / "paqi_lahore_aoi.geojson")
    gj = json.loads(path.read_text())
    pts = []
    for ft in gj["features"]:
        lon, lat = ft["geometry"]["coordinates"][:2]
        props = ft["properties"]
        pts.append(
            {
                "id": props.get("id"),
                "name": props.get("name"),
                "lon": lon,
                "lat": lat,
                "source": props.get("source", "paqi"),
            }
        )
    return pts
