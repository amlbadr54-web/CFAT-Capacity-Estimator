# CFAT Capacity Estimator

A lightweight Python/Tkinter GUI for estimating the ultimate load capacity of circular concrete-filled aluminum tubular (CFAT) columns using the exploratory geometry-based Ridge model developed in the accompanying study.

## Model scope

- Training records: 98 experimental CFAT records.
- Inputs: outer diameter `D` (mm), wall thickness `t` (mm), column length `L` (mm), load eccentricity `e` (mm), reported concrete compressive strength `fc` (MPa), and aluminum 0.2% proof stress `sigma0.2` (MPa).
- The prediction is returned in kN after exponentiating the fitted logarithmic-capacity model.
- The application checks the observed experimental ranges and withholds predictions outside those ranges.
- The tool is intended for research and preliminary assessment; it is not a design-code resistance calculator.

## Running on Windows

1. Install Python 3.10 or newer from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Extract this folder.
3. Double-click `START_WINDOWS.bat`, or run `py -3 app.py` from Command Prompt.

The application uses only Python's standard library (`tkinter`, `json`, `math`, and `pathlib`); no additional packages are required.

## Files

- `app.py` – GUI and prediction routine.
- `model.json` – frozen deployment coefficients, scaler information, ranges, and model metadata.
- `reference_cases.json` – illustrative cases used for the Load example button.
- `START_WINDOWS.bat` – Windows launcher.
- `CITATION.cff` – citation metadata.

## Reproducibility note

The model was developed after evaluation of the baseline models and is reported as an exploratory extension. Concrete strength values retain the source-reported test basis. The repository contains the deployment implementation and model parameters; the manuscript describes the data-screening, grouped-validation, and coefficient-interpretation procedures.
