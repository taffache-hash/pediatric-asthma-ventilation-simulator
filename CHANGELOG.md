# Changelog

## v1.8.1 — 2026-06-24

Submission-prep revision responding to a second severe review (verdict: major
revision). Engine logic and golden values are unchanged; this patch revises the
manuscript, documentation, figure organization, and one scenario label.

Editorial / framing pass (third review)
- Reframed the artifact in the manuscript prose as a "mechanistic educational
  computational model (implemented as an interactive simulator)" rather than a
  bare "simulator", shifting the reviewer bar from external validation toward
  plausibility. Package name and DOIs are unchanged.
- Unified versioning to v1.8.1 across generated artifacts and files: figures/ and
  outputs/ directories, CSV names, and the reproducibility manifest now use the
  v1_8_1 tag; the bibliographic snapshots and the manuscript/test files were
  renamed from the v1_8 / v1_4_snapshot family to v1_8_1.
- Journal-ready figure names matching the manuscript numbering
  (Figure_1_RR_Sweep.png ... Figure_5_PEEP_Titration.png, Figure_S1..S5),
  replacing the internal figN_..._v1_8.png scheme.
- Added a model-architecture state diagram (Supplementary Figure S5) as a teaching
  and reviewer aid.

Software-reviewer remediation (second software review)
- Real installable package (B1): the loose `src/` modules were reorganized into
  the `pediatric_asthma_ventilation_simulator` package with the scenarios and JSON
  Schema shipped as package data. The schema and built-in scenarios are now
  resolved via importlib.resources, so an installed wheel can load the schema and
  run a built-in scenario. Previously the wheel shipped only modules and the
  installed package could not locate the schema. New tests build the wheel, assert
  the scenarios/schema are inside it, and install it into a clean target dir to
  load the schema and run a scenario end to end.
- One mode vocabulary (B2): added `modes.normalize_mode` and a canonical
  UPPER_SNAKE_CASE set (VCV, PCV, PSV_CPAP, MANUAL_BAGGING_THEN_VCV). The engine,
  schema enum, scenario files, and Streamlit mode selector now share it; the
  validator normalizes any alias/case (e.g. UI "PSV" -> "PSV_CPAP") before
  checking. Fixes the prior UI/schema mismatch where UI-selectable modes were
  rejected by validation.
- Complete, faithful schema (B3): required-field lists for patient,
  airway_mechanics, and ventilator now mirror the engine dataclasses, with
  mode-specific requirements (VCV/bagging -> vt_ml_kg, PCV -> driving pressure,
  PSV_CPAP -> support). A scenario that passes the schema now also builds and runs;
  the old minimal-but-schema-valid scenario that crashed the engine is rejected.
- Absurd inputs rejected (B4): pressure_control/pressure_support must be strictly
  positive, and vt_ml_kg is capped at the engine ceiling (14 mL/kg) so over-large
  tidal volumes are rejected rather than silently clipped.
- Streamlit smoke tests run in CI (B5): added a GitHub Actions workflow with a
  minimal job (no Streamlit; smoke tests skip) and a full-app job (Streamlit
  installed; smoke tests and wheel install/build tests run for real).
- Release hygiene (B6): added strict tests asserting no build/dist/egg-info in the
  tree and that the wheel contains no __pycache__/.pyc; release packaging excludes
  all caches and build artifacts.
- README: corrected stale file references (v1_2_alpha -> v1_4_snapshot data files;
  current manuscript path).

Manuscript and open-source readiness (second review, non-code items)
- Added a "Use of AI-assisted tools" disclosure (ICMJE/JOSS-aligned).
- Added a "Statement of need" section (purpose, target audience, relation to
  existing tools) for software-paper readiness.
- Wording: "clinical(-physiology) acceptance checks" -> "expected-direction
  physiology checks"; scenario category "validation_reference" ->
  "internal_verification_reference".
- Added CONTRIBUTING.md and a CI workflow.

- Manuscript: added explicit verification/calibration/validation definitions and
  the sentence "No patient data were used for calibration or validation."
- Added Table 1 (calibrated coefficients vs literature constants, classes L/E/C/D)
  and full Supplementary Table S2 with line references.
