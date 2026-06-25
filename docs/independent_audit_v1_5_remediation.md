# Independent Remediation Audit — v1.5.0-remediation-snapshot

Date: 2026-06-24

## Verdict

v1.5 addresses the main v1.4 audit blockers that were still preventing a credible submission snapshot:

1. The silent-chest scenario now reproduces the intended low/unreliable EtCO2 signal without relying on a hidden PaCO2 cap.
2. External PEEP now produces a visible hemodynamic penalty in the passive obstructed scenario.
3. The pytest integrity test no longer fails simply because pytest creates runtime bytecode caches.
4. Figure generation and scenario export paths now use `v1_5_remediation_snapshot` rather than the obsolete `v1_1_alpha`.
5. New tests explicitly check the scenario messages that previously failed silently.

The manuscript remains **not submission-ready** until Results, captions, and claims are rewritten around the v1.5 outputs.

## Scenario validation table

| scenario_id                         |   max_autopeep_cmH2O |   max_pplat_cmH2O |   max_paco2_mmHg |   final_etco2_mmHg |   min_ph |   min_map_mmHg |   unsafe_points |
|:------------------------------------|---------------------:|------------------:|-----------------:|-------------------:|---------:|---------------:|----------------:|
| excess_external_peep_passive        |                 0.84 |             22.86 |             55.9 |               37.2 |    7.273 |          57.77 |               0 |
| high_rr_dynamic_hyperinflation      |                 6.85 |             17.97 |             98.2 |               54.1 |    6.935 |          55.08 |               0 |
| high_vt_barotrauma_risk             |                 0.99 |             30.79 |             33.7 |               23.8 |    7.4   |          68.9  |               0 |
| ketamine_bronchodilation_response   |                 1.11 |             19.08 |             54.5 |               30.9 |    7.284 |          65.17 |               0 |
| post_intubation_collapse            |                30    |             65    |            180   |               57.3 |    6.8   |          18    |             601 |
| safe_controlled_hypoventilation     |                 0.45 |              9.95 |             64.6 |               47.9 |    7.203 |          64.66 |               0 |
| silent_chest_low_etco2              |                 2.49 |             14.75 |            100.5 |               15.1 |    6.916 |          54.55 |               0 |
| spontaneous_autopeep_peep_titration |                 0.06 |             14.44 |             83.7 |               58   |    7.05  |          65.26 |               0 |

## Silent chest remediation

Previous v1.4 problem: `silent_chest_low_etco2` claimed a falsely reassuring low EtCO2 signal but produced EtCO2 around 67 mmHg while PaCO2 was pinned to the 180 mmHg display cap.

v1.5 correction:
- obstruction was recalibrated from critical/capped behavior to severe near-silent obstruction;
- an explicit monitoring field was added:
  - `monitoring.etco2_signal_fraction: 0.38`
- this modifies the displayed EtCO2 signal only, not the blood-gas surrogate.

Current behavior:
- max PaCO2: 100.5 mmHg
- final EtCO2: 15.1 mmHg
- min pH: 6.916
- unsafe points: 0

Interpretation: the scenario now demonstrates a PaCO2-EtCO2 dissociation as a monitoring pitfall rather than a cap artifact.

## External PEEP sweep

|   peep_cmH2O |   max_pplat_cmH2O |   min_map_mmHg |   max_autopeep_cmH2O |   max_paco2_mmHg |
|-------------:|------------------:|---------------:|---------------------:|-----------------:|
|            0 |             12.86 |          61.21 |                 0.84 |             55.9 |
|            3 |             15.86 |          61.21 |                 0.84 |             55.9 |
|            5 |             17.86 |          61.21 |                 0.84 |             55.9 |
|            8 |             20.86 |          59.15 |                 0.84 |             55.9 |
|           10 |             22.86 |          57.77 |                 0.84 |             55.9 |
|           12 |             24.86 |          56.4  |                 0.84 |             55.9 |
|           16 |             28.86 |          53.65 |                 0.84 |             55.9 |

Interpretation: Pplat rises with external PEEP, and MAP now falls progressively at higher external PEEP. Auto-PEEP and PaCO2 are expectedly unchanged because this sweep isolates the hemodynamic consequence of external PEEP rather than changing obstruction.

