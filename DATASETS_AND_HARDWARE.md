# DATASETS, HARDWARE & TOOLCHAIN

**Current design status is maintained in `CURRENT_DESIGN.md`.** This file provides dataset guidance, the photographed ESP32-S3 prototype baseline, EMG-front-end trade-offs, connection notes and toolchain. Prices/stock are snapshots and can change.

---

## 1. Public datasets (software-first / algorithm validation)

| Dataset | What | EMG setup | Link | Good for / limitation |
|---|---|---|---|---|
| **Ninapro DB5** | Hand/wrist movement trials | Thalmic Myo armband, 16 channels, 200 Hz | https://ninapro.hevs.ch | Wearable gesture pipeline; 200 Hz is not enough to reconstruct full conventional sEMG spectrum or median-frequency fatigue |
| **Ninapro DB2** | Hand/wrist movements, more subjects | Delsys Trigno, 12 channels, 2 kHz | https://ninapro.hevs.ch | Better-bandwidth algorithm practice; not a gym-exercise/%MVC dataset |
| **Ninapro DB7** | Hand/wrist movements | Delsys Trigno, 12 channels | https://ninapro.hevs.ch | Smaller gesture-recognition trial set |
| **CapgMyo / CSL-HDEMG** | High-density hand gestures | Electrode arrays | See Geng et al. (2016) | High-density methods, not the two-channel lifting use case |
| **PhysioNet / UCI** | Mixed physiological datasets | Varies | https://physionet.org · https://archive.ics.uci.edu | Check the specific recording, sampling and labels before use |

Use public data to test filtering, feature calculations and visualizations. Do **not** claim a model trained on hand gestures validates a gym biofeedback metric. Dataset details and licences must be checked at their source.

---

## 2. Current prototype baseline

### 2.1 Controller — in hand; exact board revision to identify

The photo shows an **ESP32-S3 N16R8 development board** with two USB-C ports and exposed GPIO labels. It is not the FireBeetle board specified in the earlier planning documents. The exact manufacturer/model is not legible in the photo; identify it from the packaging, underside or purchase listing before relying on a pin map.

- The visible board labels include `3V3`, `5V`, `GND`, GPIO4 and GPIO5. GPIO4/GPIO5 are candidate ADC1 inputs on the ESP32-S3 family; check the exact board pinout.
- Logic and analog input limit are 3.3 V; never let a sensor output exceed that at an ADC pin.
- The board has no visible PH2.0 cell socket or charger. USB-C works for bench programming; a battery power path is still needed for safe body recording.
- Nominal ESP32-S3 ADC resolution is 12 bit; effective range/noise and sample rate must be bench-tested.

### 2.2 Battery, charger and boost — in hand; verify before first power-up

User confirms a **3.7 V, 1000 mAh single-cell Li-ion battery** is available. A blue board in the photo is marked `HW-373 V1.2.1 4056` and appears to be a USB-C TP4056-style charger/protection board, with `B+`, `B−`, `OUT+`, `OUT−` pads. A second blue board marked **HW-106** is a 3.7 V → 5 V boost with a USB-A output socket.

**Power chain:**

```text
USB-C charger ──► HW-373 ──► cell (B+ / B−)
                    │
                    └─ OUT+ / OUT− ──► HW-106 VIN+ / VIN−
                                          │
                                          └─ USB-A ──► USB-A-to-C ──► ESP32 USB-C
                                                                       └─ 3V3 ──► EMG
```

- Verify the cell chemistry, connector, polarity, protection circuit and charge-current rating. Check the HW-373 board revision and protection behavior before use.
- The charger output is battery-range voltage, not a regulated 5 V supply. Do **not** connect `OUT+` directly to the ESP32 board's `5V` pin.
- The HW-106 fixes that: it steps the cell voltage up to ~5 V. Meter the USB-A socket before connecting anything (expect 4.9–5.2 V). Fixed output, no trimpot.
- Because the output is a USB-A socket, the ESP32 can be powered through its own USB-C port with a cable — no soldering to the dev board.
- The HW-106 has no low-voltage cutoff of its own. Your protection depends on the HW-373 having DW01 + 8205A protection ICs — confirm that.
- USB-powered board testing is appropriate for bench work with no person attached to the electrodes. During body recordings, use battery/boost power and do not charge the cell.
- Runtime depends on BLE duty cycle, sensor current, firmware and board revision. Measure current on the assembled prototype; 1000 mAh at ~150 mA gives roughly 5–6 h in theory, less in practice.

