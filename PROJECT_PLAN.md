# PROJECT PLAN — MyoSense sEMG Activation Biofeedback

*DH803 — Wearable Health Technologies · Jeet Gurbani (23B0023)*  
*Current design review: 7 November 2026*

## 1. Current scope

> Build and evaluate a two-channel wearable surface-EMG prototype that records a selected target muscle and a comparison muscle during a standardized strength exercise, displays each channel's amplitude relative to its own MVC reference, and tests whether simple feedback/cues change those within-person signals.

The prototype is a **measurement and biofeedback experiment**, not a validated form checker. Surface EMG reflects local electrical activity; it is not a direct force sensor, proof of correct technique, or growth predictor. Any target/comparison ratio is a project-defined exploratory index, not a standardized force-sharing or compensation measure.

**Near-term demonstration with current parts:** use the single available sensor to record one site at a time, repositioning it between selected sites. Demonstrate the acquisition and site-specific MVC/reference workflow sequentially. This is not simultaneous comparison, and independently normalized MVC readings are each about 100% by definition; raw amplitudes across different muscles are not relative-force measurements.

## 2. Need and evidence

People may not accurately perceive the relative activity of muscles during an exercise. Evidence exists but is task/sample-specific. Sevilmis et al. studied a small group of male sub-elite soccer players performing six upper-body exercises; perceived and measured activity corresponded poorly in that study [8]. Calatayud et al. found cue-related target-muscle EMG changes during bench press at 20–60% 1RM but not 80% in their sample of 18 resistance-trained men [7]. These findings motivate a controlled feedback pilot; they do not mean every lifter misjudges every exercise.

The justified product claim is: **“shows two measured EMG amplitude traces and reference-normalized values to support a within-person biofeedback experiment.”** Do not claim “detects correct form,” “measures force,” “the helper took over,” or “guarantees hypertrophy.”

## 3. Current hardware status

| Block | Current baseline | Status / caveat |
|---|---|---|
| Controller | ESP32-S3 N16R8 development board, dual USB-C, as shown in photo | In hand; exact vendor/revision and pin map unverified. Not the previously planned FireBeetle. GPIO4/GPIO5 candidates for ADC1. |
| Battery | 3.7 V, 1000 mAh single-cell Li-ion | In hand; connector, polarity, protection and charge limits to verify. |
| Charger | HW-373 / TP4056-style USB-C 1S charger board | In hand; verify revision/protection. It does not provide regulated 5 V. |
| Boost | HW-106 3.7 V → 5 V with USB-A output | In hand; fixed ~5 V. Meter before connecting; provides the missing 5 V rail |
| EMG module | One Muscle BioAmp-style board, likely Candy | In hand; exact model/revision to verify. One channel only. |
| Interface | One three-contact electrode/strap set visible | Confirm contact type and coupling gel; two channels require six contacts. |
| Retention/electrodes | One three-contact strap/lead set visible | Exact band/contact type and skin interface are unverified; suitable gel contacts/coupling may be needed |
| Communication | BLE from ESP32-S3 | After bench capture; keep body-connected tests free from USB/mains connections |
| IMU | Not in first build | Add only if motion/rep-phase validation requires it |

### EMG module comparison (two channels)

| Candidate | Approximate two-channel cost at reviewed listings | Compatibility/characteristics | Best fit |
|---|---:|---|---|
| **2× Muscle BioAmp Candy** | ~₹1,598 | Assembled, 3.3–30 V input, fixed ×2420 gain, fixed 72–720 Hz bandpass; accessory kit may include gel electrodes/cable/band (confirm stock) | **Budget activation/%MVC MVP recommendation** |
| **2× Muscle BioAmp BisCute** | ~₹1,198 | 3.3–30 V, same 72–720 Hz passband; full through-hole DIY soldering/assembly | Lowest cost only if solder assembly is intended |
| BioAmp EXG Pill 2025 Edition Explorer Pack | ~₹5,252 Robu listing checked | Two assembled channels; 2025 revision supports 3.3/5 V; configurable gain/filter; default EEG/EOG, configure EMG | More configurable/broader-band path; confirm assembled 2025 revision |
| 2× DFRobot Gravity SEN0240 | ~₹10,146 at the reviewed Robu price | 3.3–5.5 V; 0–3 V analog; reusable dry electrode; integrated conditioning | Convenient dry-electrode module, but expensive pair |
| 2× MyoWare 2.0 | ~₹9,198 at the reviewed India price | 3.1–5 V; raw/rectified/envelope outputs; snap ecosystem | Convenient output modes, expensive pair |

