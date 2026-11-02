# CFAT Capacity Estimator v2 — GUI Restore

Desktop research interface for the frozen cube-equivalent ridge model used in the revised Circular CFAT study.

## Repository files

This package contains exactly the files required to run the application:

- `app.py` — blue graphical interface
- `cfat_core.py` — frozen-model calculation and range-check functions
- `model.json` — model coefficients, development ranges, and limitations
- `README.md` — this guide
- `START_WINDOWS.bat` — Windows launcher
- `requirements.txt` — Python requirements

## Run on Windows

1. Install Python 3.10 or later, with **tkinter** included.
2. Download or clone this repository into one folder.
3. Double-click `START_WINDOWS.bat`.

Alternatively, open Command Prompt in the folder and run:

```bat
py app.py
```

No third-party Python package is required.

## Inputs and output

Inputs are outer diameter `D`, wall thickness `t`, length `L`, eccentricity `e`, cube-equivalent concrete strength `fcu,eq`, and aluminum 0.2% proof stress `σ0.2`. The model returns the predicted ultimate capacity `Pu` in kN, calculated section areas, and geometric ratios.

The input convention is cube-equivalent concrete strength. If a cylinder strength is available, the modelling convention in this study is `fcu,eq = fc,cyl / 0.80`; it is an approximation, not a universal strength conversion.

## Important limitations

This is a **research prototype**, not a structural-design or safety-verification application. Range notices check each value separately; they do not prove safe interpolation, joint data support, code compliance, or a safety margin. The model supplies no lower-bound resistance or calibrated resistance factor. Independent external evaluation indicated systematic overprediction, so the output must not be used as design resistance.
