# Development and internal verification of a transparent, open-source mechanistic educational computational model for ventilatory trade-offs in pediatric status asthmaticus

## Abstract

### Background

In mechanically ventilated status asthmaticus, rapid correction of hypercapnia is not always the safest educational target. Excess respiratory rate, insufficient expiratory time, excessive tidal volume, and poorly selected external PEEP may increase dynamic hyperinflation, intrinsic PEEP, pressure exposure, and hemodynamic compromise [2-6]. Pediatric invasive ventilation for asthma is uncommon in contemporary cohorts but remains a high-risk scenario that is important for simulation-based education [7-11].

### Objective

To develop and internally verify an open-source, mechanistic educational computational model (implemented as an interactive simulator) for pediatric status asthmaticus ventilation that links expiratory time constants to gas trapping, auto-PEEP, pressure surrogates, gas-exchange surrogates, and a hemodynamic-risk surrogate. We explicitly do not aim to predict patient-specific values or to validate the model against clinical data. **No patient data were used for calibration or validation.**

### Methods

The model is a transparent lumped-parameter mechanistic model. Scenario inputs are stored as YAML files. The central pathway is expiratory time relative to the expiratory time constant, an expiratory residual fraction r = exp(-Te/tau), a single-compartment dynamic-hyperinflation trapped-volume estimate (steady state VT*r/(1-r)), an auto-PEEP surrogate, total PEEP, a plateau-pressure surrogate, effective alveolar ventilation, a PaCO2 surrogate (0.863*VCO2/alveolar ventilation), an acute Henderson-Hasselbalch pH surrogate, an end-tidal CO2 surrogate from the alveolar (Enghoff) dead-space fraction, and a mean-arterial-pressure surrogate governed by a simplified counterbalancing-PEEP teaching approximation. We distinguish verification (internal software and physiologic-invariant testing, performed), calibration (educational/heuristic only), and validation (against patient data; not performed). Internal verification comprised schema checks, release-integrity checks, physiologic-invariant and monotonicity tests, a same-patient respiratory-rate sweep, a local one-at-a-time sensitivity exploration, and a golden-value snapshot guarding against engine-manuscript drift.

### Results

The primary internal-verification result is a same-patient respiratory-rate sweep on a fixed severely obstructed reference patient: the PaCO2 surrogate was U-shaped with an interior nadir near a respiratory rate of 22 breaths/min, while the auto-PEEP and plateau-pressure surrogates rose and the mean-arterial-pressure surrogate fell monotonically; beyond the nadir, faster rates worsened the CO2 surrogate again. The teaching scenarios behaved in the expected directions: a high respiratory rate raised the auto-PEEP surrogate without improving the CO2 surrogate; applied PEEP up to intrinsic PEEP unloaded the inspiratory threshold-load surrogate with little hemodynamic cost while higher PEEP penalized the MAP surrogate; and a silent-chest configuration produced a falsely reassuring low end-tidal CO2 surrogate despite a high arterial CO2 surrogate. All findings are internal verification of directional behavior, not clinical validation, and no patient data were used.

### Conclusions

The model is a transparent educational environment for discussing pediatric status asthmaticus ventilation trade-offs. It is not clinical decision support, is not a medical device, and must not be used for patient-specific ventilator settings. It is released as an open, modifiable resource for inspection and community improvement; it has not been validated against clinical data, and any patient-facing use would require such validation.

## Introduction

Severe pediatric status asthmaticus may require intensive care and, in selected cases, invasive mechanical ventilation [1,7-11]. Contemporary database studies suggest invasive ventilation is uncommon and noninvasive use has increased, but understanding invasive obstructive physiology persists because intubated obstructive physiology can deteriorate quickly if settings worsen dynamic hyperinflation [10,11].

