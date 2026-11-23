# MyoSense Pilot Results and Data Provenance

The **authoritative submitted report** is `MyoSense_Report.pdf` (15 pages). This supporting
summary and `data/form_comparison_2026-11-22.csv` reconcile its tables with the third lat-pulldown
participant values that the user identified in presentation slides. The PDF and presentation
deck were intentionally left unchanged.

## Study and measurement context

The report describes three participants in each exercise group. It reports lat-pulldown pairs
L1 and L2, and chest-press pairs C1, C2 and C3. The user identified an additional participant
pair, L3, from the lat/biceps demo slides: latissimus good 72% / bad 59%, biceps good 40% / bad
71%. This L3 supplement is included in the CSV and summary below, but is **not in the PDF's
tables**. The source slides label those video values “Illustrative only”; the user's later
message identifies them as participant 3, so retain this provenance note when using them.

The report describes sequential measurements with one EMG channel, three Ag/AgCl gel contacts,
approximately 20 mm active-electrode spacing aligned with the muscle fibres, and REF on a bony
site. Calibration used a 5 s resting baseline, a 5 s high-load maximal effort and a second 5 s
maximal verification; the larger MVC peak was retained. Latissimus and biceps were recorded
sequentially during lat pulldowns; pectoralis and triceps were recorded sequentially during chest
presses.

## Paired readings

Values are reported app activation percentages. Paired differences are `good − bad` in percentage
points (pp). L1/L2 and C1–C3 are the report's pair identifiers; L3 is the user-confirmed slide
supplement described above.

| Exercise / site | Pair | Good (%) | Bad (%) | Good − bad (pp) | Source |
|---|---|---:|---:|---:|---|
| Lat pulldown / latissimus | L1 | 68 | 54 | +14 | Report table 3 |
| Lat pulldown / latissimus | L2 | 78 | 63 | +15 | Report table 3 |
| Lat pulldown / latissimus | L3 | 72 | 59 | +13 | Slides 13; user identifies as participant 3 |
| Lat pulldown / biceps | L1 | 27 | 44 | −17 | Report table 3 |
| Lat pulldown / biceps | L2 | 33 | 53 | −20 | Report table 3 |
| Lat pulldown / biceps | L3 | 40 | 71 | −31 | Slides 14; user identifies as participant 3 |
| Chest press / pectoralis | C1 | 66 | 59 | +7 | Report table 4 |
| Chest press / pectoralis | C2 | 69 | 59 | +10 | Report table 4 |
| Chest press / pectoralis | C3 | 60 | 55 | +5 | Report table 4 |
| Chest press / triceps | C1 | 55 | 65 | −10 | Report table 4 |
| Chest press / triceps | C2 | 53 | 66 | −13 | Report table 4 |
| Chest press / triceps | C3 | 50 | 70 | −20 | Report table 4 |

## Group summaries

| Exercise / site | Good mean (%) | Bad mean (%) | Mean difference (pp) | Pairs included |
|---|---:|---:|---:|---:|
| Lat pulldown / latissimus | 72.67 | 58.67 | +14.00 | L1–L3* |
| Lat pulldown / biceps | 33.33 | 56.00 | −22.67 | L1–L3* |
| Chest press / pectoralis | 65.00 | 57.67 | +7.33 | C1–C3 |
| Chest press / triceps | 52.67 | 67.00 | −14.33 | C1–C3 |

`*` L3 comes from slide readouts and is absent from the authoritative PDF tables; it is included
here per the user's identification of that reading as the third participant.

## Interpretation and limitations

Within these reported pairs, good-labelled readings are higher for latissimus and pectoralis;
bad-labelled readings are higher for biceps and triceps. This demonstrates differing displayed
activation readings in these conditions. It does not establish a universal form rule, muscle
force, or that one muscle “took over.” EMG amplitude depends on anatomy, electrode placement,
skin interface, task and MVC reference.

The PDF states three participants per exercise group, but its lat-pulldown tables print only L1
and L2. The extra L3 values were taken from slides whose original footer calls them illustrative;
the user later identified them as the omitted participant. Preserve that discrepancy and do not
present L3 as independently verified against raw records. The report does not state numeric load,
tempo, range of motion, rest interval, trial order, or independent form-label scoring. No
statistical significance or accuracy claim is supported by these data.

## BLE bench check (separate from exercise data)

A 12 s laptop BLE capture on the earlier firmware received 113 rows in 11.9 s (about 9.5
rows/s) and reported 1888 ADC reads/s. Median RMS was 181.85 mV with an open/floating sensor
input; this was not an exercise or on-body result. The notification path was subsequently
changed to avoid an unconditional delay. Re-flash and repeat this check before reporting the
updated acquisition rate or packet-loss performance.
