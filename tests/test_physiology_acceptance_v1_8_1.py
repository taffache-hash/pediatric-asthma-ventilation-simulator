import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    load_scenario, simulate_scenario, summarize_outputs, load_builtin_scenario,
)
from pediatric_asthma_ventilation_simulator.asthma_engine import acute_ph  # noqa: E402


def _summary(name: str, dt: float | None = None):
    sc = load_builtin_scenario(name)
    if dt is not None:
        sc = copy.deepcopy(sc)
        sc["time_step_s"] = dt
    return summarize_outputs(simulate_scenario(sc))


def test_no_runaway_pressures_in_collapse_scenario():
    s = _summary("post_intubation_collapse")
    assert s["max_autopeep_cmH2O"] <= 30.0
    assert s["max_pplat_cmH2O"] <= 65.0
    assert s["max_ppeak_cmH2O"] <= 90.0
    assert s["unsafe_any"] is True
    assert "threshold" in s["final_safety_message"] or "capped" in s["final_safety_message"]


def test_safe_strategy_remains_physiologically_plausible():
    s = _summary("safe_controlled_hypoventilation")
    assert s["max_autopeep_cmH2O"] < 7.0
    assert s["max_pplat_cmH2O"] < 30.0
    # Permissive hypercapnia: a safe controlled-hypoventilation strategy accepts
    # an elevated PaCO2 up to a literature-tolerated ceiling. The pH floor is
    # derived from the same acute Henderson-Hasselbalch relationship the engine
    # uses, so the PaCO2 ceiling and the pH floor are mutually consistent by
    # construction rather than by coincidence (PaCO2 80 mmHg -> pH ~7.17, the
    # lower edge of accepted permissive hypercapnia in severe asthma).
    paco2_ceiling = 80.0
    assert 45.0 <= s["max_paco2_mmHg"] <= paco2_ceiling
    assert s["min_ph"] >= acute_ph(paco2_ceiling)
    assert s["unsafe_any"] is False
    # v1.8: a safe strategy in SEVERE obstruction still carries modest real intrinsic
    # PEEP and a wide resistive PIP-to-plateau gap (the core teaching distinction).
    assert s["max_autopeep_cmH2O"] >= 3.0
    assert s["max_ppeak_cmH2O"] - s["max_pplat_cmH2O"] >= 25.0


def test_high_rr_worse_than_safe_strategy_for_hyperinflation_and_co2():
    safe = _summary("safe_controlled_hypoventilation")
    high_rr = _summary("high_rr_dynamic_hyperinflation")
    assert high_rr["max_autopeep_cmH2O"] > safe["max_autopeep_cmH2O"]
    assert high_rr["max_vei_ml_kg"] > safe["max_vei_ml_kg"]
    assert high_rr["max_paco2_mmHg"] > safe["max_paco2_mmHg"]


def test_dt_invariance_for_key_scenarios():
    for name in ["high_rr_dynamic_hyperinflation", "silent_chest_low_etco2", "post_intubation_collapse"]:
        vals = [_summary(name, dt) for dt in (0.5, 1.0, 2.0, 5.0)]
        for key in ("max_autopeep_cmH2O", "max_pplat_cmH2O", "max_paco2_mmHg"):
            series = [v[key] for v in vals]
            denom = max(max(series), 1.0)
            assert (max(series) - min(series)) / denom < 0.05, (name, key, series)


def test_silent_chest_etco2_pitfall_is_reproduced_without_hidden_paco2_cap():
    s = _summary("silent_chest_low_etco2")
    assert 70.0 <= s["max_paco2_mmHg"] <= 120.0
    assert s["final_etco2_mmHg"] < 30.0
    assert s["max_paco2_mmHg"] - s["final_etco2_mmHg"] > 45.0
    assert s["max_paco2_mmHg"] < 180.0
    assert s["unsafe_any"] is False


def test_excess_external_peep_produces_hemodynamic_penalty():
    import copy
    base_scenario = load_builtin_scenario("excess_external_peep_passive")
    maps = []
    pplats = []
    for peep in (0, 5, 10, 16):
        sc = copy.deepcopy(base_scenario)
        sc["ventilator"]["peep_cmH2O"] = peep
        out = summarize_outputs(simulate_scenario(sc))
        maps.append(out["min_map_mmHg"])
        pplats.append(out["max_pplat_cmH2O"])
    assert pplats == sorted(pplats)
    assert maps[0] > maps[-1]
    assert (maps[0] - maps[-1]) >= 4.0


def test_expected_direction_smoke_checks_for_key_scenarios():
    safe = _summary("safe_controlled_hypoventilation")
    high_rr = _summary("high_rr_dynamic_hyperinflation")
    silent = _summary("silent_chest_low_etco2")
    collapse = _summary("post_intubation_collapse")

    assert safe["max_autopeep_cmH2O"] < 7.0
    assert high_rr["max_autopeep_cmH2O"] > 9.0
    assert high_rr["max_paco2_mmHg"] > safe["max_paco2_mmHg"]
    assert silent["final_etco2_mmHg"] < 30.0
    assert silent["max_paco2_mmHg"] > 70.0
    assert collapse["unsafe_any"] is True
    assert collapse["min_map_mmHg"] <= 25.0
