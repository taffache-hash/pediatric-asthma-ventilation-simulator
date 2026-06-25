"""Release schema tests (v1.8.1).

Asserts that the bundled JSON Schema is valid and that every built-in scenario
conforms to it. Scenarios and schema are resolved through the package
(importlib.resources), so this exercises the same path an installed wheel uses.
"""

import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    ScenarioValidationError,
    list_builtin_scenarios,
    load_builtin_scenario,
    load_schema,
    schema_path,
    validate_scenario,
)


def test_schema_is_present_and_valid_json_schema():
    assert schema_path().name == "scenario_schema_v1_8_1.yaml"
    Draft202012Validator.check_schema(load_schema())


def test_at_least_one_builtin_scenario():
    assert len(list_builtin_scenarios()) >= 1


@pytest.mark.parametrize("scenario_id", list_builtin_scenarios())
def test_scenario_conforms_to_schema(scenario_id):
    validate_scenario(load_builtin_scenario(scenario_id))


def test_every_scenario_declares_schema_version():
    for sid in list_builtin_scenarios():
        assert "schema_version" in load_builtin_scenario(sid), f"{sid} has no schema_version"


def test_invalid_scenario_raises_validation_error():
    bad = {
        "scenario_id": "broken",
        "patient": {"weight_kg": -1},
        "airway_mechanics": {"raw_insp_cmH2O_s_L": 30, "crs_ml_cmH2O_kg": 1.0},
        "ventilator": {"mode": "VCV"},
    }
    with pytest.raises(ScenarioValidationError):
        validate_scenario(bad)
