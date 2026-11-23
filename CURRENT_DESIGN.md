# Current Design — MyoSense sEMG Prototype

*DH803 Wearable Health Technologies · Design status: single-channel bench prototype · Reviewed 7 November 2026*

This file is the source of truth for the **current** design. Older assignment and proposal files record earlier design stages and may list superseded hardware. See `share/README.md` before relying on them.

## Project question

Can a low-cost, two-channel surface-EMG prototype show a lifter how the measured activation of a chosen target muscle changes relative to a second muscle during a standardized exercise or attentional-focus cue?

The prototype measures electrical activity and displays **activation amplitude relative to each muscle's own reference contraction**. It does not decide whether form is correct, measure muscle force, or predict growth.

## Design status

| Item | Current status | Decision / qualification |
|---|---|---|
| Use case | Defined | Two muscles: a target/primary site and a comparison/helper site; display both readings and an exploratory within-person index. |
| MCU | In hand; exact vendor/revision unverified | Photo shows a generic ESP32-S3 N16R8 development board with two USB-C ports and exposed GPIO labels. It is not the DFRobot FireBeetle in the earlier plan. GPIO4/GPIO5 appear available; verify the board pinout and ADC capability before use. |
| Battery | In hand; interface unverified | User confirms one 3.7 V, 1000 mAh Li-ion cell. Connector, polarity, protection circuit and exact chemistry/charge limits are not yet confirmed. |
| Charger | In hand; identification provisional | Photo appears to show an HW-373 / TP4056 1S USB-C charger board with B+/B− and OUT+/OUT− pads. Verify protection and current configuration. It charges/protects a cell; it does not boost or regulate the output to 5 V. |
| EMG front end | One module in hand; exact model/revision to confirm | Green board appears to be a single-channel Muscle BioAmp board, likely Candy; visible pads include VCC/GND/OUT and IN+/IN−/REF. Confirm exact label/specification before applying power. |
| Boost converter | In hand | HW-106: 3.7 V → 5 V step-up with a USB-A output socket, fixed ~5 V, 100 µF 16 V input cap. This is the missing regulated 5 V path; verify output with a meter before connecting the dev board. |
| Near-term demonstration | Sequential one-channel site measurements | Move the same sensor/electrode set between two accessible sites and record/calibrate each separately. This demonstrates site-specific signal and reference workflows, not simultaneous two-muscle activity. |
| Electrodes/retention | One dry-metal three-contact strap in hand | Ten20 conductive paste is available. The 22 Nov exercise report describes separate Ag/AgCl gel contacts at ~20 mm spacing; do not conflate that measurement setup with the current strap unless confirmed. |
| Second EMG channel | Not yet available | Two simultaneous muscle sites need a second compatible front end and three additional contacts. |
| Exercise | Pilot report and supplemental readings available | `MyoSense_Report.pdf` describes three participants per exercise group. It tabulates L1/L2 for lat pulldown and C1–C3 for chest press; slide-derived L3 values added to the CSV at the user's direction are flagged because the slides originally called them illustrative. Numeric loads, tempo, ROM and some placement/MVC metadata remain unspecified. |
| Feedback metric | Defined with limitation | Per-channel RMS/MAV and % of that channel's own MVC reference. Show both channels. Any ratio is exploratory descriptive feedback only, not a validated force, compensation, or “co-activation” metric. |
| Fatigue | Deferred / exploratory | Candy and BisCute have fixed 72–720 Hz bandpass. Do not claim conventional 20–450 Hz acquisition or validated median-frequency fatigue using those modules. Revisit with a suitable configurable front end and controlled fatigue protocol. |
| Rep counting / IMU | Future option | MVP can test envelope-based segmentation. Add an IMU only if movement-phase/rep validation requires it. |

## Current board and power interface

