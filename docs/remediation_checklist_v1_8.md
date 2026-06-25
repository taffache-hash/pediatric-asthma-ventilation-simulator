# Remediation checklist — v1.8.0

Response to the v1.7 severe technical review. Status: all mandatory and optional
items addressed. Verified with `pytest` (26 passed), full scenario re-run, and
figure/sensitivity regeneration.

## Eight identified weaknesses

| # | Reviewer weakness | Resolution in v1.8 | Where |
| --- | --- | --- | --- |
| 1 | "Validation"/"experiment" claim too strong | Reframed throughout as "development and internal verification"; added invariant/monotonicity tests and a golden snapshot | manuscript title/abstract/methods; `tests/test_invariants_v1_8.py` |
| 2 | Same-patient behavior not persuasive | Added same-patient RR sweep with a U-shaped PaCO2 nadir (~22/min) and monotonic auto-PEEP/plateau/MAP | `severe_obstruction_rr_reference.yaml`; Figure 1; `test_paco2_is_u_shaped_in_rr_sweep` |
| 3 | Auto-PEEP undercalled in the "safe" scenario (0.75 cmH2O) | Retuned safe scenario to a modest but real intrinsic PEEP (~3.7 cmH2O) | `safe_controlled_hypoventilation.yaml`; acceptance test now asserts >=3.0 |
| 4 | Plateau in safe scenario implausibly low (~10 cmH2O) | Plateau now ~15 cmH2O with a wide PIP-to-plateau gap (peak ~63) | same scenario; Figure 7; acceptance test asserts PIP-Pplat >= 25 |
| 5 | Spontaneous PEEP-titration scenario broken (backup rate used as actual rate; auto-PEEP 0.11) | Added a realistic spontaneous rate (30/min); auto-PEEP now ~5.5 and trigger work unloads with PEEP | `spontaneous_autopeep_peep_titration.yaml`; Figure 8 |
| 6 | External-PEEP model too crude; no spontaneous penalty | Single counterbalancing-PEEP rule for passive and spontaneous: penalty only on PEEP above intrinsic auto-PEEP | `src/asthma_engine.py`; `test_no_hemodynamic_penalty_until_peep_exceeds_intrinsic` |
| 7 | Therapy modifiers arbitrary | Confined to clearly labeled supplementary demonstrations; no PK/PD claim | Methods "Therapy representation"; `supplementary_v1_8.md` |
| 8 | Manuscript overstates "experiment" | Rewritten as model demonstration + internal verification; collapse moved to a separate unsafe-threshold demonstration | manuscript Results structure |

## Must-do items

| Item | Status | Where |
| --- | --- | --- |
| RR-sweep figure | Done | Figure 1; `rr_sweep_severe_obstruction_v1_8.csv` |
| Invariant/monotonicity tests | Done | `tests/test_invariants_v1_8.py` |
| Fix or remove spontaneous scenario | Done (fixed) | `spontaneous_autopeep_peep_titration.yaml` |
| Retune safe scenario | Done | `safe_controlled_hypoventilation.yaml` |
| Move collapse display caps out of the main results table | Done | manuscript "Unsafe-threshold demonstration" |
| "Internal verification" wording | Done | throughout manuscript |
| Calibrated-constants limitation | Done | manuscript Limitations |
| GitHub/Zenodo placeholders | Done | manuscript "Software availability" |

## Should-do items

| Item | Status | Where |
| --- | --- | --- |
| Parameter traceability table | Done | Supplementary Table S1; `data/parameter_source_traceability` |
| PIP-Pplat figure | Done | Figure 7 |
| Sensitivity analysis | Done | `src/sensitivity_analysis.py`; Figure 9; `sensitivity_analysis_v1_8.csv` |
| Scenario-manuscript consistency test | Done | golden snapshot `test_golden_summary_values` |
