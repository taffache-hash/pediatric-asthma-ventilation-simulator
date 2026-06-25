# Pediatric Status Asthmaticus Ventilation Simulator

**Version:** 1.8.1  
**Scope:** educational physiology simulator for ventilated pediatric status asthmaticus  
**Safety boundary:** not clinical decision support; not a medical device; not for patient-specific ventilator settings.

## Purpose

This open-source simulator illustrates how ventilator settings and airway obstruction may influence dynamic hyperinflation, auto-PEEP, plateau-pressure surrogates, gas-exchange surrogates, and hemodynamic compromise in ventilated pediatric status asthmaticus.

The core teaching message is:

```text
Te/tau_exp ↓
→ incomplete expiratory emptying
→ trapped volume ↑
→ auto-PEEP ↑
→ total PEEP / Pplat ↑
→ venous return and MAP ↓
```

PaCO2, pH, EtCO2, MAP, and risk labels are simulated educational outputs. They are not patient-specific predictions.

## What this package is

Appropriate uses:

```text
teaching airway obstruction and expiratory time constants
scenario-based pediatric ICU/anesthesia simulation
transparent software-methods publication
hypothesis-generating educational model
```

Inappropriate uses:

```text
clinical decision support
real-patient ventilator setting
validated pediatric blood gas prediction
medical-device functionality
bedside monitoring substitute
```

## Current status

1.8.1 is a maintenance release on the 1.8 physiology-fix line (version alignment, scenario input validation, JSON Schema for all scenarios, smoke tests). 1.8.0 is the underlying physiology-fix release. It does not claim clinical validation. It adds:

```text
reviewer-style manuscript audit
revised manuscript draft
figure captions
improved paper-oriented figures
scenario review table
physiology regression checks (dt-invariance, runaway prevention, silent-chest EtCO2, external-PEEP penalty, expected-direction)
clearer wording around internal verification vs clinical validation
```

## Repository structure

```text
app/          Streamlit educational interface
src/          installable package (engine, validation, scenarios package-data) + runner scripts
data/         evidence, parameter, calibration, audit, and release tables
docs/         model reports, safety disclaimer, reviewer audit, release notes
tests/        sanity checks, expected-direction physiology checks, smoke/packaging tests
outputs/      generated scenario CSV outputs
figures/      manuscript-oriented figures
manuscript/   manuscript drafts, reviewer critique, figure captions
```

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Run all scenarios

```bash
python src/run_all_scenarios.py
```

The summary is written to:

```text
outputs/v1_8_1/scenario_summary_v1_8_1.csv
```

## Compare two strategies

```bash
python src/compare_strategies.py \
    src/pediatric_asthma_ventilation_simulator/scenarios/safe_controlled_hypoventilation.yaml \
    src/pediatric_asthma_ventilation_simulator/scenarios/high_rr_dynamic_hyperinflation.yaml
```

## Generate manuscript-oriented figures

```bash
python src/generate_paper_figures.py
```

Figures are written to:

```text
figures/v1_8_1/
```

## Test

Run the full suite with pytest (recommended):

```bash
pytest
```

Or run the individual test modules directly:

```bash
pytest tests/test_invariants_v1_8_1.py
pytest tests/test_release_integrity_v1_8_1.py
```

The physiology suite covers dt-invariance, runaway prevention, the silent-chest
low-EtCO2 pitfall, the external-PEEP hemodynamic penalty, and expected-direction
smoke checks. The integrity suite covers version alignment, dependency pinning,
and absence of stray build artifacts.

## Scenario library

```text
safe_controlled_hypoventilation.yaml
high_rr_dynamic_hyperinflation.yaml
high_vt_barotrauma_risk.yaml
excess_external_peep_passive.yaml
spontaneous_autopeep_peep_titration.yaml
post_intubation_collapse.yaml
ketamine_bronchodilation_response.yaml
silent_chest_low_etco2.yaml
```

## Model boundary

This is a low-dimensional transparent educational model. It intentionally favors interpretability over patient-level prediction. It does not model regional ventilation, full cardiopulmonary interaction, bronchial heterogeneity in a mechanistic CFD sense, exact pharmacokinetics, or patient-specific disease evolution. Several thresholds are teaching anchors derived from mixed pediatric/adult sources and must not be interpreted as validated pediatric cutoffs.

## Version history

- v0.1: evidence pack
- v0.2: physiological model specification
- v0.3: parameter tables and YAML scenarios
- v0.4: first Python engine
- v0.5: calibration of effective ventilation/dead space/flow limitation
- v0.6: Streamlit interface
- v0.7: strategy comparison, teaching summary, figure generation
- v0.8: release-candidate package, license, citation file, manuscript draft, GitHub/Zenodo guide
- v0.9: public-repository cleanup, release integrity checks, manuscript polish, pre-submission checklist
- v1.0-alpha: scenario-by-scenario clinical audit, acceptance tests, updated outputs, manuscript v1.0 draft
- v1.2-alpha: reviewer-style cleanup, revised figures, manuscript audit, clearer validation language
- v1.3-alpha: physiology fix (closed-form trapping, 0.863 alveolar-ventilation constant, acute respiratory acidosis pH, explicit unsafe-physiology flags)
- v1.4-submission-snapshot: clean release snapshot and bibliography/traceability tables
- v1.5-remediation-snapshot: silent-chest low-EtCO2 recalibration, external-PEEP hemodynamic penalty, expected-direction tests, integrity-test fix
- v1.8.0: severe-obstruction same-patient respiratory-rate sweep added as the primary internal-verification figure (U-shaped CO2 nadir); controlled-hypoventilation scenario retuned to show modest real intrinsic PEEP and a wide PIP-to-plateau gap; spontaneous PEEP-titration scenario fixed (realistic spontaneous rate) and external PEEP reworked as a single counterbalancing-PEEP rule for passive and spontaneous patients; physiologic-invariant/monotonicity tests, golden-value snapshot, and local sensitivity analysis added; "validation"/"experiment" wording replaced by "internal verification" throughout; post-intubation collapse moved out of the main quantitative table into an unsafe-threshold demonstration; therapy modifiers confined to supplementary; parameter traceability table added.
- v1.7-submission-candidate: external-PEEP penalty gated to non-spontaneous patients, README test commands corrected, manuscript and figure captions rewritten against the current engine with explicit display-cap disclosure, version alignment

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.

## Citation

Use `CITATION.cff` for software citation metadata.


## v1.3-alpha note

This release adds a verified bibliography registry and a parameter-to-source traceability table:

```text
data/verified_references_v1_8_1.csv
data/parameter_source_traceability_v1_8_1.csv
manuscript/full_manuscript_draft_v1_8_1.md
```

The physiology engine has changed from v1.2-alpha: dynamic trapping is now closed-form per breath, gas-exchange constants were corrected, and unsafe physiological thresholds are explicitly flagged.
