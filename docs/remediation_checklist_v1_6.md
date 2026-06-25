# Remediation Checklist — v1.6.0-submission-candidate

Follow-up to the v1.4 and v1.5 independent audits. This round closes the
remaining engineering and manuscript-consistency items.

## Fixed in v1.6

- [x] External-PEEP hemodynamic penalty gated to non-spontaneous patients
      (spontaneous triggering patients are no longer penalized for applied PEEP
      up to intrinsic PEEP). No change to the eight published scenario outputs.
- [x] README "Test" section corrected: it previously listed five non-existent
      test scripts; it now invokes `pytest` and the real test modules.
- [x] Version aligned to v1.6.0-submission-candidate across VERSION,
      pyproject.toml, README, engine docstring, and the integrity test.
- [x] Test modules, output directory, and figure directory renamed to v1.6.
- [x] Release-integrity compiled-artifact test restored to a meaningful check
      (flags loose .pyc/.pyo outside runtime __pycache__) instead of a no-op.
- [x] CHANGELOG updated, including a retroactive note on the v1.5
      high-RR scenario recalibration that had not been logged.
- [x] Manuscript Results and Methods rewritten against the v1.6 engine; the
      stale "v1.2-alpha" framing and the incorrect claim that high respiratory
      rate improves CO2 clearance were removed.
- [x] Figure captions rewritten (Figure 3 CO2 trade-off corrected; Figure 5
      reframed around a genuinely low EtCO2 rather than a "dissociation").
- [x] Explicit disclosure added (Results and Figure 4/Figure 5 captions) that
      post-intubation collapse reports display-capped unsafe values, not
      measured or predicted physiology.

## Still required before journal submission (author actions)

- [ ] Replace figure image files with journal-formatted versions if required by
      the target journal (current PNGs are regenerated from v1.6 outputs).
- [ ] Decide final journal target (e.g. Advances in Simulation, BMC Medical
      Education, JOSS, SoftwareX).
- [ ] Create the public GitHub release.
- [ ] Mint the Zenodo DOI and insert the repository URL/DOI into the manuscript
      Software Availability section.

## Known, intentionally retained design choices

- post_intubation_collapse remains fully saturated against the unsafe-physiology
  display caps. This is intentional: the scenario is an "off-the-cliff"
  teaching configuration, is flagged unsafe, and is now explicitly disclosed as
  capped in the manuscript and figure captions.
