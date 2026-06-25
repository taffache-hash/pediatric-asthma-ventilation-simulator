"""Input-validation tests (v1.8.1).

Before v1.8.1, pathological scenarios either crashed with an opaque
ZeroDivisionError (weight = 0, dt = 0) or ran silently and produced
non-physiological output (negative weight / PEEP / RR, unknown mode). These
tests assert that each such input is now rejected up front with a clear
ScenarioValidationError, and that a well-formed scenario still passes and runs.
"""

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import load_scenario, simulate_scenario, load_builtin_scenario  # noqa: E402
from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    ScenarioValidationError,
    validate_scenario,
)

BASE = "high_rr_dynamic_hyperinflation"


def _base_scenario():
    return load_builtin_scenario(BASE)


def _patch(scenario, path, value):
    """Set a nested key, e.g. _patch(s, ['patient', 'weight_kg'], 0)."""
    node = scenario
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value
    return scenario


# --- the baseline must be valid -------------------------------------------------

def test_baseline_scenario_is_valid():
    validate_scenario(_base_scenario())  # must not raise


def test_baseline_scenario_runs():
    outputs = simulate_scenario(_base_scenario())
    assert len(outputs) > 0


# --- pathological inputs must be rejected --------------------------------------

PATHOLOGICAL_CASES = [
    ("zero_weight", ["patient", "weight_kg"], 0),
    ("negative_weight", ["patient", "weight_kg"], -10),
    ("zero_time_step", ["time_step_s"], 0),
    ("negative_time_step", ["time_step_s"], -5),
    ("zero_duration", ["duration_min"], 0),
    ("negative_duration", ["duration_min"], -30),
    ("negative_peep", ["ventilator", "peep_cmH2O"], -5),
    ("zero_rr", ["ventilator", "rr_bpm"], 0),
    ("negative_rr", ["ventilator", "rr_bpm"], -12),
    ("nonpositive_raw", ["airway_mechanics", "raw_insp_cmH2O_s_L"], 0),
    ("nonpositive_crs", ["airway_mechanics", "crs_ml_cmH2O_kg"], 0),
    ("implausible_vt", ["ventilator", "vt_ml_kg"], 80),
    ("unknown_mode", ["ventilator", "mode"], "JET_OSCILLATOR"),
]


@pytest.mark.parametrize("name,path,value", PATHOLOGICAL_CASES,
                         ids=[c[0] for c in PATHOLOGICAL_CASES])
def test_pathological_input_is_rejected(name, path, value):
    scenario = _patch(_base_scenario(), path, value)
    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


@pytest.mark.parametrize("name,path,value", PATHOLOGICAL_CASES,
                         ids=[c[0] for c in PATHOLOGICAL_CASES])
def test_pathological_input_blocks_simulation(name, path, value):
    """The engine must refuse to simulate invalid input (no silent garbage)."""
    scenario = _patch(_base_scenario(), path, value)
    with pytest.raises(ScenarioValidationError):
        simulate_scenario(scenario)


# --- malformed I:E ratio (semantic check the schema cannot express) ------------

@pytest.mark.parametrize("bad_ie", ["abc", "1:0", "0:2", "-1:2", "1:2:3", ""])
def test_invalid_ie_ratio_is_rejected(bad_ie):
    scenario = _patch(_base_scenario(), ["ventilator", "ie_ratio"], bad_ie)
    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


def test_patient_determined_ie_ratio_is_accepted():
    scenario = _patch(_base_scenario(), ["ventilator", "ie_ratio"], "patient-determined")
    validate_scenario(scenario)  # must not raise


# --- missing required structure -------------------------------------------------

def test_missing_patient_block_is_rejected():
    scenario = _base_scenario()
    scenario.pop("patient")
    with pytest.raises(ScenarioValidationError):
        validate_scenario(scenario)


def test_non_mapping_scenario_is_rejected():
    with pytest.raises(ScenarioValidationError):
        validate_scenario(["not", "a", "dict"])  # type: ignore[arg-type]


# --- the validate=False escape hatch still allows opt-out (used nowhere in prod)

def test_validation_can_be_disabled_explicitly():
    scenario = _base_scenario()
    # Should run without invoking the validator at all.
    outputs = simulate_scenario(scenario, validate=False)
    assert len(outputs) > 0
