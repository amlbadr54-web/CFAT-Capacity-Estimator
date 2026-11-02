"""Blue desktop GUI for the frozen Circular CFAT research model."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from cfat_core import DEMO_CASE, FIELDS, predict_capacity, range_warnings


NAVY = "#0b2f5b"
BLUE = "#1464aa"
PALE_BLUE = "#eaf4ff"
TEXT = "#152536"
MUTED = "#5e7185"
WARNING = "#a13918"


class CapacityEstimator(ttk.Frame):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent, padding=0)
        self.parent = parent
        parent.title("CFAT Capacity Estimator v2 | Research Prototype")
        parent.minsize(980, 690)
        parent.configure(bg=PALE_BLUE)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        self.grid(sticky="nsew")
        self.values = {key: tk.StringVar() for key, _ in FIELDS}
        self.capacity = tk.StringVar(value="—")
        self.summary = tk.StringVar(value="Enter a complete input set, then select Calculate capacity.")
        self.warning = tk.StringVar(value="Research use only — this tool is not a structural design check.")
        self._configure_style()
        self._build()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background=PALE_BLUE)
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", background=NAVY, foreground="white", font=("Segoe UI", 21, "bold"))
        style.configure("SubTitle.TLabel", background=NAVY, foreground="#cfe8ff", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background="white", foreground=BLUE, font=("Segoe UI", 12, "bold"))
        style.configure("Field.TLabel", background="white", foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Hint.TLabel", background="white", foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Result.TLabel", background="white", foreground=NAVY, font=("Segoe UI", 25, "bold"))
        style.configure("ResultNote.TLabel", background="white", foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Warning.TLabel", background="#fff4ed", foreground=WARNING, font=("Segoe UI", 9))
        style.configure("Primary.TButton", background=BLUE, foreground="white", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.map("Primary.TButton", background=[("active", "#0d508c")])
        style.configure("Secondary.TButton", background="#d8eafa", foreground=NAVY, font=("Segoe UI", 10), padding=(12, 8))

    def _build(self) -> None:
        shell = ttk.Frame(self, style="App.TFrame", padding=20)
        shell.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)

        header = tk.Frame(shell, bg=NAVY, padx=25, pady=20)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(header, text="CIRCULAR CFAT CAPACITY ESTIMATOR", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="v2 GUI Restore  •  Frozen cube-equivalent ridge formulation  •  Research prototype", style="SubTitle.TLabel").pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(shell, style="App.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=11)
        body.columnconfigure(1, weight=9)
        body.rowconfigure(0, weight=1)
        inputs = ttk.Frame(body, style="Card.TFrame", padding=22)
        results = ttk.Frame(body, style="Card.TFrame", padding=22)
        inputs.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        results.grid(row=0, column=1, sticky="nsew")
        inputs.columnconfigure(1, weight=1)

        ttk.Label(inputs, text="Model inputs", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(inputs, text="Use consistent units shown below. All fields are required.", style="Hint.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(3, 17))
        for row, (key, label) in enumerate(FIELDS, start=2):
            ttk.Label(inputs, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w", pady=7, padx=(0, 16))
            ttk.Entry(inputs, textvariable=self.values[key], width=25, font=("Segoe UI", 10)).grid(row=row, column=1, sticky="ew", pady=7)
        buttons = ttk.Frame(inputs, style="Card.TFrame")
        buttons.grid(row=8, column=0, columnspan=2, sticky="w", pady=(22, 0))
        ttk.Button(buttons, text="Calculate capacity", style="Primary.TButton", command=self.calculate).pack(side="left")
        ttk.Button(buttons, text="Load demo", style="Secondary.TButton", command=self.load_demo).pack(side="left", padx=8)
        ttk.Button(buttons, text="Clear", style="Secondary.TButton", command=self.clear).pack(side="left")

        ttk.Label(results, text="Predicted capacity", style="Section.TLabel").pack(anchor="w")
        ttk.Label(results, text="Ultimate load, Pu", style="Hint.TLabel").pack(anchor="w", pady=(15, 0))
        ttk.Label(results, textvariable=self.capacity, style="Result.TLabel").pack(anchor="w", pady=(2, 0))
        ttk.Label(results, text="kN", style="ResultNote.TLabel").pack(anchor="w")
        ttk.Separator(results).pack(fill="x", pady=20)
        ttk.Label(results, textvariable=self.summary, style="ResultNote.TLabel", wraplength=350, justify="left").pack(anchor="w")
        warning_box = tk.Label(results, textvariable=self.warning, bg="#fff4ed", fg=WARNING, anchor="nw", justify="left", wraplength=350, padx=12, pady=12, font=("Segoe UI", 9))
        warning_box.pack(fill="x", pady=(20, 0))
        foot = ttk.Label(shell, text="For research and preliminary estimation only. No resistance factor, lower-bound capacity, or code compliance check is provided.", style="Hint.TLabel", wraplength=900)
        foot.grid(row=2, column=0, sticky="w", pady=(14, 0))

    def _read_inputs(self) -> dict[str, float]:
        try:
            return {key: float(self.values[key].get().strip()) for key, _ in FIELDS}
        except ValueError as exc:
            raise ValueError("Please enter a numeric value in every input field.") from exc

    def calculate(self) -> None:
        try:
            values = self._read_inputs()
            pu, derived = predict_capacity(values)
            warnings = range_warnings(values, derived)
        except ValueError as exc:
            messagebox.showerror("Input check", str(exc))
            return
        self.capacity.set(f"{pu:,.2f}")
        self.summary.set(f"Aa = {derived['Aa_mm2']:,.1f} mm²   |   Ac = {derived['Ac_mm2']:,.1f} mm²\nD/t = {derived['D_over_t']:.2f}   |   L/D = {derived['L_over_D']:.2f}   |   e/D = {derived['e_over_D']:.3f}")
        self.warning.set("Range warning(s):\n• " + "\n• ".join(warnings) if warnings else "All individual values are within the model development ranges. This does not establish multivariate support, safety, or design validity.")

    def load_demo(self) -> None:
        for key, value in DEMO_CASE.items():
            self.values[key].set(str(value))
        self.calculate()

    def clear(self) -> None:
        for variable in self.values.values():
            variable.set("")
        self.capacity.set("—")
        self.summary.set("Enter a complete input set, then select Calculate capacity.")
        self.warning.set("Research use only — this tool is not a structural design check.")


def main() -> None:
    root = tk.Tk()
    CapacityEstimator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
