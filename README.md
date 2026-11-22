# brick-kilns

Detect brick kilns around **Lahore** (plus Kasur, Sheikhupura, Nankana Sahib) from **open Sentinel-2** imagery, score against **PAQI** ground truth, and explore results on an interactive map.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py --steps all
python -m http.server 8000 --directory web
```

Open [http://localhost:8000](http://localhost:8000).

## What you get

| Piece | Location |
| --- | --- |
| Spec | [`docs/SPEC.md`](docs/SPEC.md) |
| Research notes | [`docs/research/`](docs/research/) |
| AOI | `data/aoi/lahore_pilot.geojson` |
| PAQI GT (AOI) | `data/ground_truth/paqi_lahore_aoi.geojson` |
| Model | `data/models/kiln_rf.joblib` |
| Candidates | `data/outputs/candidates.geojson` |
| Accuracy report | `data/outputs/accuracy_report.json` |
| Map | `web/index.html` |

## Stack

Python · Element 84 Earth Search STAC · AWS Open Data Sentinel-2 COGs · scikit-learn · Leaflet

## Constraints

Open data + open tools only (no paid imagery APIs). Urban Unit census has no public point dump; v1 uses PAQI crowd-sourced points as available ground truth.

## Wayfinding

Planning map: [Brick kiln detector spec (Lahore pilot)](https://github.com/hamzaafridi/brick-kilns/issues/1)