Once intubated, the problem is not limited to normalizing carbon dioxide. In obstructed airways, short expiratory time relative to the expiratory time constant prevents complete lung emptying before the next breath, producing gas trapping, intrinsic PEEP, increased pressure exposure, and potentially impaired venous return [2-6]. This is a clinically important teaching paradox: increasing respiratory rate or tidal volume may raise nominal minute ventilation while worsening the mechanical conditions that limit effective ventilation and compromise hemodynamics.

Bedside management requires clinician judgment, waveform interpretation, measured pressures, blood gases, and continuous reassessment. The purpose of this project is narrower: a transparent, inspectable, open-source educational model that illustrates major directional trade-offs in ventilated pediatric obstructive physiology. We describe the model and report its internal verification; we make no claim of clinical validity.

## Statement of need

Invasive ventilation in pediatric status asthmaticus is high-risk and comparatively rare, so trainees seldom accumulate hands-on experience with the core trade-off: shortening expiratory time to raise minute ventilation worsens dynamic hyperinflation, auto-PEEP, plateau pressure, and venous return. This mechanistic educational model provides a transparent, fully inspectable sandbox in which learners and educators can vary respiratory rate, I:E ratio, tidal volume, resistance, compliance, and PEEP and immediately see directional surrogate responses, with a same-patient respiratory-rate sweep that makes the U-shaped CO2 trade-off explicit. It is aimed at pediatric critical-care trainees, fellows, and educators. Unlike full physiological lung-mechanics packages or proprietary mannequin-based simulators, it is deliberately minimal, open source, and reproducible: every coefficient is visible, every scenario is a YAML file, and every reported number is regenerated by a single command. It is intended to complement, not replace, bedside teaching and validated training tools, and it is explicitly not a clinical or predictive instrument.

## Methods

### Verification, calibration, validation: scope of claims

We use three terms deliberately and distinctly. **Verification** means internal software and physiologic-invariant testing: that the engine computes what the equations specify and responds in the physiologically correct direction; this was performed. **Calibration** means choosing coefficient values so the teaching behavior is reasonable; here calibration is heuristic/educational only and uses no patient data. **Validation** means demonstrating agreement with measured patient data; this was not performed. Every clinical-looking output (PaCO2, EtCO2, MAP, pressures, pH) is therefore a *surrogate*: a directional educational quantity, never a measured or predicted patient value.

### Design principle

The model was designed as a mechanistic educational physiology model, not a patient-specific prediction tool. Interpretability was prioritized over complexity: a low-dimensional lumped-parameter structure, reproducible YAML scenarios, CSV outputs, and simple figures.

### Software architecture

```text
app/          Streamlit educational interface
src/          physiology engine, scenario runner, strategy comparison, figure and sensitivity generation
data/         parameter tables, source anchors, calibration constants, release manifests
docs/         model reports, safety boundary, reviewer audit, release notes
scenarios/    predefined YAML scenarios
tests/        invariant/monotonicity tests, expected-direction physiology checks, smoke tests, release checks
outputs/      generated scenario outputs
figures/      manuscript-oriented figures
manuscript/   draft manuscript, figure captions, supplementary material
```

### Core model pathway

```text
Te/tau_exp down -> incomplete expiratory emptying -> trapped volume up -> auto-PEEP up -> total PEEP/Pplat up -> MAP down
```

This mechanism is grounded in established obstructive ventilation physiology [2-6]. The expiratory time constant is computed from expiratory resistance and compliance; the expiratory residual fraction is an exponential function of Te/tau; trapped volume is the single-compartment dynamic-hyperinflation steady state (VT*r/(1-r)) updated over equivalent breaths, which removes time-step dependence; it is converted into the auto-PEEP surrogate using effective compliance and a pressure-amplification term. Plateau and peak pressure surrogates follow from PEEP, auto-PEEP, tidal volume, compliance, and resistive pressure.

### Gas-exchange and hemodynamic surrogates

