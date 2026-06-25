# Release audit v1.5.0-remediation-snapshot

Purpose: clean submission-oriented snapshot after the v1.3 physiology-fix branch.

## Included
- Current physiology engine only.
- Current YAML scenarios only.
- v1.3 physiology validation outputs.
- Current regression tests for physiology and release hygiene.
- Essential manuscript/reference materials retained with explicit labels where regeneration is still needed.

## Removed from this snapshot
- Historical v0.4-v1.2 output folders.
- Legacy tests hard-coded to older version numbers.
- `__pycache__`, `.pyc`, `.pytest_cache` and other generated cache artifacts.
- Duplicate application README files from older development snapshots.

## Known remaining work before actual journal submission
- Regenerate paper figures from the v1.4/v1.3-fixed engine.
- Update manuscript Results and Figure captions after figure regeneration.
- Replace placeholder software availability fields with real GitHub release URL and Zenodo DOI.
- Complete final independent reference spot-check.
