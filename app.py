"""Original-layout desktop GUI for the frozen Circular CFAT ridge model."""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from cfat_core import FIELDS, predict_capacity, range_warnings


NAVY = "#173450"
BLUE = "#3b70b5"
PAGE = "#edf3fa"
CARD = "#ffffff"
INK = "#2f4054"
MUTED = "#718198"
GREEN = "#1e7864"
RED = "#bd2929"

EXAMPLE = {
    "D_mm": 100.0, "t_mm": 3.0, "L_mm": 300.0,
    "e_mm": 25.0, "fcu_eq_MPa": 45.0, "sigma02_MPa": 170.0,
}


class CircularCFATGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Circular CFAT Capacity Estimator")
        self.geometry("1031x740")
        self.minsize(980, 690)
        self.configure(bg=PAGE)
        self.vars = {key: tk.StringVar(value=str(EXAMPLE[key])) for key, _ in FIELDS}
        self.strength_basis = tk.StringVar(value="Cube / cube-equivalent — no conversion")
        self.result_value = tk.StringVar(value="327.90 kN")
        self.detail_value, self.screening_title, self.screening_detail = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self._setup_style()
        self._build()
        self.calculate()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background=PAGE)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Header.TLabel", background=NAVY, foreground="white", font=("Segoe UI", 16, "bold"))
        style.configure("HeaderNote.TLabel", background=NAVY, foreground="#f7d97a", font=("Segoe UI", 8, "bold"))
        style.configure("HeaderSub.TLabel", background=NAVY, foreground="#bdcce0", font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background=CARD, foreground=INK, font=("Segoe UI", 12, "bold"))
        style.configure("CardText.TLabel", background=CARD, foreground=INK, font=("Segoe UI", 9))
        style.configure("Hint.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Unit.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 8))
        style.configure("Result.TLabel", background=CARD, foreground=BLUE, font=("Segoe UI", 28, "bold"))
        style.configure("ResultLabel.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Primary.TButton", background=BLUE, foreground="white", padding=(12, 8), font=("Segoe UI", 9, "bold"))
        style.map("Primary.TButton", background=[("active", "#285d9f")])
        style.configure("Secondary.TButton", background="#eef3f8", foreground=INK, padding=(10, 8), font=("Segoe UI", 9))
        style.map("Secondary.TButton", background=[("active", "#dce7f1")])

    @staticmethod
    def _entry(parent: tk.Widget, variable: tk.StringVar) -> ttk.Entry:
        return ttk.Entry(parent, textvariable=variable, justify="right", font=("Segoe UI", 10))

    def _build(self) -> None:
        header = tk.Frame(self, bg=NAVY, height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        ttk.Label(header, text="CIRCULAR CFAT | CAPACITY ESTIMATOR", style="Header.TLabel").place(x=24, y=18)
        ttk.Label(header, text="Frozen Geometry Ridge · 98 experimental records · cube-equivalent concrete strength", style="HeaderSub.TLabel").place(x=24, y=50)
        ttk.Label(header, text="Research only • NOT for design verification", style="HeaderNote.TLabel").place(relx=1.0, x=-23, y=23, anchor="ne")

        main = ttk.Frame(self, style="App.TFrame", padding=(17, 14, 17, 8))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=49)
        main.columnconfigure(1, weight=49)
        main.rowconfigure(0, weight=1)
        left = ttk.Frame(main, style="Card.TFrame", padding=20)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        left.configure(relief="solid", borderwidth=1)
        right = ttk.Frame(main, style="App.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        self._build_inputs(left)
        self._build_results(right)

        footer = tk.Frame(self, bg="#e5edf6", height=57)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="Evidence: 98 development tests · nested grouped CV: R² 0.924, RMSE 173.12 kN | 21 external tests: R² 0.757, RMSE 203.96 kN; mean overprediction 122.60 kN.", bg="#e5edf6", fg="#5d6f83", font=("Segoe UI", 8), anchor="w").place(x=20, y=13)
        tk.Label(footer, text="Caution: external specimens were previously inspected on an earlier model; the prediction is NOT a code-compliant design capacity.", bg="#e5edf6", fg=RED, font=("Segoe UI", 8, "bold"), anchor="w").place(x=20, y=32)

    def _build_inputs(self, card: ttk.Frame) -> None:
        ttk.Label(card, text="Member & material inputs", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(card, text="Geometry in mm; strengths in MPa. Nominal/mean properties must be source-defined.", style="Hint.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(5, 18))
        card.columnconfigure(1, weight=1)
        rows = [
            ("D_mm", "Outer diameter D", "mm"), ("t_mm", "Wall thickness t", "mm"),
            ("L_mm", "Member length L", "mm"), ("e_mm", "Load eccentricity e", "mm"),
            ("fcu_eq_MPa", "Cube / cube-equivalent fcu,eq", "MPa"),
            ("sigma02_MPa", "Aluminum proof stress σ₀.₂", "MPa"),
        ]
        for row, (key, label, unit) in enumerate(rows, start=2):
            ttk.Label(card, text=label, style="CardText.TLabel").grid(row=row, column=0, sticky="w", pady=5)
            self._entry(card, self.vars[key]).grid(row=row, column=1, sticky="ew", pady=5, padx=(14, 10))
            ttk.Label(card, text=unit, style="Unit.TLabel").grid(row=row, column=2, sticky="w")

        ttk.Label(card, text="Concrete strength definition", style="CardText.TLabel", font=("Segoe UI", 9, "bold")).grid(row=8, column=0, columnspan=3, sticky="w", pady=(15, 7))
        combo = ttk.Combobox(card, textvariable=self.strength_basis, state="readonly", font=("Segoe UI", 9), values=("Cube / cube-equivalent — no conversion", "Cylinder strength — convert fc,cyl / 0.80"))
        combo.grid(row=9, column=0, columnspan=3, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda _event: self.calculate())
        ttk.Label(card, text="Enter measured cube strength or its documented cube-equivalent value.", style="Hint.TLabel").grid(row=10, column=0, columnspan=3, sticky="w", pady=(7, 17))
        action = ttk.Frame(card, style="Card.TFrame")
        action.grid(row=11, column=0, columnspan=3, sticky="w")
        ttk.Button(action, text="Calculate estimate", style="Primary.TButton", command=self.calculate).pack(side="left")
        ttk.Button(action, text="Example", style="Secondary.TButton", command=self.example).pack(side="left", padx=9)
        ttk.Button(action, text="Clear", style="Secondary.TButton", command=self.clear).pack(side="left")
        note = tk.Frame(card, bg="#f2f6fa", padx=12, pady=10)
        note.grid(row=12, column=0, columnspan=3, sticky="ew", pady=(20, 12))
        tk.Label(note, text="Strength-conversion note", bg="#f2f6fa", fg=INK, font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        tk.Label(note, text="If cylinder strength is selected: fc,cube,eq = fc,cyl / 0.80 (approximate conversion, not a universal concrete relationship).", bg="#f2f6fa", fg=MUTED, font=("Segoe UI", 8), justify="left", wraplength=400, anchor="w").pack(fill="x", pady=(4, 0))
        ttk.Label(card, text="DEVELOPMENT LIMITS — input screening only", style="Hint.TLabel", font=("Segoe UI", 8, "bold")).grid(row=13, column=0, columnspan=3, sticky="w", pady=(2, 3))
        ttk.Label(card, text="D 38–180.5 | t 2.02–10.24 | L 114–1920 | e 0–60 (mm)\nfcu,eq 22.38–132.5 | σ₀.₂ 70–516.94 (MPa)\nD/t 9.69–59.33 | L/D 2.99–18.20 | e/D 0–0.40", style="Hint.TLabel", justify="left").grid(row=14, column=0, columnspan=3, sticky="w")

    def _build_results(self, parent: ttk.Frame) -> None:
        top = ttk.Frame(parent, style="Card.TFrame", padding=20)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 13))
        top.configure(relief="solid", borderwidth=1)
        ttk.Label(top, text="Preliminary predicted ultimate load", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(top, text="Pû  (kN)", style="ResultLabel.TLabel").pack(anchor="w", pady=(11, 0))
        ttk.Label(top, textvariable=self.result_value, style="Result.TLabel").pack(anchor="w")
        ttk.Label(top, text="No design safety factor or resistance factor applied.", style="Hint.TLabel").pack(anchor="w", pady=(2, 13))
        ttk.Label(top, text="Converted strength & ratios", style="CardText.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Label(top, textvariable=self.detail_value, style="Hint.TLabel", justify="left").pack(anchor="w", pady=(5, 0))

        screen = ttk.Frame(parent, style="Card.TFrame", padding=20)
        screen.grid(row=1, column=0, sticky="nsew")
        screen.configure(relief="solid", borderwidth=1)
        ttk.Label(screen, text="Applicability screening", style="CardTitle.TLabel").pack(anchor="w")
        tk.Label(screen, textvariable=self.screening_title, bg=CARD, fg=GREEN, font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w", pady=(11, 9))
        tk.Label(screen, textvariable=self.screening_detail, bg=CARD, fg=INK, font=("Consolas", 8), justify="left", anchor="nw", wraplength=420).pack(anchor="w", fill="x")
        bottom = ttk.Frame(parent, style="App.TFrame")
        bottom.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(bottom, text="Copy report", style="Secondary.TButton", command=self.copy_report).pack(side="left")
        ttk.Button(bottom, text="Save report (.txt)", style="Secondary.TButton", command=self.save_report).pack(side="left", padx=10)
        ttk.Button(bottom, text="Model details", style="Secondary.TButton", command=self.model_details).pack(side="right")

    def _values(self) -> dict[str, float]:
        try:
            return {key: float(var.get().strip()) for key, var in self.vars.items()}
        except ValueError as exc:
            raise ValueError("Enter numeric values for all six inputs.") from exc

    def calculate(self) -> None:
        try:
            values = self._values()
            if "Cylinder" in self.strength_basis.get():
                values["fcu_eq_MPa"] /= 0.80
            pu, derived = predict_capacity(values)
            warnings = range_warnings(values, derived)
        except ValueError as exc:
            messagebox.showerror("Input check", str(exc), parent=self)
            return
        self.result_value.set(f"{pu:,.2f} kN")
        self.detail_value.set(f"Concrete fcu,cube,eq = {values['fcu_eq_MPa']:.3f} MPa   |   Eccentric loading\nD/t = {derived['D_over_t']:.2f}     L/D = {derived['L_over_D']:.2f}     e/D = {derived['e_over_D']:.3f}")
        if warnings:
            self.screening_title.set("Outside one or more individual development limits")
            self.screening_detail.set("\n".join("• " + warning for warning in warnings) + "\n\nThis is NOT proof of design capacity or safe extrapolation.")
        else:
            self.screening_title.set("Within all individual development limits")
            self.screening_detail.set("All six inputs and the three geometric ratios lie inside their individual development ranges.\n\nThis is NOT proof of joint-data support or safe design resistance.\n\nData limitations: only 27 eccentric tests in the 98 experimental development records; 8 source groups.")

    def example(self) -> None:
        self.strength_basis.set("Cube / cube-equivalent — no conversion")
        for key, value in EXAMPLE.items():
            self.vars[key].set(str(value))
        self.calculate()

    def clear(self) -> None:
        for var in self.vars.values():
            var.set("")
        self.result_value.set("— kN")
        self.detail_value.set("Enter an input set and calculate an estimate.")
        self.screening_title.set("Awaiting model inputs")
        self.screening_detail.set("The screening panel will show individual range checks after calculation.")

    def report(self) -> str:
        return f"CIRCULAR CFAT CAPACITY ESTIMATOR\nGenerated: {datetime.now():%Y-%m-%d %H:%M}\n\nPredicted ultimate load: {self.result_value.get()}\n\n{self.detail_value.get()}\n\nApplicability screening\n{self.screening_title.get()}\n{self.screening_detail.get()}\n\nResearch only — NOT for design verification."

    def copy_report(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.report())
        self.update()
        messagebox.showinfo("Copy report", "The summary was copied to the clipboard.", parent=self)

    def save_report(self) -> None:
        path = filedialog.asksaveasfilename(parent=self, title="Save estimator report", defaultextension=".txt", initialfile="CFAT_capacity_estimate.txt", filetypes=[("Text file", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as report_file:
                report_file.write(self.report())

    def model_details(self) -> None:
        messagebox.showinfo("Model details", "Frozen geometry ridge formulation\n98 experimental records; 8 source groups\nNested grouped CV: R² = 0.924; RMSE = 173.12 kN\n\nThis GUI evaluates fixed coefficients only. It does not train or tune a model.", parent=self)


if __name__ == "__main__":
    CircularCFATGUI().mainloop()