Effective alveolar ventilation is reduced by dynamic dead-space expansion, obstruction, heterogeneity, occult auto-PEEP, and short Te/tau. The PaCO2 surrogate uses the standard relationship 0.863*VCO2/alveolar ventilation; the pH surrogate uses an acute Henderson-Hasselbalch relationship; the EtCO2 surrogate uses the Enghoff alveolar dead-space fraction. **These are directional surrogates, not blood-gas predictions.** The MAP surrogate is affected by baseline MAP, preload, the auto-PEEP surrogate, plateau-pressure excess, and an acidosis penalty, with external PEEP entering through a single simplified counterbalancing-PEEP teaching approximation applied identically to passive and spontaneous patients: applied PEEP up to intrinsic auto-PEEP counterbalances inspiratory threshold load without raising mean intrathoracic pressure, and only the fraction above intrinsic PEEP penalizes venous return.

### Calibrated coefficients versus literature constants

A central limitation is that several numeric coefficients are educational calibration values, not measured or literature constants. Table 1 classifies the main quantities into four classes: **L** literature-grounded structural relationship; **E** expert clinical assumption; **C** educational calibration coefficient (heuristic, tuned for teaching behavior); **D** display cap/limit. The complete, line-referenced list is in Supplementary Table S2.

**Table 1. Classification of model quantities**

| Quantity | Role | Class |
| --- | --- | --- |
| r = exp(-Te/tau); trapped = VT*r/(1-r) | dynamic-hyperinflation kernel | L |
| tau = R_exp * Crs | expiratory time constant | L |
| PaCO2 = 0.863*VCO2/VA | alveolar ventilation relationship | L |
| Acute Henderson-Hasselbalch pH (HCO3 +1/-2 mEq per 10 mmHg) | acid-base surrogate | L |
| EtCO2 = PaCO2*(1 - alveolar dead-space fraction) | Enghoff relationship | L |
| Pplat warning 30, critical ~50 cmH2O | safety zones | E |
| VT/PEEP defaults; permissive-hypercapnia stance | scenario defaults | E |
| Flow-limitation ventilation-loss terms (0.014, 0.008, 0.26) | effective-ventilation penalty | C |
| Dynamic dead-space terms (0.010, 0.06; cap 0.82*VT) | dead-space expansion | C |
| Pressure-amplification (0.10*obstruction + 0.08*het) | trapped-volume-to-auto-PEEP | C |
| Compliance penalty (0.70 slope, 0.65 cap, 0.35 floor) | hyperinflation stiffening | C |
| Occult auto-PEEP fraction (0.33, 0.18; cap 0.55) | occult trapping | C |
| MAP penalty weights (0.75*autoPEEP, 0.45*plateau excess, 0.55*excess PEEP) | hemodynamic surrogate | C |
| Acidosis MAP penalty ((7.20 - pH)*18) | acidosis effect | C |
| Trigger-work unloading factor (0.35) | spontaneous unloading | C |
| Display caps: auto-PEEP 30, Pplat 65, Ppeak 90, PaCO2 28-180, MAP 18-95 | unsafe-threshold ceilings | D |
| Therapy modifiers (albuterol, ipratropium, magnesium, ketamine, steroid) | supplementary illustration only | C |

### Internal verification

Verification included schema validation, engine sanity checks, scenario-level expected-direction physiology checks, Streamlit smoke tests, and release-integrity tests. A dedicated suite asserts that, with all other inputs fixed: higher respiratory rate under severe obstruction increases the auto-PEEP surrogate; longer expiratory time reduces it; larger tidal volume increases the plateau and hyperinflation surrogates; lower compliance increases the plateau surrogate; higher resistance increases the peak-pressure surrogate; the PaCO2 surrogate is U-shaped across a respiratory-rate sweep; time-step changes do not materially alter outputs; and applied PEEP unloads the trigger-work surrogate without a hemodynamic penalty until it exceeds intrinsic PEEP. A golden-value snapshot fixes representative outputs so the engine and reported numbers cannot drift apart. These tests verify directional behavior, internal consistency, and software integrity; they do not establish clinical validity.

