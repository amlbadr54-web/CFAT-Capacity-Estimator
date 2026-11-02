"""Core functions for the Circular CFAT Capacity Estimator.

The model is intentionally loaded as a frozen equation: this module contains
no fitting, tuning, or training routine.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL = json.loads((ROOT / "model.json").read_text(encoding="utf-8"))

FIELDS = (
    ("D_mm", "Outer diameter, D (mm)"),
    ("t_mm", "Wall thickness, t (mm)"),
    ("L_mm", "Member length, L (mm)"),
    ("e_mm", "Load eccentricity, e (mm)"),
    ("fcu_eq_MPa", "Cube-equivalent concrete strength, fcu,eq (MPa)"),
    ("sigma02_MPa", "Aluminum 0.2% proof stress, σ0.2 (MPa)"),
)

DEMO_CASE = {
    "D_mm": 100.0,
    "t_mm": 2.0,
    "L_mm": 300.0,
    "e_mm": 0.0,
    "fcu_eq_MPa": 48.0,
    "sigma02_MPa": 170.0,
}


def predict_capacity(values: dict[str, float]) -> tuple[float, dict[str, float]]:
    """Return predicted Pu (kN) and calculated section/geometry values."""
    d, t, length, eccentricity, fcu, sigma02 = (values[key] for key, _ in FIELDS)
    if min(d, t, length, fcu, sigma02) <= 0 or eccentricity < 0:
        raise ValueError("D, t, L, fcu,eq and σ0.2 must be positive; e cannot be negative.")
    if d <= 2.0 * t:
        raise ValueError("The outer diameter D must be greater than twice the wall thickness (2t).")

    aa = math.pi * (d * t - t**2)
    ac = math.pi / 4.0 * (d - 2.0 * t) ** 2
    ratios = {"D_over_t": d / t, "L_over_D": length / d, "e_over_D": eccentricity / d}
    c = MODEL["equation"]
    log_pu = (
        c["intercept"]
        + c["ln_Aa"] * math.log(aa)
        + c["ln_Ac"] * math.log(ac)
        + c["ln_L_over_D"] * math.log(ratios["L_over_D"])
        + c["ln_1_plus_e_over_D"] * math.log1p(ratios["e_over_D"])
        + c["ln_sigma02"] * math.log(sigma02)
        + c["ln_fcu_eq"] * math.log(fcu)
    )
    return math.exp(log_pu), {"Aa_mm2": aa, "Ac_mm2": ac, **ratios}


def range_warnings(values: dict[str, float], derived: dict[str, float]) -> list[str]:
    """Report values outside individual development ranges."""
    warnings: list[str] = []
    for key, limits in MODEL["marginal_development_ranges"].items():
        value = {**values, **derived}[key]
        if not limits[0] <= value <= limits[1]:
            warnings.append(f"{key} = {value:.3g} is outside [{limits[0]}, {limits[1]}].")
    return warnings
