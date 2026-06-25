"""One-at-a-time local sensitivity analysis (v1.8).

For a fixed severe-obstruction reference patient, each ventilator/mechanics input
is perturbed up and down while all others are held constant. The script reports
how the main simulated outputs respond, and draws a simple tornado figure on the
auto-PEEP and PaCO2 surrogates.

This is a transparency/illustration tool, not a formal global (Sobol) analysis.

Usage from project root:
    python src/sensitivity_analysis.py
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pediatric_asthma_ventilation_simulator import (
    load_scenario, simulate_scenario, summarize_outputs, load_builtin_scenario,
)

def load_named(name):
    return load_builtin_scenario(name[:-5] if name.endswith('.yaml') else name)

ROOT = Path(__file__).resolve().parents[1]
VERSION_TAG = "v1_8_1"
FIG_DIR = ROOT / "figures" / VERSION_TAG
OUTPUT_DIR = ROOT / "outputs" / VERSION_TAG

# (label, section, key, low_value, high_value). I:E uses string values.
PERTURBATIONS = [
    ("Raw_insp -/+30%", "airway_mechanics", "raw_insp_cmH2O_s_L", 33.6, 62.4),
    ("Crs -/+30%", "airway_mechanics", "crs_ml_cmH2O_kg", 0.70, 1.30),
    ("Heterogeneity -/+", "airway_mechanics", "heterogeneity_factor", 1.10, 1.60),
    ("VT 5.5 / 8.0 mL/kg", "ventilator", "vt_ml_kg", 5.5, 8.0),
    ("RR 14 / 30 bpm", "ventilator", "rr_bpm", 14, 30),
    ("I:E 1:2 / 1:5", "ventilator", "ie_ratio", "1:2", "1:5"),
]

OUTPUT_KEYS = ["max_autopeep_cmH2O", "max_pplat_cmH2O", "max_ppeak_cmH2O",
               "max_paco2_mmHg", "min_map_mmHg"]


def _run(ref, section, key, value):
    sc = copy.deepcopy(ref)
    sc[section][key] = value
    return summarize_outputs(simulate_scenario(sc))


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    ref = load_named("severe_obstruction_rr_reference.yaml")
    base = summarize_outputs(simulate_scenario(ref))

    rows = []
    for label, section, key, low, high in PERTURBATIONS:
        lo = _run(ref, section, key, low)
        hi = _run(ref, section, key, high)
        row = {"parameter": label}
        for k in OUTPUT_KEYS:
            row[f"low_{k}"] = lo[k]
            row[f"base_{k}"] = base[k]
            row[f"high_{k}"] = hi[k]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / f"sensitivity_analysis_{VERSION_TAG}.csv", index=False)

    for target, nice in [("max_autopeep_cmH2O", "auto-PEEP (cmH2O)"),
                         ("max_paco2_mmHg", "PaCO2 surrogate (mmHg)")]:
        base_val = base[target]
        spans = []
        for _, r in df.iterrows():
            lo, hi = r[f"low_{target}"], r[f"high_{target}"]
            spans.append((r["parameter"], min(lo, hi), max(lo, hi)))
        spans.sort(key=lambda s: (s[2] - s[1]))
        fig, ax = plt.subplots(figsize=(8.2, 4.6))
        for i, (name, lo, hi) in enumerate(spans):
            ax.barh(i, hi - lo, left=lo, color="tab:blue", alpha=0.6)
        ax.axvline(base_val, linestyle="--", color="grey", linewidth=1,
                   label=f"Baseline = {base_val:g}")
        ax.set_yticks(range(len(spans)))
        ax.set_yticklabels([s[0] for s in spans])
        ax.set_xlabel(f"Resulting {nice}")
        ax.set_title(f"Local sensitivity of {nice} (severe-obstruction reference)")
        ax.legend(frameon=False)
        plt.tight_layout()
        _sens_name = {"max_autopeep_cmH2O": "Figure_S4_AutoPEEP_Sensitivity",
                      "max_paco2_mmHg": "Figure_S4_PaCO2_Sensitivity"}.get(target, f"Figure_S4_{target}")
        out = FIG_DIR / f"{_sens_name}.png"
        plt.savefig(out, dpi=220)
        plt.close()
        print(f"Wrote {out}")

    print(f"Wrote {OUTPUT_DIR / f'sensitivity_analysis_{VERSION_TAG}.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
