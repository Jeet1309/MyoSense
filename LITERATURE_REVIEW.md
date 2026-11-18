# LITERATURE REVIEW — Annotated Reading List
## Surface EMG wearables for muscle activation during strength training

Every entry gives: **citation → why it matters → where to find it** (downloaded file in `references/pdfs/`, or DOI for library access).
Tiers: **★ Start here** · **◆ Core** · **○ Supplementary** · **🔒 Paywalled (get via IITB library / interlibrary loan)**.

> **Current scope:** a two-channel target/comparison sEMG prototype with per-channel amplitude relative to a reference. The user has one photographed Muscle BioAmp-style module, likely Candy, but its exact model/revision is unconfirmed; a second channel is not yet available. If Candy is confirmed, its fixed 72–720 Hz analog bandwidth makes general 20–450 Hz and frequency-fatigue literature background, not a claim that this hardware reproduces those signals.

---

## A. Foundations of sEMG (what the signal is, how to detect it)

**★ Chowdhury et al. (2013). Surface Electromyography Signal Processing and Classification Techniques. *Sensors* 13(9):12431.** — DOI 10.3390/s130912431
Best single entry point: EMG generation, noise sources, filtering, features, classifiers, applications.
→ `03_Chowdhury2013_sEMG_processing_classification.pdf`

**◆ Merletti & Cerone (2020). Tutorial. Surface EMG detection, conditioning and pre-processing: Best practices. *J Electromyogr Kinesiol* 54:102440.** — DOI 10.1016/j.jelekin.2020.102440 🔒
The authoritative "how to acquire sEMG properly" guide: electrodes, electrode–skin interface, amplifier specs (input impedance, CMRR, noise), interference reduction, A/D.
→ Library.

**○ Merletti & Muceli (2019). Tutorial. Surface EMG detection in space and time: Best practices. *J Electromyogr Kinesiol*.** — DOI 10.1016/j.jelekin.2019.102363 🔒
Electrode size, inter-electrode distance, location, detection volume.

**◆ SENIAM — Hermens et al. (2000). Development of recommendations for SEMG sensors and sensor placement procedures. *J Electromyogr Kinesiol* 10(5):361–374.** — DOI 10.1016/S1050-6411(00)00027-4 🔒
The standard electrode-placement reference. 20 mm spacing and placement parallel to fibres are general recommendations; placement should be muscle-specific. Free resources: http://www.seniam.org (sensor placement PDFs).
→ Library / seniam.org.

**○ CEDE project — see normalization (B).**

---

## B. Signal processing, filtering, and normalization

**★ Besomi et al. (2020). Consensus for Experimental Design in Electromyography (CEDE) project: Amplitude normalization matrix. *J Electromyogr Kinesiol* 53:102438.** — DOI 10.1016/j.jelekin.2020.102438
Definitive guide to **normalizing EMG to %MVC** (and 5 other approaches), with pros/cons and reporting requirements. Your activation metric lives or dies on this.
→ `02_Besomi2020_CEDE_amplitude_normalization.pdf`

**★ Boyer et al. (2023). Reducing Noise, Artifacts and Interference in Single-Channel EMG Signals: A Review. *Sensors* 23(6):2927.** — DOI 10.3390/s23062927
Practical catalogue of motion artifact, power-line, ECG interference and the filters that remove them.
→ `05_Boyer2023_reducing_noise_artifacts_EMG_review.pdf`

**◆ De Luca et al. (2010). Filtering the surface EMG signal: Movement artifact and baseline noise contamination. *J Biomech* 43(8):1573–1579.** — DOI 10.1016/j.jbiomech.2010.01.027 🔒
Classic lower-corner guidance for a general-purpose pipeline; not universal. The analog front end's bandwidth determines what data remain available, and digital filtering cannot recover removed frequencies.
→ Library.

