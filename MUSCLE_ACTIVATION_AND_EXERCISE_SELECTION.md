# MUSCLE ACTIVATION & EXERCISE SELECTION
## How the body makes the EMG signal, how it varies with exercise, and how to use the 2-muscle (%MVC ratio) prototype

*DH803 — Wearable Health Technologies · Jeet Gurbani (23B0023)*
Companion to `STUDY_GUIDE.md` (deep-dive on **M9** and **M10**). Written in the
"explain it simply, with examples" style. No sensor electronics here — only what
the **body** does before any electrode sees it.

> **Current-design correction:** this is a learning note, not the final hardware specification. The current design status and corrected project guide are in `CURRENT_DESIGN.md` and `share/EMG_WEARABLE_FROM_SCRATCH.md`. A two-muscle ratio is exploratory; it does not diagnose compensation or compare force.

---

## PART A — THE PHYSIOLOGY, SIMPLIFIED

### A1. The basics: where the electricity comes from
- Every muscle cell is a tiny battery: **negative inside (~ −80 mV)** because the
  Na⁺/K⁺ pump pushes 3 Na⁺ out for every 2 K⁺ in, and the membrane leaks K⁺ out.
- A nerve "pulse" (action potential, **AP**) is **all-or-nothing**: Na⁺ rushes in,
  the cell flips positive, then K⁺ leaves and it resets (refractory period). This
  is the electrical event.
- The AP travels to the muscle, releases **calcium**, and calcium makes the
  myofilaments pull. So the chain is:

  **pulse (electrical) → calcium (biochemical) → contraction (mechanical)**

  The pulse is the cause; the pull is the effect. Your electrodes see the **pulse**,
  not the pull. *(This same chain is drawn on the biomech slide S05E06 pp. 12 & 19.)*

### A2. Motor units — the part that matters
One α-motor neuron + **all** the muscle fibres it innervates = **one motor unit (MU)**.

- A pulse from that nerve fires **all** its fibres at once → the summed electrical
  spike is the **MUAP (motor unit action potential)**.
- The brain increases force in **two ways**:
  - **Recruitment** — switch on *more* MUs (small/slow units first, "size principle").
  - **Rate coding** — fire the *same* units faster.
- At the skin, **thousands of MUAPs overlap in time and space** = the blurry
  "**interference pattern**" you actually record.
- **Firing rate** ≈ 8–40 Hz; **MUAP duration** ≈ 5–15 ms.

> **Example:** lift a light cup → few small MUs, slow firing → small EMG.
> Grind out a heavy curl → many MUs, fast firing → big EMG.
> **EMG amplitude ≈ how hard the nervous system is driving the muscle — not the
> weight on the bar.**

### A3. Getting to the skin (brief)
- The AP travels along the fibre as a moving charge wave. Muscle, fat and skin
  **smear and weaken** it (volume conduction). **More fat = weaker signal.**
- Recorded signal = **sum of many MUAPs, low-pass filtered by the tissue in between.**
- A **bipolar pair** oriented along the fibres subtracts the travelling wave as it
  passes electrode 1 then electrode 2 → the classic biphasic pulse.

---

## PART B — HOW ACTIVATION VARIES ACROSS EXERCISES

Think of three "knobs" an exercise turns:

| Knob | Plain meaning | Effect on EMG |
|---|---|---|
| **Neural drive** | how many MUs + how fast | more load/effort → more EMG |
| **Muscle length** | where you are in the range | length and angle affect mechanics and recorded EMG; effects depend on task |
| **Contraction mode** | concentric vs eccentric | patterns can differ; there is no universal higher-EMG phase |

Fuller table:

