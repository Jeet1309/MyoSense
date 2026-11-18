# RECONCILIATION & ADDITIONS
## Review of `my deep-research-report.md` and current-design audit

The original report is retained as a historical source draft and is **not itself the current technical specification**. Its broad overview is useful, but it contains overclaims and outdated component suggestions. Below I record corrections and additions; `CURRENT_DESIGN.md` and `share/EMG_WEARABLE_FROM_SCRATCH.md` now take precedence for the prototype and interpretation. The same applies to `MyoSense_A2_DH803.docx`, `MyoSense_A2_DH803.pptx`, and `EMG Project Communications Subsystem Plan.pdf`, which describe an earlier SEN0240/generic-ESP32 proposal.

---

## 1. What your report got right (and I've adopted)

- The **signal chain**: bipolar electrodes → instrumentation amp (high CMRR) → band-pass → notch → ADC → MCU → BLE/Wi-Fi. Correct, and it matches the course's building blocks.
- **Feature set**: ARV, MAV, RMS, iEMG (time domain) and median frequency (fatigue). Correct.
- **Normalization to MVC** for %MVC comparisons. Correct — this is the crux.
- **Wearability concerns**: electrode contact, motion artifact, skin prep, flexible/stretchable form factor, sweat/waterproofing.
- **Safety/ethics**: biocompatibility, consent, data privacy.
- **Industry examples**: Myontec, Delsys Trigno, Myo armband — all real.
- **GenENet (Stanford)**: **verified real.** Kim KK, Zaluska TJ, Skov S, Lee Y, Park H, Zhong D, … Bao Z (2025/2026). *A simplified wearable device powered by a generative EMG network for hand-gesture recognition and gait prediction.* **Nature Sensors 1:27–38**, doi:10.1038/s44460-025-00002-2. A **6-channel** stretchable device reconstructs 32-channel high-density EMG via self-supervised learning (~93.6% sign-language accuracy, ~71% lower power). Open code: github.com/nature-sensors/GenENet.
  → Added: `40_GenENet2025_NatureSensors_generative_EMG.pdf`

---

## 2. Corrections to make in your report

| # | Your report says | Correction |
|---|---|---|
| 1 | "notch filter at **60 Hz**" | **India's mains is 50 Hz** — use a **50 Hz** notch (60 Hz is US). Make this explicit; it's a common exam/report slip. |
| 2 | "EMG amplitude **generally reflects** the number of active fibers and contraction force" | The **EMG–force relation is nonlinear and saturates** at high forces; it also depends on muscle length, contraction velocity, fibre type, and fat layer. Better wording: *EMG amplitude indexes activation; its relationship to force is monotonic but nonlinear/saturating.* |
| 3 | "EMG **directly** assesses muscle activation / effort" | It measures **electrical activation**, not effort or force directly. For long-term outcomes it is a **mixed surrogate** — see the free-weight-vs-machine meta-analysis (`25_...txt`) where higher acute activation did **not** mean more growth. Add this caveat. |
| 4 | "**GenENet** … achieved near lab-grade EMG performance" | True, **but** GenENet is for **hand-gesture recognition and gait prediction**, not strength training. It is **proof-of-concept** evidence for compact wearables, not validation of your use case. Don't overstate it as a strength-training result. |
| 5 | Textbook: "**Winter & Rivière**, *Electromyography: Physiology & Engineering*" | This citation looks conflated. Correct standard references: **Merletti & Parker (eds), *Electromyography: Physiology, Engineering and Non-Invasive Applications* (Wiley-IEEE, 2004)**; **Basmajian & De Luca, *Muscles Alive* (1985)**; and the free **Konrad, *The ABC of EMG* (Noraxon)**. |
| 6 | "**Eliseichev et al. (2022)** – *Review of Devices for sEMG*" | I could **not verify** this citation. Either supply a DOI or drop it; use `13`/`14` (Gomez-Correa; Côté-Allard) and `11` (Kim 2022) for device reviews instead. |
| 7 | "amplify the signal (gain ~100–1000)" | Fine, but add the specs that actually matter: **input impedance >10 MΩ (ideally 100 MΩ)**, **CMRR > 80–100 dB**, **input-referred noise < 1–5 µV RMS**, and a **driven reference / active ground**. |
| 8 | Fatigue "via shifts in frequency or amplitude" | Be specific: **median/mean power frequency shifts down**; RMS/amplitude often **rises** at fixed submaximal load. Give the direction. |

---

## 3. Additions now incorporated

Your report omits several things that matter for the DH803 project; these are now in the docs:

