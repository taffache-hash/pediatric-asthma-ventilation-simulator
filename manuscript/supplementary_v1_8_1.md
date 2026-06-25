# Supplementary material — v1.8.1

## Supplementary Table S1. Parameter traceability

Each modeling choice is linked to supporting references and an explicit confidence level. This table is also provided machine-readable as `data/parameter_source_traceability`.

| Parameter / claim | Model use | Supporting refs | Confidence |
| --- | --- | --- | --- |
| model_kernel | Te/tau -> incomplete emptying -> trapped volume -> auto-PEEP | R02; R04; R05; R06 | high |
| ventilator_default_VT | Low VT / pressure-limited ventilation; initial VT approximately 6-8 ml/kg in severe asthma ventilation guidance | R02; R03 | moderate |
| ventilator_default_RR | Low respiratory rate to permit expiration; RR increase should shorten Te and increase trapping in obstruction | R02; R04; R05 | high |
| peep_default_and_caution | External PEEP 0-5 cmH2O default; ambivalent effect; may unload spontaneous trigger but worsen passive hyperinflation | R02; R06; R08 | moderate |
| pplat_warning | Pplat target/warning around 30 cmH2O and critical >35 cmH2O | R02; R03 | moderate |
| permissive_hypercapnia | Accept elevated PaCO2 if pH/trajectory acceptable; avoid chasing normocapnia at cost of hyperinflation | R02; R03 | high |
| VEI_proxy_threshold | VEI >20 ml/kg as high-risk educational anchor | R02; R04 | low_to_moderate |
| occult_autopeep | Measured auto-PEEP can underestimate trapped gas in noncommunicating units | R02; R06 | moderate |
| pediatric_imv_context | Pediatric intubated asthma exists but is uncommon; use simulator for rare high-risk physiology education | R07; R09; R10; R11 | high |
| pressure_control_scenario | Pressure-controlled ventilation is represented in scenario library | R07 | moderate |
| pressure_support_spontaneous_scenario | Pressure-support/PEEP titration in spontaneous obstructed children is represented cautiously | R08 | low_to_moderate |
| magnesium_effect | Delayed modest airway-resistance reduction and possible hypotension at high exposure | R12; R16; R17 | moderate |
| ketamine_effect | Gradual optional airway-resistance reduction with hemodynamic preservation; effect uncertain | R13; R14; R15 | low_to_moderate |
| steroid_effect | Minimal acute minute-to-minute bronchodilator effect; slower inflammation modifier | R01; R12 | moderate |
| picu_red_flags | Hypercapnia, persistent hypoxemia, HFNC/NIV need, altered consciousness | R18; R19 | moderate |
| etco2_paco2_gap | EtCO2 can be falsely reassuring in severe obstruction/dead-space states | R02; R03 | moderate |

## Supplementary scenarios (therapy modifiers)

The therapy-modifier scenarios (continuous albuterol, ipratropium, magnesium, ketamine, steroid) are illustrative demonstrations only. The modifiers adjust airway resistance over time as conservative signals and are NOT pharmacokinetic/pharmacodynamic models. They must not be read as predictions of therapeutic response. The ketamine demonstration (`ketamine_bronchodilation_response`) is retained in the scenario library for teaching the *gradual, non-immediate* nature of any response, with this caveat.

## Supplementary Table S2. Calibrated coefficients versus literature constants (full list)

Class key: L = literature-grounded structural relationship; E = expert clinical assumption; C = educational calibration coefficient (heuristic, tuned for teaching behavior); D = display cap/limit. Locations refer to `src/pediatric_asthma_ventilation_simulator/asthma_engine.py`.

| Quantity / coefficient | Value(s) | Role | Class |
| --- | --- | --- | --- |
| Expiratory residual fraction r = exp(-Te/tau) | structural | dynamic-hyperinflation kernel | L |
| Trapped volume = VT*r/(1-r) | structural | single-compartment steady state | L |
| Expiratory time constant tau = R_exp * Crs | structural | mechanics | L |
| Inspiratory filling 1 - exp(-Ti/tau_insp) | structural | PC/PS filling | L |
| PaCO2 = 0.863 * VCO2 / VA | 0.863 | alveolar ventilation relationship | L |
| Acute pH: HCO3 = 24 + 0.10*(PaCO2-40) or 24 - 0.20*(40-PaCO2); pH = 6.1 + log10(HCO3/(0.03*PaCO2)) | 0.10 / 0.20 | acute Henderson-Hasselbalch | L |
| EtCO2 = PaCO2 * (1 - f_alv) | structural | Enghoff dead-space relationship | L |
| Plateau warning / critical | 30 / ~50 cmH2O | safety zones | E |
| Peak-pressure risk flag | >60 cmH2O | resistive-pressure flag | E |
| Default VT / PEEP ranges; permissive hypercapnia | scenario defaults | teaching defaults | E |
| Dynamic dead-space terms | 0.010*autoPEEP, 0.010*trapped_ml_kg, 0.06*(het-1) | dead-space expansion | C |
| Dynamic dead-space cap | 0.82 * VT | upper bound | C/D |
| Flow-limitation ventilation loss | 0.014*autoPEEP, 0.008*trapped_ml_kg, 0.26*max(0,1.45-Te/tau) | effective-ventilation penalty | C |
| Flow-limitation loss cap | 0.90 | upper bound | D |
| Pressure amplification | 1 + 0.10*obstruction_index + 0.08*(het-1) | trapped-volume-to-auto-PEEP | C |
| Compliance penalty | slope 0.70, cap 0.65, floor factor 0.35 | hyperinflation stiffening | C |
| Occult auto-PEEP fraction | 0.33, 0.18; cap 0.55 | occult trapping | C |
| Inspiratory load (PC/PS) | 0.030*raw / 0.020*raw | pressure-mode load | C |
| External-PEEP penalty | 0.55 * max(PEEP - autoPEEP, 0) | counterbalancing-PEEP teaching approximation | C |
| MAP penalty weights | 0.75*autoPEEP + 0.45*max(Pplat-30,0) | hemodynamic surrogate | C |
| Acidosis MAP penalty | (7.20 - pH) * 18 | acidosis effect | C |
| Trigger-work unloading factor | 0.35 | spontaneous unloading | C |
| Barotrauma proxy combiner | max(Pplat, 2.6 * VEI); warn 30, crit 50 | risk label | C |
| Display caps | autoPEEP 30, Pplat 65, Ppeak 90, PaCO2 28-180, MAP 18-95 | unsafe-threshold ceilings | D |
| Therapy modifiers (albuterol, ipratropium, magnesium, ketamine, steroid) | various; floor 0.55 | supplementary illustration only | C |

These C-class and D-class entries are explicitly NOT validated clinical constants. They are chosen so the teaching behavior is directionally correct and bounded. No patient data were used to fit them.
