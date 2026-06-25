"""Scenario input validation for the pediatric asthma ventilation simulator.

This module is the single gate that protects the engine from non-physiological
or malformed input. It validates a scenario dictionary against the shipped
JSON Schema (``scenarios/scenario_schema_v1_8_1.yaml``), which encodes both the
structural contract and the safety-critical range constraints (weight > 0,
time_step > 0, respiratory rate > 0, PEEP >= 0, plausible tidal volume, allowed
ventilation mode, ...). A small amount of semantic validation that JSON Schema
cannot express (parseability of the I:E ratio string) is added on top.

Rationale: before v1.8.1, pathological scenarios either crashed with an opaque
``ZeroDivisionError`` (weight = 0, dt = 0) or — worse — ran silently and produced
non-physiological output (negative weight/PEEP/RR). Both failure modes are now
converted into a single, explicit :class:`ScenarioValidationError` raised before
any simulation work is done.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - environment guard
    raise RuntimeError(
        "jsonschema is required for scenario validation. "
        "Install with: pip install jsonschema"
    ) from exc


from .modes import CANONICAL_MODES, normalize_mode
from .scenarios import SCHEMA_FILENAME, load_schema as _load_bundled_schema

ALLOWED_MODES = CANONICAL_MODES


class ScenarioValidationError(ValueError):
    """Raised when a scenario fails structural or range validation.

    Subclasses :class:`ValueError` so existing ``except ValueError`` handlers and
    tests keep working.
    """


def load_schema(schema_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """Load the scenario JSON Schema (stored as YAML).

    With no argument, the schema is resolved from the bundled package data via
    importlib.resources, so it works identically from the source tree and from an
    installed wheel. An explicit ``schema_path`` overrides this (used in tests).
    """
    if schema_path is not None:
        with Path(schema_path).open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return _load_bundled_schema()


def _normalize_modes_in_place(scenario: Dict[str, Any]) -> None:
    """Canonicalize the ventilation-mode string before validation.

    A mode chosen in the UI (e.g. "PSV") or written in any letter-case is mapped
    to its canonical name (e.g. "PSV_CPAP") so the same vocabulary is enforced by
    the schema, the engine, and the interface.
    """
    vent = scenario.get("ventilator")
    if isinstance(vent, dict) and "mode" in vent:
        vent["mode"] = normalize_mode(vent["mode"])


def _check_ie_ratio(scenario: Dict[str, Any]) -> List[str]:
    """Semantic check the schema cannot express: I:E ratio must be parseable.

    Accepts a patient-determined ratio (string containing 'patient') or a
    'insp:exp' form with strictly positive numbers.
    """
    vent = scenario.get("ventilator") or {}
    value = vent.get("ie_ratio")
    if value is None:
        return []  # engine has a safe default
    text = str(value).strip()
    if "patient" in text.lower():
        return []
    parts = text.replace(" ", "").split(":")
    if len(parts) != 2:
        return [f"ventilator.ie_ratio: {value!r} is not a valid 'insp:exp' ratio"]
    try:
        insp, exp = float(parts[0]), float(parts[1])
    except ValueError:
        return [f"ventilator.ie_ratio: {value!r} contains non-numeric components"]
    if insp <= 0 or exp <= 0:
        return [f"ventilator.ie_ratio: {value!r} must have strictly positive components"]
    return []


def _format_path(error) -> str:
    """Render a jsonschema error path like 'patient.weight_kg'."""
    parts = [str(p) for p in error.absolute_path]
    return ".".join(parts) if parts else "<root>"


def validate_scenario(
    scenario: Dict[str, Any],
    *,
    schema: Optional[Dict[str, Any]] = None,
    schema_path: Optional[str | Path] = None,
    source: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate a scenario dict; raise :class:`ScenarioValidationError` on failure.

    Returns the scenario unchanged on success so callers can write
    ``scenario = validate_scenario(scenario)``.

    Parameters
    ----------
    scenario : dict
        Parsed scenario.
    schema : dict, optional
        Pre-loaded schema; loaded from disk if omitted.
    schema_path : str or Path, optional
        Explicit schema location.
    source : str, optional
        Label (e.g. file name) included in error messages.
    """
    if not isinstance(scenario, dict):
        raise ScenarioValidationError(
            f"Scenario must be a mapping, got {type(scenario).__name__}"
        )

    _normalize_modes_in_place(scenario)

    if schema is None:
        schema = load_schema(schema_path)

    validator = Draft202012Validator(schema)
    messages: List[str] = []
    for err in sorted(validator.iter_errors(scenario), key=lambda e: list(e.absolute_path)):
        messages.append(f"{_format_path(err)}: {err.message}")

    messages.extend(_check_ie_ratio(scenario))

    if messages:
        label = f" [{source}]" if source else ""
        sid = scenario.get("scenario_id", "<unknown>")
        header = f"Invalid scenario '{sid}'{label}:"
        bullet_list = "\n".join(f"  - {m}" for m in messages)
        raise ScenarioValidationError(f"{header}\n{bullet_list}")

    return scenario


def validate_scenario_file(
    scenario_path: str | Path,
    *,
    schema: Optional[Dict[str, Any]] = None,
    schema_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Load and validate a scenario from disk; return the validated dict."""
    path = Path(scenario_path)
    with path.open("r", encoding="utf-8") as f:
        scenario = yaml.safe_load(f)
    return validate_scenario(
        scenario, schema=schema, schema_path=schema_path, source=path.name
    )
