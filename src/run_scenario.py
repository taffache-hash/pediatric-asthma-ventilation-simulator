"""Run one scenario and optionally export the time series.

Example:
    python src/run_scenario.py scenarios/high_rr_dynamic_hyperinflation.yaml --csv outputs/high_rr.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pediatric_asthma_ventilation_simulator import run_scenario_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one pediatric asthma ventilation scenario.")
    parser.add_argument("scenario", help="Path to scenario YAML file")
    parser.add_argument("--csv", help="Optional output CSV path", default=None)
    args = parser.parse_args()
    summary = run_scenario_file(Path(args.scenario), args.csv)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
