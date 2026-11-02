"""Research-only GUI for the frozen cube-equivalent CFAT ridge formulation.

The application evaluates the published full-98 ridge equation directly. It does
not retrain, tune, or validate a model. See model.json and README.md.
"""

from __future__ import annotations

import json
import math
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


ROOT = Path(__file__).resolve().parent
MODEL = json.loads((ROOT / "model.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "reference_cases.json").read_text(encoding="utf-8"))

FIELDS = (
    ("D_mm", "Outer diameter D (mm)"),
    ("t_mm", "Wall thickness t (mm)"),
    ("L_mm", "Member length L (mm)"),
    ("e_mm", "Eccentricity e (mm)"),
    ("fcu_eq_MPa", "Cube-equivalent strength fcu,eq (MPa)"),
    ("sigma02_MPa", "Aluminum proof stress sigma0.2 (MPa)"),
)


def predict(values: dict[str, float]) -> tuple[float, dict[str, float]]:
    d, t, length, eccentricity, fcu, sigma02 = (values[key] for key, _ in FIELDS)
    if min(d, t, length, fcu, sigma02) <= 0 or eccentricity < 0:
        raise ValueError("D, t, L, fcu,eq and sigma0.2 must be positive; e cannot be negative.")
    if d <= 2.0 * t:
        raise ValueError("Outer diameter D must be greater than twice the wall thickness 2t.")
    aa = math.pi * (d * t - t * t)
    ac = math.pi / 4.0 * (d - 2.0 * t) ** 2
    ratios = {"D_over_t": d / t, "L_over_D": length / d, "e_over_D": eccentricity / d}
    c = MODEL["equation"]
    log_pu = (
        c["intercept"]
        + c["ln_Aa"] * math.log(aa)
        + c["ln_Ac"] * math.log(ac)
        + c["ln_L_over_D"] * math.log(length / d)
        + c["ln_1_plus_e_over_D"] * math.log1p(eccentricity / d)
        + c["ln_sigma02"] * math.log(sigma02)
        + c["ln_fcu_eq"] * math.log(fcu)
    )
    return math.exp(log_pu), {"Aa_mm2": aa, "Ac_mm2": ac, **ratios}


def range_warnings(values: dict[str, float], derived: dict[str, float]) -> list[str]:
    ranges = MODEL["marginal_development_ranges"]
    all_values = {**values, **derived}
    warnings = []
    for key, limits in ranges.items():
        value = all_values[key]
        if not limits[0] <= value <= limits[1]:
            warnings.append(f"{key} = {value:.3g} is outside the development range [{limits[0]}, {limits[1]}].")
    return warnings


class CapacityEstimator(ttk.Frame):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, padding=18)
        self.parent = parent
        self.parent.title("Circular CFAT Capacity Estimator - Research Prototype")
        self.parent.minsize(820, 620)
        self.grid(sticky="nsew")
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.values = {key: tk.StringVar() for key, _ in FIELDS}
        self.result = tk.StringVar(value="Enter an in-domain input set and select Calculate.")
        self.warning_text = tk.StringVar(value="Research use only. This tool is not a structural design check.")
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="CIRCULAR CFAT CAPACITY ESTIMATOR", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        ttk.Label(
            self,
            text="Frozen cube-equivalent ridge formulation | research prototype | alpha = 0.01",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 15))
        input_box = ttk.LabelFrame(self, text="Model inputs", padding=12)
        input_box.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        result_box = ttk.LabelFrame(self, text="Estimate and warnings", padding=12)
        result_box.grid(row=2, column=1, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        for row, (key, label) in enumerate(FIELDS):
            ttk.Label(input_box, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(input_box, textvariable=self.values[key], width=20).grid(row=row, column=1, sticky="ew", pady=4)
        input_box.columnconfigure(1, weight=1)
        buttons = ttk.Frame(input_box)
        buttons.grid(row=len(FIELDS), column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(buttons, text="Calculate", command=self.calculate).pack(side="left")
        ttk.Button(buttons, text="Load demo", command=self.load_demo).pack(side="left", padx=6)
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left")
        ttk.Label(result_box, textvariable=self.result, wraplength=330, justify="left", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Separator(result_box).grid(row=1, column=0, sticky="ew", pady=12)
        ttk.Label(result_box, textvariable=self.warning_text, wraplength=330, justify="left", foreground="#9b1c1c").grid(
            row=2, column=0, sticky="w"
        )
        note = (
            "Input convention: fcu,eq is cube-equivalent concrete strength. If entering a cylinder strength, "
            "the optional model convention is fcu,eq = fc,cyl / 0.80; this approximation is not universal.\n\n"
            "No safety factor, calibrated resistance factor, or guaranteed individual prediction error is provided. "
            "Passing the displayed marginal range checks does not establish safe interpolation."
        )
        ttk.Label(self, text=note, wraplength=760, justify="left").grid(row=3, column=0, columnspan=2, sticky="w", pady=(18, 0))

    def get_values(self) -> dict[str, float]:
        try:
            return {key: float(self.values[key].get().strip()) for key, _ in FIELDS}
        except ValueError as exc:
            raise ValueError("Enter a numeric value for every input.") from exc

    def calculate(self) -> None:
        try:
            values = self.get_values()
            pu, derived = predict(values)
            warnings = range_warnings(values, derived)
        except ValueError as exc:
            messagebox.showerror("Input check", str(exc))
            return
        self.result.set(
            f"Predicted ultimate capacity: {pu:,.2f} kN\n\n"
            f"Aa = {derived['Aa_mm2']:,.2f} mm² | Ac = {derived['Ac_mm2']:,.2f} mm²\n"
            f"D/t = {derived['D_over_t']:.2f} | L/D = {derived['L_over_D']:.2f} | e/D = {derived['e_over_D']:.3f}"
        )
        if warnings:
            self.warning_text.set("Range warning(s):\n- " + "\n- ".join(warnings))
        else:
            self.warning_text.set(
                "All values fall within the marginal development ranges. This does not establish multivariate support, "
                "design validity or a safety margin."
            )

    def load_demo(self) -> None:
        case = CASES["cases"][0]
        for key, _ in FIELDS:
            self.values[key].set(str(case[key]))
        self.calculate()

    def clear(self) -> None:
        for variable in self.values.values():
            variable.set("")
        self.result.set("Enter an in-domain input set and select Calculate.")
        self.warning_text.set("Research use only. This tool is not a structural design check.")


def main() -> None:
    app = tk.Tk()
    ttk.Style().configure("Title.TLabel", font=("TkDefaultFont", 15, "bold"))
    CapacityEstimator(app)
    app.mainloop()


if __name__ == "__main__":
    main()
