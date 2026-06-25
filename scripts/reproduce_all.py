#!/usr/bin/env python3
"""End-to-end reproducibility driver for the Pediatric Asthma Ventilation Simulator.

Runs the full pipeline in a fixed order and records a manifest so that the
artifacts referenced by the manuscript can be regenerated and audited with a
single command:

    python scripts/reproduce_all.py        # or:  make reproduce

Steps (each must succeed):
    1. pytest                       (the whole test suite must pass)
    2. run_all_scenarios.py         (scenario summaries + timeseries CSVs)
    3. generate_paper_figures.py    (main + supplementary figures and CSVs)
    4. sensitivity_analysis.py      (local one-at-a-time exploration)

After generation it:
    * hashes every figure (figures/<tag>/*.png) and output CSV (outputs/<tag>/*.csv);
    * checks that no stale-version artifact (v0_8, v1_0, v1_5, v1_6, v1_7) is
      left behind in figures/ or outputs/;
    * writes outputs/<tag>/reproducibility_manifest.json.

Exit code is non-zero if any step fails, the suite does not pass, or a stale
artifact is detected.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VERSION_TAG = "v1_8_1"  # matches figure/output directory names
FIG_DIR = ROOT / "figures" / VERSION_TAG
OUT_DIR = ROOT / "outputs" / VERSION_TAG
MANIFEST_PATH = OUT_DIR / "reproducibility_manifest.json"

STALE_TOKENS = ("v0_8", "v0.8", "v1_0", "v1_5", "v1_6", "v1_7")


def _env() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + existing if existing else "")
    return env


def _rel(args: list[str]) -> str:
    """Render a portable command string for the manifest (no absolute/env paths)."""
    out = []
    for a in args:
        if a == sys.executable:
            out.append("python")
        else:
            try:
                out.append(str(Path(a).resolve().relative_to(ROOT)))
            except (ValueError, OSError):
                out.append(a)
    return " ".join(out)


def _run(label: str, args: list[str]) -> dict:
    print(f"\n=== {label} ===")
    proc = subprocess.run(args, cwd=ROOT, env=_env(), text=True)
    ok = proc.returncode == 0
    print(f"--- {label}: {'OK' if ok else 'FAILED'} (exit {proc.returncode})")
    return {"step": label, "command": _rel(args), "returncode": proc.returncode, "ok": ok}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_dir(directory: Path, pattern: str) -> dict:
    result = {}
    if directory.is_dir():
        for p in sorted(directory.glob(pattern)):
            result[p.name] = {"sha256": _sha256(p), "bytes": p.stat().st_size}
    return result


def _find_stale() -> list[str]:
    stale = []
    for base in (FIG_DIR.parent, OUT_DIR.parent):
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file() and any(tok in p.name for tok in STALE_TOKENS):
                stale.append(str(p.relative_to(ROOT)))
    return sorted(stale)


def main() -> int:
    steps = []
    steps.append(_run("pytest", [sys.executable, "-m", "pytest", "-q"]))
    steps.append(_run("run_all_scenarios", [sys.executable, str(SRC / "run_all_scenarios.py")]))
    steps.append(_run("generate_paper_figures", [sys.executable, str(SRC / "generate_paper_figures.py")]))
    steps.append(_run("sensitivity_analysis", [sys.executable, str(SRC / "sensitivity_analysis.py")]))

    stale = _find_stale()

    try:
        sys.path.insert(0, str(SRC))
        pkg_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    except Exception:
        pkg_version = "unknown"

    manifest = {
        "package": "pediatric-asthma-ventilation-simulator",
        "version": pkg_version,
        "version_tag": VERSION_TAG,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "steps": steps,
        "all_steps_ok": all(s["ok"] for s in steps),
        "stale_artifacts": stale,
        "figures": _hash_dir(FIG_DIR, "*.png"),
        "output_csvs": _hash_dir(OUT_DIR, "*.csv"),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Do not let the manifest hash itself on a re-run.
    manifest["output_csvs"].pop(MANIFEST_PATH.name, None)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("\n=== reproducibility summary ===")
    print(f"version            : {manifest['version']}")
    print(f"all steps ok       : {manifest['all_steps_ok']}")
    print(f"figures hashed     : {len(manifest['figures'])}")
    print(f"output CSVs hashed : {len(manifest['output_csvs'])}")
    print(f"stale artifacts    : {len(stale)}")
    if stale:
        for s in stale:
            print(f"   STALE -> {s}")
    print(f"manifest written   : {MANIFEST_PATH.relative_to(ROOT)}")

    ok = manifest["all_steps_ok"] and not stale
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
