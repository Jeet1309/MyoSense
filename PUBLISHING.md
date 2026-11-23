# Publishing this project to GitHub

Target repository: `git@github.com:Jeet1309/MyoSense.git`

This file records what is published, what is deliberately kept local, and why. The rule applied throughout: **ship everything a reader needs to understand and rebuild the project; ship nothing that is someone else's copyrighted work, personal data, or generated build output.**

---

## 1. What gets published

| Path | Size | Why it belongs in the repo |
|---|---|---|
| `README.md` | 6 KB | Landing page: what the project is, how to navigate |
| `share/EMG_WEARABLE_FROM_SCRATCH.md` | 40 KB | The main document — physiology through firmware, calibration, testing, two-channel plan |
| `share/EMG_WEARABLE_FROM_SCRATCH.pdf` | 0.5 MB | Same content, rendered for reading and sharing |
| `share/figures/system_architecture.png` | — | Signal chain diagram |
| `share/figures/power_tree.png` | — | Power and charging diagram |
| `figures/myosense_web_photo_circuit_schematic.png` | 0.6 MB | Photo-annotated acquisition, power and battery-divider schematic; this single figure is an explicit exception to the local-only `figures/` rule |
| `tools/build_web_photo_circuit_schematic.py` | — | Rebuilds that schematic from manufacturer/product image URLs; photo credits are printed on the image |
| `share/SHARE_REFERENCES.md` | 6 KB | Every citation with DOI, plus the local source map |
| `share/README.md` | 2 KB | What the share pack is |
| `CURRENT_DESIGN.md` | 11 KB | Live decision record: part status, open questions, interpretation rules |
| `PROJECT_PLAN.md` | 16 KB | Scope, evidence, protocol, phases, risks, validation |
| `PRELIMINARY_RESULTS.md` | — | Raw observations, descriptive means, caveats and next data to collect |
| `data/exercise_pairs_2026-11-22.csv` | — | 24 reported site/condition readings from the six participant experiments only |
| `MyoSense_Report.pdf` | 1.2 MB | Authoritative 15-page report, uploaded unchanged |
| `MyoSense_final_results.pptx` | 8.2 MB | Separate 20-slide presentation deck; left unchanged as requested |
| `ENCLOSURE.md` | — | Enclosure prototype inventory and safety/fit caveats |
| `box_with_fin*.stl`, `box_with_plate.stl` | — | Printable enclosure iterations |
| `make_box_stl*.py`, `draw_*views.py`, `preview*.py`, `render3d.py`, `build_viewer.py` | — | CAD generation and preview source |
| `box_*.png`, `plate_views*.png`, `viewer.html` | — | CAD previews and interactive STL viewer |
| `DATASETS_AND_HARDWARE.md` | 18 KB | Datasets, hardware trade-offs, wiring, toolchain, safety |
| `STUDY_GUIDE.md` | 22 KB | 12-module course-aligned curriculum |
| `LITERATURE_REVIEW.md` | 21 KB | Annotated reading list, tiered by importance |
| `MUSCLE_ACTIVATION_AND_EXERCISE_SELECTION.md` | 16 KB | Deep-dive on muscle physiology and exercise choices |
| `RECONCILIATION_AND_ADDITIONS.md` | 9 KB | Corrections applied to the original research draft |
| `REFERENCES_INDEX.md` | 15 KB | File-to-citation map for the local archive |
| `PROTOTYPE_BENCH_TEST_HANDOFF.md` | 11 KB | Hardware identification, safe power sequence, bench procedure |
| `HARDWARE_BATTERY.md` | 9 KB | Optional battery-level / charging wiring, with meter checks and failure modes |
| `firmware/team_mvc/team_mvc.ino` | 4 KB | The working acquisition sketch |
| `firmware/team_ble/team_ble.ino` | 7 KB | Same acquisition, plus the BLE stream |
| `firmware/README.md` | 5 KB | Upload instructions, IDE settings, expected output, troubleshooting |
| `tools/emg_capture.py` | 8 KB | Logs the serial stream to CSV with a statistics summary |
| `tools/emg_plot.py` | 10 KB | Plots a captured log |
| `tools/emg_ble.py` | 8 KB | Logs the BLE stream to CSV with a statistics summary |
| `tools/plot_session.py` | 9 KB | Plots a session (activation with target band, RMS, battery) and prints its statistics |
| `tools/test_meter_logic.py` | 6 KB | Headless checks for the browser page logic |
| `tools/test_ble_and_results.py` | — | BLE payload and CSV plotting regression tests |
| `tools/update_results_deck.py` | — | Rebuilds results slides from the photo-schematic source deck |
| `app/meter.html` | 16 KB | Browser app: live activation meter, target zone, rep counter, CSV export |
| `app/README.md` | 3 KB | How to run the app and why Web Bluetooth needs HTTPS/localhost |
| `my deep-research-report.md` | 11 KB | Original draft, kept for provenance (its errors are corrected in `RECONCILIATION_AND_ADDITIONS.md`) |
| `.gitignore` | 1 KB | Keeps the repo clean |

The updated release includes the final presentation and enclosure design files. Raw exercise
videos are not published as separate files; the presentation contains selected demo clips used
in the slides. Machine-specific G-code is also kept local.

---

## 2. What stays local, and why