**◆ Muceli & Merletti (2024). Tutorial. Frequency analysis of the surface EMG signal: Best practices. *J Electromyogr Kinesiol* 79:102937.** — DOI 10.1016/j.jelekin.2024.102937
Fourier/PSD, sampling, filtering, stationarity, and frequency features. Dynamic muscle movement under electrodes can disrupt simple frequency-fatigue interpretation; see task-specific cautions. Free full text from Chalmers.
→ `33_Muceli2024_frequency_analysis_tutorial.pdf`

**◆ Clancy et al. (2023). Tutorial. Surface electromyogram (sEMG) amplitude estimation: best practices. *J Electromyogr Kinesiol* 72:102807.** — DOI 10.1016/j.jelekin.2023.102807 🔒
RMS/MAV/linear-envelope estimation, window sizes, smoothing. Companion to the frequency tutorial.

**○ Smart EMG envelope extraction & denoising (2023). *Sci Rep* 13.** — DOI 10.1038/s41598-023-33319-4
FFC (fast-Fourier-constant?) filter approach for power-line + motion artifact removal; envelope accuracy >0.94 correlation even with heavy noise.
→ `28_SmartEMGenvelope2023_denoising.pdf`

**○ Reaz et al. (2006). Techniques of EMG signal analysis: detection, processing, classification and applications.** — PMC3821366
Older but broad; good for background/definitions.

---

## C. EMG fatigue measurement

**★ Application of Surface Electromyography in Exercise Fatigue: A Review (2022). *Front Syst Neurosci* 16:893275.** — DOI 10.3389/fnsys.2022.893275
Time-domain (RMS/MAV), frequency-domain (MF/MDF) and time–frequency features for fatigue. Interpret them in relation to the contraction/task and sensor band; dynamic movement changes geometry and can confound spectra.
→ `15_ExerciseFatigue_sEMG_review2022.pdf`

**◆ Rodrigues et al. (2022). EMG Signal Processing for the Study of Localized Muscle Fatigue. *Int J Environ Res Public Health* 19(20):13270.** — DOI 10.3390/ijerph192013270
Pipeline and features for localized fatigue. Its controlled task is useful method background, not validation of median-frequency fatigue in moving gym repetitions.
→ `16_Rodrigues2022_EMG_localized_muscle_fatigue.pdf`

**◆ Allison & Fujiwara (2002). The relationship between EMG median frequency and low frequency band amplitude changes at different levels of muscle capacity. *Clin Biomech* 17(6):464–469.** — DOI 10.1016/S0268-0033(02)00033-5 🔒
Examines median-frequency and low-frequency-band changes in its experimental conditions; do not infer that spectral fatigue can be measured at low sample rates without checking bandwidth/Nyquist requirements.

**○ Slow-time changes in EMG fatigue states (J Biomech Eng / PMC9116448).** — full text `17_...` not downloaded (paywalled/DOI mismatch); optional.

**○ Rate of change in longitudinal EMG indicates neuromuscular adaptation (PMC9676259).** — full text
Longitudinal tracking of EMG amplitude slope over 100 days of hypertrophy vs endurance training — relevant to your "progress over weeks" feature.
→ `31_LongitudinalEMG_neuromuscular_adaptation.pdf`

---

## D. Wearable EMG devices: electrodes, hardware, and validation

### D1. Electrodes (dry/flexible/soft)
**★ Nunes & da Silva (2023). Characterization and Validation of Flexible Dry Electrodes for Wearable Integration. *Sensors* 23(3):1468.** — DOI 10.3390/s23031468
Silver/carbon/graphene dry electrodes vs Ag/AgCl gel; long-term monitoring rationale.
→ `09_Nunes2023_flexible_dry_electrodes.pdf`

**◆ Kim et al. (2022). Advances in Soft and Dry Electrodes for Wearable Health Monitoring Devices. *Micromachines* 13(4):629.** — DOI 10.3390/mi13040629
Review of soft/dry electrode materials and performance.
→ `11_Kim2022_soft_dry_electrodes_review.pdf`

