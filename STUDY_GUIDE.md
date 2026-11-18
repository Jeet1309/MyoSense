# STUDY GUIDE
## Learning the EMG Wearable Project the way DH803 is taught
*Step-by-step curriculum · Jeet Gurbani (23B0023)*

> **How to use this:** work through one module at a time. Each module has
> **① What the course taught → ② What you need for this project → ③ Key concepts explained → ④ Formulas → ⑤ Read (from `references/pdfs/`) → ⑥ Self-check.**
> The course's spine is the **building-block chain**: *Signal → Interface → Transducer → Signal Processing → Communication → Data/Visualization → Battery → Networks.* We follow it exactly, then add the domain science ("other things you need to know").

---

## THE MAP

```
PART I — FOUNDATIONS (how the course frames everything)
  M0  Course map & the building-block chain
  M1  Signals & samples (Chemical / Physical / Electrical / Radiative) → where EMG sits
  M2  Design process & systems / surrogate thinking

PART II — THE BUILDING BLOCKS APPLIED TO EMG
  M3  Sampling interface      → electrodes, skin, SENIAM, dry vs wet
  M4  Transducer / sensor     → EMG front-end, amp, filters, ADC, IMU
  M5  Signal processing       → filtering, rectification, envelope, features, %MVC
  M6  Communication & battery → BLE, power management
  M7  Data processing & viz   → reps, fatigue, ML, app/UI
  M8  Networks, privacy, ethics

PART III — DOMAIN SCIENCE ("other things you need to know")
  M9  Muscle physiology & EMG biophysics
  M10 Strength-training science (activation, fatigue, mind–muscle, hypertrophy)
  M11 Validation & statistics (ICC, Bland–Altman, agreement)
  M12 Standards & regulatory (IEC 60601, ISO 10993, SENIAM/CEDE)
```

---

# PART I — FOUNDATIONS

## M0 — Course map & the building-block chain

**① Course:** Class 1–2 define "wearable health technology" = wearable tech + healthcare; give the design process and the **critical building blocks**. Grading: assignments 25%, quiz/midsem 40%, **project 35% (2 presentations + report)**.

**② Project:** your EMG wearable is *literally* the chain in a row. You will be assessed on how well you reason about each block and how they interact.

**③ Concept — the chain and its questions:**
| Block | Question it answers |
|---|---|
| Sample / Signal | What are we measuring? |
| Interface | How do we get it from the body cleanly? |
| Transducer / Sensor | How do we turn it into electricity? |
| Signal Processing | How do we clean and quantify it? |
| Communication | How does data leave the device? |
| Data processing & visualization | How do we turn data into insight? |
| Battery management | How do we keep it alive? |
| Data transfer & networks | How does it connect and stay private? |

**⑥ Self-check:** Name the block where each of these lives: (a) Ag/AgCl electrode, (b) Butterworth filter, (c) BLE chip, (d) %MVC gauge, (e) 50 Hz notch, (f) LiPo battery.
*Answers: a=Interface, b=Signal Processing, c=Communication, d=Visualization, e=Signal Processing, f=Battery.*

---

## M1 — Signals & samples (where EMG sits)

**① Course (Class 6):** four signal/sample types:
- **Chemical** — molecules/ions in blood, interstitial fluid, breath, sweat, urine, tears; pH.
- **Physical** — movement, joints, blood flow, texture, force; displacement/strain/velocity/acceleration.
- **Electrical** — **ECG, EMG, EEG, EOG**; resistance, capacitance, inductance.
- **Radiative** — temperature (heat), light, colour.

**② Project:** **EMG is an Electrical signal.** But your *device* also uses **physical** signals (IMU for movement) and could add **radiative** (temperature) or **chemical** (sweat) later. Knowing the taxonomy lets you justify sensor choices.

**③ Concepts explained:**
- An **electrical biopotential** is a voltage produced by charge separation across cell membranes. For muscle, depolarisation of muscle fibres creates a time-varying potential (µV–mV range) detectable on the skin.
- EMG is **active**: the body is the source; you don't inject anything (unlike iontophoresis, which is an *active sampling* method).
- Range: sEMG typically **~10 µV to a few mV**; bandwidth **~20–450(500) Hz**; so it's a *low-amplitude, mid-frequency* signal — noise is the central enemy.

**④ Formula:**
- Signal-to-noise ratio: **SNR = 20·log₁₀(V_signal / V_noise)** dB.
- Dynamic range of ADC needed: `bits ≈ log₂(V_fullscale / V_LSB)`.

