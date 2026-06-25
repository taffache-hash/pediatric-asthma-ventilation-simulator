"""Streamlit smoke tests (v1.8.1).

These do not drive the UI; they assert the import-time and discovery contract the
manuscript refers to as "Streamlit smoke tests":
  * the app module imports without executing the UI (all st.* calls live in main());
  * scenario discovery returns a non-empty list;
  * schema files are excluded from the scenario picker;
  * every discoverable scenario loads, validates, and produces output;
  * the app advertises a version string consistent with the package VERSION file.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

pytest.importorskip("streamlit", reason="streamlit not installed")

APP_PATH = ROOT / "app" / "streamlit_app.py"


def _load_app_module():
    """Import app/streamlit_app.py as a module without running Streamlit."""
    spec = importlib.util.spec_from_file_location("streamlit_app_under_test", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # safe: all st.* calls are inside main()
    return module


def test_app_imports():
    module = _load_app_module()
    assert hasattr(module, "main")
    assert hasattr(module, "list_scenarios")


def test_scenario_discovery_nonempty():
    module = _load_app_module()
    scenarios = module.list_scenarios()
    assert len(scenarios) >= 1


def test_schema_files_excluded_from_picker():
    module = _load_app_module()
    names = [p.name for p in module.list_scenarios()]
    assert not any("schema" in n for n in names), (
        f"schema file leaked into scenario picker: {names}"
    )


def test_every_listed_scenario_loads_validates_and_runs():
    module = _load_app_module()
    from pediatric_asthma_ventilation_simulator import simulate_scenario, load_scenario

    for path in module.list_scenarios():
        scenario = load_scenario(path)
        outputs = simulate_scenario(scenario)  # validates internally
        assert len(outputs) > 0, f"{path.name} produced no output"


def test_scenario_labels_are_unique_and_nonempty():
    module = _load_app_module()
    labels = [module.scenario_label(p) for p in module.list_scenarios()]
    assert all(labels), "empty scenario label encountered"
    assert len(labels) == len(set(labels)), "duplicate scenario labels"


def test_app_version_matches_package_version():
    module = _load_app_module()
    pkg_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    app_version = getattr(module, "VERSION", "").lstrip("v")
    assert app_version == pkg_version, (
        f"app VERSION {app_version!r} != package VERSION {pkg_version!r}"
    )