**○ Myers et al. (2015). Wearable silver nanowire dry electrodes for electrophysiological sensing. *RSC Adv* 5:11627.** — DOI 10.1039/C4RA15160C
AgNW dry electrodes; comparable to Ag/AgCl at rest, fewer motion artifacts.
→ `12_Myers2015_silver_nanowire_dry_electrodes.pdf`

**○ Ruvalcaba et al. (2020). Wearable Active Electrode for sEMG Monitoring Using Two-Channel Brass Dry Electrodes. *J Healthc Eng* 2020:9652765.** — DOI 10.1155/2020/9652765
Custom active-electrode design, CMRR 96 dB, 15–450 Hz.
→ `10_Ruvalcaba2020_active_dry_electrode_sEMG.txt` (full text; PDF blocked)

### D2. Wearable systems & their validity
**★ Lynn et al. (2018). Validity and Reliability of Surface Electromyography Measurements from a Wearable Athlete Performance System (Athos). *J Sports Sci Med* 17(2):205–215.** — PMC5950737
The template for validating a garment-embedded sEMG system vs research-grade (Biopac): torque–EMG relationship, reliability, contact-quality caveats.
→ `06_Lynn2018_Athos_wearable_validity.txt` (full text; PDF blocked)

**◆ Molina-Molina et al. (2020). Validation of mDurance, A Wearable Surface Electromyography System for Muscle Activity Assessment. *Frontiers in Physiology* 11:606287.** — DOI 10.3389/fphys.2020.606287
Second validation template (Shimmer + app vs Delsys): concurrent validity, ICC, Bland–Altman.
→ `07_MolinaMolina2020_mDurance_validation.pdf`

**○ Reliability and validity of muscle activity analysis using wearable electromyographs (NOK, 2024).** — PMC10904218
Rubberized no-electrode wearable vs Delsys.
→ `08_NOK2024_wearable_EMG_reliability.pdf`

**○ Gomez-Correa & Cruz-Ortiz (2022). Low-Cost Wearable Band Sensors of Surface Electromyography for Detecting Hand Movements. *Sensors* 22(16):5931.** — DOI 10.3390/s22165931
DIY armband design (WyoFlex, ESP32, DFRobot sensors) — directly reusable build.
→ `13_LowCost2022_wearable_band_sEMG_hand.pdf`

**○ Côté-Allard et al. (2019). A Low-Cost, Wireless, 3-D-Printed Custom Armband for sEMG Hand Gesture Recognition. *Sensors* 19(12):2811.** — DOI 10.3390/s19122811
10-channel custom armband vs Myo; open hardware (Github) — useful if you go custom.
→ `14_3DC2019_lowcost_3Dprinted_armband_sEMG.pdf`

**○ Deep Learning Model Coupling Wearable Bioelectric and Mechanical Sensors for Refined Muscle Strength Assessment (2024). *Research* 7:0366.** — DOI 10.34133/research.0366
sEMG + strain sensor fusion + TCN-Transformer for muscle-strength grading — a "sensor fusion" direction.
→ `30_DeepLearning_bioelectric_mechanical_muscle_strength.txt` (full text)

**○ Towards Soft Wearable Strain Sensors for Muscle Activity Monitoring (2022). *IEEE TNSRE*.** — PMC9421605
Mechanomyography alternative: soft strain sensors track muscle deformation/torque.
→ `29_SoftStrainSensors_muscle_activity2022.pdf`

---

## E. Machine learning for exercise recognition, rep counting, and EMG

**★ Soro et al. (2019). Recognition and Repetition Counting for Complex Physical Exercises with Deep Learning. *Sensors* 19(3):714.** — DOI 10.3390/s19030714
CNN on smartwatch IMU; 99.96% exercise recognition, ±1 rep in 91% of sets. Rep-counting blueprint.
→ `18_Soro2019_deeplearning_exercise_recognition_counting.pdf`