**Current module status:** The photographed green board appears to be a Muscle BioAmp board, likely Candy, but its exact label/revision must be confirmed before assuming specifications. If it is Candy, its stated 72–720 Hz band and gain support a one-channel activation-amplitude bench prototype; the band is not conventional 20–450 Hz and does not justify a standard-band fatigue claim. The second channel is not yet in hand.

### Chosen wiring concept

For initial disconnected-electrode bench testing, power the ESP32-S3 board from USB and, after module identification, connect sensor `VCC → 3V3`, `GND → common GND`, `OUT → GPIO4/ADC1`. For a second module, use GPIO5/ADC1 after checking the board pin map. Connect electrode leads only by their `IN+`, `IN−`, and `REF` markings/manual.

The pictured TP4056-style board outputs the cell's battery voltage, not 5 V. Never connect its battery output directly to the ESP32 development board's `5V` pin. The **HW-106** boost supplies the 5 V: `HW-373 OUT+ / OUT− → HW-106 VIN+ / VIN−`, then its USB-A socket → USB-A-to-C cable → ESP32 USB-C. Meter the boost output (expect 4.9–5.2 V) before connecting. No charging or USB-to-computer cable may remain attached while electrodes are on a person. Keep every sensor output within the ESP32-S3 ADC range and bench-check for clipping first.

## 4. Exercise and measurement design

### Candidate exercise pairs

1. **Lat pulldown:** latissimus dorsi / biceps brachii. Lehman et al. measured both and found variation by exercise and substantial person-to-person variability [9].
2. **Bench or machine chest press:** pectoralis major / triceps brachii. The pair is well studied; activation varies with load, phase, technique and stability [7, 10].
3. **Lateral raise:** middle deltoid / upper trapezius. Exercise variations affect recorded patterns in a small competitive-bodybuilder study; crosstalk and site proximity are concerns [11].

Treat each pair as a testable question, not a universal “wrong muscle” claim. Select one pair after a placement pilot. Begin with a stable, low-to-moderate-load task; standardize apparatus, load, range, tempo, order, cue and rest. Internal cues at 20–60% 1RM are worth testing based on the bench-press study, but this is not a universal threshold [7].

### MVC/reference protocol

- Familiarize the participant with the exercise and MVC maneuvers.
- For each muscle, select a safe, muscle-specific standardized isometric reference posture; report position, joint angle, resistance method and instructions.
- Collect preferably 3–5 brief, consistent efforts with adequate rest (often 1–2 minutes, adjusted to effort and participant). Stop for pain/discomfort. Follow required course ethics/consent procedures.
- Use the same electrode location, analog front end, filter, rectification/RMS window and amplitude definition for the task and reference.
- State the calculation: `% of reference = 100 × task RMS / MVC-reference RMS`. If the MVC is an unmatched standardized isometric posture, call it “% of isometric MVC reference” and explain the mismatch to dynamic exercise.
- Report the two channel values. If a comparison ratio is shown, label it an exploratory project index; do not interpret as relative force or validated compensation.

CEDE notes that MVC normalization can express amplitude relative to a reference under specified conditions, but the EMG–force relationship is not always linear, MVC posture matters, and normalized EMG cannot compare absolute force contributions between different muscles (Besomi et al., 2020; ref. [1]).

## 5. Signal acquisition and processing

### Acquisition

