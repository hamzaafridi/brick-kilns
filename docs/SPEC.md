# Spec: Lahore brick-kiln detector (v1)

Agent-implementable specification for the Lahore pilot. Open data and open tools only.

## Destination

A supervised brick-kiln detector over **Lahore + Kasur + Sheikhupura + Nankana Sahib** that:

1. Uses **Sentinel-2 L2A** via Element 84 Earth Search STAC + anonymous AWS Open Data COGs.
2. Trains on chips around **PAQI** kiln points (Urban Unit census has no public dump; dashboard often down).
3. Emits **candidate points** (GeoJSON) + an **accuracy report** vs PAQI.
4. Presents results on an **interactive HTML map** (`web/index.html`).

## AOI

- File: `data/aoi/lahore_pilot.geojson`
- CRS: WGS84 (CRS84)
- Geometry: bbox union covering the four districts (approx. lon 73.50–74.70, lat 30.85–31.95)

## Imagery

- STAC: `https://earth-search.aws.element84.com/v1`, collection `sentinel-2-l2a`
- Pixels: public HTTPS COGs (`AWS_NO_SIGN_REQUEST=YES`)
- Season: Nov–Feb window (winter kiln season)
- Chip: **128×128** @ 10 m (~1.28 km), RGB+NIR bands

## Labels

- Primary intended GT: Urban Unit — **blocked** (no bulk file; host down). Recorded as risk.
- Working GT: PAQI Google My Maps KML (`docs/research/kiln-ground-truth.md`)
- Positives: chips centered on AOI-clipped PAQI points
- Negatives: AOI grid points ≥ 800 m from any PAQI point
- Split: 80/20 random held-out for metrics (not spatial block — note for v2)

## Model

- Features: per-band stats, NDVI / built-up proxy, edge energy, RGB histograms
- Classifier: RandomForest (`data/models/kiln_rf.joblib`)
- Borrowed from research: SentinelKilnDB chip size; SustainBench chip-classifier framing; Nazir indices optional later

## Outputs

| Artifact | Path |
| --- | --- |
| Candidates GeoJSON | `data/outputs/candidates.geojson` |
| Accuracy report | `data/outputs/accuracy_report.json` |
| Train metrics | `data/outputs/train_metrics.json` |
| Interactive map | `web/index.html` (+ `web/data/*`) |

### Candidate schema

```json
{
  "type": "Feature",
  "properties": {
    "id": "cand-123",
    "score": 0.81,
    "scene": "S2B_…_L2A",
    "role": "candidate"
  },
  "geometry": { "type": "Point", "coordinates": [lon, lat] }
}
```

### Accuracy report fields

- `precision_vs_gt`, `recall_vs_gt` at `match_radius_m` (default 500 m)
- `matched_gt`, `gt_count`, `candidate_count`, `threshold`

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_pipeline.py --steps all
python -m http.server 8000 --directory web
# open http://localhost:8000
```

## Out of scope (v1)

- Historical / change detection
- Community crowdvoting product
- Paid APIs / requester-pays L1C
- All-Pakistan coverage
- Urban Unit redistribution until license + export obtained
