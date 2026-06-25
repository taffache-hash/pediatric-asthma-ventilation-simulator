"""Single source of truth for ventilation-mode names.

The engine, the JSON Schema, the Streamlit UI, and the scenario files must all
agree on one vocabulary. Canonical names are UPPER_SNAKE_CASE. ``normalize_mode``
maps legacy/UI aliases and any letter-case to the canonical form, so a mode
selected in the UI (e.g. "PSV") validates and runs identically to the canonical
name ("PSV_CPAP").
"""

from __future__ import annotations

CANONICAL_MODES = ("VCV", "PCV", "PSV_CPAP", "MANUAL_BAGGING_THEN_VCV")

# Aliases (compared case-insensitively) -> canonical name.
_ALIASES = {
    "VCV": "VCV",
    "VOLUME_CONTROL": "VCV",
    "PCV": "PCV",
    "PRESSURE_CONTROL": "PCV",
    "PSV": "PSV_CPAP",
    "CPAP": "PSV_CPAP",
    "PSV_CPAP": "PSV_CPAP",
    "PS_CPAP": "PSV_CPAP",
    "MANUAL_BAGGING_THEN_VCV": "MANUAL_BAGGING_THEN_VCV",
    "MANUAL_BAGGING": "MANUAL_BAGGING_THEN_VCV",
}


def normalize_mode(mode) -> str:
    """Return the canonical mode name for *mode*, or the upper-cased input if unknown.

    Unknown modes are returned upper-cased (not silently coerced to VCV); the
    schema enum is responsible for rejecting them.
    """
    if mode is None:
        return ""
    key = str(mode).strip().upper()
    return _ALIASES.get(key, key)