- ESP32-S3 ADC is nominally 12-bit; verify the photographed board's pin map and measure effective resolution/noise rather than assuming performance from bit count.
- If the current module is confirmed as Candy/BisCute, its upper analog passband is 720 Hz. Nyquist minimum is >1.44 ksample/s/channel; use a **2 ksample/s/channel target** for initial raw capture and confirm actual timed acquisition, missing samples and BLE load.
- Use ADC1-capable pins (GPIO4/GPIO5 appear exposed on the photographed board); verify the exact board pinout. Use a verified battery-only power path during body recordings and keep sensor cables fixed.
- Log board revision, sensor revision, electrode site/photo, reference posture, sampling rate, ADC attenuation, analog filter/gain, exercise/load, cue and trial conditions.

### MVP processing (activation and %reference)

```text
Analog EMG out → ADC samples + timestamps
→ inspect bias, clipping and idle noise
→ band/line-noise handling consistent with the module and sampling
→ rectification and 50–200 ms RMS windows (pilot window; keep same for MVC/task)
→ per-channel MVC-reference normalization
→ separate target/comparison display and per-rep summary
```

If the current module is Candy/BisCute, do not blindly apply the generic project-library 20–450 Hz filter: its analog filtering is already 72–720 Hz, and digital processing cannot recover removed frequencies. Inspect spectra before adding a 50 Hz notch. Candy's high-pass attenuates the 50 Hz fundamental, but harmonics or other artefacts may remain. A notch also removes signal energy if it overlaps the EMG spectrum.

### Deferred fatigue / frequency features

Mean/median-frequency decreases can support fatigue analysis in controlled sustained or slowly varying contractions when posture and geometry remain stable [3, 5]. Frequency estimates during moving repetitions are confounded by muscle/electrode motion and changing load sharing. With Candy/BisCute's fixed 72–720 Hz passband, do not claim conventional 20–450 Hz or validated median-frequency fatigue. For MVP, label fatigue as **not implemented** or use an exploratory within-set RMS trend with limitations.

## 6. System blocks (DH803 mapping)

| Block | Project implementation |
|---|---|
| Signal/sample | Summed, tissue-filtered sEMG from two selected surface sites |
| Interface | Two active contacts + reference per channel; gel adhesive or dry band + coupling gel; repeatable placement/strain relief |
| Transducer | One analog EMG AFE per muscle channel (Candy/BisCute/EXG alternative) |
| Signal processing | ADC, quality checks, amplitude envelope/RMS, per-channel reference normalization; spectral fatigue deferred unless front end/protocol support it |
| Communication | ESP32-S3 BLE; timestamped values/features to phone/laptop |
| Visualization | Two channel traces/bars, MVC-reference values, per-rep summaries; no “correct form” label without validation |
| Battery | 1S 3.7 V 1000 mAh cell with HW-373/TP4056-style charger board; protection, polarity and regulated 5 V power path must be verified |
| Data/privacy | Local pilot CSV; consent, data minimization, no diagnostic claims |

## 7. Work plan and decision gates

| Phase | Work | Exit check |
|---|---|---|
| 1. Identify | Read exact ESP32 board and EMG-module labels; verify cell polarity/charger/power path and sensor supply/output specifications | Pinout and limits recorded; no powering an unidentified module into ADC |
| 2. Bench | Follow `firmware/README.md`: wire EMG `OUT → GPIO4`, upload `team_mvc.ino`, confirm the `Mean/RMS/Activation` stream, then log with `tools/emg_capture.py`. No person connected at this stage | Stream prints at 10 Hz, `Mean` is not at a rail, envelope responds to contraction and release |
| 2b. Battery power | Assemble `cell → HW-373 → HW-106 → ESP32`; meter the boost output before connecting | Board boots from battery with no laptop attached |
| 3. Sequential demo | Use the one sensor at two selected sites one at a time; document repositioning and site-specific references | Clearly labeled per-site traces/reference values; no simultaneous comparison or force claims |
| 4. Complete BOM | Confirm exact sensor model; obtain second matching module and contacts for two channels | Two powered channels have safe output range and usable signal |
| 5. Skin/placement | Test appropriate gel contacts, reference position, band/strap tension and cable strain relief | Repeatable contact and acceptable movement artifact |
| 6. Calibration | Standardize reference MVC posture, trials, rest and processing; retain raw and normalized data | Test/retest variation measured and reported |
| 7. Pilot exercise | One exercise pair, low/moderate load, repeat conditions/cues | Display each channel and exploratory index; no form verdict |
| 8. Evaluate | Compare repeatability, manual/video rep labels, and optionally a reference EMG if available | Report limitations, agreement, and next hardware/algorithm needs |

