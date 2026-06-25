# Contributing

Thanks for your interest in improving the Pediatric Asthma Ventilation Simulator.
This is an **educational, non-clinical** open-source project: it is a transparent
teaching sandbox for ventilation trade-offs in pediatric status asthmaticus. It is
not a medical device, not clinical decision support, and is not validated against
patient data. Contributions are welcome in that spirit.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # core + app + dev deps
pip install -e .                     # editable install of the package
```

## Running things

```bash
make test          # full test suite (pytest)
make reproduce     # regenerate all CSVs/figures + reproducibility manifest
make app           # launch the Streamlit teaching UI
```

The package itself is importable and installable:

```python
import pediatric_asthma_ventilation_simulator as sim
sim.list_builtin_scenarios()
sim.simulate_scenario(sim.load_builtin_scenario("high_rr_dynamic_hyperinflation"))
```

## Adding or editing a scenario

Scenarios live as YAML in `src/pediatric_asthma_ventilation_simulator/scenarios/`
and ship with the package. Every scenario is validated against
`scenario_schema_v1_8_1.yaml`, which encodes the required fields, value ranges,
the canonical ventilation-mode vocabulary (`VCV`, `PCV`, `PSV_CPAP`,
`MANUAL_BAGGING_THEN_VCV`), and mode-specific requirements. After any change:

```bash
python -m pytest tests/test_release_schema_v1_8_1.py tests/test_schema_completeness_v1_8_1.py
```

A scenario that passes the schema must also build and run; the tests enforce this.

## Coding norms

- Keep the model transparent: no hidden tuning. New coefficients must be documented
  and, where possible, traceable to literature, with honest labeling of teaching
  constants.
- Outputs are **directional surrogates**, not blood-gas or hemodynamic predictions.
  Do not add language or features implying clinical prediction.
- Add or update tests for any behavioral change. The golden-value snapshot guards
  against silent engine/manuscript drift; update it deliberately, not casually.

## Pull requests

1. Branch from `main`.
2. Ensure `make test` is green and `make reproduce` runs cleanly with no stale
   artifacts.
3. Run `make clean` before committing so no `__pycache__`, `.pytest_cache`,
   `build/`, `dist/`, or `*.egg-info` are included.
4. Describe the physiological or software rationale in the PR.

## Scope reminder

If a proposed change would push the tool toward clinical use, prediction, or
decision support, it is out of scope. The goal is inspectable, reproducible
teaching, not a clinical instrument.