- The pictured controller is an ESP32-S3 N16R8 development board, not the previously planned FireBeetle. It has USB-C programming/power ports and exposed `3V3`, `5V`, `GND`, GPIO4 and GPIO5 labels; exact manufacturer and pin map remain unverified.
- GPIO4 and GPIO5 are candidate ADC1 inputs on ESP32-S3. Confirm the board pinout and sensor output range before wiring. Never apply more than the ESP32-S3 ADC input range (3.3 V) to an analog pin.
- The pictured HW-373 board appears to charge a single-cell Li-ion battery through its TP4056-type circuit. `OUT+ / OUT−` are battery-range outputs, roughly 3.0–4.2 V, not regulated 5 V. Do not connect the battery or charger output directly to the ESP32 board's `5V` pin.
- The pictured **HW-106** board supplies the missing regulated 5 V: cell/charger `OUT+ / OUT−` → HW-106 `VIN+ / VIN−`, and its USB-A socket feeds the ESP32 through a USB-A-to-USB-C cable. Fixed output, no adjustment. Meter it before connecting.
- Full power chain: `1000 mAh cell → HW-373 (charge + protection) → HW-106 (3.7 V→5 V) → USB-C → ESP32-S3 → 3V3 → EMG module`.
- For USB bench testing, power the ESP32 board from the laptop with no person connected to electrodes. For body recording, use the battery/boost chain with no charger or USB-to-computer cable attached.
- Confirm battery chemistry, polarity and charger current compatibility. Check polarity with a multimeter before connecting; do not charge a damaged cell or charge while electrodes are attached to a person.
- Optional telemetry: a two-resistor divider from HW-373 `OUT+` to GPIO1 lets the BLE firmware report pack voltage and an estimated charge percentage. Wiring, meter checks and the approximation limits are in `HARDWARE_BATTERY.md`. It is not required for the EMG measurement, and the build currently running on the board has no battery tap.

## Sensor decision

### Module currently in hand: Muscle BioAmp (likely Candy; verify)

- The photographed green board appears to have one channel, with `VCC`, `GND`, `OUT` and `IN+`, `IN−`, `REF` labels. Verify the exact product/revision before wiring; the Candy figures below apply only if that identification is confirmed.
- If confirmed as Candy, vendor-listed input begins at 3.3 V, gain is ×2420 and analog bandpass is fixed at 72–720 Hz. One board is one channel.
- First connection, after confirming model: VCC to 3V3, GND to common ground, OUT to GPIO4/ADC1. Keep the ESP32 analog input within range; inspect the output before attaching electrodes to a person.

### Budget activation MVP: Muscle BioAmp Candy

- One channel per board; specified input range begins at 3.3 V, suitable in principle for a verified ESP32-S3 board's 3.3 V rail.
- Vendor specification: fixed gain ×2420 and fixed 72–720 Hz bandpass.
- An assembled SMD module; its kit listing includes a cable, jumpers and three gel electrodes, plus a Muscle BioAmp Band while the free-accessory offer remains available.
- Two boards cost about ₹1,598 at the reviewed vendor price. Confirm the kit contents and current stock before ordering.
- **Trade-off:** useful for an activation-envelope/%MVC prototype, but its fixed bandpass is not the conventional 20–450 Hz band. It limits comparability with conventional sEMG spectral studies and makes median-frequency fatigue a poor MVP claim. At a 720 Hz upper passband, target approximately 2 ksample/s/channel, then verify actual acquisition timing and clipping.

### Lowest cost, more assembly: Muscle BioAmp BisCute

- Same vendor-stated 3.3–30 V input and 72–720 Hz bandpass as Candy; one channel.
- About ₹599 each (about ₹1,198 for two); this is a **DIY through-hole soldering kit** with resistors, capacitors and a quad op-amp. It is not a ready-assembled module.
- Its accessory kit (cable, electrodes, band, jumpers) is listed as free while stock lasts. Confirm before ordering.
- Choose only if the team wants the assembly work and can inspect/test both builds before human trials.

### Broader analysis option: BioAmp EXG Pill