| Situation | What happens | Why it matters to this project |
|---|---|---|
| **Sustained isometric hold** | At controlled, steady force, RMS may rise and spectral frequency may fall with fatigue | Possible fatigue test; control force, posture and electrode geometry |
| **Concentric (lifting)** | Pattern varies by exercise, phase and load | Rep-phase feature, not inherently the harder phase |
| **Eccentric (lowering)** | Pattern varies by exercise, phase and load | Don't infer effort from contraction mode alone |
| **Heavier load** | more recruitment + faster firing | %MVC climbs toward 100 |
| **Light/moderate load** | A cue may change target EMG in some tasks | Calatayud's 20–60% 1RM result was specific to bench press and its study sample |
| **Different joint angle** | length changes + electrode shifts | EMG changes without effort changing (confound) |
| **Faster rep** | more concentric EMG | tempo changes the number |
| **Isolation exercise** | one muscle dominates | cleaner signal, less crosstalk |
| **Compound exercise** | helpers + stabilisers + crosstalk | blurrier picture; more muscles to watch |
| **Dynamic fatiguing set** | EMG amplitude/spectrum can change for several reasons | Simple median-frequency slope is not a stand-alone fatigue detector |

*(The biomech slides support each row: **force–length** S05E06 pp. 17–18;
**load–velocity** S05E06 p. 23; **concentric/eccentric/isometric** S05E06 p. 22;
**agonist/synergist/antagonist** S05E06 pp. 30–31; **pennation & PCSA** S05E06 pp. 27–29.)*

---

## PART C — WHAT THIS MEANS FOR THE WEARABLE (plain version)

Take a **biceps curl**:
1. You curl up → the biceps' MUs fire → a burst of EMG.
2. The device **rectifies + smooths** that burst into a hill (the **envelope**).
3. Each curl = **one hill** → count hills → **count reps**.
4. Taller hill = more activation → **%MVC gauge**.
5. In a controlled sustained contraction, RMS may rise and spectrum may shift down as
   fatigue develops. During dynamic reps, movement and changing geometry also affect
   the signal; treat these as features to validate, not an automatic fatigue verdict.
6. But the number is **activation, not force**. 80% MVC does **not** promise growth.
   Claim *"measure and improve muscle activation / mind–muscle connection,"* never
   *"guarantees more muscle."*

---

## PART D — THE 2-MUSCLE PROTOTYPE (%MVC RATIO)

The prototype may record **two muscles (target + comparison)** and normalize each
channel to its own MVC reference. Show both values. A ratio is a **project-defined,
exploratory within-person index**, not a standardized compensation measure or force-
sharing metric. Co-activation usually refers specifically to simultaneous agonist–
antagonist activity, not any pair of muscles.

**Method**
1. Measure each muscle separately.
2. Normalise each to **its own MVC** → `%MVC_primary`, `%MVC_secondary`.
3. Optionally calculate **comparison index = %MVC_comparison ÷ %MVC_target** under
   one repeatable protocol. Interpret it only as a change in the two recorded signals;
   a high value does not establish that the comparison muscle produced more force or
   took over the task.

**The single most important article for the motivation** (not yet in `references/pdfs/`):
> **Sevilmiş E, Atalağ O, Baytaş E, Henselmans M, Balyan M, Binboğa E (2024).
> "The Disconnect Between Soccer Players' Perceived and Actual Electromyographic-
> Measured Muscle Activation."**
> This study tested a small, specific sample (13 male sub-elite soccer players) across
> six upper-body exercises at 4–6RM. It reported poor correspondence between perceived
> and measured activation in those conditions. Use it as motivation to test feedback,
> not as proof that all lifters cannot feel target-muscle activity.

### Where to use it — exercises with a real, documented primary/secondary problem

| Exercise candidate | Target/comparison sites | Why it is a candidate (not a universal “form problem”) | Evidence and limits |
|---|---|---|---|
| **Lateral raise** | middle deltoid / upper trapezius | Variations can change recorded muscle patterns | Coratella 2020 studied variations in competitive bodybuilders; placement and crosstalk remain limits |
| **Bench press** | pectoralis / triceps (optionally anterior deltoid) | Multi-joint press with load- and phase-dependent patterns | Stastny 2017 review; Calatayud 2016 tested cues at specific bench loads in 18 trained men |
| **Lat pulldown** | latissimus / biceps | Published example measured both and compared activation ratios | Lehman 2004 found substantial person-to-person variability; not proof biceps universally takes over |
| **Hip thrust / squat / RDL** | gluteus / hamstrings or erector spinae | Different joint demands and muscle lengths | Use exercise-specific studies; an EMG difference alone does not establish a better exercise or technique |

