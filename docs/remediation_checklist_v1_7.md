# Remediation Checklist — v1.7.0-submission-candidate

Follow-up to the v1.4/v1.5 audits and the v1.6 remediation. This release applies
a literature-grounded physiology revision (four coupled engine changes) and
re-aligns the manuscript with the new engine outputs.

## Physiology revision (v1.7)

- [x] pH via acute Henderson-Hasselbalch (shared acute_ph function); linear
      slope removed. Resolves over-acidification at high PaCO2.
- [x] Safe-scenario acceptance test made internally consistent (pH floor derived
      from the PaCO2 ceiling through acute_ph).
- [x] Auto-PEEP via single-compartment dynamic-hyperinflation steady state
      VT*r/(1-r); high-RR auto-PEEP now ~13 cmH2O (literature-consistent).
- [x] Flow-limitation loss recalibrated so PaCO2 stays physiologic with the
      larger auto-PEEP; high-RR auto-PEEP test threshold tightened to >9.0.
- [x] End-tidal CO2 via the Enghoff alveolar dead-space relationship; opaque
      etco2_signal_fraction replaced by an explicit vq_mismatch_dead_space_fraction.

## Manuscript / package re-alignment (v1.7)

- [x] Version bumped and aligned across all metadata and the integrity test.
- [x] Outputs, figures, validation table and dt/PEEP sweeps regenerated.
- [x] Abstract, Methods model description, Results, Limitations and figure
      captions rewritten against the v1.7 outputs.
- [x] CHANGELOG documents all four changes with literature rationale.

## Still required before journal submission (author actions)

- [ ] Choose the target journal (e.g. Advances in Simulation, BMC Medical
      Education, JOSS, SoftwareX).
- [ ] Public GitHub release; mint Zenodo DOI; insert repository URL/DOI into the
      manuscript Software Availability section.
- [ ] Optional: replace figure PNGs with journal-formatted versions if required.

## Known, intentionally retained design choices

- post_intubation_collapse remains saturated against the unsafe-physiology
  display caps (intended off-the-cliff teaching configuration, flagged unsafe and
  explicitly disclosed as capped in the manuscript and captions).
- Several modulating coefficients (heterogeneity factor, flow-limitation loss,
  alveolar dead-space scaling) are educational calibration values, labelled as
  such in code and Limitations; they are not measured constants.