**⑤ Read:** `03_Chowdhury2013` (Ch. "EMG signal" sections); `41_Alcan2023`.

**⑥ Self-check:** Why is EMG classified "electrical" and not "physical", even though it measures muscle *activity*? *(Because the measurable quantity is an electrical potential, not a mechanical one.)*

---

## M2 — Design process & systems / surrogate thinking

**① Course (Class 2–3):**
1. Meet the **end-user / domain expert** → understand use-case + existing limitations.
2. Define the **design objective** from a **literature meta-review**; make a **project schematic**; separate **research** vs **integration** components.
3. **Systems approach**: the body is interconnected; beware **surrogates**.
   - **True surrogate** — downstream of the same causal pathway (e.g. LDL → CAD).
   - **Mixed surrogate** — related to the pathway, but also affected by other factors (e.g. BP → CAD).
   - **Independent surrogate** — statistical association only (e.g. resting HR).

**② Project:**
- End-user = a lifter/coach/physio. Their stated problem: "I can't tell if I'm hitting the target muscle."
- Longer-term objective: **record two selected muscles and display each channel relative to its own MVC reference, then test within-person feedback/cue changes.** For the current one-sensor demo, record sites sequentially and calibrate each separately. This is not a form classifier or force measurement.
- EMG amplitude is an **activation-related electrical measure**, not force. Its relationship to activation/force depends on tissue, crosstalk, electrode geometry, muscle length, contraction type and velocity. %MVC is amplitude relative to a stated muscle-specific reference; it is not a universal force percentage.

**③ Concept — why surrogate thinking matters:** it tells you how far you can trust your metric. You can claim "activation", not "force" or "growth".

**④ Project schematic (draw this):**
```
[Two muscle sites] → [3 contacts/channel] → [2 EMG front ends] → [ESP32-S3 ADC1]
                                                             → BLE → [phone/laptop]
                                                             → [two traces + %reference]
```
The IMU and fatigue-frequency features are extensions, not part of the current minimum build.

**⑤ Read:** `README.md` (caution), `25_Haugen2023` (surrogate caution), `PROJECT_PLAN.md` §3.

**⑥ Self-check:** Is sEMG a true, mixed, or independent surrogate for *muscle force*? *(Mixed.)* For *hypertrophy*? *(Weak/mixed — many confounders; do not over-claim.)*

---

# PART II — THE BUILDING BLOCKS APPLIED TO EMG

## M3 — Sampling interface (electrodes & skin)

**① Course (Class 6–13):** the interface's job = collect the signal with minimal loss/noise. Position-based (surface / below-surface / proximity) and energy-based (**passive** = natural forces; **active** = external energy). Passive: capillary action, contact electrodes, membranes. Active: differential pressure, ultrasound, iontophoresis. Materials: adhesives, skin properties, biocompatibility, sterilization.

**② Project:** you use **surface contact electrodes (passive)**. No microfluidics needed — but you must master **electrode type, placement, and skin interface**.

**③ Concepts explained:**
- **Bipolar differential recording:** two electrodes over the muscle + a **reference** on a bony landmark; the amp measures the *difference*, cancelling common noise.
- **SENIAM placement:** electrodes generally align parallel to fibres and are commonly 20 mm apart on the muscle belly, between the innervation zone and a tendon. Treat 20 mm as a general recommendation; consult muscle-specific guidance.
- **Wet vs dry:** Ag/AgCl gel = best signal, dries out; **dry/textile** = wearable, higher impedance, more motion artifact. **Electrode–skin impedance** is the key number (lower = better SNR).
- **Crosstalk:** signal from neighbouring muscles leaking in — controlled by small inter-electrode distance and good placement.
- **Innervation zone:** where nerve enters muscle; signals there cancel — avoid.

**④ Formulas/numbers:** inter-electrode distance **20 mm**; electrode Ø ~**10 mm**; skin prep (clean/abrade) lowers impedance; sEMG bandwidth **20–450 Hz**.

**⑤ Read:** `09_Nunes2023`, `11_Kim2022`, `12_Myers2015`, `10_Ruvalcaba2020`, `13`/`14` (armbands), `45`/`48` (textiles); `SENIAM` (seniam.org).

**⑥ Self-check:** Why does the reference electrode go on bone? *(Low electrical activity → clean baseline.)* Why does electrode displacement matter more in dynamic exercise? *(It changes the detected volume → changes amplitude.)*

---

## M4 — Transducer / sensor (front-end electronics)

**① Course (Class 14):** a sensor converts one energy form to another; for biopotentials the sensor is the **electrode + amplifier chain**. Key specs: range, resolution, accuracy, response time. Sensor = sensing element + associated components.