### 2.3 EMG front ends — current unit to identify; second channel open

All modules below are single-channel; two are required for simultaneous target/comparison recording.

| Module | Approx. 1-ch / 2-ch price | Supply/output facts | Advantages | Trade-offs with this project |
|---|---:|---|---|---|
| **Muscle BioAmp Candy** — budget recommendation | ~₹799 / ~₹1,598 | 3.3–30 V input; gain ×2420; fixed 72–720 Hz bandpass | Assembled; EMG-specific; kit listing may include cable, jumpers, 3 gel electrodes and a Muscle Band | Non-standard narrower/lower-shifted band vs conventional 20–450 Hz; poor basis for conventional median-frequency fatigue; accessories free only while stock lasts |
| **Muscle BioAmp BisCute** — lowest price | ~₹599 / ~₹1,198 | 3.3–30 V input; gain ×2420; fixed 72–720 Hz | Low-cost, open DIY design; listed accessories may include cable/electrodes/band/jumpers | DIY through-hole kit: solder resistors, capacitors and quad op-amp; assembly/testing workload |
| **BioAmp EXG Pill, 2025 3.3/5 V revision** | ~₹2,638 each; assembled Explorer Pack ~₹5,252 at Robu listing checked | Configurable gain/bandpass; default EEG/EOG; configure for EMG | Broader flexible biopotential platform and more electrode/filter options | Verify exact **2025 revision**, assembled status and analog configuration. Avoid listing titled **UNASSEMBLED** unless intentionally building SMD circuitry. Costlier |
| **DFRobot Gravity SEN0240** | ~₹5,073 each at Robu listing checked | 3.3–5.5 V supply; 0–3.0 V output, 1.5 V reference; integrated conditioning; metal dry electrode | Ready module and reusable dry electrode | Two channels ~₹10k; verify ADC output range and full acquisition behavior |
| **MyoWare 2.0** | ~₹4,599 each at MG Super Labs | 3.1–5 V; raw, rectified and envelope outputs | Established snap connector ecosystem; convenient output choices | Two channels cost ~₹9.2k; output choice affects sampling/features |
| **EMG Muscle Sensor V3.0 clone** | ~₹999–1,400 each (seller dependent) | Listings describe dual supply, typically ±9 V (minimum ±3.5 V) | Cheap and may include electrodes/cable | Not a direct single-cell ESP32-S3 module; would need an additional dual-rail supply and output verification. Not recommended for a low-complexity build |
| **Generic AD8232 module** | Usually low cost | ECG-oriented biopotential front end | Easy to find and useful for learning analog biopotentials | Not a ready sEMG solution; filtering/gain/output need redesign and validation. Not the recommended project sensor |

**Selection guidance:** The photographed one-channel board is likely Candy, but verify its model and revision before assuming specifications. If confirmed, it is a low-friction option for activation amplitude/%MVC with its fixed 72–720 Hz band. A second matching module is still needed for the two-channel concept. BisCute is a DIY alternative; EXG Pill is the more configurable option if a wider passband is required. Update the final BOM in `CURRENT_DESIGN.md` after verification.

### 2.4 Wiring concept for the photographed Muscle BioAmp and ESP32-S3

The green photographed board appears to be a single-channel Muscle BioAmp board, likely Candy, with `VCC`, `GND`, `OUT`, `IN+`, `IN−`, and `REF`. Confirm its exact model/revision first. If it is Candy and its printed pin labels agree:

| Sensor pad | ESP32-S3 development board |
|---|---|
| VCC | 3V3 (if exact module specifications confirm 3.3 V operation) |
| GND | GND (common reference) |
| OUT | GPIO4 / ADC1 for first-channel bench test; GPIO5 / ADC1 for a second module, after verifying pin map |
| IN+, IN−, REF | Three electrode contacts, wired by module labels/manual; do not infer from lead colors |

Do not wire a 5 V sensor output into an ESP32-S3 ADC input. Check sensor identity, output bias/range and clipping before attaching electrodes to a person. Use USB only for disconnected-electrode bench checks. For body recording, keep the whole subject-connected system battery-powered and disconnect charger/programming cables; use BLE for telemetry.

### 2.5 Electrodes, bands and straps

