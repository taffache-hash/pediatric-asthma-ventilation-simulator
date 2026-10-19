# Android distribution and scientific provenance checklist

**Last updated:** 19 October 2026  
**Project:** Pediatric Status Asthmaticus Ventilation Simulator  
**Scientific core:** 1.8.1 (GitHub tag `v1.8.1-post1`; the post-release tag does not define the Android app version)  
**Baseline source revision inspected:** `4a3c5a680dc8a781cbfe69c87f9c5a2657304e5f`  
**Android test status:** maintainer reports an active Google Play closed-testing track; not independently verified.

## Distribution status — verified vs pending

| Item | Status | Required evidence before publishing a link or binary |
| --- | --- | --- |
| Python core + Streamlit code | Present in this repository | Source under `src/` and `app/` |
| Android application in Play Console | Reported by maintainer | Confirm the package ID, track, versionCode, versionName and exact AAB |
| Play tester opt-in link | Not provided or verified | Paste the **exact** link copied from Play Console > Closed testing > Manage track > Testers |
| Android source matching submitted AAB | Not available in connected GitHub repositories | Import real source and record commit + source checksums |
| GitHub pre-release and APK | Not created | Build independently reproducible, test installation, check intended publicity, then publish only if appropriate |
| General-public Play listing | Not released | Add official Store URL only after it is genuinely available |

A closed test is **not** a general-public release. Sharing the opt-in link on a public README does not enroll readers or make them eligible for the test. For invite-only testing, prefer providing the link directly to enrolled testers rather than advertising it as a public install link.

## Integration procedure

1. Retrieve the **real** Android project used for the existing Play Console AAB; do not generate a new imitation of the current Play build.
2. Pin the scientific source to an immutable commit/tag and record its complete vendor manifest / SHA-256 checksums in the Android project. Keep scientific version and Android version separately identifiable.
3. Audit the original Python engine and package data for numerical equivalence across all nine built-in scenarios, parameter overrides, model limitations and warnings; compare Android results with reference Python results. A passing Android build alone is not evidence of physiological equivalence.
4. Add Android code under `android/` or link to a genuine dedicated repository. Preserve `src/`, `app/`, `tests/`, manuscripts, original releases and version metadata without changing physiological code.
5. Run Android build/tests and a physical-device or emulator test. Record actual build results, package ID, versionCode, signing certificate fingerprint (public certificate only), and which Play artifact corresponds to the source revision.
6. Add the **verified** tester opt-in URL to `android/README.md` and the root README only after confirming its correct destination; identify it explicitly as restricted closed testing. Do not claim public Play availability.
7. If an APK is intentionally shared on GitHub, publish it as a clearly labeled **pre-release asset** (not as scientific core v1.8.1) with its SHA-256 and relevant version. GitHub release assets on a public repository are public and can bypass Play's closed-test enrollment: do not upload a restricted-test APK by accident. Never upload production signing keys or secrets.

## Play Console tester-link retrieval

In the app's Play Console: **Test and release → Testing → Closed testing → Manage track → Testers → copy shareable link**. Verify the resulting URL manually. Testers must be included in the track's selected email list or Google Group and follow the opt-in process; new links may take time to become available.

## Open items

- Exact package identifier and Play Console opt-in URL.
- Android source repository or project archive for the deployed build.
- Built APK (if GitHub pre-release distribution is desired), its version and checksums.
- Android test and scientific parity evidence.

## Scope and safety

The simulator is a transparent, non-clinically validated **educational** model of ventilated pediatric status asthmaticus. It is not a medical device, not validated for patient-specific predictions and not a tool for selecting ventilator settings at the bedside. The Android interface must maintain these limitations and model warnings.