**② Project:** the current transducer chain is the **EMG front-end** (electrodes → amplifier/filters → ADC). An IMU is a future option, not part of the photographed prototype parts.

**③ Concepts explained:**
- **Instrumentation amplifier (InAmp):** high **input impedance** so it doesn't load the tiny signal; high **CMRR** to reject common-mode noise (mains hum); low noise.
- **Gain:** EMG is µV–mV, ADC needs ~volts → gain ~**100–1000**.
- **Anti-aliasing low-pass** before the ADC; **high-pass** to remove DC/motion.
- **ADC:** resolution and sample rate matter. The current generic ESP32-S3 board has the chip's nominal **12-bit** internal ADC; test its effective noise/range and verify the board pin map. GPIO4/GPIO5 are candidate ADC1 pins. Choose sample rate based on the confirmed sensor's actual analog bandwidth, not a generic number.
- **IMU (accelerometer/gyro):** for movement, ROM, tempo, rep validation, sensor fusion.

**④ Formulas:**
- **CMRR = 20·log₁₀(A_differential / A_common)** dB (want > 80–100 dB).
- Input loading: need **Z_in ≫ Z_electrode** (Z_in > 10 MΩ, ideally 100 MΩ).
- ADC LSB = **V_ref / 2^N**; e.g. 3.3 V / 2¹⁶ ≈ 50 µV.
- Nyquist: **f_s ≥ 2·f_max** (⇒ ≥ ~1 kHz for 500 Hz EMG).

**⑤ Read:** `03_Chowdhury2013` (front-end/conditioning); `08_NOK2024`; datasheets in `DATASETS_AND_HARDWARE.md`.

**⑥ Self-check:** Your signal is 200 µV and your ADC LSB is 50 µV. Problem? *(Resolution is marginal; need more gain or a 24-bit AFE like ADS1299.)*

---

## M5 — Signal processing (the heart of your project)

**① Course (Class 14 + Section 2):** A/D conversion, **noise filtering**, **amplification**, then feature extraction. Interference/validation is an explicit topic.

**② Project:** this is your **deep-dive block**. Pipeline: filter → rectify → envelope → features → normalize.

**③ Concepts explained:**
- A **20–450 Hz** digital band-pass is a common general example for broadband raw sEMG; it is not universal and cannot recover signal removed by a sensor's analog filter.
- A **50 Hz notch** may attenuate Indian mains interference if it is present; inspect the spectrum first because the notch also removes signal energy in that band and harmonics may remain.
- **Motion artifact** is often low-frequency; a high-pass can reduce it, but filtering cannot fully correct electrode movement and can remove real signal.
- **ECG artifact** on trunk/shoulder → high-pass + template subtraction.
- **Full-wave rectification** |x| then **low-pass (~4–6 Hz)** = **linear envelope**; or **RMS/MAV** in sliding windows.
- **Features:** time-domain — RMS, MAV, iEMG, waveform length, zero-crossings, slope-sign changes; frequency-domain — mean/median frequency, spectral moments; time-frequency — STFT, wavelets.
- **Normalization to %MVC** — the single most important step for comparability.

> **Current prototype note:** Muscle BioAmp Candy and BisCute specify fixed **72–720 Hz** analog bandpass. A generic digital 20–450 Hz filter cannot restore frequencies removed by that analog front end. That candidate setup can support a consistent activation-amplitude MVP, but conventional-band spectral-fatigue analysis is deferred unless the front end changes.

**④ Formulas:**
- RMS = √( (1/N) Σ xᵢ² ) · MAV = (1/N) Σ |xᵢ| · iEMG = Σ |xᵢ|
- %MVC = (EMG / EMG_MVC) × 100
- Median frequency f_med: ∫₀^{f_med} PSD = ½ ∫₀^∞ PSD
- In a controlled, sustained/slowly varying protocol, a downward trend in mean/median frequency may be one fatigue-related feature; it is not a stand-alone dynamic-set fatigue verdict.

**⑤ Read:** `02_Besomi2020` (normalization), `05_Boyer2023` (noise), `33_Muceli2024` (frequency/fatigue), `28_SmartEMGenvelope2023`, `16_Rodrigues2022`.

