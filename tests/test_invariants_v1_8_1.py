"""Physiologic-invariant and monotonicity tests (v1.8).

These tests do not assert hand-picked absolute values; they assert that the
engine responds in the physiologically correct *direction* when a single input
is changed, plus a small golden snapshot to prevent silent numeric drift between
the engine and the manuscript.
"""

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    load_scenario, simulate_scenario, summarize_outputs, load_builtin_scenario,
)

REF = "severe_obstruction_rr_reference"


def _run(name, overrides=None):
    sc = load_builtin_scenario(name)
    if overrides:
        sc = copy.deepcopy(sc)
        for section, kv in overrides.items():
            sc[section].update(kv)
    return sc, summarize_outputs(simulate_scenario(sc))


# ----------------------------------------------------------------------------
# Monotonicity / direction invariants
# ----------------------------------------------------------------------------

def test_higher_rr_increases_autopeep_under_severe_obstruction():
    _, low = _run(REF, {"ventilator": {"rr_bpm": 10}})
    _, high = _run(REF, {"ventilator": {"rr_bpm": 30}})
    assert high["max_autopeep_cmH2O"] > low["max_autopeep_cmH2O"]


def test_longer_expiratory_time_reduces_autopeep():
    _, short_te = _run(REF, {"ventilator": {"rr_bpm": 24, "ie_ratio": "1:2"}})
    _, long_te = _run(REF, {"ventilator": {"rr_bpm": 24, "ie_ratio": "1:5"}})
    assert long_te["max_autopeep_cmH2O"] < short_te["max_autopeep_cmH2O"]


def test_larger_vt_increases_pplat_and_vei():
    _, small = _run(REF, {"ventilator": {"vt_ml_kg": 5.5}})
    _, large = _run(REF, {"ventilator": {"vt_ml_kg": 8.0}})
    assert large["max_pplat_cmH2O"] > small["max_pplat_cmH2O"]
    assert large["max_vei_ml_kg"] > small["max_vei_ml_kg"]


def test_lower_compliance_increases_pplat():
    _, compliant = _run(REF, {"airway_mechanics": {"crs_ml_cmH2O_kg": 1.2}})
    _, stiff = _run(REF, {"airway_mechanics": {"crs_ml_cmH2O_kg": 0.7}})
    assert stiff["max_pplat_cmH2O"] > compliant["max_pplat_cmH2O"]


def test_higher_raw_increases_ppeak():
    _, low_raw = _run(REF, {"airway_mechanics": {"raw_insp_cmH2O_s_L": 30}})
    _, high_raw = _run(REF, {"airway_mechanics": {"raw_insp_cmH2O_s_L": 70}})
    assert high_raw["max_ppeak_cmH2O"] > low_raw["max_ppeak_cmH2O"]


def test_paco2_is_u_shaped_in_rr_sweep():
    """An interior PaCO2 nadir proves the central teaching point: raising RR helps
    only up to a point, then worsens CO2 via dynamic hyperinflation."""
    rrs = list(range(6, 41, 2))
    paco2 = []
    for rr in rrs:
        _, s = _run(REF, {"ventilator": {"rr_bpm": rr}})
        paco2.append(s["max_paco2_mmHg"])
    nadir_idx = paco2.index(min(paco2))
    assert 0 < nadir_idx < len(paco2) - 1, paco2          # interior nadir
    assert paco2[0] > paco2[nadir_idx]                    # falls before nadir
    assert paco2[-1] > paco2[nadir_idx]                   # rises after nadir


def test_timestep_invariance_reference():
    series = {}
    for dt in (0.5, 1.0, 2.0, 5.0):
        _, s = _run(REF)
        sc = load_builtin_scenario(REF)
        sc = copy.deepcopy(sc)
        sc["time_step_s"] = dt
        s = summarize_outputs(simulate_scenario(sc))
        for key in ("max_autopeep_cmH2O", "max_pplat_cmH2O", "max_paco2_mmHg"):
            series.setdefault(key, []).append(s[key])
    for key, vals in series.items():
        denom = max(max(vals), 1.0)
        assert (max(vals) - min(vals)) / denom < 0.05, (key, vals)


# ----------------------------------------------------------------------------
# Counterbalancing-PEEP gate (spontaneous patient)
# ----------------------------------------------------------------------------

def _spont_peep(peep):
    sc = load_builtin_scenario("spontaneous_autopeep_peep_titration")
    sc = copy.deepcopy(sc)
    sc["ventilator"]["peep_cmH2O"] = peep
    outs = simulate_scenario(sc)
    s = summarize_outputs(outs)
    return {
        "autopeep": s["max_autopeep_cmH2O"],
        "trigger": max(o.trigger_work_index for o in outs),
        "excess": max(o.external_peep_excess_cmH2O for o in outs),
        "map": s["min_map_mmHg"],
    }


def test_peep_unloads_trigger_work():
    no_peep = _spont_peep(0)
    matched = _spont_peep(5)
    assert matched["trigger"] < no_peep["trigger"] * 0.5


def test_no_hemodynamic_penalty_until_peep_exceeds_intrinsic():
    intrinsic = _spont_peep(0)["autopeep"]
    below = _spont_peep(max(intrinsic - 1.0, 0.0))
    above = _spont_peep(intrinsic + 5.0)
    assert below["excess"] <= 0.5          # essentially counterbalanced
    assert above["excess"] > 1.0           # excess appears above intrinsic
    assert above["map"] < below["map"]     # and only then does MAP fall


# ----------------------------------------------------------------------------
# Golden snapshot: guards against silent engine/manuscript drift
# ----------------------------------------------------------------------------

GOLDEN = {
    # scenario: (max_autopeep, max_pplat, max_paco2, min_map)
    "safe_controlled_hypoventilation": (3.73, 15.44, 75.4, 61.94),
    "high_rr_dynamic_hyperinflation": (13.26, 25.51, 91.5, 53.72),
    "silent_chest_low_etco2": (4.24, 16.15, 105.4, 55.96),
    "spontaneous_autopeep_peep_titration": (5.56, 17.26, 55.9, 63.83),
    "severe_obstruction_rr_reference": (8.30, 18.97, 77.2, 58.38),
}


@pytest.mark.parametrize("scenario,expected", GOLDEN.items())
def test_golden_summary_values(scenario, expected):
    _, s = _run(scenario)
    got = (s["max_autopeep_cmH2O"], s["max_pplat_cmH2O"],
           s["max_paco2_mmHg"], s["min_map_mmHg"])
    for g, e in zip(got, expected):
        assert abs(g - e) <= max(0.5, 0.03 * abs(e)), (scenario, got, expected)
