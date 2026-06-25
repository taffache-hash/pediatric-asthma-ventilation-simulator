"""Built-in scenario discovery and loading via importlib.resources.

These functions work whether the package is run from the source tree or
installed from a wheel, because they resolve the bundled ``scenarios/`` package
data rather than a path relative to the repository.
"""

from __future__ import annotations

import importlib.resources as resources
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required. Install with: pip install pyyaml") from exc

SCHEMA_FILENAME = "scenario_schema_v1_8_1.yaml"
_SCENARIOS_SUBPKG = f"{__package__}.scenarios" if __package__ else "scenarios"


def _scenarios_traversable():
    return resources.files(__package__).joinpath("scenarios")


def schema_path() -> Path:
    """Filesystem path to the bundled JSON Schema (works for unpacked installs)."""
    return Path(str(_scenarios_traversable().joinpath(SCHEMA_FILENAME)))


def read_schema_text() -> str:
    return _scenarios_traversable().joinpath(SCHEMA_FILENAME).read_text(encoding="utf-8")


def load_schema() -> Dict[str, Any]:
    return yaml.safe_load(read_schema_text())


def _is_scenario(name: str) -> bool:
    return (
        name.endswith(".yaml")
        and "schema" not in name
        and not name.startswith("_")
    )


def list_builtin_scenarios() -> List[str]:
    """Sorted list of built-in scenario *ids* (filename stems)."""
    names = [
        p.name
        for p in _scenarios_traversable().iterdir()
        if p.is_file() and _is_scenario(p.name)
    ]
    return sorted(n[: -len(".yaml")] for n in names)


def builtin_scenario_path(scenario_id: str) -> Path:
    return Path(str(_scenarios_traversable().joinpath(f"{scenario_id}.yaml")))


def load_builtin_scenario(scenario_id: str) -> Dict[str, Any]:
    text = _scenarios_traversable().joinpath(f"{scenario_id}.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)