1. **Datasets** (Ninapro DB5/DB2/DB7, etc.) → `DATASETS_AND_HARDWARE.md` §1.
2. **Normalization methodology** (CEDE matrix, %MVC protocol) → `LITERATURE_REVIEW.md` §B; `PROJECT_PLAN.md` §8–9.
3. **Fatigue indices** (median frequency, STFT) → `LITERATURE_REVIEW.md` §C; `PROJECT_PLAN.md` §9.
4. **Rep/set detection & ML literature** (RecoFit, Soro, ExerSense, Prabhu) → `LITERATURE_REVIEW.md` §E.
5. **Mind–muscle connection evidence** (Calatayud, Schoenfeld, meta-analysis) → `LITERATURE_REVIEW.md` §F — this is the *scientific basis* for your product.
6. **Validation protocol** (concurrent validity, ICC, Bland–Altman, test–retest) → `PROJECT_PLAN.md` §12; templates in `06`/`07`.
7. **Surrogate-validity caution** → `README.md`, `PROJECT_PLAN.md` §3.
8. **SENIAM placement & crosstalk** → `LITERATURE_REVIEW.md` §A; `PROJECT_PLAN.md` §8.
9. **Hardware specifics & costs** (MyoWare 2.0, BITalino, AD8232/ADS1299) → `DATASETS_AND_HARDWARE.md` §2.
10. **Course building-block mapping + timeline + deliverables** → `PROJECT_PLAN.md` §2, §14, §15.

### New verified references added
- **Alcan & Zinnuroğlu (2023).** Current developments in surface electromyography. *Turk J Med Sci* 53(5):1019–1031. doi:10.55730/1300-0144.5667 — recent scoping review. → `41_...txt`
- **Phinyomark et al. (2019).** Surface EMG Signal Processing, Classification, and Practical Considerations (book chapter). doi:10.1007/978-981-13-9097-5_1 — feature/classifier challenges (paywalled). → listed
- **E-textile modular sEMG suit (2022).** *Sci Rep* 12:9650. doi:10.1038/s41598-022-13701-4 → `45_...pdf`
- **Stretchable array EMG + graph neural network (2023).** *npj Flexible Electronics*. doi:10.1038/s41528-023-00246-3 → `47_...pdf`
- **Body-scale textile EMG with coaxially shielded yarns (2025).** *Sci Adv* 11(42):eadx4518. doi:10.1126/sciadv.adx4518 → `48_...txt`
- **Karacan & Türker (2024).** A comparison of EMG techniques: surface vs intramuscular. *Eur J Appl Physiol.* (paywalled) — crosstalk, impedance, motion artifact.

---

## 4. Net effect

The project documents cover the **how, why, and evidence** for the two-channel activation concept. The photographed prototype parts are a generic ESP32-S3 N16R8 development board, one 3.7 V 1000 mAh Li-ion cell, an HW-373/TP4056-style charger, and one Muscle BioAmp-style EMG module (likely Candy, exact revision unconfirmed). The second channel and a regulated battery-to-5V path remain outstanding. Earlier FireBeetle assumptions are historical and superseded by the photographed controller. If Candy/BisCute is used, its fixed 72–720 Hz band is distinct from a conventional 20–450 Hz raw sEMG pipeline.

**Suggested merge:** keep your report as the "background/narrative" section and use `PROJECT_PLAN.md` + `LITERATURE_REVIEW.md` as the analytical backbone. Fix items 1–6 in §2 above before any submission.

---

## 5. Current-design interpretation corrections

- **%MVC is not %force.** CEDE states that EMG amplitude relates to activation but is affected by anatomy, tissue, electrode geometry and task context. The biomech slide's EMG/ MVC-to-force expression is a simplified model example; do not quote it as a general equality.
- **Two-channel ratio is exploratory.** Report both per-muscle %MVC-reference readings. A derived ratio is a within-person prototype index; it is not a validated co-activation, compensation or relative-force measure.
- **Frequency fatigue is conditional.** Median/mean frequency shifts are most interpretable in controlled sustained or slowly varying contractions with stable geometry. Dynamic repetitions introduce movement/placement confounds. Candy/BisCute fixed 72–720 Hz hardware also cannot deliver a conventional 20–450 Hz spectrum.
- **Attention evidence is task-limited.** Calatayud's threshold is from a specific bench-press experiment. The 2021 Grgic meta-analysis concerns strength, not EMG amplitude or hypertrophy. Schoenfeld's small 8-week study found elbow-flexor thickness favored internal focus; quadriceps thickness did not differ.
- **Older hardware BOM is superseded.** Do not order DFRobot SEN0240 or generic ESP32 solely from the earlier Assignment-2 files. Current status is in `CURRENT_DESIGN.md`.