**★ Morris et al. (2014). RecoFit: Using a Wearable Sensor to Find, Recognize, and Count Repetitive Exercises. *ACM CHI*.** — Microsoft Research
Seminal strength-training tracking paper: segmentation, recognition, rep counting from an arm-worn IMU; SVM + 224 features. Free PDF.
→ `22_RecoFit2014_wearable_recognize_count_exercises.pdf`

**◆ Ishii et al. (2020). ExerSense: Physical Exercise Recognition and Counting from Wearables Robust to Positioning. *Sensors* 21(1):60.** — DOI 10.3390/s21010060
Correlation-based real-time recognition robust to sensor position; compares with ML.
→ `19_ExerSense2020_exercise_recognition_counting.pdf`

**◆ Prabhu et al. (2020). Recognition and Repetition Counting for Local Muscular Endurance Exercises. *Sensors* 20(18):5419.** — DOI 10.3390/s20185419
Wearable exercise recognition/counting for rehabilitation.
→ `20_Prabhu2020_repetition_counting_local_muscular.pdf`

**○ Geng et al. (2016). Gesture recognition by instantaneous surface EMG images. *Sci Rep* 6:36571.** — DOI 10.1038/srep36571
High-density sEMG image + CNN; state-of-the-art gesture recognition on Ninapro/CapgMyo. Useful if you add an ML/gesture angle.
→ `21_Geng2016_instantaneous_sEMG_images_gesture.txt` (full text; Nature PDF blocked)

**○ A Large-Scale Wearable Sensor Dataset for Exercise Motion Classification with CNN (2016). arXiv:1610.07031.** — 50-class exercise classification, 92.14% accuracy.
→ `23_ExerciseMotionCNN2016_largescale.pdf`

**○ Hybrid CNN-Dilated Self-attention using Inertial and Body-Area Electrostatic Sensing for Gym Workout Recognition (2025). arXiv:2503.06311.** — Modern multimodal gym-workout recognition/counting.
→ `24_HybridCNN2025_gym_workout_recognition.pdf`

---

## F. Strength-training science: activation, attention, and hypertrophy

**★ Calatayud et al. (2016). Importance of mind–muscle connection during progressive resistance training. *Eur J Appl Physiol* 116(3):527–533.** — DOI 10.1007/s00421-015-3305-7 🔒
In 18 resistance-trained men performing bench press, target-focus cues changed muscle EMG at 20–60% 1RM but not at 80% in that protocol. This is task-specific evidence for a cue pilot, not a universal threshold.

**★ Schoenfeld et al. (2018). Differential effects of attentional focus strategies during long-term resistance training. *Eur J Sport Sci* 18(5):705–712.** — DOI 10.1080/17461391.2018.1447020 🔒
Small 8-week study in untrained men: elbow-flexor thickness favored internal focus; quadriceps thickness did not differ. Supports a limited hypothesis, not a general promise.

**◆ Haugen et al. (2023). Effect of free-weight vs. machine-based strength training on maximal strength, hypertrophy and jump performance — systematic review & meta-analysis. *BMC Sports Sci Med Rehabil* 15:103.** — DOI 10.1186/s13102-023-00713-4
Pooled long-term outcomes were broadly similar between modalities. Acute EMG differences alone do not establish that one modality produces more growth.
→ `25_Haugen2023_freeweight_vs_machine_meta.txt` (full text)

**◆ Lacerda et al. (2021). Resistance training with different repetition duration to failure: effect on hypertrophy, strength and muscle activation. *PeerJ* 9:e10939.** — PMC7916538
Higher EMG amplitude (shorter rep duration) vs longer time-under-tension → similar hypertrophy. Good for your "activation ≠ growth" nuance.
→ `26_Lacerda2021_repetition_duration_hypertrophy_EMG.pdf`

