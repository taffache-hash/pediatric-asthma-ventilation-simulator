"""Schema-completeness tests (v1.8.1).

The schema claims to describe the structure the engine consumes. These tests
enforce that claim: a scenario that passes the schema must also build and run
without a TypeError, and an under-specified scenario (schema-valid shape but
missing engine-required fields) must be rejected by the schema, not crash later.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    ScenarioValidationError,
    list_builtin_scenarios,
    load_builtin_scenario,
    simulate_scenario,
    validate_scenario,
)


@pytest.mark.parametrize("scenario_id", list_builtin_scenarios())
def test_schema_valid_scenario_also_runs(scenario_id):
    # Validation passing must imply the engine can construct and run it.
    validate_scenario(load_builtin_scenario(scenario_id))
    assert len(simulate_scenario(load_builtin_scenario(scenario_id))) > 0


def test_minimal_underspecified_scenario_is_rejected():
    """The B3 regression: minimal patient block passed schema but crashed engine."""
    minimal = {
        "scenario_id": "minimal",
        "patient": {"weight_kg": 25},
        "airway_mechanics": {"raw_insp_cmH2O_s_L": 35, "crs_ml_cmH2O_kg": 1},
        "ventilator": {"mode": "VCV"},
    }
    with pytest.raises(ScenarioValidationError):
        validate_scenario(minimal)


def _full_base():
    return load_builtin_scenario("high_rr_dynamic_hyperinflation")


def test_missing_patient_field_rejected():
    s = _full_base()
    s["patient"].pop("frc_ml_per_kg")
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)


def test_missing_airway_field_rejected():
    s = _full_base()
    s["airway_mechanics"].pop("heterogeneity_factor")
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)


def test_vcv_without_vt_rejected():
    s = _full_base()
    s["ventilator"].pop("vt_ml_kg", None)
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)


def test_pcv_without_pressure_control_rejected():
    s = load_builtin_scenario("excess_external_peep_passive")
    s["ventilator"].pop("pressure_control_cmH2O_above_peep", None)
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)


@pytest.mark.parametrize("bad", [-10, 0])
def test_nonpositive_pressure_control_rejected(bad):
    s = load_builtin_scenario("excess_external_peep_passive")
    s["ventilator"]["pressure_control_cmH2O_above_peep"] = bad
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)


def test_excessive_vt_rejected():
    s = _full_base()
    s["ventilator"]["vt_ml_kg"] = 20  # above engine ceiling -> must be rejected, not silently clipped
    with pytest.raises(ScenarioValidationError):
        validate_scenario(s)