## 8. Validation and reporting

### Preliminary user-reported observations (22 November 2026)

An informal single-session comparison has been recorded for the lat exercise, a biceps
exercise, and bench press. Reported activation values and descriptive means are in
`PRELIMINARY_RESULTS.md` and `data/form_comparison_2026-11-22.csv`. The pattern differed by
muscle/site: the user-labelled good condition was higher for lat and chest, while the
user-labelled bad condition was higher for biceps and triceps. Treat these as exploratory
observations only. Exercise variants, load, tempo, electrode landmarks, trial order and MVC
details were not recorded, and the good/bad labels were not independently assessed. The
readings do not validate form detection or indicate relative force.

A separate 12 s BLE telemetry check on the earlier firmware received 113 rows in 11.9 s
(about 9.5 rows/s) and reported 1888 ADC reads/s. The sensor input was open during that check,
so its high RMS was not an exercise result. The notification path has since been changed to
avoid an unconditional per-packet delay; re-flash and remeasure before reporting the revised
acquisition rate or BLE loss rate.

- **Signal quality:** idle-noise RMS, clipping percentage, missing-sample rate, and mains/artifact spectra.
- **Repeatability:** repeated trials with same electrode placement; report within-session variability. Repositioning/day-to-day reliability is a later phase.
- **Rep segmentation:** compare algorithm count/timestamps with manual or video annotations. It does not validate muscle activation.
- **Concurrent validity:** if a research EMG is available, synchronously compare same-site same-task signals; correlation alone is not agreement. Consider Bland–Altman and ICC only with a design/sample suited to them.
- **Human study:** obtain course/instructor guidance and ethics/consent. A small convenience pilot can demonstrate feasibility, not establish population-wide effectiveness.

## 9. Risks, limits and safety

| Risk/limit | Mitigation |
|---|---|
| MVC not truly maximal or posture mismatch | Familiarize; multiple consistent efforts/rest; state reference type and posture; don't force values below 100% |
| Comparing different muscles as if equal force | Show each %MVC separately; label any ratio exploratory; no force claims |
| Candy/BisCute filter bandwidth | Make 72–720 Hz explicit; defer conventional spectrum/fatigue interpretation |
| Crosstalk / sensor shift | Select accessible sites, fibre-aligned spacing, repeatable mounting, photos/marks, careful exercise choice |
| Motion/mains/cable artifacts | Fix cables, test on battery, inspect data, apply only justified digital filters/notches |
| Battery connector/polarity | Identify the cell connector and protection; verify polarity with a multimeter before connection |
| Skin irritation | Clean intact skin, single-use gel pads; stop for irritation; clean reusable bands |
| Overclaiming form, force or growth | Call it activation biofeedback; validate any feedback outcome separately |

## 10. Reporting checklist

Report participant/task/load/cue; muscle and electrode sites; electrode type, spacing and orientation; reference location; sensor/module revision, analog bandwidth and gain; ADC pins, nominal resolution, sampling rate/timestamps; digital filters and RMS window; MVC/reference protocol; electrode preparation; excluded/clipped trials; and all limitations. This follows the intent of CEDE reporting guidance [1].

## References

See `SHARE_REFERENCES.md` for full citations, DOIs, local filenames and hardware documentation. Core citations used here: CEDE normalization [1]; sEMG processing [2]; frequency analysis [3]; exercise fatigue [5, 6]; cue/activation evidence [7, 8]; lat-pulldown [9]; bench-press review [10]; lateral-raise variants [11]; controller, sensor and battery documentation [14, 16–20].
