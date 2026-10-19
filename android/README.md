# Android application — closed testing

**State (19 October 2026):** A screenshot supplied by the maintainer from Google Play Console shows the Pediatric Status Asthmaticus Ventilation Simulator in the **closed-testing `alpha` track**. Release **`1.0.2-educational`**, **versionCode `4`** (App Bundle), is reported as **available on Google Play to eligible testers**, with rollout **100% of the closed-testing track** across **178 selected countries/regions**. The last displayed update is **18 October 2026, 14:02** (screenshot-local display time; timezone not established). The screenshot verifies the visible Console status but does **not** establish a publicly accessible store listing, tester opt-in URL, package ID, Android source code, install success, or quantitative scientific parity.

**Contents of this directory:** This is a documentation entry point, **not** an Android project or a distributable build. No actual Kotlin/Java, Gradle, Android manifest, embedded Python bridge, APK or AAB was available in the linked GitHub account or accompanying project files at the time of this commit. Do not mistake this directory for a buildable app.

## Where to find the software

- Python scientific core: [`../src/`](../src/), tagged as scientific version 1.8.1.
- Streamlit teaching UI: [`../app/streamlit_app.py`](../app/streamlit_app.py).
- Android: **Google Play closed test; invitation and verified opt-in URL required.** There is no verified public Android install link in this repository yet.

The developer can obtain the **actual tester opt-in URL** from Play Console > Test and release > Testing > Closed testing > Manage track > Testers, then copy the shareable link. The app may not be searchable on Google Play before open testing/production release. Only enrolled testers can install through the closed-test link.

## Importing the Android source

The Android project produced for the already uploaded Play build should be preserved as a separate, reviewable component (inside this directory or in a separately linked Android repository). Before any source upload, confirm its **package ID, versionCode/versionName, commit SHA, toolchain, and scientific-core source revision** against the real Play Console artifact. Do not add a reconstructed or unrelated starter app and describe it as the submitted build.

The Android interface must retain the original, unchanged scientific Python equations, report model limits and unsafe-physiology flags, and stay clearly educational/non-validated rather than offer patient-specific decisions. See [distribution and verification checklist](../docs/ANDROID_DISTRIBUTION.md).

Never commit keystores, signing credentials, Play service-account JSON, personal tester data, or release secrets. An AAB uploaded to Play Console is not the same as an installable APK; neither is currently available here.