- **Gel Ag/AgCl electrodes:** adhesive hydrogel pads; generally the best first choice for repeatable signal quality. The two-Candy accessory kits list three pads per channel, subject to included-accessory stock. Two simultaneous channels need six contacts (IN+, IN−, REF per channel).
- **Muscle BioAmp Band:** reusable, one channel, stretchable 13 in to about 26 in circumference. Suitable for arms and many thighs, not a torso/chest circumference. Dry metal contacts need conductive electrode gel/Ten20 between metal and skin. This is separate from the Brain BioAmp Band included in the EXG Explorer Pack.
- **Torso:** use adhesive gel electrodes secured with a long wide belt (the reviewed Mulligan belt is about 2 in × 6.5 ft) or make a purpose-designed chest carrier. A belt retains electrodes; it is not itself an electrode.
- **Skin prep:** alcohol cleaning is usually sufficient to start with adhesive hydrogel pads. NuPrep is mildly abrasive skin-prep gel and is wiped off. Ten20/electrode gel is conductive coupling gel left at the dry-electrode/skin interface. They are different products; both are only needed for dry-band workflows (NuPrep is optional).
- Confirm actual kit contents before buying; accessory bundles can change with stock.

---

## 3. Acquisition and signal-processing choices

### 3.1 General conventional sEMG pipeline (for a suitable broadband front end)

```text
Raw sEMG (analog front end; adequate anti-alias filter)
  → sample at 2 ksample/s/channel (or justified rate for actual bandwidth)
  → inspect DC offset, clipping, noise and mains components
  → optional digital band-pass/notch chosen for the analog front end and task
  → rectify / RMS or MAV window
  → per-channel reference normalization
  → per-rep / per-condition features → BLE/display/log
```

A 20–450 Hz digital band-pass is a **general literature pipeline**, not a universal setting. It cannot restore frequencies removed by a sensor's analog filter. Use a 50 Hz notch only if mains interference is present and report it; notching also removes real EMG energy in that band and harmonics may remain.

### 3.2 Candy/BisCute-specific limitation

If the module is confirmed as Candy/BisCute, its vendor-listed analog passband is **72–720 Hz**. At 720 Hz, the Nyquist minimum is >1.44 ksample/s; a **2 ksample/s/channel target** is reasonable for initial testing, but verify actual ESP32-S3 throughput, timestamps and clipping. These modules can support a consistent amplitude-envelope/%MVC MVP. They cannot provide conventional 20–450 Hz data, so do not compare their PSD or median-frequency fatigue values directly with conventional-band research data. Do not infer that a rising RMS or one spectral slope proves fatigue during dynamic repetitions.

### 3.3 MVC normalization and the two-muscle display

For each muscle, collect a safe, standardized reference contraction (often isometric), familiarize the participant, take several consistent short trials with adequate rest, and record posture/resistance/instructions. Apply **identical signal processing** to the task and reference.

`percent of reference = 100 × task RMS / reference RMS`

Call it `%MVC` only if the reference is a maximal voluntary contraction; state the position and task. Standard isometric references do not perfectly match dynamic exercise. Show each channel's normalized value. If an exploratory project index is used, disclose its formula and do not call it force sharing, compensation, or standard co-activation. See CEDE [1].

---

## 4. Datasets and analysis

Public datasets are useful to verify code and plotting; most gesture datasets are not gym-lifting or MVC validation data.

| Dataset | Typical use | Important limit |
|---|---|---|
| Ninapro DB5 | Wearable hand-gesture pipelines | Myo armband; 200 Hz does not support full conventional sEMG spectrum |
| Ninapro DB2/DB7 | Higher-quality hand/wrist gesture methods | Delsys Trigno, not the selected Candy/BisCute module or lifting pair |
| CapgMyo / CSL-HDEMG | High-density hand gesture research | Not a two-channel resistance-exercise dataset |
| Soro / RecoFit / ExerSense / Prabhu papers | Rep segmentation/counting methods | Mostly IMU/recognition methods; don't treat as device validation |

The project should keep its signal-processing validation separate from its human exercise pilot. Preserve raw data, metadata and normalization values; use subject-wise separation if any classifier is evaluated.

---

## 5. Firmware/software and validation tools