## Results

### Scenario library

The package includes a severe-obstruction reference patient (used for the respiratory-rate sweep and sensitivity analysis) and teaching scenarios: controlled hypoventilation with prolonged expiratory time; high respiratory rate causing dynamic hyperinflation; excessive tidal volume as a pressure-exposure scenario; excessive external PEEP in a passive obstructed patient; counterbalancing PEEP to unload trigger work in a spontaneously breathing patient; and silent chest with a falsely reassuring low EtCO2 signal. A post-intubation collapse configuration and the therapy-modifier scenarios are provided separately as labeled demonstrations (see below and Supplementary material).

### Primary internal-verification result: same-patient respiratory-rate sweep

The central teaching claim is that, in a fixed severely obstructed patient, raising the respiratory rate improves CO2 clearance only up to a point. Holding all inputs constant and sweeping the set respiratory rate produced a U-shaped PaCO2 surrogate with an interior nadir, monotonically rising auto-PEEP and plateau surrogates, and a monotonically falling MAP surrogate (Figure 1; selected values below).

| RR (breaths/min) | Auto-PEEP surrogate (cmH2O) | Plateau surrogate (cmH2O) | PaCO2 surrogate (mmHg) | MAP surrogate (mmHg) |
| --- | --- | --- | --- | --- |
| 6  | 0.7  | 10.2 | 154.2 | 59.3 |
| 12 | 3.4  | 13.2 | 90.0  | 61.2 |
| 18 | 6.9  | 17.4 | 78.6  | 59.3 |
| 22 | 9.8  | 20.7 | 76.8 (nadir) | 57.3 |
| 28 | 14.9 | 26.6 | 81.9  | 53.1 |
| 34 | 21.2 | 34.0 | 102.8 | 45.4 |
| 40 | 29.3 | 43.3 | 180.0 (cap) | 32.5 |

A complementary I:E sweep at a fixed rate is directionally consistent (longer expiratory time lowers the auto-PEEP and PaCO2 surrogates).

### Comparative scenario behavior

Representative maxima/minima from the v1.8 outputs are summarized below. These scenarios are **illustrative comparisons**, not controlled single-variable contrasts: they differ simultaneously in resistance, compliance, respiratory rate, I:E ratio, and CO2 production, so the differences between them cannot be attributed to any single setting. The controlled, single-variable evidence for the rate trade-off is the same-patient respiratory-rate sweep above; the comparisons here illustrate distinct clinical patterns rather than prove causation. The post-intubation collapse configuration is intentionally excluded from this quantitative table because its outputs are display caps, not computed physiology; it is reported separately.

| Scenario | Auto-PEEP surrogate max (cmH2O) | Plateau surrogate max (cmH2O) | Peak surrogate max (cmH2O) | PaCO2 surrogate max (mmHg) | pH surrogate min | MAP surrogate min (mmHg) |
| --- | --- | --- | --- | --- | --- | --- |
| Controlled hypoventilation | 3.7 | 15.4 | 63.1 | 75.4 | 7.19 | 61.9 |
| High respiratory rate | 13.3 | 25.5 | 59.4 | 91.5 | 7.13 | 53.7 |
| Excessive tidal volume (pressure-exposure) | 1.7 | 31.8 | 64.7 | 33.4 | 7.46 | 67.2 |
| Excessive external PEEP (passive) | 1.4 | 23.3 | 24.0 | 56.3 | 7.28 | 54.8 |
| Spontaneous PEEP titration | 5.6 | 17.3 | 17.3 | 55.9 | 7.28 | 63.8 |
| Silent chest / EtCO2 pitfall | 4.2 | 16.2 | 19.0 | 105.4 | 7.09 | 56.0 |