**◆ Grgic, Mikulic & Mikulic (2021). Acute and Long-Term Effects of Attentional Focus Strategies on Muscular Strength: A Meta-Analysis. *Sports* 9(11):153.** — DOI 10.3390/sports9110153
Strength outcomes only: external focus favored acute strength; the main long-term strength comparison was not significant. This is not an EMG-amplitude or hypertrophy meta-analysis.
→ `27_AttentionalFocus_meta_analysis2021.pdf`

**○ Kristiansen et al. (2018). External and internal focus of attention increases muscular activation during bench press. *J Strength Cond Res* 32(9):2442–2451.** — DOI 10.1519/JSC.0000000000002613 🔒
Both focus types raised EMG vs baseline in 6 upper-body muscles.

**○ Paoli et al. (2019). Mind–muscle connection: effects of verbal instructions on muscle activity during bench press. *Eur J Transl Myol* 29(2):8250.** — PMC. Free.

### F1. Exercise-pair pilot evidence (task-specific, not form diagnoses)

**Sevilmis et al. (2024). The Disconnect Between Soccer Players' Perceived and Actual Electromyographic-Measured Muscle Activation. *Perceptual and Motor Skills*.** — DOI 10.1177/00315125241279086
Small study of male sub-elite soccer players across six upper-body exercises. Useful motivation for measuring rather than relying only on perceived activation; its sample and exercises limit generalization.

**Lehman et al. (2004). Variations in muscle activation levels during traditional latissimus dorsi weight training exercises. *Dynamic Medicine* 3:4.** — DOI 10.1186/1476-5918-3-4
Measures latissimus dorsi, biceps and mid-trapezius/rhomboids across pulldown/row variations. It reports exercise-dependent ratios and substantial participant variability; it does not establish a universal “arms take over” threshold.

**Stastny et al. (2017). A systematic review of surface electromyography analyses of the bench press movement task. *PLoS One* 12(2):e0171632.** — DOI 10.1371/journal.pone.0171632
Shows that bench-press EMG patterns vary with intensity, movement phase, stability and cues. Helpful for choosing/standardizing a test, not for judging form from one channel.

**Coratella et al. (2020). An Electromyographic Analysis of Lateral Raise Variations and Frontal Raise in Competitive Bodybuilders. *Int J Environ Res Public Health* 17(17):6015.** — DOI 10.3390/ijerph17176015
Small exercise-variation study of shoulder muscles. Use to motivate a lateral-raise pilot while recognizing that its participants and specific variants limit generalization.

> **Interpretation across exercise papers:** compare each muscle's own standardized reference, state the task and electrode setup, and show both channel values. A ratio derived from two %MVC values is an exploratory project index, not a validated force-sharing, “co-activation,” or technique-correctness measure.

**○ Schick et al. (2010). A comparison of muscle activation between a Smith machine and free weight bench press. *J Strength Cond Res* 24(3):779–784.** — DOI 10.1519/JSC.0b013e3181cc2237 🔒
Classic free-weight vs machine EMG comparison.

---

## G. Datasets

**★ Ninapro (Non-Invasive Adaptive Prosthetics) database.** — https://ninapro.hevs.ch
Largest public sEMG benchmark. **DB5** (Thalmic Myo armband, 16 channels, 200 Hz) is closest to a consumer wearable; DB2/DB7 use Delsys Trigno. Cite Atzori et al. (2015), DOI 10.1109/EMBC.2015.7320041.
→ See `DATASETS_AND_HARDWARE.md`.

**○ Assessment of EMG Benchmark Data for Gesture Recognition (Chang et al., 2020).** — DOI 10.1109/JBHI.2020.3025997 🔒
Critically evaluates Ninapro signal quality — read before trusting the benchmark.

---

## H. Standards, guidelines, and materials

