# Preliminary Form-Condition Observations

**Recorded:** 22 November 2026, one informal session. Raw values are in
`data/form_comparison_2026-11-22.csv`.

## Results

The values below are the user's reported MyoSense activation readings. They are treated as
percentages because the app displays activation in `%`; confirm this interpretation before
using the values in a final submission. Means are descriptive only. `Good` and `bad` are the
user's labels, not labels independently assessed by a coach or validated classifier.

| Exercise / site | Good readings (%) | Good mean (%) | Bad readings (%) | Bad mean (%) | Good − bad (percentage points) |
|---|---:|---:|---:|---:|---:|
| Lat exercise / latissimus (variant not recorded) | 68, 78 | 73.0 | 54, 63 | 58.5 | +14.5 |
| Biceps exercise / biceps (variant not recorded) | 27, 33 | 30.0 | 44, 53 | 48.5 | −18.5 |
| Bench press / chest | 66, 69, 60 | 65.0 | 59, 59, 55 | 57.7 | +7.3 |
| Bench press / triceps | 55, 53, 50 | 52.7 | 65, 66, 70 | 67.0 | −14.3 |

## BLE bench telemetry

A separate 12 s laptop BLE capture on the earlier firmware received 113 rows in 11.9 s
(about 9.5 rows/s) and reported 1888 ADC reads/s. Median RMS was 181.85 mV with an open/
floating sensor input; this is not an exercise or on-body result. The notification path was
subsequently changed to avoid an unconditional delay. Re-flash and repeat this check before
reporting the updated acquisition or packet-loss performance.

## Interpretation

The observations vary by site: the readings are higher in the user-labelled good condition for
the lat and chest, and higher in the user-labelled bad condition for biceps and triceps. This
does **not** establish a general relationship between form and muscle activation. Higher or
lower sEMG amplitude is not a direct measure of force, technique quality, or which muscle
"takes over".

The values are a small descriptive pilot (two readings per lat/biceps condition and three per
bench-press site/condition), not independent participants or a controlled validation study.
The available notes do not record the exact lat/biceps exercise variants, load, tempo, range of
motion, rest interval, electrode landmarks and spacing, MVC trial values, trial order, or whether
electrodes were moved between conditions. If the one-channel prototype was used, muscle-site
readings are sequential, not simultaneous. These omissions prevent causal or statistical claims.

## What to record next

For each trial, record the exercise and muscle site, load, repetitions, tempo, ROM, rest interval,
electrode type/preparation/landmarks/spacing/orientation, reference site, MVC and rest-baseline
values, trial order, and the app CSV. Predefine the form cues and have a second person label
them if possible. Repeat several trials per condition with the same placement; do not move
electrodes between good/bad trials when the goal is a within-site comparison. Report all raw
trials and descriptive summaries; avoid significance tests with this sample size.
