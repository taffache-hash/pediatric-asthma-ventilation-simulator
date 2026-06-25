"""Mode-vocabulary consistency tests (v1.8.1).

The engine, schema, UI, and scenario files must share one ventilation-mode
vocabulary. These tests assert that every mode offered by the Streamlit UI
normalizes to a schema-valid canonical name and runs.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    CANONICAL_MODES,
    load_builtin_scenario,
    normalize_mode,
    simulate_scenario,
    validate_scenario,
)

UI_MODE_OPTIONS = ["VCV", "PCV", "PSV_CPAP", "MANUAL_BAGGING_THEN_VCV"]
LEGACY_ALIASES = {"PSV": "PSV_CPAP", "psv": "PSV_CPAP",
                  "manual_bagging_then_VCV": "MANUAL_BAGGING_THEN_VCV",
                  "vcv": "VCV", "Pcv": "PCV"}


@pytest.mark.parametrize("alias,canonical", LEGACY_ALIASES.items())
def test_normalize_known_aliases(alias, canonical):
    assert normalize_mode(alias) == canonical


@pytest.mark.parametrize("mode", UI_MODE_OPTIONS)
def test_ui_mode_options_are_canonical(mode):
    assert mode in CANONICAL_MODES


def _base_for_mode(mode):
    """Pick a built-in scenario already using this mode and return its dict."""
    by_mode = {
        "VCV": "high_rr_dynamic_hyperinflation",
        "PCV": "excess_external_peep_passive",
        "PSV_CPAP": "spontaneous_autopeep_peep_titration",
        "MANUAL_BAGGING_THEN_VCV": "post_intubation_collapse",
    }
    return load_builtin_scenario(by_mode[mode])


@pytest.mark.parametrize("mode", UI_MODE_OPTIONS)
def test_every_ui_mode_validates_and_runs(mode):
    scenario = _base_for_mode(mode)
    scenario["ventilator"]["mode"] = mode
    validate_scenario(scenario)             # must not raise
    outputs = simulate_scenario(_base_for_mode(mode))
    assert len(outputs) > 0


def test_legacy_psv_alias_from_ui_validates():
    scenario = _base_for_mode("PSV_CPAP")
    scenario["ventilator"]["mode"] = "PSV"   # legacy UI label
    validated = validate_scenario(scenario)
    assert validated["ventilator"]["mode"] == "PSV_CPAP"