- **SENIAM** recommendations (electrodes, placement, signal processing): http://www.seniam.org
- **CEDE** (Consensus for Experimental Design in EMG): https://isek.org/cede/
- **ISO 10993-1** — biological evaluation of medical devices (biocompatibility) — relevant if you touch skin/wear long-term.
- **ISO 2137 / ASTM D2979** — adhesive tack (course material on adhesives).
- **IEEE 802.15.1 (Bluetooth) / BLE** — your communication layer.
- Course references: Kaniusas, *Biomedical Signals and Sensors I*; Sazonov & Neuman, *Wearable Sensors* (2020); Godfrey & Stuart, *Digital Health* (2021).

---

## I. Industry & commercial landscape (for your "current solutions" section)

**★ Myontec (Finland).** Wearable **EMG smart clothing** (Mbody shorts/sleeve + MCell unit) that measures real-time muscle **load, balance, activation order, and fatigue**; commercial, used in elite sport and research. https://www.myontec.com
→ Validation study: Belbasis et al. (2018), *Muscle Performance Investigated With a Novel Smart Compression Garment*, PMC5917022.

**◆ Athos** — compression garments with embedded sEMG (validated by Lynn 2018, `06_...txt`); the canonical "smart apparel" EMG product.

**◆ Delsys Trigno** — wireless research-grade EMG; the reference system in most validation papers. Not a consumer product.

**◆ Thalmic Myo armband** — 8-channel sEMG + IMU, 200 Hz; discontinued but ubiquitous in research (Ninapro DB5).

**○ Sensoria** — pressure/IMU running wearables (course example, Class 10).

**○ OYMotion gForce** — 8-channel sEMG armband with IMU + BLE.

**○ GenENet (Stanford, 2025)** — compact 6-channel stretchable EMG device + generative network that reconstructs high-density muscle activity; proof of concept for low-channel wearables. → `40_GenENet2025_NatureSensors_generative_EMG.pdf`

> Positioning: consumer EMG apparel exists (Myontec, Athos) but is expensive and mostly **load/balance** oriented. Your differentiator is **real-time %MVC + mind–muscle biofeedback** at a low-cost, single/dual-channel form factor.

---

## J. Recent wearable-EMG hardware advances (2022–2025)

- **E-textile based modular sEMG suit for large-area level-of-effort analysis (2022).** *Sci Rep* 12:9650. doi:10.1038/s41598-022-13701-4 → `45_ETextile2022_modular_sEMG_suit.pdf`
- **Stretchable array EMG sensor + graph neural network for gesture recognition (2023).** *npj Flexible Electronics*. doi:10.1038/s41528-023-00246-3 → `47_StretchableArrayEMG_GNN2023.pdf`
- **Body-scale textile EMG with coaxially shielded conductive yarns (2025).** *Sci Adv* 11(42):eadx4518. doi:10.1126/sciadv.adx4518 → `48_BodyScaleTextileEMG2025_SciAdv.txt`
- **Alcan & Zinnuroğlu (2023).** Current developments in surface electromyography. *Turk J Med Sci* 53(5):1019–1031. doi:10.55730/1300-0144.5667 → `41_Alcan2023_current_developments_surface_EMG.txt`
- **Karacan & Türker (2024).** A comparison of EMG techniques: surface vs intramuscular. *Eur J Appl Physiol.* doi:10.1007/s00421-024-05611-2 🔒 (crosstalk, impedance, motion artifact, technique selection)
- **Phinyomark et al. (2019).** Surface EMG Signal Processing, Classification, and Practical Considerations (book chapter). doi:10.1007/978-981-13-9097-5_1 🔒 (feature/classifier challenges under dynamic conditions)

---

## Reading order suggestion

1. `03` Chowdhury (overview) →
2. `02` Besomi (normalization) →
3. `33` Muceli (frequency/fatigue) →
4. `05` Boyer (noise) →
5. `06` Lynn + `07` Molina-Molina (validation) →
6. `09`/`11` electrodes →
7. `18`/`22` rep counting →
8. `15` fatigue review →
9. mind–muscle `35`/`36`/`27` →
10. `25` surrogate caution.
