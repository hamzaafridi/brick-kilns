# Machine-readable Urban Unit and PAQI kiln points

**Ticket:** [#3](https://github.com/hamzaafridi/brick-kilns/issues/3)  
**Question:** How can we obtain machine-readable kiln location data for the Lahore pilot AOI from the Urban Unit / Gov Punjab census (primary) and PAQI mapping (secondary), including formats, access URLs/APIs, license/terms, and known quality issues that affect training and eval?  
**AOI:** Lahore + Kasur + Sheikhupura + Nankana Sahib, Pakistan  
**Researched:** 2026-11-22

## Verdict (one line each)

- **Urban Unit (primary):** There is **no published bulk GeoJSON/shapefile/CSV of kiln coordinates** from Urban Unit / Open Data Pakistan; coordinates historically lived behind the Brick Kiln Census **web dashboard** (now largely unreachable), so obtain points by restoring access to that dashboard / requesting GIS export from Urban Unit or EPA Punjab, not from a public download portal.
- **PAQI (secondary):** Download the public Google My Maps layer as **KML** (or layer **CSV** via My Maps UI) — the map is machine-readable today and covers only a **partial, crowd-sourced** subset of kilns.

---

## 1. Urban Unit / Gov Punjab Brick Kiln Census (primary)

### What it is

The Urban Unit (Govt. of Punjab) ran a brick-kiln census starting January 2016 for a Chief Minister Punjab child-labour initiative. GIS/satellite imagery was used to identify kilns by their satellite signature; the exercise identified **about 10,000** brick kilns, with family/child records and kiln photos uploaded to a database.  
Source: [Open Data Pakistan — Brick Kilns Census Punjab](https://opendata.com.pk/dataset/brick-kilns-census-punjab) (author field: The Urban Unit, Punjab Government).

A later Urban Unit project page describes a related **“Industries and Brick Kiln Data Inventory under SMOG Action Plan”** for EPA Punjab (map locations and technologies) but does **not** publish a download link.  
Source: [The Urban Unit — GIS & Remote Sensing projects](https://urbanunit.gov.pk/projects/Index/2).

### Access URLs (verify live)

| Role | URL | Notes |
| --- | --- | --- |
| README shortlink | `http://bit.ly/PAQI_GovPunjab_brickkilns` | Resolves to the IP-hosted dashboard below (checked 2026-11-22). |
| Dashboard (IP host cited in README/literature) | `http://202.166.167.115/brick_kiln_dashboard/index.php` | **Timed out / unreachable** from this research environment (2026-11-22). |
| Dashboard (hostname) | `http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/` | Same product; also **unreachable** here (2026-11-22). Also cited by [arXiv:2301.07521](https://arxiv.org/abs/2301.07521). |
| Older literature URL | `http://202.166.167.115/brick_kiln_dashboard/` | Cited as “publicly available” Punjab Brick Kiln Census in [arXiv:1907.05552](https://ar5iv.labs.arxiv.org/html/1907.05552). |
| Open Data Pakistan catalogue | [Brick Kilns Census Punjab](https://opendata.com.pk/dataset/brick-kilns-census-punjab) | Points at dashboard report URL; **does not host a geospatial file**. |
| Catalogue resource | [children_analysis.php](http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/brick_reports/children_analysis.php) | Linked as “Brick Kiln Data Download” in the archived dashboard nav (see below). |
| Wayback HTML (2021-04-14) | [archived index](https://web.archive.org/web/20210414013704id_/http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/) | Confirms app structure when the host was up. |

### Machine-readable formats / APIs

**Finding:** No official public **GeoJSON, Shapefile, or documented REST/STAC API** for kiln point coordinates was found on Urban Unit or Open Data Pakistan primary pages.

What *is* documented or evidenced:

1. **Interactive dashboard, not a dump.** The archived home page is an AngularJS + Google Maps + ArcGIS JS app (`ng-app="brickKilnApp"`, `initMap()`, Esri CSS). Nav links include:
   - `brick_kiln_detail/brick_kiln_info.php` — Brick Kiln Detail info  
   - `brick_reports/children_analysis.php` — labelled **“Brick Kiln Data Download”**  
   - `bricklin_gis/brick_kiln_gis.php` — **GIS**  
   Source: [Wayback HTML 20210414013704](https://web.archive.org/web/20210414013704id_/http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/).

2. **Open Data Pakistan classifies the catalogue entry as non-geospatial** and the sole resource format as **URL**, not a spatial file.  
   Source: [dataset page](https://opendata.com.pk/dataset/brick-kilns-census-punjab) (`Data Type: non-geospatial`); [resource metadata](https://www.opendata.com.pk/dataset/brick-kilns-census-punjab/resource/3460a74a-c4be-44b3-b397-6f98dacf8c6f) (`Format: URL`).

3. **Coordinates existed in the census product when the dashboard was reachable.** Independent researchers report retrieving **9,348** kiln locations from the Punjab Brick Kiln Census dashboard and separating lat/lon for analysis.  
   Source: Nazir et al., *Detection of Illegal Kiln Activity During SMOG Period*, [arXiv:2301.07521](https://arxiv.org/abs/2301.07521) §III-A (footnote to `http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/`).  
   The extraction method is **not** published as an official API contract; treat any JSON/table scrape as **undocumented and host-dependent**.

4. **JS backend for the archived UI was not preserved** on Wayback (only the HTML index returned 200; `script/angular_controller.js` and GIS PHP returned 404 in archive), so endpoint names could not be recovered from primary archival assets in this pass.

### License / terms

| Source | Stated terms |
| --- | --- |
| Open Data Pakistan resource | **“No License Provided”** — [resource page](https://www.opendata.com.pk/dataset/brick-kilns-census-punjab/resource/3460a74a-c4be-44b3-b397-6f98dacf8c6f) |
| Urban Unit project pages | No open-data license text found for kiln coordinates |
| Practical implication | Do **not** assume CC/ODC reuse rights. Prefer written permission or a formal GIS export from Urban Unit / EPA Punjab before redistributing census points. |

### Quality issues for training / eval

| Issue | Evidence | Impact on supervised detector |
| --- | --- | --- |
| Known discrepancies vs reality | README quote from Abid Omar (PAQI): Urban Unit dashboard has “a lot of discrepancies” on random inspection — [repo README](https://github.com/hamzaafridi/brick-kilns/blob/main/README.md) | Label noise; prefer human visual QA of chips before trusting as hard positives |
| Vintage | Census pilot began **January 2016** — [Open Data Pakistan](https://opendata.com.pk/dataset/brick-kilns-census-punjab) | Kilns built/demolished/converted (e.g. zigzag) since 2016 → temporal mismatch with current Sentinel-2 |
| Completeness of public portal | Catalogue is child-labour / demographic oriented; marked **non-geospatial** | Public “download” path may not equal a clean point layer for ML |
| Host availability | Live dashboard hosts unreachable (2026-11-22); limited Wayback coverage | Blocks reproducible agent pipelines until host returns or an official export is obtained |
| Count ambiguity | ~10,000 identified (ODP) vs 9,348 retrieved in later study ([arXiv:2301.07521](https://arxiv.org/abs/2301.07521)) | Split/eval set sizes depend on which snapshot is obtained |
| Functional vs non-functional | Dashboard UI exposes functional / non-functional kiln counters (live page template) | Operational status may not match “visible kiln in imagery” |

### Practical obtain path (primary)

1. Re-check `http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/` and `http://202.166.167.115/brick_kiln_dashboard/` periodically.  
2. If up: use **GIS** (`bricklin_gis/brick_kiln_gis.php`) and **Brick Kiln Data Download** (`brick_reports/children_analysis.php`) first; capture any export that includes coordinates.  
3. If down: request a **district-filtered GIS export** (Lahore, Kasur, Sheikhupura, Nankana Sahib) from Urban Unit / EPA under the SMOG inventory programme ([project listing](https://urbanunit.gov.pk/projects/Index/2)).  
4. Until a licensed file exists, treat Urban Unit as **primary ground truth only after QA**, not as a drop-in open training set.

---

## 2. PAQI mapping (secondary)

### What it is

Pakistan Air Quality Initiative (PAQI) maintains a **crowd-sourced** Google My Maps titled **“Brick kilns in Pakistan”**, described by founder Abid Omar as mapping plus community awareness. The map description explicitly points contributors to the Urban Unit census for help.  
Sources: README shortlink; map description on [Google My Maps viewer](https://www.google.com/maps/d/viewer?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&usp=sharing).

### Access URLs

| Role | URL |
| --- | --- |
| README shortlink | `http://bit.ly/PAQI_brickkilns` → My Maps viewer below (checked 2026-11-22) |
| Interactive map | `https://www.google.com/maps/d/viewer?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&usp=sharing` |
| Machine-readable KML (public map) | `https://www.google.com/maps/d/kml?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&forcekml=1` |
| Official UI export | My Maps → Menu → **Export to KML/KMZ**; per-layer **Export data CSV** — [Google My Maps Help](https://support.google.com/mymaps/answer/3109452) |

### Formats observed (2026-11-22)

Downloaded KML from the `forcekml=1` URL:

| Property | Value |
| --- | --- |
| Format | OGC **KML 2.2** (`text/xml`), inline `<Point>` placemarks (no NetworkLink) |
| Document name | `Brick kilns in Pakistan` |
| Layers | Single folder: `Untitled layer` |
| Placemarks with coordinates | **1,868** |
| Approx nationwide bbox | lat 25.29–33.98, lon 66.94–75.21 |
| Rough AOI counts (bbox proxies, not official district polygons) | Lahore ~208, Kasur ~228, Sheikhupura ~142, Nankana ~15; combined Lahore-division-ish box ~633 |
| Naming | Mostly `Point N` (1,823); few named brick works |

Convert KML → GeoJSON/CSV locally with `ogr2ogr` / `geopandas` for training pipelines. Layer CSV export from the My Maps UI is the official alternate tabular path ([Help](https://support.google.com/mymaps/answer/3109452)).

### License / terms

| Layer | Terms |
| --- | --- |
| PAQI-contributed placemarks | Google Terms: **“Your content remains yours”** (IP in user content) — [Google Terms — Permission to use your content](https://policies.google.com/terms). The map itself states PAQI crowd-sourcing; **no CC license text** appears in the KML description. Contact PAQI / Abid Omar for reuse beyond personal/research if redistributing. |
| Google Maps / My Maps platform | [Google Maps Additional Terms](https://www.google.com/help/terms_maps/): license to view/annotate/create KML; **prohibited** to mass-download Google Maps *content*, redistribute Google Maps, or build a substitute mapping dataset from Google content. Use the **My Maps export** for *user layer* points; do **not** scrape basemap tiles/POIs. |
| Attribution | When displaying Google Maps UI/imagery, follow Google geo attribution rules; for PAQI points, credit **Pakistan Air Quality Initiative** and the map title. |

### Quality issues for training / eval

| Issue | Evidence | Impact |
| --- | --- | --- |
| Incomplete vs census | ~1.9k PAQI points vs ~10k Urban Unit identified kilns | Severe under-recall if used as sole positives; good as **secondary / soft** labels only |
| Crowd-sourced edits | Map invites community layers/points; default names like `Point 13` — [My Maps description](https://www.google.com/maps/d/viewer?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&usp=sharing) | Uneven coverage, duplicate risk, variable geolocation care |
| AOI skew | Nankana proxy count very low vs Lahore/Kasur | District-stratified eval will be unstable |
| Not a substitute for Urban Unit | Map text directs users to Urban Unit census | Aligns with ticket: PAQI = secondary |
| Platform volatility | Hosted on Google My Maps; can change without versioning | Pin a dated KML snapshot in-repo (if license allows) for eval reproducibility |

---

## 3. Recommended use for the Lahore pilot

| Role | Source | How to get points | Use in ML |
| --- | --- | --- | --- |
| Primary GT | Urban Unit census | Official GIS/export when host is up, or request from Urban Unit/EPA | Positives **after** chip QA; hold out districts for eval |
| Secondary GT | PAQI My Maps | KML URL or UI CSV export | Cross-check / soft labels; never sole eval truth |
| Out of ticket scope | AI-derived IGP kiln datasets (e.g. Zenodo CC BY 4.0) | Not Urban Unit or PAQI | Optional third comparator only — not a substitute for this ticket’s sources |

**Training/eval hygiene:** (1) filter to AOI polygons, (2) dedupe within ~chip diameter, (3) visual-confirm a stratified sample against current imagery, (4) treat 2016 census vintage and PAQI incompleteness as first-class error sources in the metrics write-up.

---

## Sources (primary)

1. [Open Data Pakistan — Brick Kilns Census Punjab](https://opendata.com.pk/dataset/brick-kilns-census-punjab)  
2. [Open Data Pakistan — children_analysis.php resource metadata](https://www.opendata.com.pk/dataset/brick-kilns-census-punjab/resource/3460a74a-c4be-44b3-b397-6f98dacf8c6f)  
3. [The Urban Unit — GIS & Remote Sensing / SMOG brick kiln inventory](https://urbanunit.gov.pk/projects/Index/2)  
4. [Wayback — Urban Unit Brick Kiln Dashboard HTML (2021-04-14)](https://web.archive.org/web/20210414013704id_/http://dashboards.urbanunit.gov.pk/brick_kiln_dashboard/)  
5. Shortlink resolutions (2026-11-22): `bit.ly/PAQI_GovPunjab_brickkilns` → `http://202.166.167.115/brick_kiln_dashboard/index.php`; `bit.ly/PAQI_brickkilns` → Google My Maps `mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2`  
6. [PAQI Google My Maps viewer](https://www.google.com/maps/d/viewer?mid=10XfGkHOhKQMa5U6ddfa3yGEH-lI3iNv2&usp=sharing) and KML `…/kml?mid=…&forcekml=1`  
7. [Google My Maps Help — Share, download, or print](https://support.google.com/mymaps/answer/3109452)  
8. [Google Maps Additional Terms of Service](https://www.google.com/help/terms_maps/)  
9. [Google Terms of Service — Permission to use your content](https://policies.google.com/terms)  
10. Nazir et al. (2023), [arXiv:2301.07521](https://arxiv.org/abs/2301.07521) — 9,348 coordinates from Punjab Brick Kiln Census dashboard  
11. Nazir et al. (2019), [arXiv:1907.05552](https://ar5iv.labs.arxiv.org/html/1907.05552) — cites IP dashboard as public census  
12. Repo README (Abid Omar email excerpt on Urban Unit discrepancies and PAQI map purpose)