| Path | Size | Reason | If a reader needs it |
|---|---|---|---|
| `references/pdfs/` | 102 MB | Publisher PDFs; licences do not permit public re-hosting | DOIs are in `SHARE_REFERENCES.md` and `REFERENCES_INDEX.md` |
| `share/references/*.pdf` | 20 MB | Same problem — the curated bundle is for local reading | Same DOIs; most are open access at the publisher |
| `biomech/` | 19 MB | Instructor's lecture slides (ME 6114), not ours to publish | Link to the course instead |
| `videos/` | 31 MB | Generated HyperFrames project: renders, caches, logs | Not needed to understand the device |
| Root `*.mp4` exercise clips | 74 MB | Raw workout footage; avoids publishing duplicate/unedited personal video | Selected demonstration clips are embedded in the final deck |
| `*.gcode` | 1.9 MB | Printer/profile-specific generated output | Re-slice the STL for the target printer |
| `Myosense_final.pptx` | 8.9 MB | Original input deck; superseded by `MyoSense_final_results.pptx` | Use the updated results deck |
| `MyoSense_final_with_circuit_schematic.pptx` / `MyoSense_final_web_photo_schematic.pptx` | 8.2 / 8.6 MB | Intermediate source decks; the latest photo schematic and results are in `MyoSense_final_results.pptx` | Use the updated results deck |
| `figures/` other than `myosense_web_photo_circuit_schematic.png` | 6.6 MB | Older figures plus team member photographs (personal data) | The new circuit schematic is the only published exception |
| `MyoSense_A2_DH803.docx` / `.pptx` | 7 MB | Superseded graded submission, out of date technically | History is summarised in `CURRENT_DESIGN.md` |
| `EMG Project Communications Subsystem Plan.pdf` | 75 KB | Superseded proposal (SEN0240 / generic ESP32 BOM) | Summarised in `REFERENCES_INDEX.md` |
| `R1.pdf`, `R2.pdf`, `Wrist*`, `Team8_stage2_report.pdf`, `writs_readings_ss.pdf` | 5 MB | Belong to a separate wrist-ROM project | Unrelated |
| `me6114_project_imu.zip` | 44 KB | Another course's submission | Unrelated |
| Hardware photos (`WhatsApp Image*.jpeg`, `boosto .jpeg`) | 0.4 MB | Personal photos; not needed once the build is documented | — |

`.gitignore` enforces the local-footage, G-code and scratch exclusions, so an accidental `git add .`
will not publish those files.

---

## 3. About the bundled research PDFs

`share/references/` currently holds 11 journal articles so the guide can be read offline. **Do not publish that folder.** Two of the papers (Calatayud 2016, Schoenfeld 2018) are paywalled; the rest are open access but re-hosting is still governed by each licence.

`SHARE_REFERENCES.md` already carries a DOI for every citation, which is the correct way for a public repo to point at them.

---

## 4. Licensing

The repository is released under the **MIT License** (`LICENSE`), covering the firmware, the host tools and the written documentation.

Notes:

- MIT is a permissive software licence; applying it to the prose documents is unusual but harmless and keeps the repository simple.
- Third-party material is **not** covered and is not redistributed: cited papers belong to their authors and publishers, and their DOIs are listed in `SHARE_REFERENCES.md`.
- The photo-annotated schematic and final slide deck contain product photographs credited on the schematic and selected demonstration clips; the project licence does not grant rights to reuse those embedded third-party assets.
- `MyoSense_Report.pdf` contains team identifiers and participant electrode-placement photographs. It is included unchanged at the user's request; keep participant/team permission in mind before further redistribution.
- The report lists three participants per exercise group. Its lat-pulldown tables contain L1/L2; supporting CSV/notes add the user-confirmed L3 values from unchanged slides 13–14. The original slide footers label those readouts illustrative, so the supplementary L3 provenance is explicitly flagged and the PDF/deck are not silently rewritten.
- If you later want the documents under CC BY 4.0 instead, add `LICENSE-docs` and state the split in `README.md`.
- The `README.md` states that this is a student prototype, not a medical device. Keep that sentence if the text is edited.

---

## 5. Commands

The working repository is initialised and tracks `origin/main`. To publish a new update from
`D:\SEM -1\dh\project`:

```bash
# stage and review what will actually be published
git add .
git status --short

# commit
git commit -m "Describe the update"

# push
git push origin main
```

If the remote already has commits (for example a README created by GitHub), pull first:

```bash
git pull --rebase origin main
git push -u origin main
```

### Verify before pushing

`git status --short` may list the result deck `MyoSense_final_results.pptx` and the enclosure
STLs/previews. It should **not** list publisher PDFs, course slides, the original source decks,
standalone `.mp4` footage, `.gcode`, or personal photos.

```powershell
git ls-files | Measure-Object
Get-ChildItem -File | Sort-Object Length -Descending | Select-Object -First 10 Name,Length
```

---

## 6. Recommended repository layout on the landing page

The `README.md` landing page links the project overview, current design, preliminary results,
firmware, app and enclosure files.

---

## 7. Reading order for someone new

1. `share/EMG_WEARABLE_FROM_SCRATCH.pdf` — the whole project in one document
2. `CURRENT_DESIGN.md` — what exists, what is still open
3. `firmware/README.md` — how to reproduce the measurement
4. `PROJECT_PLAN.md` — protocol, phases, risks
5. `STUDY_GUIDE.md` — the theory, if they want to go deeper
6. `LITERATURE_REVIEW.md` — the evidence base
