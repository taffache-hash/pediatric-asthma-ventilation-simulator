"""Core physiology engine for the Pediatric Asthma Ventilation Simulator.

Version: v1.8.1
Purpose: educational simulation of dynamic hyperinflation in ventilated pediatric
status asthmaticus. This is not clinical decision support.

The model is deliberately transparent and low dimensional:
    Te/tau_exp -> incomplete emptying -> trapped volume -> auto-PEEP
    -> pressures/hemodynamics; CO2/pH are secondary outputs.

Calibration v0.5-v0.8 adds dynamic effective dead space and stronger distinction
between nominal minute ventilation and effective alveolar ventilation.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
import csv
import math

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc


@dataclass(frozen=True)
class Patient:
    age_years: float
    weight_kg: float
    frc_ml_per_kg: float
    vco2_ml_kg_min: float
    dead_space_ml_kg: float
    map_baseline_mmHg: float
    preload_status: str
    patient_effort: str


@dataclass(frozen=True)
class Mechanics:
    obstruction_severity: str
    raw_insp_cmH2O_s_L: float
    raw_exp_multiplier: float
    crs_ml_cmH2O_kg: float
    secretions_factor: float
    heterogeneity_factor: float


@dataclass(frozen=True)
class Ventilator:
    mode: str
    rr_bpm: float
    peep_cmH2O: float
    ie_ratio: str
    insp_flow_l_min: float
    inspiratory_pause_s: float = 0.0
    vt_ml_kg: float | None = None
    pressure_control_cmH2O_above_peep: float | None = None
    pressure_support_cmH2O: float | None = None
    backup_rr_bpm: float | None = None
    trigger_sensitivity: str | None = None


@dataclass
class SimState:
    time_s: float = 0.0
    trapped_volume_ml: float = 0.0
    raw_insp_cmH2O_s_L: float = 0.0
    raw_exp_cmH2O_s_L: float = 0.0


@dataclass
class BreathOutput:
    time_min: float
    rr_bpm: float
    ti_s: float
    te_s: float
    vt_ml: float
    vt_ml_kg: float
    raw_insp_cmH2O_s_L: float
    raw_exp_cmH2O_s_L: float
    crs_ml_cmH2O: float
    tau_exp_s: float
    expiratory_residual_fraction: float
    trapped_volume_ml: float
    trapped_volume_ml_kg: float
    autopeep_cmH2O: float
    measured_autopeep_cmH2O: float
    occult_autopeep_cmH2O: float
    total_peep_cmH2O: float
    pplat_cmH2O: float
    ppeak_cmH2O: float
    alveolar_ventilation_l_min: float
    paco2_mmHg: float
    etco2_mmHg: float
    ph: float
    map_mmHg: float
    trigger_work_index: float
    external_peep_excess_cmH2O: float
    barotrauma_risk: str
    hemodynamic_risk: str
    ventilation_risk: str
    global_risk_score: float
    unsafe_physiology: bool = False
    simulation_terminated: bool = False
    safety_message: str = ""


def load_scenario(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_ie_ratio(value: str, rr_bpm: float, effort: str = "passive") -> Tuple[float, float]:
    """Return Ti and Te in seconds from an I:E string.

    For spontaneous/patient-determined breathing, use conservative defaults.
    """
    cycle_s = 60.0 / max(rr_bpm, 1e-6)
    if not value or "patient" in str(value).lower():
        # Spontaneous obstructed child: relatively long expiration but variable.
        ti_s = min(1.0, cycle_s * 0.32)
        te_s = max(0.4, cycle_s - ti_s)
        return ti_s, te_s
    txt = str(value).replace(" ", "")
    try:
        left, right = txt.split(":")
        insp = float(left)
        exp = float(right)
    except Exception as exc:
        raise ValueError(f"Invalid I:E ratio: {value!r}") from exc
    ti_s = cycle_s * insp / (insp + exp)
    te_s = cycle_s - ti_s
    return ti_s, te_s


def _obstruction_factor(label: str) -> float:
    txt = (label or "").lower()
    if "critical" in txt:
        return 1.35
    if "severe" in txt:
        return 1.0
    if "moderate" in txt:
        return 0.72
    if "mild" in txt:
        return 0.45
    return 0.85


def _obstruction_index(label: str) -> float:
    """Normalized obstruction intensity used for losses and warnings.

    This is deliberately not a clinical score; it is an internal calibration
    scalar to keep equations readable.
    """
    factor = _obstruction_factor(label)
    return min(max((factor - 0.45) / (1.35 - 0.45), 0.0), 1.0)


def _preload_multiplier(preload_status: str) -> float:
    txt = (preload_status or "normal").lower()
    if "low" in txt:
        return 1.55
    if "borderline" in txt:
        return 1.25
    return 1.0


def build_objects(scenario: Dict[str, Any]) -> Tuple[Patient, Mechanics, Ventilator, Dict[str, Any]]:
    p = Patient(**scenario["patient"])
    m = Mechanics(**scenario["airway_mechanics"])
    vraw = dict(scenario["ventilator"])
    # Normalize optional fields so dataclass construction is robust.
    allowed = Ventilator.__dataclass_fields__.keys()
    vdata = {k: v for k, v in vraw.items() if k in allowed}
    if "rr_bpm" not in vdata and "backup_rr_bpm" in vdata:
        vdata["rr_bpm"] = float(vdata["backup_rr_bpm"])
    v = Ventilator(**vdata)
    therapies = scenario.get("therapies", {}) or {}
    return p, m, v, therapies


def therapy_resistance_multiplier(therapies: Dict[str, Any], t_min: float) -> float:
    """Conservative smooth effect of bronchodilator therapies on airway resistance.

    Multipliers are intentionally small; the model should not imply reliable or
    immediate clinical response.
    """
    mult = 1.0
    if therapies.get("continuous_albuterol", False):
        # Slow partial reduction toward 12% by 60 min.
        mult *= 1.0 - 0.12 * (1.0 - math.exp(-t_min / 28.0))
    if therapies.get("ipratropium", False):
        mult *= 0.97
    mag = therapies.get("magnesium", {}) or {}
    if mag.get("enabled", False):
        # Delayed modest effect; onset around 20-40 min.
        mult *= 1.0 - 0.08 / (1.0 + math.exp(-(t_min - 30.0) / 8.0))
    ket = therapies.get("ketamine", {}) or {}
    if ket.get("enabled", False):
        # Conservative gradual bronchodilatory signal; no immediate normalization.
        infusion = float(ket.get("infusion_mg_kg_h", 1.0) or 1.0)
        dose_scale = min(max(infusion / 1.0, 0.5), 2.0)
        mult *= 1.0 - (0.16 * dose_scale) * (1.0 - math.exp(-t_min / 18.0))
    steroid = therapies.get("steroid", {}) or {}
    if steroid.get("enabled", False):
        minutes_since = float(steroid.get("minutes_since_first_dose", 0.0) or 0.0) + t_min
        # Very small early effect; not an acute bronchodilator.
        if minutes_since > 180:
            mult *= 0.95
        elif minutes_since > 60:
            mult *= 0.98
    return max(mult, 0.55)


def compute_effective_resistance(m: Mechanics, therapies: Dict[str, Any], t_min: float) -> Tuple[float, float]:
    obstruction = _obstruction_factor(m.obstruction_severity)
    therapy_mult = therapy_resistance_multiplier(therapies, t_min)
    raw_insp = m.raw_insp_cmH2O_s_L * m.secretions_factor * obstruction * therapy_mult
    raw_exp = raw_insp * m.raw_exp_multiplier * m.heterogeneity_factor
    return raw_insp, raw_exp


def compute_vt_ml(p: Patient, m: Mechanics, v: Ventilator, raw_insp: float, trapped_ml: float, ti_s: float) -> float:
    mode = (v.mode or "").upper()
    crs_ml_cmH2O = p.weight_kg * m.crs_ml_cmH2O_kg
    tau_insp = max((raw_insp * crs_ml_cmH2O / 1000.0), 0.05)
    filling_fraction = 1.0 - math.exp(-max(ti_s, 0.05) / tau_insp)

    if mode in {"VCV", "MANUAL_BAGGING_THEN_VCV"} or "VCV" in mode:
        vt_ml = float(v.vt_ml_kg or 7.0) * p.weight_kg
    elif mode in {"PCV"} or "PCV" in mode:
        pc = float(v.pressure_control_cmH2O_above_peep or 18.0)
        # PCV delivered volume limited by compliance, obstruction, inspiratory time,
        # and some pressure spent overcoming intrinsic PEEP.
        autopeep_now = trapped_ml / max(crs_ml_cmH2O, 1e-6)
        # v0.5: in severe obstruction, not all set inspiratory pressure reaches
        # communicating alveoli before cycling. This avoids unrealistically good
        # PaCO2 in pressure-controlled scenarios with high Raw/short Ti.
        inspiratory_load = 0.030 * raw_insp
        effective_pc = max(pc - 0.30 * autopeep_now - inspiratory_load, 2.0)
        vt_ml = effective_pc * crs_ml_cmH2O * filling_fraction
    elif "PSV" in mode or "CPAP" in mode:
        ps = float(v.pressure_support_cmH2O or 10.0)
        autopeep_now = trapped_ml / max(crs_ml_cmH2O, 1e-6)
        inspiratory_load = 0.020 * raw_insp
        effective_ps = max(ps - 0.18 * max(autopeep_now - v.peep_cmH2O, 0.0) - inspiratory_load, 2.0)
        vt_ml = effective_ps * crs_ml_cmH2O * filling_fraction
        # Spontaneous effort adds variable volume; keep it bounded.
        vt_ml *= 1.25
    else:
        vt_ml = float(v.vt_ml_kg or 7.0) * p.weight_kg

    # Guardrails: avoid impossible negative or huge volumes in educational engine.
    return max(1.5 * p.weight_kg, min(vt_ml, 14.0 * p.weight_kg))


def risk_label(value: float, warn: float, crit: float) -> str:
    if value >= crit:
        return "critical"
    if value >= warn:
        return "warning"
    return "low"


def acute_ph(paco2_mmHg: float) -> float:
    """Acute blood-gas pH from PaCO2 via Henderson-Hasselbalch.

    Acute respiratory acidosis: bicarbonate rises ~1 mEq/L per 10 mmHg PaCO2
    above 40; acute respiratory alkalosis: it falls ~2 mEq/L per 10 mmHg below
    40. This is an educational acute approximation (no full renal metabolic
    compensation) and is more faithful to acid-base physiology than a linear
    pH-PaCO2 slope at high PaCO2, where the linear rule over-estimates acidosis.
    Returns pH clamped to a plausible display range.
    """
    paco2 = max(paco2_mmHg, 1e-6)
    if paco2 >= 40.0:
        hco3 = 24.0 + 0.10 * (paco2 - 40.0)
    else:
        hco3 = 24.0 - 0.20 * (40.0 - paco2)
    hco3 = min(max(hco3, 12.0), 45.0)
    ph = 6.1 + math.log10(hco3 / (0.03 * paco2))
    return min(max(ph, 6.80), 7.55)


def simulate_scenario(scenario: Dict[str, Any], *, validate: bool = True) -> List[BreathOutput]:
    if validate:
        # Lazy import keeps the engine importable even in minimal environments;
        # enforcement happens at run time, before any division by weight/dt.
        from .scenario_validation import validate_scenario as _validate_scenario
        scenario = _validate_scenario(scenario)
    p, m, v, therapies = build_objects(scenario)
    monitoring = scenario.get("monitoring", {}) or {}
    duration_min = float(scenario.get("duration_min", 30))
    dt_s = float(scenario.get("time_step_s", 5))
    rr = float(v.rr_bpm or v.backup_rr_bpm or 12.0)
    breath_interval_s = 60.0 / max(rr, 1.0)
    steps = int(round(duration_min * 60.0 / dt_s)) + 1

    crs_ml_cmH2O_base = p.weight_kg * m.crs_ml_cmH2O_kg
    frc_ml = p.weight_kg * p.frc_ml_per_kg
    vco2_ml_min = p.weight_kg * p.vco2_ml_kg_min
    vd_ml = p.weight_kg * p.dead_space_ml_kg

    state = SimState()
    outputs: List[BreathOutput] = []

    # Trapping is updated with a closed-form equivalent-breath recurrence.
    # This avoids dt-dependent accumulation artifacts.

    for step in range(steps):
        t_s = step * dt_s
        t_min = t_s / 60.0
        raw_insp, raw_exp = compute_effective_resistance(m, therapies, t_min)
        ti_s, te_s = parse_ie_ratio(v.ie_ratio, rr, p.patient_effort)
        tau_exp = max(raw_exp * (crs_ml_cmH2O_base / 1000.0), 0.05)
        residual_fraction = min(max(math.exp(-te_s / tau_exp), 0.0), 0.98)
        vt_ml = compute_vt_ml(p, m, v, raw_insp, state.trapped_volume_ml, ti_s)

        # Update trapped volume with a per-breath recurrence solved in closed form:
        #   V_next = V * exp(-Te/tau) + VT * retained_fraction
        # over n = dt / breath_interval equivalent breaths. This preserves the
        # qualitative Te/tau physiology while preventing timestep-dependent runaway.
        equivalent_breaths = max(dt_s / breath_interval_s, 0.0)
        # Single-compartment dynamic-hyperinflation steady state: with a
        # per-breath expiratory retained fraction r = residual_fraction, the
        # end-expiratory trapped volume converges to VT * r / (1 - r). A bounded
        # heterogeneity multiplier represents additional gas held in
        # slow-emptying units. This replaces the earlier ad-hoc damping factor,
        # which under-counted trapping by ~35% relative to the textbook form.
        het_factor = 1.0 + 0.20 * (min(max(m.heterogeneity_factor, 1.0), 2.0) - 1.0)
        retention_gain = residual_fraction * het_factor
        retention_gain = min(max(retention_gain, 0.0), 0.98)
        per_breath_decay = residual_fraction
        if per_breath_decay < 0.999:
            steady_trapped = vt_ml * retention_gain / max(1.0 - per_breath_decay, 1e-6)
            decay_over_dt = per_breath_decay ** equivalent_breaths
            state.trapped_volume_ml = steady_trapped + (state.trapped_volume_ml - steady_trapped) * decay_over_dt
        else:
            # Pathological near-complete expiratory obstruction: linearized fallback.
            state.trapped_volume_ml += vt_ml * retention_gain * equivalent_breaths

        state.trapped_volume_ml = max(0.0, state.trapped_volume_ml)
        unsafe_physiology = False
        simulation_terminated = False
        safety_messages: list[str] = []
        raw_trapped_limit_ml = 40.0 * p.weight_kg
        if state.trapped_volume_ml > raw_trapped_limit_ml:
            unsafe_physiology = True
            safety_messages.append("dynamic hyperinflation threshold exceeded")
            state.trapped_volume_ml = raw_trapped_limit_ml

        # Overdistension compliance penalty. This is educational and non-predictive.
        hyperinflation_fraction = (state.trapped_volume_ml + vt_ml) / max(frc_ml, 1.0)
        compliance_penalty = min(0.65, max(0.0, (hyperinflation_fraction - 0.30) * 0.70))
        crs_ml_cmH2O_eff = max(crs_ml_cmH2O_base * (1.0 - compliance_penalty), crs_ml_cmH2O_base * 0.35)

        # v0.5: time-constant heterogeneity can make pressure consequences
        # larger than a simple volume/compliance ratio, while measured auto-PEEP
        # may still underestimate trapped gas in poorly communicating units.
        pressure_amplification = 1.0 + 0.10 * _obstruction_index(m.obstruction_severity) + 0.08 * max(m.heterogeneity_factor - 1.0, 0.0)
        raw_autopeep = (state.trapped_volume_ml / max(crs_ml_cmH2O_eff, 1e-6)) * pressure_amplification
        autopeep = min(raw_autopeep, 30.0)
        if raw_autopeep > 30.0:
            unsafe_physiology = True
            safety_messages.append("auto-PEEP display capped at 30 cmH2O")
        occult_fraction = min(0.55, max(0.0, (m.heterogeneity_factor - 1.0) * 0.33 + (_obstruction_factor(m.obstruction_severity) - 1.0) * 0.18))
        measured_autopeep = autopeep * (1.0 - occult_fraction)
        occult_autopeep = max(autopeep - measured_autopeep, 0.0)
        total_peep = v.peep_cmH2O + autopeep

        pplat = v.peep_cmH2O + autopeep + vt_ml / max(crs_ml_cmH2O_eff, 1e-6)
        flow_l_s = max(float(v.insp_flow_l_min or 50.0) / 60.0, 0.1)
        resistive_pressure = raw_insp * flow_l_s
        mode_upper = (v.mode or "").upper()
        if "PCV" in mode_upper:
            ppeak = max(v.peep_cmH2O + float(v.pressure_control_cmH2O_above_peep or 18.0), pplat)
        elif "PSV" in mode_upper or "CPAP" in mode_upper:
            ppeak = max(v.peep_cmH2O + float(v.pressure_support_cmH2O or 10.0), pplat)
        else:
            ppeak = pplat + resistive_pressure

        if pplat > 65.0:
            unsafe_physiology = True
            safety_messages.append("plateau pressure unsafe threshold exceeded")
            pplat = 65.0
        if ppeak > 90.0:
            unsafe_physiology = True
            safety_messages.append("peak pressure unsafe threshold exceeded")
            ppeak = 90.0

        # Effective alveolar ventilation: not just minute ventilation. Air trapping,
        # severe obstruction, heterogeneity and short Te/tau waste ventilation.
        # v0.5 explicitly separates nominal ventilation from effective ventilation.
        te_tau = te_s / max(tau_exp, 1e-6)
        trapped_ml_kg = state.trapped_volume_ml / max(p.weight_kg, 1e-6)
        dynamic_dead_space_ml = vd_ml * (
            1.0
            + 0.14 * _obstruction_index(m.obstruction_severity)
            + 0.010 * max(autopeep, 0.0)
            + 0.010 * max(trapped_ml_kg, 0.0)
            + 0.06 * max(m.heterogeneity_factor - 1.0, 0.0)
        )
        # Dead-space cannot exceed most of VT, otherwise the model becomes a
        # binary switch rather than a graded educational simulator.
        dynamic_dead_space_ml = min(dynamic_dead_space_ml, 0.82 * vt_ml)
        vt_alv_ml = max(vt_ml - dynamic_dead_space_ml, 3.0 * p.weight_kg * 0.15)
        base_va_l_min = vt_alv_ml * rr / 1000.0
        # Flow-limitation ventilation loss. The auto-PEEP and trapped-volume
        # coefficients are recalibrated (from 0.032/0.018) to remain physiologic
        # now that the trapped-volume model uses the full VT*r/(1-r) steady
        # state; the dominant driver is short expiratory time (te_tau). These
        # are educational calibration coefficients, not measured constants.
        flow_limitation_loss = (
            0.014 * max(autopeep, 0.0)
            + 0.008 * max(trapped_ml_kg, 0.0)
            + max(0.0, 1.45 - te_tau) * 0.26
            + occult_fraction * 0.22
        )
        trap_loss = min(0.90, max(0.0, flow_limitation_loss))
        alveolar_ventilation = max(base_va_l_min * (1.0 - trap_loss), 0.10)
        # Standard alveolar ventilation relationship using 0.863 when VCO2 is
        # expressed in ml/min and alveolar ventilation in L/min. This remains an
        # educational surrogate, not a patient-specific blood gas predictor.
        paco2 = 0.863 * vco2_ml_min / alveolar_ventilation
        paco2 = min(max(paco2, 28.0), 180.0)
        # Acid-base via the acute Henderson-Hasselbalch relationship (see
        # acute_ph). More faithful at high PaCO2 than a linear pH-PaCO2 slope.
        ph = acute_ph(paco2)
        if paco2 >= 150.0 or ph <= 6.90:
            unsafe_physiology = True
            safety_messages.append("critical gas-exchange threshold exceeded")

        # End-tidal CO2 from the alveolar (Enghoff) dead-space fraction:
        #   EtCO2 = PaCO2 * (1 - Vd_alv / Vt_alv)
        # The PaCO2-EtCO2 gradient is, by definition, the alveolar dead space
        # (West, Nunn). A mechanistic component scales with poorly communicating
        # (occult) units, obstruction severity, heterogeneity, and auto-PEEP
        # (overdistension converts perfused units into ventilated non-perfused
        # alveolar dead space). Scenarios with a clinically defined severe V/Q
        # derangement (e.g. a near-silent chest) add an explicit alveolar
        # dead-space fraction via monitoring.vq_mismatch_dead_space_fraction;
        # this replaces the earlier opaque etco2_signal_fraction knob with a
        # physically interpretable quantity.
        f_alv_mech = (
            0.60 * occult_fraction
            + 0.10 * _obstruction_index(m.obstruction_severity)
            + 0.08 * max(m.heterogeneity_factor - 1.0, 0.0)
            + 0.004 * max(autopeep, 0.0)
        )
        f_alv_scenario = float(monitoring.get("vq_mismatch_dead_space_fraction", 0.0) or 0.0)
        f_alv_total = min(max(f_alv_mech + f_alv_scenario, 0.0), 0.92)
        etco2 = paco2 * (1.0 - f_alv_total)
        etco2 = min(max(etco2, 5.0), paco2)

        preload_mult = _preload_multiplier(p.preload_status)
        # Counterbalancing-PEEP / flow-limitation gate (v1.8).
        # In flow-limited expiration the alveoli are isolated from the airway
        # opening by the expiratory choke point, so applied (external) PEEP up to
        # the level of intrinsic auto-PEEP largely counterbalances the inspiratory
        # threshold load WITHOUT adding to mean intrathoracic pressure or impairing
        # venous return. Only the fraction of applied PEEP *above* intrinsic PEEP
        # raises total alveolar pressure and penalizes venous return. This single,
        # physiologically interpretable rule replaces the earlier crude
        # "PEEP - 5 cmH2O" penalty and applies identically to passive and
        # spontaneous patients. It remains a simplified educational illustration of
        # the counterbalancing-PEEP concept, not a quantitative hemodynamic model.
        counterbalanced_peep = min(v.peep_cmH2O, autopeep)
        excess_peep_cmH2O = max(v.peep_cmH2O - autopeep, 0.0)
        external_peep_penalty = 0.55 * excess_peep_cmH2O
        pressure_drop = preload_mult * (
            0.75 * autopeep
            + 0.45 * max(pplat - 30.0, 0.0)
            + external_peep_penalty
        )
        acidosis_drop = max(0.0, (7.20 - ph) * 18.0)
        pcv_ketamine_support = 2.0 if ((therapies.get("ketamine", {}) or {}).get("enabled", False)) else 0.0
        map_mmHg = p.map_baseline_mmHg - pressure_drop - acidosis_drop + pcv_ketamine_support
        map_mmHg = max(18.0, min(map_mmHg, 95.0))

        if "spontaneous" in p.patient_effort.lower():
            peep_unloading = max(0.0, min(v.peep_cmH2O / max(autopeep * 0.8, 1.0), 1.1))
            trigger_work = max(0.0, autopeep - v.peep_cmH2O) * (1.0 - 0.35 * peep_unloading)
        else:
            trigger_work = 0.0

        vei_ml_kg = (state.trapped_volume_ml + vt_ml) / p.weight_kg
        # Resistive peak pressure may be high in asthma even when alveolar stress is
        # less alarming; barotrauma/risk scoring is therefore driven mainly by
        # plateau pressure and hyperinflation, with peak pressure as a late warning.
        ppeak_risk = 1.0 if ppeak > 60 else 0.0
        pplat_risk = 1.0 if pplat > 30 else 0.0
        hyperinflation_risk = min(2.0, max(0.0, (vei_ml_kg - 10.0) / 10.0))
        hemo_risk_score = max(0.0, (55.0 - map_mmHg) / 15.0)
        ventilation_risk_score = max(0.0, (paco2 - 75.0) / 35.0) + max(0.0, (7.20 - ph) * 6.0)
        global_risk = ppeak_risk + pplat_risk + hyperinflation_risk + hemo_risk_score + ventilation_risk_score

        outputs.append(BreathOutput(
            time_min=round(t_min, 4), rr_bpm=rr, ti_s=ti_s, te_s=te_s,
            vt_ml=vt_ml, vt_ml_kg=vt_ml / p.weight_kg,
            raw_insp_cmH2O_s_L=raw_insp, raw_exp_cmH2O_s_L=raw_exp,
            crs_ml_cmH2O=crs_ml_cmH2O_eff, tau_exp_s=tau_exp,
            expiratory_residual_fraction=residual_fraction,
            trapped_volume_ml=state.trapped_volume_ml,
            trapped_volume_ml_kg=state.trapped_volume_ml / p.weight_kg,
            autopeep_cmH2O=autopeep, measured_autopeep_cmH2O=measured_autopeep,
            occult_autopeep_cmH2O=occult_autopeep,
            total_peep_cmH2O=total_peep,
            pplat_cmH2O=pplat, ppeak_cmH2O=ppeak,
            alveolar_ventilation_l_min=alveolar_ventilation,
            paco2_mmHg=paco2, etco2_mmHg=etco2, ph=ph, map_mmHg=map_mmHg,
            trigger_work_index=trigger_work,
            external_peep_excess_cmH2O=excess_peep_cmH2O,
            barotrauma_risk=risk_label(max(pplat, 2.6 * vei_ml_kg), 30.0, 50.0),
            hemodynamic_risk=risk_label(65.0 - map_mmHg, 10.0, 22.0),
            ventilation_risk=risk_label(paco2, 75.0, 110.0),
            global_risk_score=global_risk,
            unsafe_physiology=unsafe_physiology,
            simulation_terminated=simulation_terminated,
            safety_message="; ".join(dict.fromkeys(safety_messages)),
        ))

    return outputs


def summarize_outputs(outputs: List[BreathOutput]) -> Dict[str, Any]:
    first = outputs[0]
    last = outputs[-1]
    max_autopeep = max(o.autopeep_cmH2O for o in outputs)
    max_pplat = max(o.pplat_cmH2O for o in outputs)
    max_ppeak = max(o.ppeak_cmH2O for o in outputs)
    min_map = min(o.map_mmHg for o in outputs)
    max_paco2 = max(o.paco2_mmHg for o in outputs)
    min_ph = min(o.ph for o in outputs)
    max_vei = max(o.trapped_volume_ml_kg + o.vt_ml_kg for o in outputs)
    max_global = max(o.global_risk_score for o in outputs)
    unsafe_points = sum(1 for o in outputs if o.unsafe_physiology)
    unsafe_any = any(o.unsafe_physiology for o in outputs)
    return {
        "n_points": len(outputs),
        "duration_min": last.time_min,
        "initial_autopeep_cmH2O": round(first.autopeep_cmH2O, 2),
        "final_autopeep_cmH2O": round(last.autopeep_cmH2O, 2),
        "max_autopeep_cmH2O": round(max_autopeep, 2),
        "final_pplat_cmH2O": round(last.pplat_cmH2O, 2),
        "max_pplat_cmH2O": round(max_pplat, 2),
        "max_ppeak_cmH2O": round(max_ppeak, 2),
        "min_map_mmHg": round(min_map, 2),
        "final_paco2_mmHg": round(last.paco2_mmHg, 1),
        "max_paco2_mmHg": round(max_paco2, 1),
        "min_ph": round(min_ph, 3),
        "max_vei_ml_kg": round(max_vei, 2),
        "final_etco2_mmHg": round(last.etco2_mmHg, 1),
        "max_global_risk_score": round(max_global, 2),
        "final_barotrauma_risk": last.barotrauma_risk,
        "final_hemodynamic_risk": last.hemodynamic_risk,
        "final_ventilation_risk": last.ventilation_risk,
        "unsafe_points": unsafe_points,
        "unsafe_any": unsafe_any,
        "final_safety_message": last.safety_message,
    }


def write_timeseries_csv(outputs: List[BreathOutput], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(o) for o in outputs]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_scenario_file(scenario_path: str | Path, output_csv: str | Path | None = None) -> Dict[str, Any]:
    scenario = load_scenario(scenario_path)
    outputs = simulate_scenario(scenario)
    summary = summarize_outputs(outputs)
    summary["scenario_id"] = scenario.get("scenario_id", Path(scenario_path).stem)
    if output_csv is not None:
        write_timeseries_csv(outputs, output_csv)
    return summary
