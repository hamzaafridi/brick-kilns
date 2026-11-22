from __future__ import annotations

import numpy as np


def _stats(band: np.ndarray) -> list[float]:
    band = band.astype(np.float32)
    return [
        float(np.mean(band)),
        float(np.std(band)),
        float(np.percentile(band, 10)),
        float(np.percentile(band, 50)),
        float(np.percentile(band, 90)),
    ]


def chip_features(rgbnir: np.ndarray) -> np.ndarray:
    """Hand-crafted features for a 4-band (R,G,B,NIR) chip."""
    r, g, b, nir = rgbnir[..., 0], rgbnir[..., 1], rgbnir[..., 2], rgbnir[..., 3]
    eps = 1e-6
    ndvi = (nir - r) / (nir + r + eps)
    ndbi_proxy = (r - nir) / (r + nir + eps)  # built-up-ish vs veg without SWIR
    feats: list[float] = []
    for band in (r, g, b, nir, ndvi, ndbi_proxy):
        feats.extend(_stats(band))
    # Texture-ish: local variance of luminance
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    feats.append(float(np.mean(np.abs(np.diff(lum, axis=0)))))
    feats.append(float(np.mean(np.abs(np.diff(lum, axis=1)))))
    # Downsampled RGB histogram (8 bins each)
    for band in (r, g, b):
        hist, _ = np.histogram(band, bins=8, range=(0, 1), density=True)
        feats.extend(hist.astype(np.float32).tolist())
    return np.asarray(feats, dtype=np.float32)


FEATURE_DIM = len(chip_features(np.zeros((16, 16, 4), dtype=np.float32)))
