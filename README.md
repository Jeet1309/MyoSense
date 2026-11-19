# DH803 Project — EMG Wearable for Muscle-Activation Awareness in Strength Training

Project workspace for **Jeet Gurbani (23B0023)**, B.Tech Aerospace, IIT Bombay
Course: **DH803 — Wearable Health Technologies** (Instructor: Nirmal Punjabi, PhD)

---

## The idea in one paragraph

This project is a planned **two-channel surface-EMG (sEMG) biofeedback prototype** for strength-training exercises. The current physical prototype parts are one generic ESP32-S3 N16R8 development board, one 3.7 V 1000 mAh Li-ion cell, a HW-373/TP4056-style charger board, an **HW-106 3.7 V → 5 V boost** with USB-A output, one single-channel Muscle BioAmp-style EMG board (likely Candy; verify model), and one three-contact strap/lead set. Near-term, this supports a one-channel bench test and a **sequential site-by-site MVC/reference demonstration** after the board/module and safe power path are verified. It cannot measure two sites simultaneously; two-channel testing needs another front end/contact set. The project measures EMG amplitude relative to a stated reference; it does **not** directly measure muscle force, decide whether form is correct, or predict growth. See `CURRENT_DESIGN.md` and `PROTOTYPE_BENCH_TEST_HANDOFF.md` for current status and startup steps.

---

## What is in this folder

```
project/
├─ README.md                     ← you are here (orientation + how to use)
├─ STUDY_GUIDE.md                ← 12-module course-aligned curriculum (start here to learn)
├─ PROJECT_PLAN.md               ← full plan: what to build, how to proceed, workstreams, timeline
├─ CURRENT_DESIGN.md             ← source of truth for current hardware status, pending decisions and interpretation limits
├─ PROTOTYPE_BENCH_TEST_HANDOFF.md ← next-session hardware identification, safe power and one-channel test procedure
├─ HARDWARE_BATTERY.md            ← optional battery-level and charging wiring (resistor divider, GPIO1)
├─ firmware/                      ← team_mvc.ino (USB serial) and team_ble.ino (Bluetooth LE) + firmware/README.md (step-by-step)
├─ tools/                         ← emg_capture.py (serial log), emg_ble.py (BLE log), emg_plot.py (replay) and plot_session.py (session plots + stats)
├─ app/                           ← meter.html: browser app that turns the BLE stream into a live activation meter
├─ MUSCLE_ACTIVATION_AND_EXERCISE_SELECTION.md ← deep-dive on M9/M10: how the body makes EMG, how it varies by exercise, and the 2-muscle %MVC ratio
├─ share/                         ← share pack: from-scratch guide (Markdown + PDF), citation map and curated local references
├─ LITERATURE_REVIEW.md          ← annotated reading list (what to read and why), grouped by theme
├─ DATASETS_AND_HARDWARE.md      ← public datasets, sensor boards, software toolchain, standards
├─ RECONCILIATION_AND_ADDITIONS.md ← review of your research report: corrections + additions
├─ REFERENCES_INDEX.md           ← table mapping every downloaded file → citation
├─ biomech/                       ← ME 6114 Joint Biomechanics slides (S05E01–S05E08) — supports %MVC metric
├─ R1.pdf / R2.pdf               ← wrist kinematics & functional ROM (validation template)
├─ Wrist_ROM_Mini_Literature_Review_and_Pilot_Study.pdf  ← wrist-IMU pilot (validation template)
├─ Wrist joint project at a glance.pdf / Team8_stage2_report.pdf ← team wrist-IMU docs
└─ references/
   ├─ pdfs/                      ← 34 papers (PDF where open-access, full-text .txt where not)
   └─ _download_manifest.json
```

> **Your own report `my deep-research-report.md` is kept here too** — I reviewed it in `RECONCILIATION_AND_ADDITIONS.md` (what to keep, what to fix, what was missing).

> **This folder is not the published repo.** Large, copyrighted or unrelated folders (`references/pdfs/`, `share/references/*.pdf`, `biomech/`, `videos/`, `figures/`) are excluded via `.gitignore`. See `PUBLISHING.md` for what is shared on GitHub and why.

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
