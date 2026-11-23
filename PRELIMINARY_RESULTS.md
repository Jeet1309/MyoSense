# MyoSense Pilot Results and Data Provenance

The **authoritative submitted report** is `MyoSense_Report.pdf` (15 pages). This supporting
summary and `data/exercise_pairs_2026-11-22.csv` contain only the six participant experiments:
three lat-pulldown participants and three chest-press participants, each with good/bad readings
at the two measured muscle sites. Participant labels are anonymous pair codes only. BLE logger
and other trial CSVs are excluded. The PDF and presentation deck are left unchanged for the
planned final-document revision.

## Study and measurement context

The report describes three participants in each exercise group. Its chest-press tables contain
all three pairs C1–C3. Its lat-pulldown tables contain L1/L2; the user clarified that the two
chat readings are those two participants and identified the deck's L3 readings as participant 3:
latissimus good 72% / bad 59%, biceps good 40% / bad 71%. L3 is included in the supporting CSV
and summaries, but is **not in the PDF tables**. The slide footers call the displayed video
readouts “Illustrative only”; the user's identification is recorded as the source for L3. No
participant names are included.

The report describes sequential measurements with one EMG channel, three Ag/AgCl gel contacts,
approximately 20 mm active-electrode spacing aligned with the muscle fibres, and REF on a bony
site. Calibration used a 5 s resting baseline, a 5 s high-load maximal effort and a second 5 s
maximal verification; the larger MVC peak was retained. Latissimus and biceps were recorded
sequentially during lat pulldowns; pectoralis and triceps were recorded sequentially during chest
presses.

## Paired readings

Values are reported app activation percentages. Paired differences are `good − bad` in percentage
points (pp). L1–L3 and C1–C3 are anonymous pair codes for the six participant experiments; they
are not participant names.

| Exercise / site | Pair | Good (%) | Bad (%) | Good − bad (pp) | Source |
|---|---|---:|---:|---:|---|
| Lat pulldown / latissimus | L1 | 68 | 54 | +14 | Report table 3 and chat values |
| Lat pulldown / latissimus | L2 | 78 | 63 | +15 | Report table 3 and chat values |
| Lat pulldown / latissimus | L3 | 72 | 59 | +13 | Slide 13; user identifies as participant 3 |
| Lat pulldown / biceps | L1 | 27 | 44 | −17 | Report table 3 and chat values |
| Lat pulldown / biceps | L2 | 33 | 53 | −20 | Report table 3 and chat values |
| Lat pulldown / biceps | L3 | 40 | 71 | −31 | Slide 14; user identifies as participant 3 |
| Chest press / pectoralis | C1 | 66 | 59 | +7 | Report table 4 and chat values |
| Chest press / pectoralis | C2 | 69 | 59 | +10 | Report table 4 and chat values |
| Chest press / pectoralis | C3 | 60 | 55 | +5 | Report table 4 and chat values |
| Chest press / triceps | C1 | 55 | 65 | −10 | Report table 4 and chat values |
| Chest press / triceps | C2 | 53 | 66 | −13 | Report table 4 and chat values |
| Chest press / triceps | C3 | 50 | 70 | −20 | Report table 4 and chat values |

## Group summaries

| Exercise / site | Good mean (%) | Bad mean (%) | Mean difference (pp) | Pairs included |
|---|---:|---:|---:|---:|
| Lat pulldown / latissimus | 72.67 | 58.67 | +14.00 | L1–L3* |
| Lat pulldown / biceps | 33.33 | 56.00 | −22.67 | L1–L3* |
| Chest press / pectoralis | 65.00 | 57.67 | +7.33 | C1–C3 |
| Chest press / triceps | 52.67 | 67.00 | −14.33 | C1–C3 |

`*` Lat L3 comes from the presentation's slide readouts and is absent from the authoritative PDF
tables; it is included here as participant 3 per the user's clarification.

## Interpretation and limitations

Within these six participant experiments, good-form readings are higher for latissimus and
pectoralis; bad-form readings are higher for biceps and triceps. This describes the recorded
activation values only. It does not establish a universal form rule, muscle force, or that one
muscle “took over.” EMG amplitude depends on anatomy, electrode placement, skin interface, task
and MVC reference.

The PDF states three participants per exercise group, but its lat-pulldown tables print only L1
and L2. The supplementary L3 pair is sourced from slides whose original footer calls the video
readouts illustrative; the user identified them as participant 3. Preserve that discrepancy and
do not present L3 as independently verified against raw records. The report does not state
numeric load, tempo, range of motion, rest interval, trial order, or independent form-label
scoring. No statistical significance or form-accuracy claim is supported by these data. BLE
logger/bench CSVs are intentionally excluded from this exercise dataset and its means.

## Next measurements to document

For follow-up experiments, record the exercise and muscle site, load, repetitions, tempo, ROM,
rest interval, electrode type/preparation/landmarks/spacing/orientation, reference site, MVC and
rest-baseline values, trial order, and app CSV. Predefine form cues and, if feasible, have a
second person label them. Report each participant's values separately before group summaries.
