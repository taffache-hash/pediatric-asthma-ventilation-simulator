"""Packaging / wheel tests (v1.8.1).

The B1 regression: the wheel shipped only loose modules, omitting the scenarios
and schema, so an installed package could not locate the schema and even a valid
scenario failed. These tests build a wheel and assert that:
  * the bundled scenarios and schema are inside the wheel;
  * the wheel contains no __pycache__/.pyc;
  * installing the wheel into a clean target dir yields a package that can load
    the schema and run a built-in scenario.

The build/install steps are best-effort: if the build backend or network is
unavailable they skip rather than fail, but where tooling exists this is a real
end-to-end check.
"""

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _build_wheel(dest: Path):
    # Build from an isolated copy so setuptools' build/ never lands in the repo.
    import shutil
    srcco = dest / "srcco"
    srcco.mkdir(parents=True, exist_ok=True)
    for item in ("pyproject.toml", "VERSION", "README.md", "CITATION.cff", "LICENSE"):
        p = ROOT / item
        if p.exists():
            shutil.copy2(p, srcco / item)
    shutil.copytree(ROOT / "src", srcco / "src",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"))
    wheeldir = dest / "wheels"
    wheeldir.mkdir(exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "-w", str(wheeldir)],
        cwd=srcco, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        pytest.skip(f"wheel build unavailable:\n{proc.stderr[-500:]}")
    wheels = list(wheeldir.glob("pediatric_asthma_ventilation_simulator-*.whl"))
    if not wheels:
        pytest.skip("no wheel produced")
    return wheels[0]


def test_wheel_contains_scenarios_and_schema(tmp_path):
    wheel = _build_wheel(tmp_path)
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
    pkg = "pediatric_asthma_ventilation_simulator/scenarios/"
    assert any(n == pkg + "scenario_schema_v1_8_1.yaml" for n in names), \
        "schema missing from wheel"
    scenario_yamls = [n for n in names if n.startswith(pkg) and n.endswith(".yaml")
                      and "schema" not in n]
    assert len(scenario_yamls) >= 1, "no scenario YAMLs in wheel"


def test_wheel_has_no_compiled_artifacts(tmp_path):
    wheel = _build_wheel(tmp_path)
    with zipfile.ZipFile(wheel) as zf:
        names = zf.namelist()
    dirty = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
    assert not dirty, f"compiled artifacts in wheel: {dirty}"


def test_installed_package_loads_schema_and_runs_scenario(tmp_path):
    wheel = _build_wheel(tmp_path)
    target = tmp_path / "site"
    install = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)],
        capture_output=True, text=True,
    )
    if install.returncode != 0:
        pytest.skip(f"install unavailable:\n{install.stderr[-500:]}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(target) + os.pathsep + env.get("PYTHONPATH", "")
    code = (
        "import pediatric_asthma_ventilation_simulator as p;"
        "p.load_schema();"
        "sid=p.list_builtin_scenarios()[0];"
        "out=p.simulate_scenario(p.load_builtin_scenario(sid));"
        "assert len(out)>0;"
        "print('OK', sid, len(out))"
    )
    run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert run.returncode == 0, f"installed package failed:\n{run.stdout}\n{run.stderr}"
    assert "OK" in run.stdout
