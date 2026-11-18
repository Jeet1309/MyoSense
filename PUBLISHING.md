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
| `share/SHARE_REFERENCES.md` | 6 KB | Every citation with DOI, plus the local source map |
| `share/README.md` | 2 KB | What the share pack is |
| `CURRENT_DESIGN.md` | 11 KB | Live decision record: part status, open questions, interpretation rules |
| `PROJECT_PLAN.md` | 16 KB | Scope, evidence, protocol, phases, risks, validation |
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
| `app/meter.html` | 16 KB | Browser app: live activation meter, target zone, rep counter, CSV export |
| `app/README.md` | 3 KB | How to run the app and why Web Bluetooth needs HTTPS/localhost |
| `my deep-research-report.md` | 11 KB | Original draft, kept for provenance (its errors are corrected in `RECONCILIATION_AND_ADDITIONS.md`) |
| `.gitignore` | 1 KB | Keeps the repo clean |

Total published: roughly **1 MB** — mostly the PDF.

---

## 2. What stays local, and why

| Path | Size | Reason | If a reader needs it |
|---|---|---|---|
| `references/pdfs/` | 102 MB | Publisher PDFs; licences do not permit public re-hosting | DOIs are in `SHARE_REFERENCES.md` and `REFERENCES_INDEX.md` |
| `share/references/*.pdf` | 20 MB | Same problem — the curated bundle is for local reading | Same DOIs; most are open access at the publisher |
| `biomech/` | 19 MB | Instructor's lecture slides (ME 6114), not ours to publish | Link to the course instead |
| `videos/` | 31 MB | Generated HyperFrames project: renders, caches, logs | Not needed to understand the device |
| `figures/` | 6.6 MB | Older figures plus team member photographs (personal data) | Not needed; the two new diagrams are in `share/figures/` |
| `MyoSense_A2_DH803.docx` / `.pptx` | 7 MB | Superseded graded submission, out of date technically | History is summarised in `CURRENT_DESIGN.md` |
| `EMG Project Communications Subsystem Plan.pdf` | 75 KB | Superseded proposal (SEN0240 / generic ESP32 BOM) | Summarised in `REFERENCES_INDEX.md` |
| `R1.pdf`, `R2.pdf`, `Wrist*`, `Team8_stage2_report.pdf`, `writs_readings_ss.pdf` | 5 MB | Belong to a separate wrist-ROM project | Unrelated |
| `me6114_project_imu.zip` | 44 KB | Another course's submission | Unrelated |
| Hardware photos (`WhatsApp Image*.jpeg`, `boosto .jpeg`) | 0.4 MB | Personal photos; not needed once the build is documented | — |

`.gitignore` enforces all of the above, so an accidental `git add .` cannot publish them.

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
- If you later want the documents under CC BY 4.0 instead, add `LICENSE-docs` and state the split in `README.md`.
- The `README.md` states that this is a student prototype, not a medical device. Keep that sentence if the text is edited.

---

## 5. Commands

The repo is not yet initialised here. From `D:\SEM -1\dh\project`:

```bash
# one-time setup
git init
git branch -M main
git remote add origin git@github.com:Jeet1309/MyoSense.git

# stage and review what will actually be published
git add .
git status --short

# commit
git commit -m "MyoSense: single-channel sEMG wearable prototype, guide and firmware"

# push
git push -u origin main
```

If the remote already has commits (for example a README created by GitHub), pull first:

```bash
git pull --rebase origin main
git push -u origin main
```

### Verify before pushing

`git status --short` should list roughly 20 files. If you see `references/`, `biomech/`, `videos/`, a `.pptx`, or a `.jpeg`, the ignore rules are not being applied — stop and check `.gitignore`.

```bash
# confirm nothing large slipped in
git ls-files -s | wc -l
du -sh .git
```

---

## 6. Recommended repository layout on the landing page

The existing `README.md` already works as the landing page. Consider adding three lines at the top so a reader knows where to start:

```
Read `share/EMG_WEARABLE_FROM_SCRATCH.pdf` first.
Current hardware state: `CURRENT_DESIGN.md`.
To rebuild the firmware: `firmware/README.md`.
```

---

## 7. Reading order for someone new

1. `share/EMG_WEARABLE_FROM_SCRATCH.pdf` — the whole project in one document
2. `CURRENT_DESIGN.md` — what exists, what is still open
3. `firmware/README.md` — how to reproduce the measurement
4. `PROJECT_PLAN.md` — protocol, phases, risks
5. `STUDY_GUIDE.md` — the theory, if they want to go deeper
6. `LITERATURE_REVIEW.md` — the evidence base
