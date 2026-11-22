# Free Sentinel-2 access path for Lahore pilot

**Ticket:** [#2](https://github.com/hamzaafridi/brick-kilns/issues/2)  
**Question:** Which free, open (non-billing) path should the v1 spec use to obtain Sentinel-2 imagery for the Lahore + Kasur + Sheikhupura + Nankana AOI — including search, download/COG access, and any practical quotas or auth requirements?  
**Constraint:** open data + open tools only; no paid APIs; no free tiers that can turn into billing.  
**Researched:** 2026-11-22

## Recommendation (one line)

Use **Element 84 Earth Search STAC v1** (`https://earth-search.aws.element84.com/v1`) to search collection **`sentinel-2-l2a`**, then read band assets as **anonymous HTTPS Cloud-Optimized GeoTIFFs** from the AWS Open Data buckets (`sentinel-cogs` / optionally Collection-1 `e84-earth-search-sentinel-data`) — **no account, no credentials, no requester-pays charges**.

## Why this path

| Criterion | Earth Search + AWS L2A COGs | Microsoft Planetary Computer | CDSE (Copernicus Data Space Ecosystem) |
| --- | --- | --- | --- |
| Fits “no billing / no credit-card free tier” | Yes — public S3, `RequesterPays: False` | Yes for anonymous data/API use | Free quotas; commercial upgrade path exists via CREODIAS |
| Auth for search | None | None (anonymous STAC) | Account + OAuth for downloads |
| Auth for pixels | None (HTTPS URLs) | Anonymous SAS token (sign URLs) | OAuth bearer token |
| Format | Native COGs (band-level) | COGs behind SAS | Product packages / APIs; COG HTTP also available under quota |
| Agent-friendly chip pipeline | Excellent (`pystac-client` + `rasterio`/`rioxarray` windowed reads) | Excellent, plus `planetary-computer.sign` | Good, more ceremony |

For a supervised kiln-chip detector that needs **search → windowed band reads**, Earth Search + public L2A COGs is the lowest-friction path that stays strictly non-billing.

## Recommended stack

### 1. Search

- **Endpoint:** `https://earth-search.aws.element84.com/v1`  
  Source: [Element84/earth-search README](https://github.com/Element84/earth-search/blob/main/README.md) (homepage listed as Earth Search STAC API).
- **Collection (default for v1):** `sentinel-2-l2a` — L2A with COG assets (and JP2 references).  
  Source: [Earth Search collection notes](https://github.com/Element84/earth-search/blob/main/docs/collections/sentinel-2-l2a.md); [AWS RODA Sentinel-2 COGs](https://registry.opendata.aws/sentinel-2-l2a-cogs/).
- **Optional Collection 1:** `sentinel-2-c1-l2a` — COGs processed to baseline ≥ 5.0 only.  
  Source: same collection notes.
- **Client:** open-source [`pystac-client`](https://github.com/stac-utils/pystac-client) (or raw STAC HTTP).
- **Datetime note:** this API rejects date-only ranges; use RFC 3339 instants, e.g. `2024-10-01T00:00:00Z/2024-10-31T23:59:59Z` (verified against the live API on 2026-11-22).

Example search shape (Lahore-centered bbox covering the four districts at coarse grain):

```python
import pystac_client

catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[73.5, 30.7, 74.8, 32.0],  # Lahore + Kasur + Sheikhupura + Nankana Sahib (approx)
    datetime="2024-10-01T00:00:00Z/2024-10-31T23:59:59Z",
    query={"eo:cloud_cover": {"lt": 20}},
)
items = list(search.items())
```

**Live check (2026-11-22):** POST search for `bbox=[73.8,30.9,74.7,31.8]`, October 2024, collection `sentinel-2-l2a` returned matches (e.g. `S2B_43RCQ_20241031_0_L2A`, MGRS `43RCQ`, near-zero cloud). Collection `sentinel-2-c1-l2a` also returned matches for the same AOI/month.

### 2. Download / COG access

- Prefer **HTTPS asset hrefs** returned on each STAC item (Earth Search uses `https://` for public assets; requester-pays assets would be `s3://` only).  
  Source: [Earth Search README — s3 vs http URLs](https://github.com/Element84/earth-search/blob/main/README.md).
- **Buckets (public, not requester-pays):**
  - `s3://sentinel-cogs` (region `us-west-2`) — classic L2A COGs; `RequesterPays: False`
  - `s3://e84-earth-search-sentinel-data` — Collection 1 L2A COGs; `RequesterPays: False`  
  Source: [awslabs/open-data-registry `sentinel-2-l2a-cogs.yaml`](https://raw.githubusercontent.com/awslabs/open-data-registry/main/datasets/sentinel-2-l2a-cogs.yaml); [RODA page](https://registry.opendata.aws/sentinel-2-l2a-cogs/).
- **No AWS account required** for these public objects; anonymous HTTP range requests work (verified: `HTTP 206 Partial Content` on a Lahore-tile `B04.tif` from `sentinel-cogs.s3.us-west-2.amazonaws.com`).
- Typical band asset keys on Earth Search L2A items include `blue`, `green`, `red`, `nir`, `swir16`, `swir22`, `scl`, etc. (COG `image/tiff; profile=cloud-optimized`). Read windows with GDAL/`rasterio` rather than downloading full scenes.

**Do not use for v1:** AWS `s3://sentinel-s2-l1c` — documented as **Requester Pays** (`RequesterPays: True`), which requires authenticated AWS requests and charges the requester for GET/transfer.  
Source: [awslabs/open-data-registry `sentinel-2.yaml`](https://github.com/awslabs/open-data-registry/blob/main/datasets/sentinel-2.yaml); [Amazon S3 Requester Pays docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html).

### 3. Auth & quotas

| Layer | Requirement | Practical limit |
| --- | --- | --- |
| Earth Search STAC | None | Best-effort community API; **no SLA / no guaranteed service** ([README](https://github.com/Element84/earth-search/blob/main/README.md)) |
| Public L2A COG HTTPS | None | No published hard download quota on the open-data registry entry; fair-use / rate limits may apply at the CDN/S3 edge |
| AWS L1C requester-pays | AWS credentials + accept charges | **Out of scope** under map billing constraint |

### 4. License / attribution

Sentinel data remain free, full and open under Copernicus rules; when redistributing or publishing derived products, attribute per the legal notice (e.g. “Copernicus Sentinel data [Year]” / “Contains modified Copernicus Sentinel data [Year]”).  
Source: [Sentinel Data Legal Notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice) (linked from RODA dataset license).

### 5. Processing-baseline caveat (chips)

From 2022-01-25, Baseline 04.00+ introduces a radiometric offset. Earth Search COG assets expose `raster:bands` `scale` / `offset`; apply them when comparing across baselines.  
Source: [Earth Search sentinel-2-l2a collection notes](https://github.com/Element84/earth-search/blob/main/docs/collections/sentinel-2-l2a.md); [ESA processing baseline 04.00 notice](https://sentinels.copernicus.eu/web/sentinel/-/copernicus-sentinel-2-processing-baseline-04-00-25-01-2022).

For more uniform Collection 1 processing, prefer `sentinel-2-c1-l2a` (v1) or Earth Search **v2 beta** `sentinel-2-l2a` (Collection 1 only). v2 is explicitly beta and may change.  
Source: [collection notes — v1 vs v2](https://github.com/Element84/earth-search/blob/main/docs/collections/sentinel-2-l2a.md).

## AOI notes (pilot)

- Pilot districts: **Lahore, Kasur, Sheikhupura, Nankana Sahib** (Punjab, Pakistan).
- Approximate WGS84 bbox used for verification: `[73.5, 30.7, 74.8, 32.0]`.
- Confirmed MGRS tiles overlapping the Lahore core in Oct 2024 searches include **`43RCQ` / `43RDQ`** (and neighboring `43R*` tiles for the wider four-district extent). Exact tile list for the full AOI should be derived from a final district polygon at implementation time.
- Map scope is **recent/clear scenes only** (not multi-year change detection) — filter with `eo:cloud_cover` and pick a small set of clear dates.

## Alternatives considered

### A. Microsoft Planetary Computer (acceptable backup)

- **Search:** `https://planetarycomputer.microsoft.com/api/stac/v1`, collection `sentinel-2-l2a`.  
  Source: [Reading data from the STAC API](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/).
- **Access:** Azure blob URLs signed with anonymous SAS tokens via Data Authentication API / `planetary-computer` Python package. Data described as free; STAC anonymous; assets need SAS.  
  Source: [Using Tokens for Data Access](https://planetarycomputer.microsoft.com/docs/concepts/sas/); [About / Preview](https://planetarycomputer.microsoft.com/docs/) (“publicly accessible… without an account”; anonymous downloads throttled).
- **Quotas:** rate limits and token expiry depend on region + optional subscription key; anonymous is allowed but more throttled. No credit-card requirement for anonymous use per those docs.
- **Why not primary:** still a Preview platform; every asset URL must be signed; slightly more moving parts than public HTTPS COGs.

### B. Copernicus Data Space Ecosystem (official, free with account)

- **Search:** STAC `https://stac.dataspace.copernicus.eu/v1/` (legacy catalogue STAC deprecated from 2025-11-17) and/or OData.  
  Source: [CDSE STAC docs](https://documentation.dataspace.copernicus.eu/APIs/STAC.html).
- **Download:** S3 / OData / STAC with OAuth; free **Copernicus General** quotas include e.g. 12 TB / 30 days transfer on IAD (then slowed, not billed), concurrent connection/bandwidth caps; Sentinel Hub path has monthly request/PU caps.  
  Source: [Quotas and Limitations](https://documentation.dataspace.copernicus.eu/Quotas.html); [FAQ](https://documentation.dataspace.copernicus.eu/FAQ.html).
- **Billing risk:** exceeding free quota slows access; **extra capacity is sold commercially** (CREODIAS / cloud credits). FAQ states free and commercial offerings share identity to transfer users. That adjacent commercial path makes CDSE a weaker fit for the map’s “no free tiers that can turn into billing” preference, even though the free tier itself does not auto-charge.
- **Why not primary:** registration + token refresh ceremony; product-oriented downloads less ideal for chip-level COG windowing than Earth Search HTTPS COGs.

### C. Explicitly out of scope for v1

- **Sentinel Hub paid / commercial** and CDSE commercial credit packs (map Out of scope).
- **AWS Requester Pays L1C** (`sentinel-s2-l1c`) — authenticates and bills the requester ([S3 Requester Pays](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html); [sentinel-2.yaml](https://github.com/awslabs/open-data-registry/blob/main/datasets/sentinel-2.yaml)).
- Paths that require attaching a payment method “just in case” (even if currently $0).

## Spec guidance for implementers

1. Depend on **open libraries only**: `pystac-client`, GDAL/`rasterio` (or `rioxarray`), optional `stackstac`.
2. Search Earth Search **`sentinel-2-l2a`** (or **`sentinel-2-c1-l2a`** if Collection 1 uniformity is preferred).
3. Filter by AOI geometry + `eo:cloud_cover` + a short recent datetime window.
4. For each selected item, open band HTTPS COG hrefs and **window-read** kiln chips; do not bulk-download full SAFE packages.
5. Apply `scale`/`offset` from asset metadata; cite Copernicus Sentinel data in outputs.
6. Treat Earth Search as best-effort: cache STAC item JSON + local chip GeoTIFFs in-repo or object storage you control so training is reproducible if the community API blips.
7. Keep Planetary Computer as a documented fallback if Earth Search is unavailable.

## Sources (primary)

1. [Element84/earth-search README](https://github.com/Element84/earth-search/blob/main/README.md)  
2. [Earth Search Sentinel-2 L2A collection notes](https://github.com/Element84/earth-search/blob/main/docs/collections/sentinel-2-l2a.md)  
3. [AWS Registry of Open Data — Sentinel-2 COGs](https://registry.opendata.aws/sentinel-2-l2a-cogs/)  
4. [awslabs/open-data-registry `sentinel-2-l2a-cogs.yaml`](https://raw.githubusercontent.com/awslabs/open-data-registry/main/datasets/sentinel-2-l2a-cogs.yaml)  
5. [awslabs/open-data-registry `sentinel-2.yaml`](https://github.com/awslabs/open-data-registry/blob/main/datasets/sentinel-2.yaml) (Requester Pays L1C)  
6. [Amazon S3 Requester Pays](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html)  
7. [Sentinel Data Legal Notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice)  
8. [Planetary Computer docs (Preview / free anonymous)](https://planetarycomputer.microsoft.com/docs/)  
9. [Planetary Computer SAS / tokens](https://planetarycomputer.microsoft.com/docs/concepts/sas/)  
10. [Planetary Computer reading STAC](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/)  
11. [CDSE Quotas and Limitations](https://documentation.dataspace.copernicus.eu/Quotas.html)  
12. [CDSE STAC catalogue](https://documentation.dataspace.copernicus.eu/APIs/STAC.html)  
13. [CDSE FAQ](https://documentation.dataspace.copernicus.eu/FAQ.html)  
14. Live probes of Earth Search + anonymous COG range GET + Planetary Computer STAC/SAS (2026-11-22)
