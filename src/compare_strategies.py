"""Compare two scenario YAML files and export a summary delta table.

Usage from project root:
    python src/compare_strategies.py \
        src/pediatric_asthma_ventilation_simulator/scenarios/safe_controlled_hypoventilation.yaml \
        src/pediatric_asthma_ventilation_simulator/scenarios/high_rr_dynamic_hyperinflation.yaml
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pediatric_asthma_ventilation_simulator import load_scenario, simulate_scenario, summarize_outputs

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "v1_8_1"

FIELDS = [
    ("max_autopeep_cmH2O", "Max auto-PEEP", "cmH2O", "lower_is_better"),
    ("max_pplat_cmH2O", "Max Pplat", "cmH2O", "lower_is_better"),
    ("max_vei_ml_kg", "Max VEI proxy", "mL/kg", "lower_is_better"),
    ("final_paco2_mmHg", "Final PaCO2", "mmHg", "context_dependent"),
    ("min_ph", "Min pH", "", "higher_is_better"),
    ("min_map_mmHg", "Min MAP", "mmHg", "higher_is_better"),
    ("max_global_risk_score", "Max global risk", "score", "lower_is_better"),
]


def _interpret_delta(delta: float, direction: str) -> str:
    if direction == "lower_is_better":
        return "better" if delta < 0 else "worse" if delta > 0 else "unchanged"
    if direction == "higher_is_better":
        return "better" if delta > 0 else "worse" if delta < 0 else "unchanged"
    return "context-dependent"


def compare_summary(primary: Dict[str, Any], comparator: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for key, label, unit, direction in FIELDS:
        a = float(primary[key])
        b = float(comparator[key])
        delta = b - a
        rows.append({
            "metric_key": key,
            "metric": label,
            "primary": round(a, 4),
            "comparator": round(b, 4),
            "delta_comparator_minus_primary": round(delta, 4),
            "unit": unit,
            "interpretation": _interpret_delta(delta, direction),
        })
    return rows


def write_csv(rows: Iterable[Dict[str, Any]], path: Path) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_timeseries(outputs, path: Path) -> None:
    rows = [asdict(o) for o in outputs]
    write_csv(rows, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two asthma ventilation simulator scenarios.")
    parser.add_argument("primary", type=Path, help="Primary scenario YAML")
    parser.add_argument("comparator", type=Path, help="Comparator scenario YAML")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args(argv)

    primary_scn = load_scenario(args.primary)
    comparator_scn = load_scenario(args.comparator)
    # Fair comparison: use primary duration and time step.
    comparator_scn["duration_min"] = primary_scn.get("duration_min", comparator_scn.get("duration_min", 60))
    comparator_scn["time_step_s"] = primary_scn.get("time_step_s", comparator_scn.get("time_step_s", 5))

    primary_outputs = simulate_scenario(primary_scn)
    comparator_outputs = simulate_scenario(comparator_scn)
    primary_summary = summarize_outputs(primary_outputs)
    comparator_summary = summarize_outputs(comparator_outputs)
    primary_id = primary_scn.get("scenario_id", args.primary.stem)
    comparator_id = comparator_scn.get("scenario_id", args.comparator.stem)

    delta_rows = compare_summary(primary_summary, comparator_summary)
    delta_path = args.output_dir / f"{primary_id}_vs_{comparator_id}_delta_v1_8_1.csv"
    primary_path = args.output_dir / f"{primary_id}_primary_timeseries_v1_8_1.csv"
    comparator_path = args.output_dir / f"{comparator_id}_comparator_timeseries_v1_8_1.csv"
    write_csv(delta_rows, delta_path)
    write_timeseries(primary_outputs, primary_path)
    write_timeseries(comparator_outputs, comparator_path)

    print(f"Wrote {delta_path}")
    print(f"Wrote {primary_path}")
    print(f"Wrote {comparator_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
