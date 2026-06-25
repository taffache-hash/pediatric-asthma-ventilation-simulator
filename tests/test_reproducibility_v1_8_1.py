"""Reproducibility / release-hygiene tests (v1.8.1).

Fast static checks (no figure regeneration):
  * every figure filename referenced in the figure captions exists on disk;
  * the expected primary output CSVs exist;
  * no stale-version artifact (v0_8, v1_0, v1_5, v1_6, v1_7) is left in
    figures/ or outputs/, which would signal a package assembled by
    stratification rather than a clean release.
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

VERSION_TAG = "v1_8_1"
FIG_DIR = ROOT / "figures" / VERSION_TAG
OUT_DIR = ROOT / "outputs" / VERSION_TAG
CAPTIONS = ROOT / "manuscript" / "figure_captions_v1_8_1.md"

STALE_TOKENS = ("v0_8", "v1_0", "v1_5", "v1_6", "v1_7")


def _referenced_figures():
    text = CAPTIONS.read_text(encoding="utf-8")
    return sorted(set(re.findall(r"[A-Za-z0-9_]+\.png", text)))


def test_caption_figures_exist():
    referenced = _referenced_figures()
    assert referenced, "no figures referenced in captions"
    missing = [name for name in referenced if not (FIG_DIR / name).is_file()]
    assert not missing, f"figures referenced in captions but missing on disk: {missing}"


def test_primary_output_csvs_exist():
    expected = [
        f"rr_sweep_severe_obstruction_{VERSION_TAG}.csv",
        f"scenario_summary_{VERSION_TAG}.csv",
        f"sensitivity_analysis_{VERSION_TAG}.csv",
    ]
    missing = [name for name in expected if not (OUT_DIR / name).is_file()]
    assert not missing, f"expected output CSVs missing: {missing}"


@pytest.mark.parametrize("subtree", ["figures", "outputs"])
def test_no_stale_version_artifacts(subtree):
    base = ROOT / subtree
    if not base.is_dir():
        pytest.skip(f"{subtree}/ not present")
    stale = [
        str(p.relative_to(ROOT))
        for p in base.rglob("*")
        if p.is_file() and any(tok in p.name for tok in STALE_TOKENS)
    ]
    assert not stale, f"stale-version artifacts found under {subtree}/: {stale}"


def test_reproduce_script_present_and_importable():
    script = ROOT / "scripts" / "reproduce_all.py"
    assert script.is_file(), "scripts/reproduce_all.py missing"
    # Compile-check (does not execute the pipeline).
    compile(script.read_text(encoding="utf-8"), str(script), "exec")
