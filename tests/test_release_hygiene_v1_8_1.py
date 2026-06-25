"""Release-hygiene tests (v1.8.1).

Build artifacts must never ship in a release. These directories are not created
by a normal pytest run (unlike __pycache__/.pytest_cache, which are transient),
so asserting their absence is deterministic in a clean checkout.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNED_DIR_NAMES = {"build", "dist"}
BANNED_DIR_SUFFIX = ".egg-info"


def test_no_build_or_dist_dirs():
    offenders = []
    for p in ROOT.rglob("*"):
        if p.is_dir() and (
            p.name in BANNED_DIR_NAMES or p.name.endswith(BANNED_DIR_SUFFIX)
        ):
            # ignore anything inside a temporary pytest path
            if ".pytest_tmp" in str(p) or "/tmp/" in str(p):
                continue
            offenders.append(str(p.relative_to(ROOT)))
    assert not offenders, f"build artifacts present in tree: {offenders}"


def test_gitignore_covers_build_artifacts():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for token in ("__pycache__", ".pytest_cache", "*.egg-info", "build", "dist"):
        assert token in gi, f".gitignore missing {token}"