- Reduced main figures to five (RR sweep; auto-PEEP and PaCO2 safe vs high RR;
  silent-chest PaCO2/EtCO2; counterbalancing-PEEP titration); moved the rest to
  Supplementary Figures S1-S4.
- Reinforced "surrogate" labeling for PaCO2, EtCO2, MAP, pressures, and pH
  throughout; reaffirmed the post-intubation collapse as an unsafe-threshold
  demonstration only.
- Sharpened the Discussion to three statements (passed internal testing; no
  external validation; outputs are directional surrogates) and added a paragraph
  on real-world features deliberately omitted.
- Disclosed the passive-PEEP simplification as a known limitation/planned refinement.
- Relabeled the excessive-tidal-volume scenario as a pressure-exposure scenario
  (not gas-trapping). See docs/remediation_checklist_v1_8_1.md.

Software coherence (responding to the software-reviewer items of the second review)
- Version alignment: Streamlit app docstring, VERSION constant, caption, and CSV
  download filenames moved from the stale v1.0-alpha / v0.8 strings to v1.8.1;
  README current-status line and manuscript reference/supplementary headers
  aligned to 1.8.1. Engine and golden values unchanged.
- Scenario input validation added (src/scenario_validation.py). Pathological
  input (weight <= 0, time_step <= 0, duration <= 0, negative PEEP, non-positive
  respiratory rate / resistance / compliance, implausible tidal volume, unknown
  ventilation mode, malformed I:E ratio) now raises an explicit
  ScenarioValidationError before any simulation, replacing the previous
  ZeroDivisionError / silent non-physiological output behaviour.
- Real JSON Schema (Draft 2020-12) describing the actual scenario structure:
  scenarios/scenario_schema_v1_8_1.yaml. Range and safety constraints are encoded
  in the schema, so structural and input validation share one source of truth.
  The stale, structurally-mismatched scenario_schema_v0_2.yaml was removed.
- Tests: added test_input_validation_v1_8_1.py, test_release_schema_v1_8_1.py
  (every shipped scenario validated against the schema), and
  test_streamlit_smoke_v1_8_1.py (app import, scenario discovery, schema-file
  exclusion, app/package version match). Suite grows from 26 to 84 passing tests.
- Packaging hygiene: added .gitignore; removed __pycache__/.pytest_cache from the
  release artifact; schema files are now excluded from scenario discovery in both
  the app and run_all_scenarios.py via a robust filename guard.

Manuscript wording (responding to the editorial/methodological review items)
- Abstract Results trimmed: dropped most secondary numeric ranges, kept the
  respiratory-rate-sweep U-shape as the single headline result, closed with
  "no patient data were used."
- Relabeled the external-PEEP "rule" as a "simplified counterbalancing-PEEP
  teaching approximation" throughout (manuscript, figure captions, supplementary).
- Comparative scenarios explicitly marked as illustrative comparisons (multiple
  parameters differ simultaneously), with the same-patient respiratory-rate sweep
  named as the controlled single-variable evidence; the post-table sentence was
  softened from causal to illustrative phrasing.
- "Local sensitivity analysis" qualified as "local one-at-a-time sensitivity
  exploration" in the Methods, Results heading, and Supplementary Figure S4.