**Recommended first targets for a 2-channel build:**
- **Lat pulldown — lats vs biceps** (both measured in published work; test placement and crosstalk carefully).
- **Bench/chest press — pectoralis vs triceps** (well-studied; use a stable machine variation for the first pilot if available).
- **Lateral raise — middle deltoid vs upper trapezius** (exercise variation has been studied; the sites are close, so crosstalk is a concern).

### Three rules the literature imposes
1. For an attentional-focus pilot, start at a light-to-moderate load. Calatayud et al.
   found cue-related EMG changes at 20–60% 1RM but not at 80% **in their bench-press
   protocol**; this is not a universal threshold across exercises or people.
2. A stable machine may reduce movement/placement variability in an initial pilot,
   but do not assume machines universally produce more selective activation than free
   weights without testing the specific task.
3. **Expect large person-to-person variation** (Lehman 2004: "large variability across
   subjects"). So position it as **within-person biofeedback** ("watch *your* ratio
   change rep to rep"), **not** a cross-person scoreboard.

### Corroborating evidence for the "mind–muscle connection" claim
- **Calatayud et al. (2016)** — in their bench-press protocol, focusing on a muscle raised its EMG at 20–60% 1RM, not at 80%.
- **Schoenfeld et al. (2018)** — in a small 8-week study of untrained men, elbow-flexor
  thickness favored internal focus; quadriceps thickness did not differ.
- **Henselmans (2023)** — explains *why* people misjudge: what you "feel" is mostly
  metabolic burn / stretch, not mechanical tension (an accessible summary of the
  Mitsuya 2023 sensory study).

### Honest limitations to state in the report
- Sevilmis et al. studied one small, specific sample and exercise set; do not generalize
  its findings to all lifters.
- A two-channel ratio is not a force-sharing, technique-correctness or validated
  compensation measure. The testable product value is whether repeatable feedback
  changes recorded within-person signals.
- Normalized amplitude relates to activation under a stated setup; it is not force or
  growth. CEDE cautions that EMG cannot reveal absolute force contributions of muscles
  with different sizes and architectures.

---

## PART E — WHAT THE ADDED RESOURCES CONTRIBUTE

### E1. Biomech slides — ME 6114 Joint Biomechanics (Darshan S. Shah, BiOME Lab, IITB, 2026)
Folder: `project/biomech/` (S05E01 … S05E08).

**Directly on-target:**
- **`S05E07 – Mechanics`, slide 9** states that EMG measures activation, not force,
  and presents `%act = EMG_task / EMG_MVC` in a simplified force-estimation example.
  Treat the further equality to a force fraction as a model assumption, **not a general
  measurement identity**. Use CEDE [1] for interpretation.
- **`S05E07`, slide 10** is your **workflow** exactly: break the task into joint
  motions → guess the muscles → place EMG on all → record task EMG → record isolated
  MVCs → compute `%act` → use PCSA, θ and σ to estimate force.

**Supporting theory:**
- `S05E06 – Muscles and Tendons`: electrical→biochemical→mechanical chain (pp. 12, 19);
  muscle structure & fibres (p. 10); **force–length** relationship (pp. 17–18);
  **load–velocity** (p. 23); **concentric/eccentric/isometric** (p. 22);
  **agonist/synergist/antagonist** (pp. 30–31); **architecture & pennation**
  (pp. 27–29); **Hill muscle–tendon model** (pp. 36–37); tendon/ligament properties (pp. 34–35).
- `S05E07`: levers and mechanical advantage (pp. 12–15); joint ROM and active vs
  passive ROM (pp. 4–6) — useful when you argue that EMG changes with joint angle.
- `S05E01` course overview, `S05E02` joint anatomy, `S05E03` bones, `S05E04`
  ligaments, `S05E05` cartilage, `S05E08` spine — background only.

### E2. Wrist resources (different project — methods examples only)
These concern **wrist kinematics/ROM**, not EMG. They do not inform muscle-activation
theory. Their validation methods may be useful by analogy, but the wrist-IMU protocols
are not EMG validation protocols:
- `R1.pdf` — **Ruby LK, Cooney WP, An KN, Linscheid RL, Chao EYS (1988).** *Relative
  motion of selected carpal bones: a kinematic analysis of the normal wrist.*
  J Hand Surg Am 13(1):1–10. (Wrist axes: y = flex/ext, z = radial/ulnar, x = pron/sup.)
- `R2.pdf` — **Ryu J, Cooney WP, Askew LJ, An KN, Chao EYS (1991).** *Functional ranges
  of motion of the wrist joint.* J Hand Surg Am 16(3):409–419. (Functional ROM: 60°
  extension, 54° flexion, 40° ulnar, 17° radial.)
- `Wrist_ROM_Mini_Literature_Review_and_Pilot_Study.pdf`, `Wrist joint project at a
  glance.pdf`, `Team8_stage2_report.pdf` — own/team wrist-IMU pilot documents.
- **Potentially reusable methods:** RMSE, Pearson r, **Bland–Altman** limits of
  agreement, and test–retest reliability. Select/adapt them to an EMG reference design.

---

## PART F — REFERENCE TRAIL

### Peer-reviewed — exercise EMG & activation ratio
| Citation | Why |
|---|---|
| Sevilmis E, et al. (2024). The Disconnect Between Soccer Players' Perceived and Actual Electromyographic-Measured Muscle Activation. *Perceptual and Motor Skills*. doi:10.1177/00315125241279086 | Perception vs measured activation in a specific sample |
| Contreras B, et al. (2015). A Comparison of Gluteus Maximus, Biceps Femoris, and Vastus Lateralis EMG Activity in the Back Squat and Barbell Hip Thrust. *J Appl Biomech* 31(6):452–458. doi:10.1123/jab.2014-0301 | Glute vs hamstring ratios |
| Lehman GJ, et al. (2004). Variations in muscle activation levels during traditional latissimus dorsi weight training exercises. *Dyn Med* 3:4. doi:10.1186/1476-5918-3-4 | Lat:biceps activation ratio; high subject variability |
| Coratella G, et al. (2020). An Electromyographic Analysis of Lateral Raise Variations and Frontal Raise in Competitive Bodybuilders. *Int J Environ Res Public Health* 17(17):6015. doi:10.3390/ijerph17176015 | Lateral raise: delt vs upper-trap |
| Stastny P, et al. (2017). A systematic review of surface electromyography analyses of the bench press movement task. *PLoS One* 12(2):e0171632. doi:10.1371/journal.pone.0171632 | Bench press muscle model |

*(Calatayud 2016, Schoenfeld 2018 and Grgic 2021 are listed in `REFERENCES_INDEX.md`.)*

### Non-peer-reviewed (use with caution)
- **Henselmans M (2023).** *Can we feel muscle activation?* mennohenselmans.com — accessible
  summary of Mitsuya et al. (2023) and the sensory-vs-actual activation literature.

### Added course/lab resources
- **ME 6114 Joint Biomechanics** lecture slides (Darshan S. Shah, BiOME Lab, Mechanical
  Engineering, IIT Bombay, 2026), S05E01–S05E08. Folder `project/biomech/`.
- Ruby 1988 (`R1.pdf`); Ryu 1991 (`R2.pdf`) — wrist kinematics / functional ROM.
- `Wrist_ROM_Mini_Literature_Review_and_Pilot_Study.pdf`, `Wrist joint project at a
  glance.pdf`, `Team8_stage2_report.pdf` — team wrist-IMU documents.

---

## PART G — ONE-LINE SUMMARY
Motor-unit action potentials overlap to form the surface EMG signal. A two-channel
prototype can display two muscle-specific, reference-normalized amplitude traces and test
feedback under a controlled exercise protocol. It measures **electrical activation-related
amplitude**, not force, technique correctness or growth; any cross-muscle ratio remains
exploratory.
