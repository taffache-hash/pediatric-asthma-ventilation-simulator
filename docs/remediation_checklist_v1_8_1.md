# Remediation checklist — v1.8.1 (response to the v1.8 severe review)

Verdict received: major revision — defensible as an educational simulator with
internal verification, not as a validated physiological model. All mandatory
changes were implemented. Engine logic and golden values are unchanged; this is a
manuscript/presentation revision (patch release).

## Mandatory changes before submission

| # | Required change | Resolution | Where |
| --- | --- | --- | --- |
| 1 | Move post-intubation collapse out of the main results table | Already out of the quantitative table; reinforced as a standalone "Unsafe-threshold demonstration" and as Supplementary Figure S2 | manuscript Results |
| 2 | Always label PaCO2, EtCO2, MAP (and pressures, pH) as surrogates | Surrogate labeling reinforced in abstract, methods, results, captions; explicit "directional surrogates, not blood-gas predictions" | throughout manuscript and captions |
| 3 | Add a "calibrated coefficients, not literature constants" table | New Table 1 (compact classification L/E/C/D) and Supplementary Table S2 (full line-referenced list) | manuscript Methods; `supplementary_v1_8.md` |
| 4 | Reduce main figures to 4-5 | Main figures reduced to five (RR sweep; auto-PEEP safe vs high RR; PaCO2 safe vs high RR; silent chest PaCO2/EtCO2; PEEP titration); the rest moved to Supplementary Figures S1-S4 | `figure_captions_v1_8.md` |
| 5 | Add "No patient data were used for calibration or validation." | Added verbatim in Abstract, Methods, and Limitations | manuscript |
| 6 | Separate verification / validation / calibration explicitly | New Methods paragraph defining all three; verification done, calibration heuristic-only, validation not performed | manuscript Methods |

## Severe critiques addressed (framing)

| Critique | Resolution |
| --- | --- |
| Model "too clean" / not predictive | New Discussion paragraph listing the real-world features deliberately omitted (regional heterogeneity, secretions, airway closure/derecruitment, asynchrony, tube/leak, unstable V/Q); smooth curves stated to be a teaching abstraction |
| Collapse is a code-capped crash test | Reported only as an unsafe-threshold demonstration, never as a simulation result |
| PaCO2/pH too deterministic | Stated as directional surrogates; coefficient classes exposed in Table 1 / S2 |
| Passive PEEP may underestimate auto-PEEP effect | Disclosed explicitly as a known simplification and planned refinement (Limitations) |
| Ketamine only supplementary | Therapy modifiers confined to supplementary illustration; no pharmacological-simulation claim |
| High-VT scenario is pressure-exposure, not gas-trapping | Relabeled in the scenario message and in the manuscript as a pressure-exposure scenario |

## Discussion sharpened to three surgical statements

- The model passed internal invariant and monotonicity testing.
- It did not undergo external (clinical) validation; no patient data were used for calibration or validation.
- Numerical outputs are directional surrogates and must not be interpreted clinically.

## Verification status after changes

- pytest: 26 passed (engine and golden values unchanged).
- Scenarios re-run; figures and sensitivity regenerated.
- Release-integrity version constant updated to 1.8.1.