- Discussion opens with an explicit framing sentence ("educational visualization
  engine, not a physiological prediction model") ahead of the three bounding
  statements.

Reproducibility and packaging
- Added scripts/reproduce_all.py and a Makefile (`make reproduce` / `make test`):
  one command runs the suite, regenerates all scenario CSVs, figures, and the
  sensitivity exploration, then writes outputs/v1_8/reproducibility_manifest.json
  with per-artifact SHA-256 hashes and a stale-artifact audit.
- Added test_reproducibility_v1_8_1.py: every figure referenced in the captions
  exists on disk, the primary output CSVs exist, and no stale-version artifact
  (v0_8/v1_0/v1_5/v1_6/v1_7) remains under figures/ or outputs/.
- Made the package installable: pyproject now declares the flat src/ modules via
  package-dir/py-modules (was an empty py-modules that installed nothing) and adds
  jsonschema as a runtime dependency. No files were relocated; existing flat
  imports are unchanged. A nested src/pediatric_asthma_sim/ package remains a
  possible future refactor but was deliberately deferred to avoid churn before
  submission.

Project positioning
- Positioned as an evolving, community-modifiable open-source educational
  resource. The honest scope statements are unchanged: the simulator is
  explicitly not clinically validated, educational-only, and built without any
  patient data.

## v1.8.0 — 2026-06-24

Revision addressing an external severe technical review. The review judged v1.7
a promising educational prototype that was not yet submission-ready as a
simulation-methods paper. All mandatory and optional review items were addressed:

Engine
- External PEEP reworked into a single counterbalancing-PEEP / flow-limitation
  rule applied identically to passive and spontaneous patients: applied PEEP up
  to intrinsic auto-PEEP counterbalances inspiratory threshold load without a
  venous-return penalty; only PEEP above intrinsic PEEP penalizes MAP. Replaces
  the prior rule that suppressed the spontaneous external-PEEP penalty entirely.
- New output field external_peep_excess_cmH2O exposes the excess (penalizing)
  PEEP for figures and tests.

Scenarios
- safe_controlled_hypoventilation retuned (raw_insp 35->50, raw_exp_mult 1.6->2.0,
  heterogeneity 1.1->1.4, Crs 1.0->0.78): now shows modest real intrinsic PEEP
  (~3.7 cmH2O) and a wide PIP-to-plateau gap, instead of a near-normal plateau.
- spontaneous_autopeep_peep_titration fixed: it previously used the backup rate
  (8/min) as the actual spontaneous rate, giving a non-physiologic long Te and
  ~0.1 cmH2O auto-PEEP, so it could not demonstrate trigger-work unloading. A
  realistic spontaneous rate (30/min) restores meaningful intrinsic PEEP and the
  intended PEEP-unloading teaching point.
- New severe_obstruction_rr_reference scenario underpins the primary RR-sweep
  figure and the sensitivity analysis.

Verification and figures
- New primary figure: same-patient RR sweep (6-40/min) showing a U-shaped PaCO2
  surrogate with an interior nadir near 22/min, monotonic auto-PEEP/plateau rise,
  and monotonic MAP fall.
- New invariant/monotonicity test suite, golden-value snapshot, PIP-Pplat-gap
  figure, counterbalancing-PEEP titration figure, and local sensitivity analysis.

Manuscript
- Title and wording moved from "validation"/"experiment" to "development and
  internal verification".
- Post-intubation collapse removed from the main quantitative table and reported
  as a separate unsafe-threshold demonstration.
- Therapy modifiers confined to clearly labeled supplementary demonstrations.
- Added a calibrated-teaching-constants limitation, a parameter traceability
  table, and GitHub/Zenodo DOI placeholders.

## v1.7.0-submission-candidate — 2026-06-24

Physiology revision following an independent literature-grounded engine audit.
Four coupled changes, each verified against the reference literature and the
test suite:

1. Acid-base (pH). Replaced the linear "0.08 pH units per 10 mmHg" rule with an
   acute Henderson-Hasselbalch relationship (HCO3- rises ~1 mEq/L per 10 mmHg
   PaCO2 above 40; falls ~2 mEq/L per 10 mmHg below 40). The linear rule
   over-estimated acidosis at high PaCO2 (e.g. PaCO2 98 gave pH 6.93 versus
   ~7.11 by Henderson-Hasselbalch). pH is now a shared pure function (acute_ph).
2. Safe-scenario test coherence. The permissive-hypercapnia acceptance test
   previously combined a PaCO2 ceiling (80 mmHg) with a pH floor (7.19) that
   could not coexist under the engine's own acid-base relationship. The pH floor
   is now derived from the PaCO2 ceiling via acute_ph, so the two bounds are
   consistent by construction.
3. Dynamic hyperinflation / auto-PEEP. Replaced the ad-hoc trapped-volume
   damping factor (which under-counted trapping by ~35%) with the single-
   compartment steady state VT*r/(1-r). The high respiratory-rate scenario now
   reaches an auto-PEEP of ~13 cmH2O, consistent with intrinsic PEEP magnitudes
   reported in mechanically ventilated severe asthma (Williams 1992; Leatherman).
   The flow-limitation ventilation-loss coefficients were recalibrated (auto-PEEP
   0.032->0.014, trapped 0.018->0.008) so the PaCO2 surrogate remains physiologic
   with the larger, realistic auto-PEEP. The high-RR auto-PEEP expected-direction
   threshold was tightened from >6.0 to >9.0 cmH2O.
4. End-tidal CO2. Replaced the opaque per-scenario etco2_signal_fraction knob
   with the alveolar (Enghoff) dead-space relationship EtCO2 = PaCO2*(1 - Vd_alv/
   Vt_alv). A mechanistic component scales with occult units, obstruction,
   heterogeneity, and auto-PEEP; scenarios with a clinically defined severe V/Q
   derangement add an explicit, physically interpretable
   vq_mismatch_dead_space_fraction (silent chest: 0.58). The silent-chest
   low-EtCO2 pitfall is preserved (EtCO2 ~14 mmHg at PaCO2 ~105 mmHg) but is now
   driven by an explicit alveolar dead space rather than a hidden factor.

Other: bumped version to v1.7.0-submission-candidate with aligned VERSION,
pyproject.toml, README, engine docstring, integrity test, renamed test modules
and output/figure directories; regenerated all outputs and figures; rewrote the
manuscript Results, Methods model description, Limitations, and figure captions
against the v1.7 engine. The eight-scenario directional behaviour, dt-invariance
in the operating step range, the safety caps, and the post-intubation display-cap
disclosure are unchanged.

## v1.6.0-submission-candidate — 2026-06-24

- Gated the external-PEEP hemodynamic penalty to non-spontaneous patients: in a
  spontaneously triggering child, applied PEEP up to intrinsic PEEP unloads
  trigger work rather than impairing venous return, so the MAP penalty now
  applies only when `patient_effort` is not spontaneous. No change to the eight
  published scenario outputs (only `excess_external_peep_passive` has external
  PEEP > 5 cmH2O, and it is passive).
- Fixed the README "Test" section, which previously listed five non-existent
  test scripts; it now invokes `pytest` and the real test modules.
- Bumped version to v1.6.0-submission-candidate and aligned VERSION,
  pyproject.toml, README, and the engine docstring.
- Renamed test modules to `*_v1_6.py`; renamed output/figure directories and
  files to `v1_6_submission_candidate`.
- Restored a meaningful release-integrity check: the compiled-artifact test now
  flags loose `.pyc`/`.pyo` outside runtime `__pycache__` instead of being a
  no-op, while still tolerating pytest's runtime bytecode caches.
- Manuscript Results/Discussion and figure captions rewritten against the
  current engine; explicit disclosure added that post-intubation collapse
  reports display-capped unsafe values rather than physiological measurements.
- Retroactive note (introduced in v1.5, not previously logged): the
  `high_rr_dynamic_hyperinflation` scenario was recalibrated
  (heterogeneity_factor 1.2 -> 1.4, RR 24 -> 26 bpm) to make the dynamic
  hyperinflation teaching signal more representative; this raised max auto-PEEP
  from ~4.5 to ~6.8 cmH2O and max PaCO2 from ~76 to ~98 mmHg.

## v1.5.0-remediation-snapshot — 2026-06-24

- Recalibrated `silent_chest_low_etco2` so it produces a genuinely low EtCO2 signal with high, non-capped PaCO2.
- Added scenario-level `monitoring.etco2_signal_fraction` to model poor exhaled gas sampling without altering PaCO2.
- Added external PEEP hemodynamic penalty for passive obstructed scenarios.
- Updated figure and scenario output directories to `v1_5_remediation_snapshot`.
- Added tests for silent-chest EtCO2 pitfall, external PEEP hemodynamic penalty, and key expected-direction smoke checks.
- Fixed release-integrity test so normal pytest bytecode generation does not cause a false failure.
- Regenerated v1.5 scenario validation, dt-sensitivity, PEEP sweep, and figure outputs.


## v1.0.0-alpha — Clinical-physiology alpha release

- Updated package metadata from v0.9 to v1.0-alpha.
- Rebuilt output/figure paths for `outputs/v1_0_alpha/` and `figures/v1_0_alpha/`.
- Added scenario-by-scenario clinical-physiology audit.
- Added clinical acceptance tests enforcing qualitative scenario behavior.
- Added v1.0-alpha release integrity test.
- Added v1.0-alpha manuscript draft.
- Corrected high-RR scenario expectation wording to avoid overclaiming plateau-pressure warning.


## v0.8.0-alpha

- Added Apache-2.0 LICENSE, NOTICE, CITATION.cff, VERSION, pyproject.toml and .gitignore.
- Added release-candidate documentation for GitHub/Zenodo deposition.
- Added safety disclaimer and reviewer-risk register.
- Added full manuscript draft and software availability/limitations text.
- Updated runnable scripts and app labels to v0.8 output paths.
- Tightened `high_vt_barotrauma_risk.yaml` so it generates a plateau-pressure warning as expected.
- Added v0.8 validation outputs.

## v0.7

Cumulative release including all v0.1-v0.6 contents.

### Added

- Strategy comparison tab in `app/streamlit_app.py`.
- Automatic teaching-summary logic.
- Overlay comparison plots in the interface.
- Downloadable comparison delta CSV.
- CLI comparison tool: `src/compare_strategies.py`.
- Figure generator: `src/generate_paper_figures.py`.
- Draft paper figures under `figures/v0_7/`.
- v0.7 engine/comparison sanity tests.
- v0.7 Streamlit smoke test.
- New documentation files:
  - `docs/interface_refinement_report_v0_7.md`
  - `docs/strategy_comparison_report_v0_7.md`
  - `docs/figure_generation_report_v0_7.md`
  - `docs/release_notes_v0_7.md`
  - `manuscript/results_addendum_v0_7.md`

### Changed

- README updated for v0.7 workflow.
- `requirements.txt` now includes matplotlib for draft figure generation.
- `src/run_all_scenarios.py` exports to `outputs/v0_7/`.

### Not changed

- Core engine calibration is not materially changed from v0.5/v0.6.
- v0.7 is primarily an interface, comparison and manuscript-preparation release.

## v0.6

- First Streamlit interface.

## v0.5

- Calibrated effective ventilation, dead-space and flow-limitation penalties.

## v0.4

- First executable Python engine.

## v0.3

- Concrete parameter tables and 8 YAML scenarios.

## v0.2

- Physiological model specification.

## v0.1

- Evidence pack and roadmap.

## v0.9.0-alpha — Public-repository cleanup

- Updated core package metadata from v0.8 to v0.9.
- Rebuilt output/figure paths for `outputs/v0_9/` and `figures/v0_9/`.
- Added release-integrity test covering key repository files, scenarios, docs, manuscript, and version metadata.
- Added public-release audit, pre-submission checklist, and v0.9 release notes.
- Added a more polished manuscript draft for software-report submission.
- Preserved all prior versions and cumulative documentation.


## 1.3.0-alpha - physiology-fix release

- Replaced timestep-dependent trapped-volume accumulation with a closed-form per-breath recurrence.
- Added explicit unsafe-physiology flags when dynamic hyperinflation, capped auto-PEEP, capped airway pressures, or critical gas-exchange thresholds are reached.
- Replaced the undocumented PaCO2 coefficient with the standard 0.863 alveolar ventilation relationship.
- Replaced damped pH behavior with an acute respiratory acidosis approximation.
- Recalibrated safe controlled hypoventilation and high-VT scenarios after gas-exchange correction.
- Added v1.3 physiology regression tests covering runaway prevention, safe scenario plausibility, RR-vs-safe behavior, and dt invariance.

## 1.2.0-alpha - bibliography and traceability release

- Added verified reference registry with PMID/PMCID/DOI fields.
- Added parameter-to-source traceability table.
- Added updated manuscript draft with numeric references.
- Added reference-claim audit and pre-submission checklist.
- Added reference-registry integrity test.
- No physiology engine changes.
