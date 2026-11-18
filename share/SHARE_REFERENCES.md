# Share Pack Reference Map

The reader guide and numbered citations use the numbers below. Locally held open-access PDFs selected for this guide are copied unchanged into `references/`. Other source files remain in the parent project's `references/pdfs/` or are linked by DOI. Hardware entries include comparison/older-plan parts and should not be mistaken for the photographed prototype BOM unless explicitly stated.

## Core local references bundled here

| Guide citation | Bundled file | Why it is included |
|---|---|---|
| [1] | `references/02_Besomi2020_CEDE_amplitude_normalization.pdf` | CEDE normalization choices, interpretation and reporting checklist |
| [2] | `references/03_Chowdhury2013_sEMG_processing_classification.pdf` | Introductory sEMG, artefacts, processing and classification review |
| [3] | `references/33_Muceli2024_frequency_analysis_tutorial.pdf` | Sampling, bandwidth, stationarity, PSD and fatigue-frequency best practices |
| [5] | `references/15_ExerciseFatigue_sEMG_review2022.pdf` | Exercise-fatigue review; features depend on task and measurement conditions |
| [6] | `references/16_Rodrigues2022_EMG_localized_muscle_fatigue.pdf` | Localized fatigue processing in a small, controlled task |
| [13] | `references/27_AttentionalFocus_meta_analysis2021.pdf` | Attentional focus effects on strength; not an EMG-amplitude or hypertrophy meta-analysis |
| Supplement | `references/05_Boyer2023_reducing_noise_artifacts_EMG_review.pdf` | Noise, motion artifacts and interference |
| Supplement | `references/07_MolinaMolina2020_mDurance_validation.pdf` | Wearable sEMG validation and agreement methods |
| Supplement | `references/09_Nunes2023_flexible_dry_electrodes.pdf` | Flexible dry electrode characterization |
| Supplement | `references/11_Kim2022_soft_dry_electrodes_review.pdf` | Soft/dry electrode materials and wearable trade-offs |
| Supplement | `references/13_LowCost2022_wearable_band_sEMG_hand.pdf` | Low-cost ESP32/DFRobot armband example; not the selected front end |

## Course material referenced but not redistributed in this pack

- `../biomech/S05E06 - Muscles and Tendons.pdf`: contraction modes, force-length, load-velocity, agonists/synergists and muscle architecture.
- `../biomech/S05E07 - Mechanics.pdf`: muscle force/moment context and an EMG/MVC example. Its EMG-to-force equation is a simplified biomechanical model, **not a general identity**; read alongside CEDE [1].
- `../biomech/S05E02 - Introduction to joint anatomy.pdf` and other S05 lectures: anatomy/background.
- Wrist PDFs R1/R2 are from a separate wrist-ROM project. They are not EMG theory sources; their repeatability/agreement methods may be useful by analogy only.

## Numbered references and hardware documentation

