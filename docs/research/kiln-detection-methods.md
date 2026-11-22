# Open brick-kiln detection methods usable under free data

**Ticket:** [#5](https://github.com/hamzaafridi/brick-kilns/issues/5)  
**Question:** Which existing papers, open repos, or methods for detecting brick kilns from satellite imagery are usable under our open-data/open-tools constraint, and what concrete lessons (chip size, bands, labels, architectures) should the v1 spec borrow?  
**Constraint:** open data + open tools only (no paid APIs); prefer Sentinel-2-class imagery; extract parameters for a supervised chip classifier.  
**Date:** 2026-11-22

## Verdict (for the v1 spec)

**Borrow first from SentinelKilnDB + SustainBench’s Sentinel-2 chip formulation**, not from high-res DigitalGlobe / Google Maps Static pipelines.

1. **Best end-to-end match:** [SentinelKilnDB](https://sustainability-lab.github.io/sentinelkilndb/dataset.html) — free Sentinel-2 10 m RGB chips, oriented boxes, three kiln types, includes Pakistan, public benchmark code. Use as the primary template for chip size, season, overlap, and OBB/AA label formats.
2. **Best match for “supervised chip classifier” (binary presence):** [SustainBench Brick Kiln Classification](https://sustainlab-group.github.io/sustainbench/docs/datasets/sdg13/brick_kiln.html) — 64×64×13 Sentinel-2 chips labeled from Lee et al. kiln coordinates. Use for multi-band chip-classifier baselines.
3. **Borrow as optional stage-0 filter:** Nazir et al. (2023) Sentinel-2 spectral-index rules (NDVI/EVI/NDMI/NDBI/BAI) to propose candidates or hard negatives — fully free; do **not** rely on their high-res YOLO stage unless imagery is free.

README leads (Stanford, Earth-Lens, Terrapattern, Zooniverse) are useful for **process / labeling / architecture lessons**, but most of their production imagery paths fail the open-data constraint.

---

## Constraint filter

| Source | Imagery | Tools / license | Usable for v1? |
| --- | --- | --- | --- |
| SentinelKilnDB (NeurIPS 2025) | Sentinel-2 L2A 10 m | Dataset CC BY-NC 4.0; imagery ESA free; code public | **Yes** (note NC on dataset redistribution / commercial) |
| SustainBench brick_kiln | Sentinel-2 (via GEE historically) | Public task + labels from Lee coords | **Yes** for method/params; re-download S2 via free CDSE/PEPS if avoiding GEE |
| Nazir et al. 2023 spectral stage | Sentinel-2 indices | Open method | **Yes** (stage-0 only) |
| Lee / Stanford PNAS 2021 | DigitalGlobe ~1 m | Proprietary imagery | **Lessons only** (chip CNN + iterative labeling) |
| Kiln-Net (Nazir et al. 2020) | DigitalGlobe / Google Earth ~0.15 m | Asia14 not free imagery | **Lessons only** (gated classifier→YOLO) |
| Eye in the Sky / compass24 | Google Maps Static API | Quota / cloud billing risk | **No** as imagery path |
| Pakistan IGP Scientific Data (2025) | S2 RF + GMS YOLO | Mixed; GMS not open-tools-safe | **Partial** (RF / type labels) |
| Microsoft Earth-Lens | Generic aerial demo | MIT; unmaintained since 2019 | **Low** (not kiln-specific) |
| Terrapattern | Google Maps tiles; US metros only | MIT code; not Lahore coverage | **Lessons only** (embedding search) |
| Zooniverse Slavery from Space | High-res Google Earth / DigitalGlobe | Crowdsourcing platform | **Labeling QA only** |

---

## Methods reviewed (primary sources)

### 1. SentinelKilnDB — recommended primary template

- **Paper:** Mondal et al., *SENTINELKILNDB…*, NeurIPS 2025 Datasets & Benchmarks — [PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/9ab8bb568825d49ce31aa87b7e2f4ad7-Paper-Datasets_and_Benchmarks_Track.pdf), [supplement](https://papers.nips.cc/paper_files/paper/2025/file/9ab8bb568825d49ce31aa87b7e2f4ad7-Supplemental-Datasets_and_Benchmarks_Track.pdf).
- **Project / dataset pages:** [dataset docs](https://sustainability-lab.github.io/sentinelkilndb/dataset.html), [Hugging Face](https://huggingface.co/datasets/SustainabilityLabIITGN/SentinelKilnDB), [benchmark repo](https://github.com/rishabh-mondal/SENTINELKILNDB_NeurIPS_2025).
- **What it is:** 62,671 hand-validated kilns over ~2.8M km² (India, Bangladesh, **Pakistan 12,177**, Afghanistan) with OBB + AA labels on free Sentinel-2.
- **Concrete parameters:**
  - **Chip size:** 128×128 px @ **10 m/px** (~1.28 km on a side).
  - **Bands:** B4 (Red), B3 (Green), B2 (Blue); PNG RGB.
  - **Season:** Nov–Feb (winter kiln season; farmland contrast).
  - **Cloud:** &lt;1% cloud; QA60 masking.
  - **Tiling:** large S2 tiles → overlapping 128×128 patches; **≈30 px / 0.0027° overlap**; dedupe by geo coords.
  - **Typical kiln footprint:** ~30 px.
  - **Labels:** 3 classes — FCBK, CFCBK, Zigzag; YOLO-OBB, YOLO-AA, DOTA.
  - **Architectures benchmarked:** YOLO-OBB (incl. v11L), RT-DETR, RF-DETR, MMRotate / RHINO, remote-sensing FMs (TerraMind, Galileo). Strong results reported ~86 mAP50 for top models.
- **Open-data fit:** Imagery is Sentinel-2 (free). Dataset license **CC BY-NC 4.0** — fine for this research pilot; do not assume commercial redistribution. Prefer regenerating Lahore chips from Urban Unit / PAQI + local S2 rather than depending on NC redistribution if license ambiguity matters.
- **v1 borrow:** chip size **128×128**, winter compositing, 25–30 px overlap, kiln-type taxonomy, OBB if doing detection; or collapse boxes → chip-level binary labels for a simpler classifier.

### 2. SustainBench Brick Kiln Classification — recommended chip-classifier baseline

- **Task page:** [Brick Kiln Classification (Bangladesh)](https://sustainlab-group.github.io/sustainbench/docs/datasets/sdg13/brick_kiln.html).
- **Upstream labels:** Lee et al., PNAS 2021 (kiln coordinates); high-res DigitalGlobe **not** released.
- **Concrete parameters:**
  - **Chip size:** **64×64**.
  - **Bands:** **13 Sentinel-2 bands (B1–B12)** as stored in the HDF5 task (use B2/B3/B4 for RGB baselines).
  - **Time:** Oct 2018 – May 2019 (aligned with Lee imagery window).
  - **Labels:** binary chip presence (kiln / no kiln) from published coordinates; 6,329 pos / 67,284 neg; 80/10/10 split.
  - **Metrics:** accuracy, precision, recall, AUC.
- **Open-data fit:** Sentinel-2 class. Historical download path used GEE; regenerate via free S2 access if GEE is treated as non-open-tool.
- **v1 borrow:** multi-band **64×64 chip classifier** as a cheap baseline alongside 128×128 RGB detection chips.

### 3. Nazir et al. 2023 — multi-spectral filter + orientation-aware YOLO

- **Paper:** *Mitigating climate and health impact…* — [arXiv:2303.11654](https://arxiv.org/abs/2303.11654).
- **Method:** (1) Sentinel-2 spectral rule to propose kiln candidates; (2) orientation-aware YOLOv3 (θ) on high-res to refine.
- **Spectral rule (borrowable):** classify candidate if  
  `NDVI < 0.2` ∧ `EVI < 0.2` ∧ `NDMI < 0` ∧ `NDBI > 0` ∧ `BAI > 5e-8`.  
  Indices use Red/NIR/SWIR-family bands available on Sentinel-2.
- **Open-data fit:** stage (1) **yes**; stage (2) typically needs commercial high-res → **no** for our constraint.
- **v1 borrow:** optional pre-filter / hard-negative mining; expect high false positives alone (authors’ motivation for stage 2).

### 4. Lee et al. / Stanford PNAS 2021 — process gold standard, closed imagery

- **Paper:** Lee, Brooks, et al., *Scalable deep learning to identify brick kilns…*, PNAS 2021 — [doi:10.1073/pnas.2018863118](https://www.pnas.org/doi/full/10.1073/pnas.2018863118).
- **News / lab context:** [Stanford Report](https://news.stanford.edu/stories/2021/04/ai-empowers-environmental-regulators), [Luby Lab](https://lubylab.stanford.edu/assessing-brick-kilns-number-location-and-use-bangladesh).
- **Concrete parameters:**
  - **Chip size:** **224×224** RGB @ zoom 17 ≈ **1 m/px** (DigitalGlobe).
  - **Architecture:** ImageNet-pretrained **VGG-16** selected for precision among VGG-19 / Inception / Xception / ResNet-50.
  - **Labels:** image-level kiln / no-kiln; positive if ≥25% of a kiln visible; iterative hand-validation expansion across divisions; weakly supervised localization for centroids; second model for FCK vs zigzag.
  - **Reported:** 94.2% accuracy, 88.7% precision on Bangladesh national sweep.
- **Open-data fit:** **fails** on imagery. SustainBench is the open remapping of the *labels* onto Sentinel-2.
- **v1 borrow:** transfer learning; precision-oriented model selection; iterative active labeling; dual-review hand validation; separate type classifier after detection.

### 5. Kiln-Net (Nazir et al. 2020) — gated classifier → detector pattern

- **Paper:** *Kiln-Net…*, IEEE JSTARS 2020 — [doi:10.1109/jstars.2020.3001980](https://doi.org/10.1109/jstars.2020.3001980) ([Oxford ORA copy](https://ora.ox.ac.uk/objects/uuid:e513dcf6-962e-477b-a613-16dad5b6311f/files/scc08hh992)).
- **Concrete parameters:**
  - **Chip size:** **256×256** RGB @ zoom 20 ≈ **0.149 m/px** DigitalGlobe / Google Earth.
  - **Stage 1:** ResNet-152 multi-class (14 land-use classes including kiln); gate threshold **0.1** (high recall).
  - **Stage 2:** YOLOv3 bounding boxes on gated patches.
  - **Dataset:** Asia14 — 14,000 images; 1,300 kiln images with boxes.
- **Open-data fit:** imagery path **no**. Pattern **yes**.
- **v1 borrow:** coarse-to-fine gating (cheap chip classifier → expensive localizer) on Sentinel-2 chips; prefer multi-class negatives (farm, barren, built-up, water) over pure binary if label budget allows.

### 6. Eye in the Sky / compass24 & Pakistan IGP Scientific Data — recent but API-heavy

- **Eye in the Sky:** Mondal et al. 2024 — [arXiv HTML](https://arxiv.org/html/2406.10723v1); code [rishabh-mondal/compass24](https://github.com/rishabh-mondal/compass24).  
  **Params:** Google Maps Static tiles (zoom 16, scale=2 → ~1 m/px, 1280×1280 then crop); **YOLOv8-M**; iterative predict→hand-verify; FCBK vs Zigzag; ~0.01° tile stride with overlap.
- **Pakistan IGP dataset:** Hamdani et al., *Scientific Data* 2025 — [nature.com/articles/s41597-025-05148-9](https://www.nature.com/articles/s41597-025-05148-9); code [APAD2024/brickkilnscidata](https://github.com/APAD2024/brickkilnscidata).  
  **Params:** Random Forest on **Sentinel-2 RGB** for pixel candidates → **YOLOv8** on Google Static Maps for type/validation; 11,277 Pakistan kilns with FCBK/Zigzag.
- **Open-data fit:** GMS Static / paid-quota APIs conflict with “no paid APIs / no free tiers that can turn into billing.” Keep **RF-on-S2** and **type taxonomy**; drop GMS.
- **v1 borrow:** iterative labeling loop; kiln-type classes; RF or spectral stage as optional proposal; do not make Static Maps a dependency.

### 7. README leads — Earth-Lens, Terrapattern, Zooniverse

#### Microsoft Earth-Lens

- **Repo:** [microsoft/Earth-Lens](https://github.com/Microsoft/Earth-Lens) (MIT); [Garage profile](https://www.microsoft.com/en-us/garage/profiles/earth-lens/).
- **What it is:** iPad CoreML demo for detecting/classifying objects in aerial imagery; **not brick-kiln-specific**; Microsoft ended official support Feb 2019; model “for demonstration purposes only.”
- **v1 borrow:** essentially none for kiln detection. Ignore as a method source.

#### Terrapattern

- **About / license:** [terrapattern.com/about](https://about.terrapattern.com) content at [About](https://terrapattern.com/about); code [CreativeInquiry/terrapattern](https://github.com/CreativeInquiry/terrapattern) (MIT).
- **Method:** ResNet-34 trained on OSM-labeled satellite tiles; strip classifier head; KNN in embedding space for visual query-by-example. Prototype cities: NYC, SF, Pittsburgh (not South Asia). Site uses Google Maps imagery.
- **Training notes (repo):** center-crop / resize toward **224×224** (ImageNet-style); one net per zoom level.
- **v1 borrow:** optional **few-shot discovery** / hard-negative mining after a supervised model exists — not a substitute for supervised Lahore labels.

#### Zooniverse — Slavery from Space

- **Project:** [Slavery from Space](https://www.zooniverse.org/projects/ezzjcw/slavery-from-space); Punjab FAQ notes ~307 m chips / ~1.2 m imagery ([FAQ](https://www.zooniverse.org/projects/ezzjcw/slavery-from-space-punjab/about/faq)).
- **Paper:** Boyd et al. 2018 — [PDF](https://www.nottingham.ac.uk/research/beacons-of-excellence/rights-lab/resources/academic-publications/2019/march/boyd-et-al-brick-kilns.pdf); related ML paper [MDPI Remotesensing 11(3):266](https://www.mdpi.com/2072-4292/11/3/266).
- **Label protocol:** ≥15 volunteers per extract; aggregate marks; retain clusters with ≥4 volunteers within 5 px; expert adjudicator as ground truth. Earlier sampling used 100 km² cells and expert visual counts.
- **v1 borrow:** multi-annotator consensus + adjudication for Urban Unit / PAQI cleaning — **not** a detector architecture. Map issue already marks community crowdvoting out of scope for v1 product; still useful as **internal label QA**.

### 8. Other Sentinel-2 ML note

- **AISC 2023:** *Detection of Brick Kilns Using Multi-Spectral Bands of Sentinel-2 Imagery* — [doi:10.1109/aisc56616.2023.10085085](https://doi.org/10.1109/aisc56616.2023.10085085). Pixel / point classifiers (Smile RF etc. on GEE) for classes built-up / field / water / kiln; best reported Smile RF ~96.4% accuracy, precision 0.88, recall 0.73 in Delhi-NCR. Useful as a **classical baseline**, but GEE-centric tooling and point-based eval differ from chip scanning.

---

## Recommended v1 borrow sheet (supervised chip classifier)

| Parameter | Recommendation | Source |
| --- | --- | --- |
| Imagery | Sentinel-2 L2A, free download (CDSE/PEPS/etc.; avoid paid Sentinel Hub / GMS) | Project constraint + SentinelKilnDB |
| Season | Prefer **Nov–Feb** clear scenes for Punjab IGP | SentinelKilnDB |
| Cloud | Strict cloud filter + QA60/SCL mask | SentinelKilnDB |
| Primary chip size | **128×128 @ 10 m** (~1.28 km) | SentinelKilnDB |
| Optional smaller chips | **64×64** multi-band for SustainBench-style classifier | SustainBench |
| Bands (v1) | Start **B2,B3,B4**; ablate adding **B8 (NIR), B11/B12 (SWIR)** and/or indices NDVI, NDBI, NDMI, BAI | SustainBench + Nazir 2023 |
| Overlap / scan | ~**25–30 px** (~20–25%) stride overlap; dedupe detections by distance | SentinelKilnDB; Eye-in-Sky overlap lesson |
| Label definition (chip) | Positive if kiln center (or ≥~25% of kiln) falls in chip | Lee PNAS |
| Classes | Start **binary kiln/background**; upgrade to **FCBK / Zigzag (/ CFCBK)** if Urban Unit / PAQI support it | SentinelKilnDB; Pakistan SciData |
| Negatives | Multi-class land-cover hard negatives (farm, barren, settlement, water, industry) beat random tiles | Kiln-Net Asia14 lesson |
| Architecture (classifier path) | ImageNet-pretrained CNN (ResNet / EfficientNet family; Lee used VGG-16 for precision) | Lee; Kiln-Net |
| Architecture (detector path) | YOLO-OBB / RT-DETR on 128×128 if v1 wants boxes not just chips | SentinelKilnDB benchmarks |
| Optional cascade | Spectral or cheap CNN gate (high recall) → second-stage classifier/detector | Nazir 2023; Kiln-Net |
| Label workflow | Seed from Urban Unit + PAQI; iterative predict→dual human review; optional Zooniverse-style consensus for disputed chips | Lee; Zooniverse Boyd et al. |
| External pretraining data | SentinelKilnDB Pakistan subset **only if** CC BY-NC acceptable for the pilot | SentinelKilnDB license |

### Explicit non-borrows for v1

- DigitalGlobe / Maxar / Google Maps Static / Google Earth high-res as a **required** training or inference path (Lee, Kiln-Net, Eye in the Sky, SciData high-res stage).
- Earth-Lens as a kiln detector.
- Terrapattern hosted search (no Lahore coverage; Google Maps dependency).
- Paid Sentinel Hub or credit-card “free tiers.”

---

## Suggested reading order for implementers

1. SentinelKilnDB paper + dataset page (parameters + Pakistan coverage).  
2. SustainBench brick_kiln task (chip-classifier shape).  
3. Lee PNAS methods (labeling / evaluation discipline).  
4. Nazir 2023 §3.1 (spectral thresholds) + Kiln-Net gated pattern (optional cascade).  
5. Boyd et al. / Zooniverse only if designing human label QA.

## Sources (linked claims)

1. Mondal et al., SentinelKilnDB NeurIPS 2025 — [paper](https://proceedings.neurips.cc/paper_files/paper/2025/file/9ab8bb568825d49ce31aa87b7e2f4ad7-Paper-Datasets_and_Benchmarks_Track.pdf), [supplement](https://papers.nips.cc/paper_files/paper/2025/file/9ab8bb568825d49ce31aa87b7e2f4ad7-Supplemental-Datasets_and_Benchmarks_Track.pdf), [dataset site](https://sustainability-lab.github.io/sentinelkilndb/dataset.html), [HF](https://huggingface.co/datasets/SustainabilityLabIITGN/SentinelKilnDB), [code](https://github.com/rishabh-mondal/SENTINELKILNDB_NeurIPS_2025).  
2. SustainBench Brick Kiln Classification — [task docs](https://sustainlab-group.github.io/sustainbench/docs/datasets/sdg13/brick_kiln.html).  
3. Nazir et al. 2023 multi-spectral + YOLO — [arXiv:2303.11654](https://arxiv.org/abs/2303.11654).  
4. Lee et al. 2021 PNAS — [full text](https://www.pnas.org/doi/full/10.1073/pnas.2018863118).  
5. Nazir et al. 2020 Kiln-Net — [IEEE](https://doi.org/10.1109/jstars.2020.3001980), [ORA PDF](https://ora.ox.ac.uk/objects/uuid:e513dcf6-962e-477b-a613-16dad5b6311f/files/scc08hh992).  
6. Mondal et al. 2024 Eye in the Sky — [arXiv HTML](https://arxiv.org/html/2406.10723v1), [compass24](https://github.com/rishabh-mondal/compass24).  
7. Hamdani et al. 2025 Scientific Data Pakistan IGP — [article](https://www.nature.com/articles/s41597-025-05148-9), [brickkilnscidata](https://github.com/APAD2024/brickkilnscidata).  
8. Microsoft Earth-Lens — [GitHub](https://github.com/Microsoft/Earth-Lens), [Garage](https://www.microsoft.com/en-us/garage/profiles/earth-lens/).  
9. Terrapattern — [about](https://terrapattern.com/about), [GitHub](https://github.com/CreativeInquiry/terrapattern).  
10. Boyd et al. / Zooniverse Slavery from Space — [Boyd PDF](https://www.nottingham.ac.uk/research/beacons-of-excellence/rights-lab/resources/academic-publications/2019/march/boyd-et-al-brick-kilns.pdf), [Zooniverse](https://www.zooniverse.org/projects/ezzjcw/slavery-from-space).  
11. AISC 2023 Sentinel-2 ML — [doi:10.1109/aisc56616.2023.10085085](https://doi.org/10.1109/aisc56616.2023.10085085).
