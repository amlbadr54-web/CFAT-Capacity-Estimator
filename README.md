# Circular CFAT Capacity Estimator

Research-only desktop interface for the frozen cube-equivalent ridge formulation reported in the revised Structures manuscript.

## What to upload to GitHub

Replace the repository files with the contents of this folder:

- `app.py`
- `model.json`
- `reference_cases.json`
- `requirements.txt`
- `START_WINDOWS.bat`
- `README.md`

Do not upload the manuscript, external-validation records, or reviewer-response files to the public repository unless the authors explicitly choose to make those materials public.

## Run on Windows

1. Install Python 3.10 or later, including tkinter.
2. Download the repository files into one folder.
3. Double-click `START_WINDOWS.bat`, or run `py app.py` from that folder.

No third-party packages are required.

## Model

The tool evaluates the frozen full-98 cube-equivalent ridge equation directly. Inputs are outer diameter `D`, thickness `t`, length `L`, eccentricity `e`, cube-equivalent concrete strength `fcu,eq`, and aluminum 0.2% proof stress `sigma0.2`.

The output is a predicted ultimate capacity in kN. The program checks physical validity and reports whether individual inputs and derived ratios fall within the marginal development ranges. These checks do **not** demonstrate joint data support, safe interpolation, code compliance, or a safety margin.

If a cylinder concrete strength is used, the optional model convention is `fcu,eq = fc,cyl / 0.80`. This is an explicit modelling approximation, not a universal material conversion.

## Limitations

- The application is a research prototype, not a structural-design or safety-verification tool.
- The grouped development RMSE is not a guaranteed error for an individual estimate.
- The model does not provide a lower-bound resistance, resistance factor, or monotonicity guarantee.
- External-source evaluation showed systematic overprediction, including all nine eccentric external specimens; do not use the output as a design resistance.
