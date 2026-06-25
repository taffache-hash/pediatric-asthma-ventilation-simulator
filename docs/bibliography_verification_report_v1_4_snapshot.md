# Bibliography verification report v1.2-alpha

Date: 2026-06-23  
Version: 1.2.0-alpha

## Purpose

This version was created specifically to reduce pre-submission bibliographic risk. Earlier versions used source anchors and placeholder references. In v1.2-alpha, each key source has been converted into a verified reference registry with PMID/PMCID/DOI fields where available.

## Main correction

The manuscript now uses **verified numeric references** instead of loose source anchors. The language was also tightened:

- **validation** is reserved for future external/clinical validation;
- current testing is called **internal verification**;
- drug effects are described as **scenario modifiers**, not validated PK/PD responses;
- ketamine is framed as plausible but uncertain;
- magnesium is framed as evidence-supported but heterogeneous and delayed;
- pediatric IMV literature is used as context, not equation calibration.

## Evidence hierarchy

### Stronger anchors

- R02 Stather & Stewart 2005: core severe-asthma ventilation physiology.
- R03 Leatherman 2015: modern severe-asthma ventilation review.
- R04 Tuxen & Lane 1987 and R05 Leatherman et al. 2004: respiratory pattern/expiratory time and dynamic hyperinflation.
- R10 Smith et al. 2020 and R11 Smith et al. 2023: modern pediatric NIV/IMV epidemiology.
- R12 Nievas & Anand 2013: pediatric stepwise PICU therapy review.

### Moderate/cautious anchors

- R07, R08, R09: pediatric IMV historical/retrospective data.
- R13-R15: ketamine evidence. These support a cautious educational scenario, not routine efficacy claims.
- R16-R17: magnesium evidence. These support dosing ranges and delayed/uncertain effect modeling.

### Non-peer-reviewed / guidance anchors

- R18 Children's Mercy pathway.
- R19 Canadian Paediatric Society statement.

These should remain in background or supplemental material if the target journal prefers peer-reviewed references only.

## Bibliographic risk remaining

1. Some physiological thresholds are extrapolated from adult/mixed severe-asthma literature.
2. Pediatric mechanical ventilation studies are mostly older and retrospective.
3. Ketamine evidence is mixed; the Cochrane review prevents any strong efficacy claim.
4. The simulator is internally verified but not externally validated.
5. Exact journal formatting will still need adaptation to target journal style.

## Files added

```text
data/verified_references_v1_2_alpha.csv
data/parameter_source_traceability_v1_2_alpha.csv
manuscript/references_v1_2_alpha.md
manuscript/reference_claim_map_v1_2_alpha.md
manuscript/full_manuscript_draft_v1_2_alpha.md
docs/bibliography_verification_report_v1_2_alpha.md
docs/reference_claim_audit_v1_2_alpha.md
docs/pre_submission_reference_checklist_v1_2_alpha.md
tests/test_reference_registry_v1_2_alpha.py
```
