# Figure captions — v1.8.1

Main figures are reduced to five per reviewer guidance; the remaining figures are
provided as Supplementary Figures S1-S4. PNG file names are given in brackets so
the mapping is unambiguous.

## Main figures

### Figure 1 (primary). Same-patient respiratory-rate sweep, severe obstruction [Figure_1_RR_Sweep.png]

In a fixed severely obstructed reference patient, the set respiratory rate is swept from 6 to 40 breaths/min with all other inputs held constant. The PaCO2 surrogate is U-shaped with an interior nadir near 22 breaths/min (approximately 77 mmHg): raising the rate improves the CO2 surrogate only until expiratory time becomes limiting, after which dynamic hyperinflation worsens both mechanics and gas exchange. Over the same sweep the auto-PEEP and plateau-pressure surrogates rise monotonically and the MAP surrogate falls monotonically. Central internal-verification figure.

### Figure 2. Auto-PEEP surrogate, controlled hypoventilation versus high respiratory rate [Figure_2_AutoPEEP_Controlled_vs_HighRR.png]

The controlled-hypoventilation scenario uses a lower rate and longer expiratory time; the high-rate scenario shortens expiratory time relative to the time constant. The auto-PEEP surrogate rises from approximately 3.7 to approximately 13 cmH2O when expiratory emptying is incomplete.

### Figure 3. PaCO2 surrogate, controlled hypoventilation versus high respiratory rate [Figure_3_PaCO2_Controlled_vs_HighRR.png]

A directional PaCO2 surrogate, not a blood-gas prediction. The high-rate strategy does not improve the surrogate relative to controlled hypoventilation (approximately 92 versus 75 mmHg), because shortening expiratory time wastes ventilation through dynamic hyperinflation and flow limitation.

### Figure 4. PaCO2 and EtCO2 surrogates in the silent chest scenario [Figure_4_PaCO2_EtCO2_SilentChest.png]

Near-silent severe obstruction with a severe ventilation-perfusion mismatch yields a low EtCO2 surrogate (approximately 14 mmHg) while the PaCO2 surrogate stays high and non-capped (approximately 105 mmHg). The EtCO2 surrogate is computed from the Enghoff alveolar dead-space fraction, so the gradient reflects an explicit alveolar dead space and illustrates why a low EtCO2 can be falsely reassuring.

### Figure 5. Counterbalancing PEEP: trigger-work unloading versus hemodynamic cost [Figure_5_PEEP_Titration.png]

In a spontaneously breathing patient with fixed intrinsic auto-PEEP, applied PEEP is swept. The inspiratory trigger-work surrogate falls toward zero as applied PEEP approaches intrinsic PEEP (dashed line) with little MAP penalty; above intrinsic PEEP, a progressive MAP penalty appears. Demonstrates the simplified counterbalancing-PEEP teaching approximation and its guardrail.

## Supplementary figures

### Supplementary Figure S1. Dynamic hyperinflation proxy, controlled hypoventilation versus high respiratory rate [Figure_S1_Hyperinflation_Proxy.png]

Trapped volume plus tidal volume normalized to body weight. The dashed line is a teaching threshold, not a validated pediatric cutoff.

### Supplementary Figure S2. Unsafe-threshold demonstration: MAP surrogate during post-intubation collapse [Figure_S2_MAP_PostIntubation_Collapse.png]

This configuration reaches the engine's unsafe-physiology thresholds; the MAP surrogate sits at its display floor (18 mmHg) with the unsafe-physiology flag. Capped values are deliberate ceilings indicating an unsafe configuration, not a hemodynamic prediction.

### Supplementary Figure S3. Peak-to-plateau gap under controlled hypoventilation [Figure_S3_PIP_Pplat_Gap.png]

Peak and plateau pressure surrogates over time. The wide gap between a high resistive peak pressure and an acceptable plateau is the characteristic obstructive pattern and a key bedside distinction.

### Supplementary Figure S4. Local one-at-a-time sensitivity exploration (severe-obstruction reference) [Figure_S4_AutoPEEP_Sensitivity.png and Figure_S4_PaCO2_Sensitivity.png]

One-at-a-time perturbation of inspiratory resistance, compliance, heterogeneity, tidal volume, respiratory rate, and I:E ratio. The auto-PEEP surrogate is most sensitive to respiratory rate, inspiratory resistance, and I:E ratio; the PaCO2 surrogate is most sensitive to tidal volume and respiratory rate. Dashed line marks the baseline.

### Supplementary Figure S5. Model architecture (state diagram) [Figure_S5_Model_Architecture.png]

Schematic of the deterministic pathway from validated scenario inputs through the mechanics chain (expiratory time constant, expiratory residual fraction, trapped volume, auto-PEEP, total PEEP, plateau-pressure surrogate), the gas-exchange surrogates (alveolar ventilation to PaCO2, pH, and EtCO2), and the hemodynamic surrogate (MAP with the counterbalancing-PEEP teaching approximation), to CSV and figure outputs. All quantities are directional surrogates, not clinical predictions.