The high respiratory-rate scenario illustrates a high auto-PEEP surrogate alongside a CO2 surrogate that is not improved relative to the controlled scenario, consistent with the controlled rate-sweep finding that raising rate need not improve effective ventilation when expiratory time is limiting. The retuned controlled-hypoventilation scenario shows a modest but real intrinsic-PEEP surrogate with an acceptable plateau and a wide peak-to-plateau gap (Supplementary Figure S3), the characteristic obstructive pattern. The excessive-tidal-volume scenario is explicitly a **pressure-exposure** scenario: a large tidal volume normalizes the CO2 surrogate while driving the plateau surrogate into the warning zone, with auto-PEEP staying low because expiratory time is adequate; it is not a gas-trapping demonstration. The spontaneous PEEP-titration scenario reproduces counterbalancing-PEEP unloading (Figure 5). Silent chest reproduces the falsely reassuring low-EtCO2 pitfall through the Enghoff dead-space relationship.

### Unsafe-threshold demonstration (post-intubation collapse)

A post-intubation collapse configuration is provided as a deliberate unsafe-threshold demonstration, not a quantitative result. Its auto-PEEP, plateau, peak, PaCO2, and MAP outputs reach display caps (30, 65, 90, 180 cmH2O/mmHg, and an 18 mmHg MAP floor) with explicit unsafe-physiology flags. The capped values denote only that the configuration drives the model past plausible bounds; they are deliberate ceilings, not measured or predicted physiology, and read solely as a "this configuration is unsafe" signal (Supplementary Figure S2).

### Local one-at-a-time sensitivity exploration

One-at-a-time perturbation of inspiratory resistance, compliance, heterogeneity, tidal volume, respiratory rate, and I:E ratio (Supplementary Figure S4) showed the auto-PEEP surrogate most sensitive to respiratory rate, inspiratory resistance, and I:E ratio (consistent with the Te/tau mechanism) and the PaCO2 surrogate most sensitive to tidal volume and respiratory rate. All responses were directionally consistent with the invariants.

### Parameter traceability

Each modeling choice is linked to its supporting literature and confidence level in Supplementary Table S1; the coefficient classification is in Table 1 and Supplementary Table S2.

### Figure set

Five main figures are presented: (1) the same-patient respiratory-rate sweep, primary; (2) the auto-PEEP surrogate, controlled hypoventilation versus high respiratory rate; (3) the PaCO2 surrogate, controlled hypoventilation versus high respiratory rate; (4) the PaCO2/EtCO2 dissociation in silent chest; and (5) counterbalancing-PEEP trigger-work unloading versus hemodynamic cost. Five supplementary figures (S1-S5) provide the dynamic-hyperinflation proxy, the unsafe-threshold MAP demonstration, the peak-to-plateau gap, the local sensitivity analysis, and a model-architecture state diagram.

## Discussion

This model supports teaching of obstructive ventilatory physiology in pediatric status asthmaticus. This is an educational visualization engine, not a physiological prediction model: its contribution is transparent visualization of trade-offs, not numerical prediction. Three statements bound its interpretation precisely:

- The model passed internal invariant and monotonicity testing.
- It did not undergo external (clinical) validation, and no patient data were used for calibration or validation.
- Numerical outputs are directional surrogates and must not be interpreted clinically.

The central lesson is that carbon dioxide clearance must not be read in isolation [2,3]. The same-patient respiratory-rate sweep makes this concrete: nominal minute ventilation rises with rate, but the effective CO2 surrogate improves only until expiratory time becomes limiting, after which dynamic hyperinflation worsens both mechanics and gas exchange.

Real severe pediatric asthma is far less orderly than this model: it features marked regional heterogeneity, variable secretions, intermittent airway closure and derecruitment, patient-ventilator asynchrony, tube and leak effects, and unstable ventilation-perfusion matching. The model deliberately omits these to remain interpretable; consequently its smooth curves are a teaching abstraction, not a faithful reproduction of an individual patient's trajectory.

## Limitations

