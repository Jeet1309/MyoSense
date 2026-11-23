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
| Results and circuit | Authoritative `MyoSense_Report.pdf`, `PRELIMINARY_RESULTS.md`, `data/exercise_pairs_2026-11-22.csv` (only the six participant experiments), the unchanged presentation deck and photo-annotated schematic |
| Firmware | `firmware/team_mvc/team_mvc.ino` (USB) and `firmware/team_ble/team_ble.ino` (BLE + battery) |
| App and analysis | `app/meter.html`, `tools/emg_ble.py`, `tools/emg_capture.py`, `tools/plot_session.py`, and BLE/report tests |
| Enclosure prototype | `ENCLOSURE.md`, STL variants, CAD generators, previews and `viewer.html` |
| Share guide | `share/EMG_WEARABLE_FROM_SCRATCH.md` + PDF, figures and citation map |

The local workspace also contains excluded publisher PDFs, course material, scratch files and
raw exercise footage. See `PUBLISHING.md` for exactly what is public and why.

## Start here

| If you want to… | Open / run |
|---|---|
| Read the authoritative report | [`MyoSense_Report.pdf`](MyoSense_Report.pdf) (15 pages). The existing `MyoSense_final_results.pptx` deck is unchanged and still needs its results slide reconciled; deck revision is the next task. |
| See the six exercise experiments | [`PRELIMINARY_RESULTS.md`](PRELIMINARY_RESULTS.md) and the 24-reading [`CSV`](data/exercise_pairs_2026-11-22.csv) |
| Build the USB serial version | [`firmware/team_mvc/team_mvc.ino`](firmware/team_mvc/team_mvc.ino); setup in [`firmware/README.md`](firmware/README.md) |
| Build the BLE + battery-telemetry version | [`firmware/team_ble/team_ble.ino`](firmware/team_ble/team_ble.ino); battery divider details in [`HARDWARE_BATTERY.md`](HARDWARE_BATTERY.md) |
| Use the live BLE meter | Serve the repo with `python -m http.server 8000`, open `http://localhost:8000/app/meter.html` in Chrome/Edge, then connect to `MyoSense-EMG` |
| Plot a session CSV | `python tools/plot_session.py path\to\session.csv --save-png session.png` |
| Inspect or print the enclosure | [`ENCLOSURE.md`](ENCLOSURE.md), [`viewer.html`](viewer.html), and the STL files in the repo root |

## Current system facts

- One EMG front-end is available, so muscle sites are measured **sequentially**, not simultaneously.
- Firmware targets 2 kHz sampling and sends RMS/activation features over BLE at about 10 Hz. The previous BLE build measured 1888 ADC reads/s; the optimized notify code is compiled but needs to be reflashed and measured on the board.
- Battery telemetry uses two equal 68 kΩ resistors from HW-373 `OUT+` to `OUT−`, midpoint to GPIO1 (ADC1), and common ESP32 ground; firmware divider scale is 2.0. Battery percentage and charging are estimates.
- Calibration is rest baseline → maximal effort → maximal verification. The activation value is a personal reference-normalized EMG amplitude, **not force or a form score**.
- Battery percentage is a voltage-based estimate; charging status is inferred. Do not treat either as fuel-gauge accuracy.
- The exercise results dataset contains only six participants/experiments: three lat pulldowns and three bench presses, each with two muscle-site readings and good/bad values. The lat L3 values are sourced from the deck per the user's identification. Bench/serial BLE trial captures are not included in these exercise results.

## Preliminary readings (22 Nov 2026)

| Site | Reported good-form mean | Reported bad-form mean | Difference (good − bad) |
|---|---:|---:|---:|
| Lat pulldown / latissimus | 72.67 % | 58.67 % | +14.00 percentage points |
| Lat pulldown / biceps | 33.33 % | 56.00 % | −22.67 percentage points |
| Chest press / pectoralis | 65.00 % | 57.67 % | +7.33 percentage points |
| Chest press / triceps | 52.67 % | 67.00 % | −14.33 percentage points |

The PDF's lat tables show two pairs; L3 (72/59 latissimus and 40/71 biceps) is added from the
unchanged slides per the user's identification of participant 3. The six experiments are exactly
the three lat-pulldown and three bench-press participants. Other logger/trial CSVs are excluded.
The report PDF and presentation deck are not modified. This is not a validated form score or force comparison. See
[`PRELIMINARY_RESULTS.md`](PRELIMINARY_RESULTS.md) for provenance and
[`data/exercise_pairs_2026-11-22.csv`](data/exercise_pairs_2026-11-22.csv) for every reading.

---

## Quick start

**Run the BLE meter on the laptop** (board must be running `team_ble.ino`; use Chrome or Edge):

```powershell
python -m http.server 8000
```

Open `http://localhost:8000/app/meter.html`, click **Connect**, select `MyoSense-EMG`, and
calibrate in order: rest 5 s, max effort 5 s, max-effort verification 5 s. Save CSV at the end.
Only one BLE client can connect at a time.

**Plot a saved app CSV:**

```powershell
python tools/plot_session.py "path\to\myosense-session.csv" --save-png "session.png"
```

This plots 10 Hz activation, RMS envelope, battery voltage when present, and prints summary
statistics. The BLE file contains features, **not the raw 2 kHz waveform**.

**Capture USB serial data** with the board connected to the laptop (do not also connect the boost):

```powershell
python tools/emg_capture.py --port COM8 --seconds 10 --out logs\bench.csv
```

**Check the web-app and data parser logic:**

```powershell
python tools/test_meter_logic.py
python tools/test_ble_and_results.py
```

For the full technical explanation, read `share/EMG_WEARABLE_FROM_SCRATCH.pdf`. For safe wiring,
current design and protocol details, see `PROTOTYPE_BENCH_TEST_HANDOFF.md`, `CURRENT_DESIGN.md`,
`HARDWARE_BATTERY.md` and `PROJECT_PLAN.md`. Serve the repo root with the same `http.server`
command to open the interactive enclosure viewer at `http://localhost:8000/viewer.html`.

Older course drafts and publisher/course PDFs are not part of the public repository; see `PUBLISHING.md` for exclusions.

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

This is a **student prototype for a course project**, not a medical device. The code and project documentation are released under the MIT Licence (see `LICENSE`). Third-party papers are cited by DOI, not redistributed. The final presentation and schematic contain credited product photos and selected demo clips; the MIT licence does not grant reuse rights to those embedded assets. See `PUBLISHING.md`.

---

## The main interpretation caution

EMG amplitude is an activation-related electrical measure, **not a direct force reading**. MVC normalization gives an amplitude relative to a reference contraction; even normalized values cannot establish absolute force sharing between different muscles. Higher acute EMG also does not guarantee more growth. Frame the product as measuring and testing feedback on activation-related signals, not as certifying form or promising hypertrophy. See CEDE [1] in `share/SHARE_REFERENCES.md`.
