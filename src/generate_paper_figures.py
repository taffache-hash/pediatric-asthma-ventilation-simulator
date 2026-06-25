"""Generate manuscript-oriented figures from selected scenarios (v1.8).

The figures are intentionally plain and reproducible. They are intended for
manuscript review and teaching, not as final journal artwork.

Usage from project root:
    python src/generate_paper_figures.py
"""

from __future__ import annotations

import copy
import sys
from dataclasses import asdict
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

SCENARIO_LABELS = {
    "safe_controlled_hypoventilation": "Controlled hypoventilation",
    "high_rr_dynamic_hyperinflation": "High respiratory rate",
    "post_intubation_collapse": "Post-intubation collapse",
    "silent_chest_low_etco2": "Silent chest / EtCO2 pitfall",
    "spontaneous_autopeep_peep_titration": "Spontaneous PEEP titration",
}


def scenario_df(filename: str) -> pd.DataFrame:
    scn = load_named(filename)
    outputs = simulate_scenario(scn)
    df = pd.DataFrame([asdict(o) for o in outputs])
    sid = scn.get("scenario_id", filename.replace(".yaml", ""))
    df["scenario_id"] = sid
    df["scenario_label"] = SCENARIO_LABELS.get(sid, sid.replace("_", " ").title())
    df["vei_proxy_ml_kg"] = df["trapped_volume_ml_kg"] + df["vt_ml_kg"]
    df["paco2_etco2_gap_mmHg"] = df["paco2_mmHg"] - df["etco2_mmHg"]
    df["pip_minus_pplat_cmH2O"] = df["ppeak_cmH2O"] - df["pplat_cmH2O"]
    return df


def peep_sweep_table(reference_yaml: str, peep_values) -> pd.DataFrame:
    """Applied-PEEP sweep on the spontaneous patient: trigger-work unloading and
    the hemodynamic cost that appears once applied PEEP exceeds intrinsic PEEP."""
    ref = load_named(reference_yaml)
    rows = []
    for peep in peep_values:
        sc = copy.deepcopy(ref)
        sc["ventilator"]["peep_cmH2O"] = peep
        outs = simulate_scenario(sc)
        s = summarize_outputs(outs)
        rows.append({
            "applied_peep_cmH2O": peep,
            "max_autopeep_cmH2O": s["max_autopeep_cmH2O"],
            "max_trigger_work_index": max(o.trigger_work_index for o in outs),
            "max_external_peep_excess_cmH2O": max(o.external_peep_excess_cmH2O for o in outs),
            "min_map_mmHg": s["min_map_mmHg"],
        })
    return pd.DataFrame(rows)


