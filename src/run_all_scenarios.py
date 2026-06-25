"""Run all built-in scenarios with the engine and export summaries/timeseries CSVs.

Scenarios are resolved from the installed package data (importlib.resources), so
this works from the source tree and from an installed wheel alike.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# Allow running as `python src/run_all_scenarios.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pediatric_asthma_ventilation_simulator import (  # noqa: E402
    builtin_scenario_path,
    list_builtin_scenarios,
    run_scenario_file,
)

ROOT = Path(__file__).resolve().parents[1]
VERSION_TAG = "v1_8_1"
OUTPUT_DIR = ROOT / "outputs" / VERSION_TAG


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for scenario_id in list_builtin_scenarios():
        scenario_path = builtin_scenario_path(scenario_id)
        csv_path = OUTPUT_DIR / f"{scenario_id}_timeseries.csv"
        summary = run_scenario_file(scenario_path, csv_path)
        rows.append(summary)
        print(f"{summary['scenario_id']}: autoPEEP={summary['final_autopeep_cmH2O']} cmH2O, "
              f"Pplat={summary['final_pplat_cmH2O']} cmH2O, PaCO2={summary['final_paco2_mmHg']} mmHg, "
              f"MAP_min={summary['min_map_mmHg']} mmHg")

    summary_path = OUTPUT_DIR / f"scenario_summary_{VERSION_TAG}.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
