# DH803 Project — EMG Wearable for Muscle-Activation Awareness in Strength Training

Project workspace for **Jeet Gurbani (23B0023)**, B.Tech Aerospace, IIT Bombay
Course: **DH803 — Wearable Health Technologies** (Instructor: Nirmal Punjabi, PhD)

---

## The idea in one paragraph

This project is a planned **two-channel surface-EMG (sEMG) biofeedback prototype** for strength-training exercises. The current physical prototype parts are one generic ESP32-S3 N16R8 development board, one 3.7 V 1000 mAh Li-ion cell, a HW-373/TP4056-style charger board, an **HW-106 3.7 V → 5 V boost** with USB-A output, one single-channel Muscle BioAmp-style EMG board (likely Candy; verify model), and one three-contact strap/lead set. Near-term, this supports a one-channel bench test and a **sequential site-by-site MVC/reference demonstration** after the board/module and safe power path are verified. It cannot measure two sites simultaneously; two-channel testing needs another front end/contact set. The project measures EMG amplitude relative to a stated reference; it does **not** directly measure muscle force, decide whether form is correct, or predict growth. See `CURRENT_DESIGN.md` and `PROTOTYPE_BENCH_TEST_HANDOFF.md` for current status and startup steps.

---

## Repository contents

| Area | Files |
|---|---|
| Design and protocol | `CURRENT_DESIGN.md`, `PROJECT_PLAN.md`, `PROTOTYPE_BENCH_TEST_HANDOFF.md`, `DATASETS_AND_HARDWARE.md`, `HARDWARE_BATTERY.md` |
| Theory and evidence | `STUDY_GUIDE.md`, `LITERATURE_REVIEW.md`, `MUSCLE_ACTIVATION_AND_EXERCISE_SELECTION.md`, `REFERENCES_INDEX.md` |
| Results | `PRELIMINARY_RESULTS.md`, `data/form_comparison_2026-11-22.csv`, `MyoSense_final_results.pptx` |
| Firmware | `firmware/team_mvc/team_mvc.ino` (USB) and `firmware/team_ble/team_ble.ino` (BLE + battery) |
| App and analysis | `app/meter.html`, `tools/emg_ble.py`, `tools/emg_capture.py`, `tools/plot_session.py`, `tools/test_meter_logic.py` |
| Enclosure prototype | `ENCLOSURE.md`, STL variants, CAD generators, previews and `viewer.html` |
| Share guide | `share/EMG_WEARABLE_FROM_SCRATCH.md` + PDF, figures and citation map |

The local workspace also contains excluded publisher PDFs, course material, scratch files and
raw exercise footage. See `PUBLISHING.md` for exactly what is public and why.

---

## How to use this

1. **For a new reader, start with `share/EMG_WEARABLE_FROM_SCRATCH.pdf`** (or its Markdown source). It explains the project from physiology through the prototype and its limitations.
2. **Read `PROTOTYPE_BENCH_TEST_HANDOFF.md`** to identify the photographed components and run the first safe bench test; use `CURRENT_DESIGN.md` for the live design status.
2b. **To get a signal the same day**, follow `firmware/README.md`: upload `firmware/team_mvc/team_mvc.ino`, then run `python tools/emg_capture.py --seconds 10`.
2c. **For the wireless version**, upload `firmware/team_ble/team_ble.ino` and open `app/meter.html` (see `app/README.md`) — a live activation bar, target zone, rep counter and CSV export.
3. **Use `PROJECT_PLAN.md` and `DATASETS_AND_HARDWARE.md`** for work plan, wiring and sensor comparison.
4. **Use `LITERATURE_REVIEW.md` and `REFERENCES_INDEX.md`** for the reading queue and source map. Selected open-access local PDFs are copied into `share/references/`; the full local archive remains in `references/pdfs/`.
5. `MyoSense_A2_DH803.docx`, `MyoSense_A2_DH803.pptx` and `EMG Project Communications Subsystem Plan.pdf` are earlier course drafts. Their DFRobot SEN0240/generic ESP32 BOM is **superseded**; use the current design file instead.

---

## Course-context quick facts (from the slides)

- **Grading:** Assignments 25% · Quiz/Mid-sem 40% · **Course Project 35% (2 presentations + 1 report)**.
- **Building blocks taught:** Sample/Signal → Interface (sampling, materials, contamination) → Transducer/Sensor → Signal Processing (A/D, filtering, amplification) → Communication (BLE/NFC/ANT+) → Data processing & visualization → Battery management → Data transfer & networks.
- **Signal taxonomy:** Chemical · Physical · **Electrical (ECG, EMG, EEG, EOG)** · Radiative.
- **Project scopes allowed:** whole device (system-level), an individual block, literature analysis, data/signal analysis, or device analysis. **Your idea can be a system-level design + signal-analysis project**, which fits your skills.
- **Design process taught:** (1) meet end-user/domain expert, (2) define objective from literature meta-review, (3) systems/surrogate thinking, (4) design each block with selection criteria + comparison to literature.
- **Key references named in class:** Kaniusas *Biomedical Signals and Sensors I*; Sazonov & Neuman *Wearable Sensors* (2020); Godfrey & Stuart *Digital Health* (2021).

---

## Status and licence

This is a **student prototype for a course project**, not a medical device. It is released under the MIT Licence (see `LICENSE`). Published content is limited to the firmware, tools and documentation; third-party papers are cited by DOI rather than redistributed — see `PUBLISHING.md`.

---

## The main interpretation caution

EMG amplitude is an activation-related electrical measure, **not a direct force reading**. MVC normalization gives an amplitude relative to a reference contraction; even normalized values cannot establish absolute force sharing between different muscles. Higher acute EMG also does not guarantee more growth. Frame the product as measuring and testing feedback on activation-related signals, not as certifying form or promising hypertrophy. See CEDE [1] in `share/SHARE_REFERENCES.md`.