1. **Besomi M, et al. (2020).** Consensus for Experimental Design in Electromyography (CEDE) project: Amplitude normalization matrix. *J Electromyogr Kinesiol* 53:102438. https://doi.org/10.1016/j.jelekin.2020.102438
2. **Chowdhury RH, et al. (2013).** Surface Electromyography Signal Processing and Classification Techniques. *Sensors* 13(9):12431–12466. https://doi.org/10.3390/s130912431
3. **Muceli S, Merletti R (2024).** Tutorial. Frequency analysis of the surface EMG signal: Best practices. *J Electromyogr Kinesiol* 79:102937. https://doi.org/10.1016/j.jelekin.2024.102937
4. **Hermens HJ, et al. (2000).** Development of recommendations for SEMG sensors and sensor placement procedures (SENIAM). *J Electromyogr Kinesiol* 10(5):361–374. https://doi.org/10.1016/S1050-6411(00)00027-4. Free placement summaries: http://www.seniam.org/
5. **Sun J, et al. (2022).** Application of Surface Electromyography in Exercise Fatigue: A Review. *Front Syst Neurosci* 16:893275. https://doi.org/10.3389/fnsys.2022.893275
6. **Rodrigues SB, et al. (2022).** EMG Signal Processing for the Study of Localized Muscle Fatigue. *Int J Environ Res Public Health* 19(20):13270. https://doi.org/10.3390/ijerph192013270
7. **Calatayud J, et al. (2016).** Importance of mind-muscle connection during progressive resistance training. *Eur J Appl Physiol* 116:527–533. https://doi.org/10.1007/s00421-015-3305-7
8. **Sevilmis E, et al. (2024).** The Disconnect Between Soccer Players' Perceived and Actual Electromyographic-Measured Muscle Activation. *Perceptual and Motor Skills*. https://doi.org/10.1177/00315125241279086. Findings are limited to the study's small, specific sample and exercise set.
9. **Lehman GJ, et al. (2004).** Variations in muscle activation levels during traditional latissimus dorsi weight training exercises. *Dynamic Medicine* 3:4. https://doi.org/10.1186/1476-5918-3-4
10. **Stastny P, et al. (2017).** A systematic review of surface electromyography analyses of the bench press movement task. *PLoS One* 12(2):e0171632. https://doi.org/10.1371/journal.pone.0171632
11. **Coratella G, et al. (2020).** An Electromyographic Analysis of Lateral Raise Variations and Frontal Raise in Competitive Bodybuilders. *Int J Environ Res Public Health* 17(17):6015. https://doi.org/10.3390/ijerph17176015
12. **Schoenfeld BJ, et al. (2018).** Differential effects of attentional focus strategies during long-term resistance training. *Eur J Sport Sci* 18(5):705–712. https://doi.org/10.1080/17461391.2018.1447020. In this small 8-week study, elbow-flexor thickness favored internal focus; quadriceps thickness did not differ.
13. **Grgic J, Mikulic I, Mikulic P (2021).** Acute and Long-Term Effects of Attentional Focus Strategies on Muscular Strength: A Meta-Analysis. *Sports* 9(11):153. https://doi.org/10.3390/sports9110153. This reviews strength outcomes, not EMG amplitude or hypertrophy.
14. DFRobot. **FireBeetle 2 ESP32-S3 AI Board with OV2640 camera, DFR0975 documentation.** https://wiki.dfrobot.com/dfr0975/
15. **De Luca CJ, et al. (2010).** Filtering the surface EMG signal: Movement artifact and baseline noise contamination. *J Biomech* 43(8):1573–1579. https://doi.org/10.1016/j.jbiomech.2010.01.027
16. Upside Down Labs. **Muscle BioAmp Candy** specifications and hookup guide. https://docs.upsidedownlabs.tech/hardware/bioamp/muscle-bioamp-candy/index.html
17. Upside Down Labs. **Muscle BioAmp BisCute** specifications and build guide. https://docs.upsidedownlabs.tech/hardware/bioamp/muscle-bioamp-biscute/index.html
18. Upside Down Labs. **BioAmp EXG Pill** documentation and revision/configuration notes. https://docs.upsidedownlabs.tech/hardware/bioamp/bioamp-exg-pill/
19. DFRobot/OYMotion. **Gravity Analog EMG Sensor SEN0240.** https://wiki.dfrobot.com/sen0240/
20. Thingbits Electronics. **3.7 V 1000 mAh Li-ion-polymer battery listing.** https://www.thingbits.in/products/lithium-ion-polymer-battery-3-7v-1000mah
21. **Haugen ME, et al. (2023).** Free-weight vs machine-based strength training: systematic review and meta-analysis. *BMC Sports Sci Med Rehabil* 15:103. https://doi.org/10.1186/s13102-023-00713-4. Full text is retained in the parent project archive as `../references/pdfs/25_Haugen2023_freeweight_vs_machine_meta.txt` and is not duplicated in this pack.

## Citation corrections from the older project index

- Clancy et al. (2023) amplitude-estimation tutorial DOI is **10.1016/j.jelekin.2023.102807**, not `102761`; the correct citation appears in Muceli & Merletti [3]'s bibliography.
- The 2021 Grgic et al. meta-analysis is about **strength**. Do not cite it as an EMG-amplitude or hypertrophy meta-analysis.
- The 2026 wearable-fatigue review entry previously in the main index had a mismatched journal/DOI and is removed until bibliographic details are verified.
- Buonsenso et al. (2025) should not be described as validating a primary/helper compensation index. It is an exercise-variant EMG study; verify its final bibliographic details before citing it.

## Hardware documentation

- FireBeetle 2 ESP32-S3 N16R8, an earlier comparison option and not the photographed controller: [14].
- Candy: [16]. BisCute: [17]. EXG Pill: [18]. SEN0240: [19].
- Thingbits 3.7 V 1000 mAh battery listing, a candidate from the earlier BOM; the user's current cell model is unverified: [20].