First, this is a simplified lumped-parameter model and cannot represent regional airway closure, heterogeneous time constants, secretion burden, endotracheal tube resistance, patient-ventilator asynchrony, or clinician interventions with patient-specific accuracy. Second, several modulating coefficients are calibrated teaching constants rather than measured or literature constants (Table 1; Supplementary Table S2): the flow-limitation ventilation-loss terms, dynamic dead-space scaling, pressure-amplification term, compliance penalty, occult-auto-PEEP fraction, and MAP-penalty weights. Third, the external-PEEP model in the **passive** patient is intentionally simplified: applied PEEP affects the plateau and MAP surrogates through the counterbalancing teaching approximation but does not increase the modeled end-expiratory volume or auto-PEEP, whereas in a real flow-limited passive patient external PEEP above the critical closing pressure can add to trapped volume; this is a known simplification and a planned refinement. Fourth, the trapped-volume model is a single-compartment steady state, the acid-base surrogate uses acute Henderson-Hasselbalch without full renal compensation, and the EtCO2 surrogate uses the Enghoff relationship. In particular, the PaCO2 surrogate is an instantaneous steady-state function of alveolar ventilation: it omits CO2 equilibration kinetics, tissue and blood buffering, and the venous CO2 reservoir, so it conveys the direction of CO2 change with ventilation rather than its time course. This is a deliberate teaching simplification favoring transparency over physiological fidelity, and a candidate refinement (for example, a first-order CO2 equilibration time constant) for a future version. Fifth, pediatric invasive ventilation studies are limited and often retrospective or older. Sixth, **no patient data were used for calibration or validation**; accordingly this manuscript reports internal verification only, and the model must not be interpreted as clinical decision support.

## Use of AI-assisted tools

AI-assisted tools were used during software drafting, code review, documentation refinement, and manuscript language editing. All equations, scenarios, outputs, references, and claims were reviewed by the human author, who remains responsible for the accuracy, integrity, reproducibility, and interpretation of the work. AI tools were not used as authors and were not treated as primary sources.

## Software availability

Source code, scenario library, documentation, outputs, and figures are intended for public release on GitHub and archival release on Zenodo.

- Repository: https://github.com/taffache-hash/pediatric-asthma-ventilation-simulator
- Archived release: https://doi.org/10.5281/zenodo.20847206

The final URL and DOI must be inserted only after public release and must resolve to the exact version described here (v1.8.1).

## References

R01. Joseph A; Ganatra H. Status Asthmaticus in the Pediatric ICU: A Comprehensive Review of Management and Challenges. *Pediatric Reports*. 2024;16(3):644-656. PMID: 39189288; PMCID: PMC11348376; doi: 10.3390/pediatric16030054

R02. Stather DR; Stewart TE. Clinical review: Mechanical ventilation in severe asthma. *Critical Care*. 2005;9(6):581-587. PMID: 16356242; PMCID: PMC1414026; doi: 10.1186/cc3733

R03. Leatherman J. Mechanical ventilation for severe asthma. *Chest*. 2015;147(6):1671-1680. PMID: 26033128; doi: 10.1378/chest.14-1733

R04. Tuxen DV; Lane S. The effects of ventilatory pattern on hyperinflation, airway pressures, and circulation in mechanical ventilation of patients with severe air-flow obstruction. *American Review of Respiratory Disease*. 1987;136(4):872-879. PMID: 3662241; doi: 10.1164/ajrccm/136.4.872

R05. Leatherman JW; McArthur C; Shapiro RS. Effect of prolongation of expiratory time on dynamic hyperinflation in mechanically ventilated patients with severe asthma. *Critical Care Medicine*. 2004;32(7):1542-1545. PMID: 15241099; doi: 10.1097/01.CCM.0000130993.43076.20