## dt sensitivity

| scenario_id                    |   dt_s |   max_autopeep_cmH2O |   max_pplat_cmH2O |   max_paco2_mmHg |   min_map_mmHg |   final_etco2_mmHg |   unsafe_points |
|:-------------------------------|-------:|---------------------:|------------------:|-----------------:|---------------:|-------------------:|----------------:|
| high_rr_dynamic_hyperinflation |   0.25 |                 6.85 |             17.96 |             98.1 |          55.09 |               54.1 |               0 |
| high_rr_dynamic_hyperinflation |   0.5  |                 6.85 |             17.96 |             98.1 |          55.09 |               54.1 |               0 |
| high_rr_dynamic_hyperinflation |   1    |                 6.85 |             17.96 |             98.1 |          55.09 |               54.1 |               0 |
| high_rr_dynamic_hyperinflation |   2    |                 6.85 |             17.96 |             98.2 |          55.09 |               54.1 |               0 |
| high_rr_dynamic_hyperinflation |   5    |                 6.85 |             17.97 |             98.2 |          55.08 |               54.1 |               0 |
| high_rr_dynamic_hyperinflation |  10    |                 6.85 |             17.97 |             98.2 |          55.08 |               54.1 |               0 |
| silent_chest_low_etco2         |   0.25 |                 2.49 |             14.75 |            100.4 |          54.57 |               15.1 |               0 |
| silent_chest_low_etco2         |   0.5  |                 2.49 |             14.75 |            100.4 |          54.57 |               15.1 |               0 |
| silent_chest_low_etco2         |   1    |                 2.49 |             14.75 |            100.4 |          54.57 |               15.1 |               0 |
| silent_chest_low_etco2         |   2    |                 2.49 |             14.75 |            100.4 |          54.57 |               15.1 |               0 |
| silent_chest_low_etco2         |   5    |                 2.49 |             14.75 |            100.5 |          54.55 |               15.1 |               0 |
| silent_chest_low_etco2         |  10    |                 2.49 |             14.75 |            100.7 |          54.52 |               15.1 |               0 |
| post_intubation_collapse       |   0.25 |                30    |             65    |            180   |          18    |               57.3 |            4794 |
| post_intubation_collapse       |   0.5  |                30    |             65    |            180   |          18    |               57.3 |            2398 |
| post_intubation_collapse       |   1    |                30    |             65    |            180   |          18    |               57.3 |            1200 |
| post_intubation_collapse       |   2    |                30    |             65    |            180   |          18    |               57.3 |             601 |
| post_intubation_collapse       |   5    |                30    |             65    |            180   |          18    |               57.3 |             241 |
| post_intubation_collapse       |  10    |                30    |             65    |            180   |          18    |               57.3 |             121 |

Interpretation: clinically relevant outputs remain stable across dt from 0.25 to 10 seconds. Residual differences occur mainly in capped/unsafe display states or very small auto-PEEP values.

## Tests added or modified

Added:
- `test_silent_chest_etco2_pitfall_is_reproduced_without_hidden_paco2_cap`
- `test_excess_external_peep_produces_hemodynamic_penalty`
- `test_expected_direction_smoke_checks_for_key_scenarios`

Modified:
- release-integrity cache test now ignores runtime `__pycache__`/`.pytest_cache` artifacts created by pytest itself.

Current test result:
- `12 passed`

## Remaining limitations before submission

1. `post_intubation_collapse` remains intentionally capped/unsafe for most of the simulation:
   - auto-PEEP 30
   - Pplat 65
   - Ppeak 90
   - PaCO2 180
   - MAP 18
   This can be defended only if described as an unsafe arrest-threshold scenario with capped display values.

2. The manuscript still requires a full rewrite from v1.2/v1.4 language to v1.5 outputs.

3. Figures must be regenerated and inserted from:
   - `figures/v1_5_remediation_snapshot/`

4. The Results section should not claim external validation. Use:
   - internal verification
   - face-validity against known physiology
   - educational surrogate
   - non-predictive model

## Submission status

Do not submit yet.

Next required step: rewrite manuscript Results, Methods calibration description, limitations, and figure captions around v1.5.