- One channel per board. The manufacturer says the 2025 edition supports 3.3/5 V and allows gain and band-pass configuration; the default is EEG/EOG, so it must be configured for EMG.
- The Explorer Pack contains two assembled sensor boards and more gel electrodes/accessories, but costs substantially more (Robu listing reviewed around ₹5,252).
- Buy only an **assembled 2025 3.3/5 V revision**. Do not accidentally order the Robu listing marked **UNASSEMBLED**. Ask the seller to confirm revision and output range.
- This is the preferred option if the project needs a configurable analog band for a future broader-band EMG/frequency-analysis study and the configuration is documented and verified.

## Interpretation rules

1. Calculate RMS/MAV from the **same sensor configuration and processing** for the exercise task and that muscle's MVC reference.
2. `percent_of_reference = 100 × task amplitude / reference amplitude`. State the reference contraction posture/type. A standard isometric MVC is a practical reference but is not necessarily matched to dynamic exercise muscle length or contraction type.
3. Report the target and comparison muscle percentages separately. A project-defined comparison ratio may be shown as exploratory descriptive feedback only; it does **not** estimate relative force or prove that a helper muscle “took over.”
4. Do not cap results at 100% automatically. A task reading above the MVC reference can indicate that the reference was not maximal, the posture differed, or measurement conditions changed.
5. Standardize, photograph/mark placement, provide familiarization, take 3–5 consistent brief reference contractions with adequate rest, and repeat the same placement/processing. Follow CEDE guidance and obtain instructor/ethics approval for human data collection.
6. With one sensor, measure sites **sequentially**: document each site, reposition the same sensor/electrode set, and collect a site-specific reference. The MVC/reference for each site normalizes to approximately 100% by definition. Raw MVC amplitudes between different sites are affected by anatomy, placement and tissue and must not be presented as relative force.

## Exercise selection

Choose exercises as test cases, not as universal diagnoses of bad technique. Start with one stable, low-to-moderate-load exercise and a clearly specified cue. Candidate pairs with relevant EMG literature are listed in `share/EMG_WEARABLE_FROM_SCRATCH.md`. The pilot should document exercise variant, load, range of motion, tempo, cue, electrode placement and rest. Do not infer “correct form” solely from a two-muscle amplitude ratio.

## Source-of-truth order

1. `CURRENT_DESIGN.md` — current design decisions and unresolved choices.
2. `share/EMG_WEARABLE_FROM_SCRATCH.md` and its PDF — from-scratch explanation and protocol.
3. `DATASETS_AND_HARDWARE.md` — procurement, wiring, software and safety details.
4. `STUDY_GUIDE.md` and `MUSCLE_ACTIVATION_AND_EXERCISE_SELECTION.md` — theory study notes.
5. `MyoSense_A2_DH803.docx`, `MyoSense_A2_DH803.pptx`, and `EMG Project Communications Subsystem Plan.pdf` — earlier course drafts; their SEN0240/older ESP32 bill of materials is superseded and must not be treated as the current purchase list.

## Firmware and first data

- `firmware/team_mvc/team_mvc.ino` — the working ESP32-S3 sketch: samples GPIO4 at 2 kHz, removes the window mean, computes a 100 ms RMS, captures an MVC reference on `C`, and prints `Mean`, `RMS` and `Activation %` at 10 Hz.
- `tools/emg_capture.py` — fixed-duration capture with CSV log and a statistics summary; parses both CSV and `Mean/RMS/Activation` output.
- `tools/emg_plot.py` — replays a captured CSV as a plot.
- `firmware/README.md` — step-by-step laptop hookup, Arduino IDE settings, what a valid trace looks like, and the first rest/contraction protocol.

## Next-session handoff

Start with `PROTOTYPE_BENCH_TEST_HANDOFF.md`. It records the photographed hardware, bench wiring, safe power sequence, verification checks and the missing items before two-channel/body testing.
