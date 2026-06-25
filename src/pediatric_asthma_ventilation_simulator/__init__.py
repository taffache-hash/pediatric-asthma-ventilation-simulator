"""Pediatric Asthma Ventilation Simulator — educational, non-clinical.

Open-source physiology teaching simulator for invasive ventilation in pediatric
status asthmaticus. Internal verification only; not clinically validated, not a
medical device, not clinical decision support. No patient data were used.
"""

from .modes import CANONICAL_MODES, normalize_mode
from .scenarios import (
    builtin_scenario_path,
    list_builtin_scenarios,
    load_builtin_scenario,
    load_schema,
    schema_path,
)
from .scenario_validation import (
    ScenarioValidationError,
    validate_scenario,
    validate_scenario_file,
)
from .asthma_engine import (
    load_scenario,
    run_scenario_file,
    simulate_scenario,
    summarize_outputs,
)

__version__ = "1.8.1"

__all__ = [
    "CANONICAL_MODES",
    "normalize_mode",
    "list_builtin_scenarios",
    "load_builtin_scenario",
    "builtin_scenario_path",
    "load_schema",
    "schema_path",
    "ScenarioValidationError",
    "validate_scenario",
    "validate_scenario_file",
    "load_scenario",
    "run_scenario_file",
    "simulate_scenario",
    "summarize_outputs",
    "__version__",
]