def plot_peep_sweep(df: pd.DataFrame, intrinsic_peep: float, filename: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    fig, ax1 = plt.subplots(figsize=(7.6, 4.6))
    ax1.plot(df["applied_peep_cmH2O"], df["max_trigger_work_index"],
             marker="o", color="tab:blue", label="Inspiratory trigger-work index")
    ax1.set_xlabel("Applied (external) PEEP (cmH2O)")
    ax1.set_ylabel("Trigger-work index", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.axvline(intrinsic_peep, linestyle="--", linewidth=1, color="grey",
                label=f"Intrinsic PEEP (~{intrinsic_peep:g} cmH2O)")
    ax2 = ax1.twinx()
    ax2.plot(df["applied_peep_cmH2O"], df["min_map_mmHg"],
             marker="s", color="tab:red", label="MAP surrogate")
    ax2.set_ylabel("MAP surrogate (mmHg)", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="center right")
    plt.title("Counterbalancing PEEP: trigger-work unloading vs hemodynamic cost")
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def _finish(path: Path) -> Path:
    plt.tight_layout()
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def plot_overlay(dfs, y, ylabel, title, filename, threshold=None) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    plt.figure(figsize=(7.2, 4.3))
    for df in dfs:
        plt.plot(df["time_min"], df[y], label=str(df["scenario_label"].iloc[0]))
    if threshold is not None:
        plt.axhline(threshold, linestyle="--", linewidth=1, label=f"Teaching threshold: {threshold:g}")
    plt.xlabel("Time (min)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(frameon=False)
    return _finish(path)


def plot_single(df, y, ylabel, title, filename, threshold=None) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    plt.figure(figsize=(7.2, 4.3))
    plt.plot(df["time_min"], df[y], label=str(df["scenario_label"].iloc[0]))
    if threshold is not None:
        plt.axhline(threshold, linestyle="--", linewidth=1, label=f"Teaching threshold: {threshold:g}")
    plt.xlabel("Time (min)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(frameon=False)
    return _finish(path)


def plot_two_series(df, y1, y2, label1, label2, ylabel, title, filename) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    plt.figure(figsize=(7.2, 4.3))
    plt.plot(df["time_min"], df[y1], label=label1)
    plt.plot(df["time_min"], df[y2], label=label2)
    plt.xlabel("Time (min)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(frameon=False, loc="best")
    return _finish(path)


def rr_sweep_table(reference_yaml: str, rr_values) -> pd.DataFrame:
    """Same-patient respiratory-rate sweep on a fixed severe-obstruction patient."""
    ref = load_named(reference_yaml)
    rows = []
    for rr in rr_values:
        sc = copy.deepcopy(ref)
        sc["ventilator"]["rr_bpm"] = rr
        s = summarize_outputs(simulate_scenario(sc))
        rows.append({
            "rr_bpm": rr,
            "max_autopeep_cmH2O": s["max_autopeep_cmH2O"],
            "max_pplat_cmH2O": s["max_pplat_cmH2O"],
            "max_paco2_mmHg": s["max_paco2_mmHg"],
            "min_map_mmHg": s["min_map_mmHg"],
        })
    return pd.DataFrame(rows)


def plot_rr_sweep(df: pd.DataFrame, filename: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    nadir_idx = df["max_paco2_mmHg"].idxmin()
    nadir_rr = df.loc[nadir_idx, "rr_bpm"]
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 7.0))
    panels = [
        ("max_paco2_mmHg", "PaCO2 surrogate (mmHg)", "CO2 clearance is U-shaped vs RR"),
        ("max_autopeep_cmH2O", "Auto-PEEP (cmH2O)", "Auto-PEEP rises monotonically"),
        ("max_pplat_cmH2O", "Plateau pressure (cmH2O)", "Plateau pressure rises monotonically"),
        ("min_map_mmHg", "MAP surrogate (mmHg)", "MAP falls monotonically"),
    ]
    for ax, (col, ylabel, title) in zip(axes.ravel(), panels):
        ax.plot(df["rr_bpm"], df[col], marker="o", markersize=3)
        ax.axvline(nadir_rr, linestyle="--", linewidth=1, color="grey")
        ax.set_xlabel("Set respiratory rate (breaths/min)")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=10)
    fig.suptitle(
        f"Same-patient RR sweep, severe obstruction (PaCO2 nadir at RR {nadir_rr:g})",
        fontsize=12,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(path, dpi=220)
    plt.close()
    return path


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    safe = scenario_df("safe_controlled_hypoventilation.yaml")
    high_rr = scenario_df("high_rr_dynamic_hyperinflation.yaml")
    collapse = scenario_df("post_intubation_collapse.yaml")
    silent = scenario_df("silent_chest_low_etco2.yaml")
    spont = scenario_df("spontaneous_autopeep_peep_titration.yaml")

    safe.to_csv(OUTPUT_DIR / f"figure_safe_controlled_hypoventilation_{VERSION_TAG}.csv", index=False)
    high_rr.to_csv(OUTPUT_DIR / f"figure_high_rr_dynamic_hyperinflation_{VERSION_TAG}.csv", index=False)
    collapse.to_csv(OUTPUT_DIR / f"figure_post_intubation_collapse_{VERSION_TAG}.csv", index=False)
    silent.to_csv(OUTPUT_DIR / f"figure_silent_chest_low_etco2_{VERSION_TAG}.csv", index=False)
    spont.to_csv(OUTPUT_DIR / f"figure_spontaneous_autopeep_peep_titration_{VERSION_TAG}.csv", index=False)

    # Primary internal-verification figure: same-patient RR sweep (U-shaped CO2 trade-off).
    rr_df = rr_sweep_table("severe_obstruction_rr_reference.yaml", list(range(6, 41, 2)))
    rr_df.to_csv(OUTPUT_DIR / f"rr_sweep_severe_obstruction_{VERSION_TAG}.csv", index=False)

    paths = [
        plot_rr_sweep(rr_df, "Figure_1_RR_Sweep.png"),
        plot_overlay(
            [safe, high_rr], "autopeep_cmH2O",
            "Simulated auto-PEEP (cmH2O)",
            "High respiratory rate increases simulated auto-PEEP",
            "Figure_2_AutoPEEP_Controlled_vs_HighRR.png",
        ),
        plot_overlay(
            [safe, high_rr], "vei_proxy_ml_kg",
            "Simulated VEI proxy (mL/kg)",
            "High respiratory rate increases dynamic hyperinflation proxy",
            "Figure_S1_Hyperinflation_Proxy.png", threshold=20.0,
        ),
        plot_overlay(
            [safe, high_rr], "paco2_mmHg",
            "Simulated PaCO2 surrogate (mmHg)",
            "Carbon dioxide trade-off between safer timing and high RR",
            "Figure_3_PaCO2_Controlled_vs_HighRR.png",
        ),
        plot_single(
            collapse, "map_mmHg",
            "Simulated MAP surrogate (mmHg)",
            "Post-intubation collapse scenario: unsafe-threshold demonstration",
            "Figure_S2_MAP_PostIntubation_Collapse.png", threshold=55.0,
        ),
        plot_two_series(
            silent, "paco2_mmHg", "etco2_mmHg",
            "Simulated PaCO2 surrogate", "Simulated EtCO2 surrogate",
            "CO2 surrogate (mmHg)",
            "Silent chest scenario: PaCO2-EtCO2 dissociation",
            "Figure_4_PaCO2_EtCO2_SilentChest.png",
        ),
        # Optional figure: high resistive PIP with acceptable plateau (safe scenario).
        plot_two_series(
            safe, "ppeak_cmH2O", "pplat_cmH2O",
            "Peak inspiratory pressure", "Plateau pressure",
            "Airway pressure (cmH2O)",
            "Controlled hypoventilation: wide PIP-to-plateau gap in obstruction",
            "Figure_S3_PIP_Pplat_Gap.png",
        ),
    ]

    # Optional figure: counterbalancing PEEP in the spontaneous patient.
    peep_df = peep_sweep_table("spontaneous_autopeep_peep_titration.yaml", [0, 2, 3, 5, 7, 9, 12])
    peep_df.to_csv(OUTPUT_DIR / f"peep_sweep_spontaneous_{VERSION_TAG}.csv", index=False)
    intrinsic = float(peep_df["max_autopeep_cmH2O"].iloc[0])
    paths.append(plot_peep_sweep(peep_df, intrinsic, "Figure_5_PEEP_Titration.png"))

    paths.append(plot_model_architecture("Figure_S5_Model_Architecture.png"))

    for path in paths:
        print(f"Wrote {path}")
    return 0


def plot_model_architecture(filename: str) -> Path:
    """Render a state/architecture diagram of the model pathway (teaching aid)."""
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9); ax.axis("off")

    def box(x, y, w, h, text, fc):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.2, edgecolor="#333333", facecolor=fc))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#555555", lw=1.1))

    IN, MECH, GAS, HEMO, OUT = "#E8F0FE", "#FCE8E6", "#FEF7E0", "#E6F4EA", "#F1F3F4"

    # Inputs
    box(0.3, 6.6, 2.5, 1.5, "Scenario (YAML)\npatient · mechanics\nventilator", IN)
    box(0.3, 0.8, 2.5, 1.3, "Schema validation\n(canonical modes,\nranges)", IN)
    arrow(1.55, 6.6, 1.55, 2.1)

    # Mechanics pathway
    box(3.4, 7.0, 2.6, 1.1, "Te / tau\nr = exp(-Te/tau)", MECH)
    box(3.4, 5.4, 2.6, 1.1, "Trapped volume\nVT·r/(1-r)", MECH)
    box(3.4, 3.8, 2.6, 1.1, "Auto-PEEP\nsurrogate", MECH)
    box(3.4, 2.2, 2.6, 1.1, "Total PEEP →\nPplat surrogate", MECH)
    for y1, y2 in [(7.0, 6.5), (5.4, 4.9), (3.8, 3.3)]:
        arrow(4.7, y1, 4.7, y2)
    arrow(2.8, 7.35, 3.4, 7.55)

    # Gas exchange
    box(6.6, 6.2, 2.6, 1.6, "Alveolar ventilation\n→ PaCO2 (0.863·VCO2/VA)\n→ pH · EtCO2 surrogates", GAS)
    arrow(6.0, 5.95, 6.6, 6.6)

    # Hemodynamics
    box(6.6, 3.2, 2.6, 1.6, "MAP surrogate\npreload · auto-PEEP\ncounterbalancing-PEEP\n(teaching approximation)", HEMO)
    arrow(6.0, 2.75, 6.6, 3.6)

    # Outputs
    box(9.7, 4.6, 2.0, 1.6, "Outputs\nCSV · figures\n(directional\nsurrogates)", OUT)
    arrow(9.2, 7.0, 9.7, 5.9)
    arrow(9.2, 4.0, 9.7, 5.0)

    ax.text(6, 8.6, "Model architecture — directional surrogates, not clinical predictions",
            ha="center", va="center", fontsize=10, fontweight="bold")
    out = FIG_DIR / filename
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close(fig)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