| Task | Tools / note |
|---|---|
| MCU firmware | Arduino IDE or ESP-IDF; ADC1 sampling; BLE GATT notifications; timestamp samples. Working sketch: `firmware/team_mvc/team_mvc.ino` (GPIO4, 2 kHz, 100 ms RMS, MVC capture on `C`, 10 Hz serial output) |
| Live plotting | `tools/emg_plot.py` — pyserial + matplotlib live view, CSV logging, `--replay` for saved logs |
| Signal processing | Python NumPy/SciPy for offline verification; reproduce known filters and RMS/MAV features before firmware port |
| App / visualization | Start with serial/CSV + notebook or minimal BLE plot; UI polish is later work |
| BLE | Send envelope/features when raw sample retention is not required; include units, channel IDs, sampling/window metadata |
| Rep check | Compare segmented counts/timestamps with video/manual labels |
| Repeatability | Repeated trials, placement notes/photos, coefficient of variation; evaluate agreement, not correlation alone |
| Concurrent validity | Same-site synchronized reference system (Delsys/Biopac) if lab access exists; otherwise describe the prototype as a feasibility demonstration |

---

## 6. Current parts checklist

### In hand / current prototype

- [x] Generic ESP32-S3 N16R8 development board with dual USB-C ports (exact vendor/model and pinout unverified; not the previously planned FireBeetle).
- [x] One 3.7 V, 1000 mAh Li-ion cell (connector, polarity, protection and charge limits unverified).
- [x] One HW-373 / TP4056-style USB-C charger board (exact revision/protection/current unverified).
- [x] One single-channel Muscle BioAmp-style EMG board, likely Candy (exact model/revision to verify); one 3-contact strap/lead set visible.
- [x] One HW-106 3.7 V → 5 V boost module with USB-A output (output voltage to verify).
- [ ] Identify and validate the sensor board before power-up; complete one-channel bench test.
- [ ] Demonstrate site-specific recording sequentially by moving the one sensor; collect a separate reference at each site and do not imply simultaneous comparison.
- [ ] Add a regulated battery-to-5V path (or use an uncharging USB power bank for a safe temporary body-test supply); do not feed battery voltage into the board's 5V pin.
- [ ] For two-channel use, obtain a second compatible front end and a second three-contact electrode set.
- [ ] Confirm included accessory bundles, assembled/revision status and seller stock.
- [ ] Select the first exercise pair and locations; get coach/physio input.
- [ ] Conductive gel or suitable adhesive Ag/AgCl contacts if the photographed strap contacts require coupling gel.
- [ ] USB-C cable, computer, Arduino IDE/ESP-IDF, and phone/laptop for plotting.

### Not in initial BOM

- FireBeetle: not in the photographed setup; its integrated charger/battery path must not be assumed.
- Second EMG front end and second 3-contact electrode set: still needed for simultaneous two-channel recording.
- USB isolator (optional): would make laptop-connected body recordings safe without relying on battery-only operation.
- IMU: optional, not required to test the two-channel amplitude concept.
- Cloud storage: out of the first prototype; keep pilot data local and consented.

---

## 7. Safety, standards and ethics

- This prototype records passively; it must not inject electrical stimulation.
- Use clean, intact skin and stop if irritation occurs. Clean reusable bands between users; don't reuse disposable gel pads.
- Battery protection and polarity must be verified. Do not short, puncture or charge damaged Li-ion cells; follow the battery/vendor charging instructions.
- Use battery-only operation on a person unless the entire acquisition/computer link is appropriately isolated. Avoid simultaneous body connection to a non-isolated mains-powered setup.
- Obtain course/instructor guidance for human testing, consent, data retention and privacy. Do not describe this educational prototype as diagnostic or therapeutic.
- Relevant guidance: SENIAM placement; CEDE EMG design/normalization reporting; IEC 60601 / ISO 10993 only as relevant background—not as a claim of device certification.

---

## 8. References and related project files

Use `REFERENCES_INDEX.md` and `share/SHARE_REFERENCES.md` for citations. Key local files include CEDE normalization (`02`), Chowdhury processing (`03`), Muceli frequency analysis (`33`), exercise fatigue reviews (`15`, `16`), wearable validation (`06`–`08`), and dry electrode reviews (`09`, `11`).

The old `EMG Project Communications Subsystem Plan.pdf`, `MyoSense_A2_DH803.docx` and `MyoSense_A2_DH803.pptx` describe a prior DFRobot SEN0240 / generic ESP32 proposal. They are historical coursework artifacts; the current design baseline and share guide supersede their purchase lists.