**⑥ Self-check:** Why normalize to a reference before comparing repeated trials? *(It can reduce some amplitude scaling differences if the reference and setup are appropriate; it does not remove crosstalk or make different muscles' values equal in force.)*

---

## M6 — Communication & battery

**① Course:** communication module (BLE, NFC, ANT+), battery management (hardware + app), power optimization for life.

**② Project:** stream time-stamped samples/features over **BLE**. The user has a 3.7 V, 1000 mAh single-cell Li-ion battery and a TP4056-style charger board; the regulated power path to the generic ESP32-S3 board remains to be built/verified. For two channels stored as 16-bit words at 2 ksample/s, raw payload is about 64 kbit/s before packet overhead, normally feasible for BLE but must be tested.

**③ Concepts explained:**
- **BLE** = low energy, phone-friendly; **NFC** = tap pairing; **ANT+** = sports ecosystem.
- **Data rate vs power trade-off:** send raw vs on-device features (envelope only → far less data/power).
- **Battery:** a charger is not a regulator. The HW-373/TP4056-style board charges a one-cell battery and exposes battery-range output; do not connect it directly to the ESP32 board's `5V` pin. Verify cell polarity, protection and charger current. A regulated 5 V boost (or a USB power bank not charging) is required for battery-powered operation. For body recordings, disconnect charging/ordinary USB-to-computer cables and use the isolated battery-powered system; never charge while electrodes are attached.
- **Latency** matters for real-time feedback (< ~100 ms).

**④ Numbers:** BLE application throughput varies by connection settings and interference. Estimate data rate from actual sample rate, encoding and packet overhead, then benchmark sustained streaming on the prototype.

**⑤ Read:** course slides Class 1–2; `DATASETS_AND_HARDWARE.md` §2.4.

**⑥ Self-check:** Why might you compute the envelope **on the device** instead of streaming raw EMG? *(Cuts bandwidth/battery dramatically; enables real-time feedback without a phone.)*

---

## M7 — Data processing, algorithms & visualization

**① Course:** extract information from data/signal; visualize; app/UI. Project scope includes "data/signal analysis" and "new algorithms".

**② Project:** reps/sets detection, fatigue trend, activation ratios, ML, and the **app/UI**.

**③ Concepts explained:**
- **Rep detection:** an adaptive threshold on the envelope can be piloted; IMU fusion is an optional future improvement, not in the selected first BOM.
- **Set detection / rest segmentation.**
- **Fatigue:** in controlled sustained/slowly varying contractions, median/mean-frequency and RMS trends can be studied. During dynamic repetitions, movement and changing electrode geometry confound them; validate task-specifically.
- **Ratios/symmetry:** show channels separately. Any target/comparison ratio is a project-defined exploratory index, not force-sharing or a validated compensation measure.
- **ML:** exercise classification, %MVC regression, LOSO cross-validation; classical (SVM/RF) vs deep (CNN/LSTM).
- **UI:** live gauge, per-rep bars, post-set summary, history, CSV export.

**④ Read:** `18_Soro2019`, `22_RecoFit2014`, `19_ExerSense2020`, `20_Prabhu2020`, `21_Geng2016`, `23`/`24`, `30`.

**⑤ Self-check:** Which is harder — counting reps or measuring %MVC — and why? *(%MVC: needs reliable MVC normalization; rep counting can work from motion/envelope alone.)*

---

## M8 — Networks, privacy, security, ethics

**① Course (Section 4):** encryption, standard data files, multi-device communication, privacy/security/ethics, VR/AR, gamification.

**② Project:** app sync/history; discuss that EMG is health-related data.

**③ Concepts:** encryption in transit (BLE pairing), consent, data minimization, GDPR-style thinking.

**⑤ Read:** course slides; `PROJECT_PLAN.md` §11–13.

**⑥ Self-check:** What EMG data could reveal beyond "muscle activation"? *(Neuromuscular disorders, fatigue, possibly stress — hence privacy matters.)*

---

# PART III — DOMAIN SCIENCE ("other things you need to know")

## M9 — Muscle physiology & EMG biophysics

**③ Concepts:**
- **Motor unit (MU)** = one motor neuron + all fibres it innervates. **MUAP** = its electrical signature.
- **Recruitment (Henneman size principle):** small MUs first; more recruited as force rises. **Rate coding:** firing frequency rises.
- **EMG = sum of many MUAPs (interference pattern).** Amplitude is influenced by recruitment and discharge rates, but also MUAP shape/cancellation, anatomy, tissue, placement and recording configuration; it is not a simple product or direct force scale.
- **Volume conduction:** signal passes through tissue (fat attenuates/smears) to skin.
- **Fatigue:** conduction velocity and motor-unit behavior can change; under controlled sustained contractions the spectrum often shifts lower. This is not a universal dynamic-set detector.
- **Fibre types:** I (slow, fatigue-resistant) vs II (fast, fatigable) — affect EMG/fatigue behaviour.

**⑤ Read:** `31_LongitudinalEMG`, `16_Rodrigues2022`, `41_Alcan2023`; textbook `Merletti & Parker (2004)`.

**⑥ Self-check:** Why can EMG amplitude rise during a sustained submaximal hold? *(The nervous system may increase recruitment/firing to maintain the target force as fatigue develops; this is context-dependent, not a guaranteed pattern.)*

---

## M10 — Strength-training science (the "why")

**③ Concepts:**
- **Mind–muscle connection:** in one bench-press study, focusing on pectoralis/triceps changed EMG at 20–60% 1RM, but not 80%, in that sample. Do not generalize the threshold to all tasks.
- **Long-term attention evidence:** one small 8-week study in untrained men found greater elbow-flexor thickness with internal focus; quadriceps thickness did not differ. A separate meta-analysis was about strength outcomes, not EMG amplitude or hypertrophy.
- **Activation ≠ growth:** acute EMG and long-term hypertrophy are different outcomes; free-weight vs machine training can have different acute EMG without clear hypertrophy differences.
- **Fatigue & volume:** time-under-tension, reps-to-failure, load all interact.
- **Practical prototype display:** per-rep amplitude and two separate per-channel %MVC-reference values. A target/comparison ratio is exploratory; intra-set spectral fatigue and left/right comparison require task-specific validation.

**⑤ Read:** `35`/`36` (Calatayud, Schoenfeld), `27_AttentionalFocus_meta_analysis`, `25_Haugen2023`, `26_Lacerda2021`.

**⑥ Self-check:** What is the honest, defensible product claim? *("Helps you measure and improve muscle activation / mind–muscle connection", not "grows more muscle".)*

---

## M11 — Validation & statistics

**③ Concepts:**
- **Concurrent validity:** wearable vs reference system (Delsys/Biopac).
- **Relative validity:** Pearson r / ICC. **Absolute validity:** Bland–Altman (bias ± limits of agreement).
- **Reliability:** test–retest (CV, ICC).
- **Functional validity:** rep count vs video/manual; fatigue slope vs force decline.
- **Study design:** within-subject, familiarisation, randomised order, standardised MVC protocol.

**④ Formulas:** ICC; Bland–Altman bias = mean(diff); LoA = bias ± 1.96·SD(diff); CV = SD/mean × 100%.

**⑤ Read:** `06_Lynn2018`, `07_MolinaMolina2020`, `08_NOK2024`.

**⑥ Self-check:** A device has high Pearson r but a large Bland–Altman bias. Valid? *(Relative yes, absolute no — it's systematically off.)*

---

## M12 — Standards & regulatory

**③ Standards:**
- **IEC 60601** — medical electrical equipment safety.
- **ISO 10993-1** — biocompatibility of skin-contact materials.
- **SENIAM / CEDE** — EMG placement & processing.
- **IEEE 802.15.1 (BLE)** — communication.
- **ISO 2137 / ASTM D2979** — adhesive tack (course material).

**⑤ Read:** `DATASETS_AND_HARDWARE.md` §6; course slides Class 12–13.

**⑥ Self-check:** Which standard governs whether your dry electrode is safe to wear for 7 days? *(ISO 10993-1.)*

---

## SUGGESTED STUDY ORDER (4 passes)

**Pass 1 — Foundations (1 week):** M0 → M1 → M2. Read `03`, `02`, `25`.
**Pass 2 — Chain (2 weeks):** M3 → M4 → M5 → M6 → M7 → M8. Read `09`,`11`,`05`,`33`,`18`,`22`.
**Pass 3 — Domain (1 week):** M9 → M10 → M11 → M12. Read `16`,`31`,`35/36`,`27`,`06`,`07`.
**Pass 4 — Synthesis:** re-read `PROJECT_PLAN.md`, then build the pipeline (M5) and UI (M7).

---

## MASTER SELF-QUIZ (after all modules)

1. Classify EMG in the course's signal taxonomy and justify it.
2. Name the 8 building blocks in order.
3. Why 50 Hz, not 60 Hz, for the notch in India?
4. Give the sEMG bandwidth and minimum sampling rate.
5. Define %MVC and explain why normalization is essential.
6. Which frequency-domain feature signals fatigue, and in which direction?
7. Is EMG a true/mixed/independent surrogate for force? For hypertrophy?
8. What is crosstalk and how does SENIAM reduce it?
9. State the mind–muscle connection finding and its load threshold.
10. How would you validate your wearable against a reference system?