R06. Ranieri VM; Grasso S; Fiore T; Giuliani R. Auto-positive end-expiratory pressure and dynamic hyperinflation. *Clinics in Chest Medicine*. 1996;17(3):379-394. PMID: 8875002; doi: 10.1016/S0272-5231(05)70322-1

R07. Sarnaik AP; Daphtary KM; Meert KL; Lieh-Lai MW; Heidemann SM. Pressure-controlled ventilation in children with severe status asthmaticus. *Pediatric Critical Care Medicine*. 2004;5(2):133-138. PMID: 14987342; doi: 10.1097/01.PCC.0000112374.68746.E8

R08. Wetzel RC. Pressure-support ventilation in children with severe asthma. *Critical Care Medicine*. 1996;24(9):1603-1605. PMID: 8797637; doi: 10.1097/00003246-199609000-00028

R09. Cox RG; Barker GA; Bohn DJ. Efficacy, results, and complications of mechanical ventilation in children with status asthmaticus. *Pediatric Pulmonology*. 1991;11(2):120-126. PMID: 1758729; doi: 10.1002/ppul.1950110208

R10. Smith A; Franca UL; McManus ML. Trends in the Use of Noninvasive and Invasive Ventilation for Severe Asthma. *Pediatrics*. 2020;146(4):e20200534. PMID: 32917845; doi: 10.1542/peds.2020-0534

R11. Smith MA; Dinh D; Ly NP; Ward SL; McGarry ME; Zinter MS. Changes in the Use of Invasive and Noninvasive Mechanical Ventilation in Pediatric Asthma: 2009-2019. *Annals of the American Thoracic Society*. 2023;20(2):245-253. PMID: 36315585; PMCID: PMC9989865; doi: 10.1513/AnnalsATS.202205-461OC

R12. Nievas IF; Anand KJS. Severe Acute Asthma Exacerbation in Children: A Stepwise Approach for Escalating Therapy in a Pediatric Intensive Care Unit. *Journal of Pediatric Pharmacology and Therapeutics*. 2013;18(2):88-104. PMID: 23798903; PMCID: PMC3668947; doi: 10.5863/1551-6776-18.2.88

R13. Goyal S; Agrawal A. Ketamine in status asthmaticus: A review. *Indian Journal of Critical Care Medicine*. 2013;17(3):154-161. PMID: 24082612; PMCID: PMC3777369; doi: 10.4103/0972-5229.117048

R14. Jat KR; Chawla D. Ketamine for management of acute exacerbations of asthma in children. *Cochrane Database of Systematic Reviews*. 2012;2012(11):CD009293. PMID: 23152273; PMCID: PMC6483733; doi: 10.1002/14651858.CD009293.pub2

R15. Youssef-Ahmed MZ; Silver P; Nimkoff L; Sagy M. Continuous infusion of ketamine in mechanically ventilated children with refractory bronchospasm. *Intensive Care Medicine*. 1996;22(9):972-976. PMID: 8905436; doi: 10.1007/BF02044126

R16. Johnson PN; Drury AS; Gupta N. Continuous Magnesium Sulfate Infusions for Status Asthmaticus in Children: A Systematic Review. *Frontiers in Pediatrics*. 2022;10:853574. PMID: 35391743; PMCID: PMC8983002; doi: 10.3389/fped.2022.853574

R17. Griffiths B; Kew KM. Intravenous magnesium sulfate for treating children with acute asthma in the emergency department. *Cochrane Database of Systematic Reviews*. 2016;2016(4):CD011050. PMID: 27126744; doi: 10.1002/14651858.CD011050.pub2

R18. Children's Mercy Kansas City. Asthma Management in the PICU: Asthma Clinical Practice Guideline Reference Guide. *Institutional clinical pathway*. current online version checked 2026-06-23; web resource. No PMID/DOI available; pathway/guidance source.

R19. Canadian Paediatric Society. Managing an acute asthma exacerbation in children. *Canadian Paediatric Society position statement*. 2021; web resource. No PMID/DOI available; pathway/guidance source.
