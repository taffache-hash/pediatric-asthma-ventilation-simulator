"""Streamlit interface for Pediatric Asthma Ventilation Simulator v1.8.1.

Run from the project root:
    streamlit run app/streamlit_app.py

Educational simulator only. Not clinical decision support.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import copy
import sys
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    load_scenario, simulate_scenario, summarize_outputs,
    list_builtin_scenarios, builtin_scenario_path,
)

VERSION = "v1.8.1"


def list_scenarios() -> List[Path]:
    return [builtin_scenario_path(sid) for sid in list_builtin_scenarios()]


def scenario_label(path: Path) -> str:
    try:
        scn = load_scenario(path)
        title = scn.get("title", path.stem)
        return f"{scn.get('scenario_id', path.stem)} — {title}"
    except Exception:
        return path.stem


def as_dataframe(outputs) -> pd.DataFrame:
    return pd.DataFrame([asdict(o) for o in outputs])


def risk_badge(label: str) -> str:
    label = str(label).lower()
    if label == "critical":
        return "CRITICAL"
    if label == "warning":
        return "WARNING"
    return "LOW"


def apply_sidebar_controls(base: Dict[str, Any]) -> Dict[str, Any]:
    scenario = copy.deepcopy(base)

    st.sidebar.header("Scenario controls")
    scenario["duration_min"] = st.sidebar.slider(
        "Simulation duration (min)", 5, 120, int(scenario.get("duration_min", 60)), 5
    )
    scenario["time_step_s"] = st.sidebar.select_slider(
        "Time step (s)", options=[1, 2, 5, 10, 15, 30], value=int(scenario.get("time_step_s", 5))
    )

    st.sidebar.header("Patient")
    p = scenario["patient"]
    p["age_years"] = st.sidebar.slider("Age (years)", 1.0, 18.0, float(p.get("age_years", 8)), 0.5)
    p["weight_kg"] = st.sidebar.slider("Weight (kg)", 8.0, 80.0, float(p.get("weight_kg", 25)), 0.5)
    p["map_baseline_mmHg"] = st.sidebar.slider("Baseline MAP (mmHg)", 40, 90, int(p.get("map_baseline_mmHg", 65)), 1)
    p["preload_status"] = st.sidebar.selectbox(
        "Preload status", ["normal", "borderline", "low"],
        index=["normal", "borderline", "low"].index(p.get("preload_status", "normal"))
        if p.get("preload_status", "normal") in ["normal", "borderline", "low"] else 0,
    )
    p["patient_effort"] = st.sidebar.selectbox(
        "Patient effort", ["passive", "spontaneous"],
        index=1 if "spontaneous" in str(p.get("patient_effort", "passive")).lower() else 0,
    )

    st.sidebar.header("Airway mechanics")
    m = scenario["airway_mechanics"]
    obstruction_options = ["mild", "moderate", "severe", "critical"]
    current_obstruction = str(m.get("obstruction_severity", "severe")).lower()
    if current_obstruction not in obstruction_options:
        current_obstruction = "severe"
    m["obstruction_severity"] = st.sidebar.selectbox(
        "Obstruction severity", obstruction_options, index=obstruction_options.index(current_obstruction)
    )
    m["raw_insp_cmH2O_s_L"] = st.sidebar.slider(
        "Inspiratory resistance Raw (cmH₂O·s/L)", 5.0, 80.0, float(m.get("raw_insp_cmH2O_s_L", 35)), 1.0
    )
    m["raw_exp_multiplier"] = st.sidebar.slider(
        "Expiratory resistance multiplier", 1.0, 3.5, float(m.get("raw_exp_multiplier", 1.6)), 0.1
    )
    m["crs_ml_cmH2O_kg"] = st.sidebar.slider(
        "Compliance (mL/cmH₂O/kg)", 0.35, 2.0, float(m.get("crs_ml_cmH2O_kg", 1.0)), 0.05
    )
    m["heterogeneity_factor"] = st.sidebar.slider(
        "Heterogeneity factor", 1.0, 2.5, float(m.get("heterogeneity_factor", 1.1)), 0.05
    )
    m["secretions_factor"] = st.sidebar.slider(
        "Secretions factor", 1.0, 2.2, float(m.get("secretions_factor", 1.0)), 0.05
    )

    st.sidebar.header("Ventilator")
    v = scenario["ventilator"]
    mode_options = ["VCV", "PCV", "PSV_CPAP", "MANUAL_BAGGING_THEN_VCV"]
    current_mode = str(v.get("mode", "VCV")).upper()
    if current_mode not in mode_options:
        current_mode = "VCV"
    v["mode"] = st.sidebar.selectbox("Mode", mode_options, index=mode_options.index(current_mode))
    v["rr_bpm"] = st.sidebar.slider("Respiratory rate (/min)", 4, 40, int(v.get("rr_bpm", v.get("backup_rr_bpm", 12))), 1)
    v["peep_cmH2O"] = st.sidebar.slider("External PEEP (cmH₂O)", 0.0, 14.0, float(v.get("peep_cmH2O", 3)), 0.5)
    ie_options = ["1:2", "1:3", "1:4", "1:5", "1:6", "patient_determined"]
    current_ie = str(v.get("ie_ratio", "1:4"))
    if current_ie not in ie_options:
        current_ie = "1:4"
    v["ie_ratio"] = st.sidebar.selectbox("I:E ratio", ie_options, index=ie_options.index(current_ie))
    v["insp_flow_l_min"] = st.sidebar.slider("Inspiratory flow (L/min)", 10, 100, int(v.get("insp_flow_l_min", 60)), 5)

    if v["mode"] in {"VCV", "MANUAL_BAGGING_THEN_VCV"}:
        v["vt_ml_kg"] = st.sidebar.slider("VT (mL/kg)", 4.0, 14.0, float(v.get("vt_ml_kg", 6.5) or 6.5), 0.5)
    if v["mode"] == "PCV":
        v["pressure_control_cmH2O_above_peep"] = st.sidebar.slider(
            "PC above PEEP (cmH₂O)", 6.0, 40.0, float(v.get("pressure_control_cmH2O_above_peep", 18) or 18), 1.0
        )
    if v["mode"] == "PSV_CPAP":
        v["pressure_support_cmH2O"] = st.sidebar.slider(
            "PS above PEEP (cmH₂O)", 4.0, 30.0, float(v.get("pressure_support_cmH2O", 10) or 10), 1.0
        )

    st.sidebar.header("Therapies")
    therapies = scenario.setdefault("therapies", {})
    therapies["continuous_albuterol"] = st.sidebar.checkbox(
        "Continuous beta-agonist", value=bool(therapies.get("continuous_albuterol", True))
    )
    therapies["ipratropium"] = st.sidebar.checkbox("Ipratropium", value=bool(therapies.get("ipratropium", False)))
    magnesium = therapies.setdefault("magnesium", {}) or {}
    magnesium["enabled"] = st.sidebar.checkbox("Magnesium", value=bool(magnesium.get("enabled", False)))
    therapies["magnesium"] = magnesium
    ketamine = therapies.setdefault("ketamine", {}) or {}
    ketamine["enabled"] = st.sidebar.checkbox("Ketamine", value=bool(ketamine.get("enabled", False)))
    if ketamine["enabled"]:
        ketamine["infusion_mg_kg_h"] = st.sidebar.slider(
            "Ketamine infusion (mg/kg/h)", 0.25, 3.0, float(ketamine.get("infusion_mg_kg_h", 1.0) or 1.0), 0.25
        )
    therapies["ketamine"] = ketamine
    steroid = therapies.setdefault("steroid", {}) or {}
    steroid["enabled"] = st.sidebar.checkbox("Steroid already given", value=bool(steroid.get("enabled", True)))
    if steroid["enabled"]:
        steroid["minutes_since_first_dose"] = st.sidebar.slider(
            "Minutes since steroid", 0, 360, int(steroid.get("minutes_since_first_dose", 60) or 60), 15
        )
    therapies["steroid"] = steroid

    return scenario


def show_key_metrics(summary: Dict[str, Any], prefix: str = "") -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{prefix}Max auto-PEEP", f"{summary['max_autopeep_cmH2O']:.1f} cmH₂O")
    c2.metric(f"{prefix}Max Pplat", f"{summary['max_pplat_cmH2O']:.1f} cmH₂O")
    c3.metric(f"{prefix}Final PaCO₂", f"{summary['final_paco2_mmHg']:.0f} mmHg")
    c4.metric(f"{prefix}Min MAP", f"{summary['min_map_mmHg']:.0f} mmHg")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(f"{prefix}Min pH", f"{summary['min_ph']:.2f}")
    c6.metric(f"{prefix}Max VEI proxy", f"{summary['max_vei_ml_kg']:.1f} mL/kg")
    c7.metric(f"{prefix}Barotrauma risk", risk_badge(summary["final_barotrauma_risk"]))
    c8.metric(f"{prefix}Hemodynamic risk", risk_badge(summary["final_hemodynamic_risk"]))


def generate_teaching_points(summary: Dict[str, Any]) -> List[str]:
    points: List[str] = []
    if summary["max_pplat_cmH2O"] >= 30:
        points.append("Pplat crosses the educational 30 cmH₂O boundary: focus on trapped volume and expiratory time, not only PaCO₂.")
    if summary["max_vei_ml_kg"] >= 20:
        points.append("VEI proxy exceeds 20 mL/kg: this is the simulator's high dynamic-hyperinflation warning.")
    if summary["min_map_mmHg"] < 55:
        points.append("MAP falls below 55 mmHg: the model is signaling preload compromise from hyperinflation/pressure load.")
    if summary["min_ph"] < 7.20:
        points.append("pH is below 7.20: permissive hypercapnia has crossed the model's severe boundary.")
    if summary["final_etco2_mmHg"] + 20 < summary["final_paco2_mmHg"]:
        points.append("EtCO₂ is much lower than PaCO₂: the scenario illustrates dead-space/heterogeneity mismatch.")
    if not points:
        points.append("The scenario remains within the model's low-risk educational envelope.")
    return points


def show_interpretation(summary: Dict[str, Any]) -> None:
    points = generate_teaching_points(summary)
    if len(points) == 1 and points[0].startswith("The scenario remains"):
        st.success(points[0])
    else:
        st.warning("\n".join(f"• {p}" for p in points))


def compare_summaries(primary: Dict[str, Any], comparator: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    fields = [
        ("max_autopeep_cmH2O", "Max auto-PEEP", "cmH₂O", "lower_is_better"),
        ("max_pplat_cmH2O", "Max Pplat", "cmH₂O", "lower_is_better"),
        ("max_vei_ml_kg", "Max VEI proxy", "mL/kg", "lower_is_better"),
        ("final_paco2_mmHg", "Final PaCO₂", "mmHg", "context_dependent"),
        ("min_ph", "Min pH", "", "higher_is_better"),
        ("min_map_mmHg", "Min MAP", "mmHg", "higher_is_better"),
        ("max_global_risk_score", "Max global risk", "score", "lower_is_better"),
    ]
    for key, label, unit, direction in fields:
        a = float(primary[key])
        b = float(comparator[key])
        delta = b - a
        if direction == "lower_is_better":
            interpretation = "better" if delta < 0 else "worse" if delta > 0 else "unchanged"
        elif direction == "higher_is_better":
            interpretation = "better" if delta > 0 else "worse" if delta < 0 else "unchanged"
        else:
            interpretation = "context-dependent"
        rows.append({
            "metric": label,
            "primary": round(a, 3),
            "comparator": round(b, 3),
            "delta_comparator_minus_primary": round(delta, 3),
            "unit": unit,
            "interpretation": interpretation,
        })
    return pd.DataFrame(rows)


def merge_for_comparison(df_a: pd.DataFrame, df_b: pd.DataFrame, variables: List[str], labels: tuple[str, str]) -> pd.DataFrame:
    a = df_a[["time_min", *variables]].copy()
    b = df_b[["time_min", *variables]].copy()
    a = a.rename(columns={v: f"{labels[0]}: {v}" for v in variables})
    b = b.rename(columns={v: f"{labels[1]}: {v}" for v in variables})
    return pd.merge(a, b, on="time_min", how="outer").sort_values("time_min")


def main() -> None:
    st.set_page_config(
        page_title="Pediatric Asthma Ventilation Simulator", layout="wide", initial_sidebar_state="expanded"
    )
    st.title("Pediatric Status Asthmaticus Ventilation Simulator")
    st.caption("v1.8.1 educational simulator — dynamic hyperinflation, auto-PEEP and ventilator strategy trade-offs. Not clinical decision support.")

    scenarios = list_scenarios()
    if not scenarios:
        st.error("No scenario YAML files found.")
        return

    selected = st.sidebar.selectbox("Base scenario", scenarios, format_func=scenario_label)
    base = load_scenario(selected)
    scenario = apply_sidebar_controls(base)

    st.subheader(scenario.get("title", scenario.get("scenario_id", "Scenario")))
    st.write(scenario.get("educational_message", ""))

    outputs = simulate_scenario(scenario)
    summary = summarize_outputs(outputs)
    df = as_dataframe(outputs)

    show_key_metrics(summary)
    show_interpretation(summary)

    tabs = st.tabs([
        "Pressures",
        "Gas exchange",
        "Hemodynamics",
        "Mechanics",
        "Strategy comparison",
        "Teaching summary",
        "Data",
    ])
    with tabs[0]:
        st.line_chart(
            df.set_index("time_min")[["autopeep_cmH2O", "measured_autopeep_cmH2O", "occult_autopeep_cmH2O", "pplat_cmH2O", "ppeak_cmH2O"]]
        )
        st.caption("Ppeak includes resistive pressure; risk scoring relies mainly on Pplat and hyperinflation.")
    with tabs[1]:
        st.line_chart(df.set_index("time_min")[["paco2_mmHg", "etco2_mmHg", "alveolar_ventilation_l_min"]])
        st.line_chart(df.set_index("time_min")[["ph"]])
        st.caption("PaCO₂ is a simplified educational estimate, not a blood gas calculator.")
    with tabs[2]:
        st.line_chart(df.set_index("time_min")[["map_mmHg", "global_risk_score"]])
    with tabs[3]:
        st.line_chart(
            df.set_index("time_min")[["trapped_volume_ml_kg", "tau_exp_s", "expiratory_residual_fraction", "trigger_work_index"]]
        )
    with tabs[4]:
        comparator_path = st.selectbox("Comparator scenario", scenarios, index=0, format_func=scenario_label)
        comparator = load_scenario(comparator_path)
        # Match simulation length/time step to the actively edited primary scenario for fair plotting.
        comparator["duration_min"] = scenario.get("duration_min", comparator.get("duration_min", 60))
        comparator["time_step_s"] = scenario.get("time_step_s", comparator.get("time_step_s", 5))
        comp_outputs = simulate_scenario(comparator)
        comp_summary = summarize_outputs(comp_outputs)
        comp_df = as_dataframe(comp_outputs)
        labels = ("Primary", "Comparator")

        st.markdown("#### Summary delta")
        delta_df = compare_summaries(summary, comp_summary)
        st.dataframe(delta_df, use_container_width=True, hide_index=True)

        st.markdown("#### Overlay curves")
        pressure_cmp = merge_for_comparison(df, comp_df, ["autopeep_cmH2O", "pplat_cmH2O"], labels)
        st.line_chart(pressure_cmp.set_index("time_min"))
        gas_cmp = merge_for_comparison(df, comp_df, ["paco2_mmHg", "ph"], labels)
        st.line_chart(gas_cmp.set_index("time_min"))
        map_cmp = merge_for_comparison(df, comp_df, ["map_mmHg", "global_risk_score"], labels)
        st.line_chart(map_cmp.set_index("time_min"))

        csv = delta_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download comparison delta CSV",
            data=csv,
            file_name=f"{scenario.get('scenario_id', 'primary')}_vs_{comparator.get('scenario_id', 'comparator')}_v1_8_1_delta.csv",
            mime="text/csv",
        )
    with tabs[5]:
        st.markdown("#### Automatic teaching summary")
        for point in generate_teaching_points(summary):
            st.write(f"- {point}")
        st.markdown("#### Model boundary")
        st.write(
            "The intended lesson is not to calculate the correct ventilator setting. The intended lesson is to visualize why "
            "short expiratory time, high trapped volume and occult auto-PEEP can make apparent CO₂-driven escalation unsafe."
        )
        st.markdown("#### Variables reviewers may question")
        st.write(
            "VEI proxy, dead-space penalty, occult auto-PEEP fraction and drug-response multipliers are educational calibration variables, "
            "not patient-specific predictors. They should remain explicit in the Methods and Limitations sections."
        )
    with tabs[6]:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download simulated time series CSV", data=csv,
            file_name=f"{scenario.get('scenario_id', 'scenario')}_v1_8_1_timeseries.csv",
            mime="text/csv",
        )

    with st.expander("Scenario YAML currently simulated"):
        st.code(yaml.safe_dump(scenario, sort_keys=False, allow_unicode=True), language="yaml")

    st.divider()
    st.markdown(
        "**Safety boundary:** this prototype is for teaching dynamic hyperinflation, auto-PEEP and ventilator trade-offs. "
        "It must not be used to set ventilator parameters in a real patient."
    )


if __name__ == "__main__":
    main()
