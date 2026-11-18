# Prototype Bench-Test Handoff

Use this file to start a fresh session for identifying and testing the current ESP32-S3 + sEMG prototype. It records what is known from the user's photos and what must be checked before wiring or attaching electrodes to a person.

## Current Parts

| Part | Status from user/photos | Verify before use |
|---|---|---|
| Controller | ESP32-S3 N16R8 development board; two USB-C ports; visible labels include 3V3, 5V, GND, GPIO4 and GPIO5 | Exact manufacturer/revision, pinout, USB-UART vs native USB port, ADC-capable pins |
| Battery | User confirms one 3.7 V, 1000 mAh Li-ion cell | Cell label/chemistry, polarity, connector, protection circuit, physical condition and allowed charge current |
| Charger | Blue board marked `HW-373 V1.2.1 4056`, with `B+`, `B-`, `OUT+`, `OUT-`; appears to be TP4056-style USB-C 1S charger/protection board | Exact circuit/revision, protection presence, charge current and correct battery connection |
| Boost | Blue board marked `HW-106`, 3.7 V→5 V step-up with USB-A output socket, 100 µF 16 V cap, 470 inductor | Output voltage (~5 V, fixed), input pad polarity, current capability under load |
| EMG front end | One green Muscle BioAmp-style board. Visible pads appear to be `VCC`, `GND`, `OUT`, `IN+`, `IN-`, `REF`; likely Muscle BioAmp Candy | Exact product/revision and its supply/output/bandwidth specifications. Do not assume Candy until confirmed from marking or seller/manual. |
| Electrodes | One 3-contact cable/strap assembly visible | Contact material, whether adhesive Ag/AgCl pads or conductive gel are needed, and which lead maps to each labeled input |

## Current Readiness

- Enough to begin controller identification and a one-channel, disconnected-electrode bench check.
- One EMG module supports one muscle site only. Two simultaneous channels need a second compatible module and a second 3-contact set.
- The charger board is not a voltage regulator. Its output is approximately the cell's voltage, not 5 V.
- The HW-106 boost provides the missing 5 V and outputs through a USB-A socket, so the ESP32 can be powered with a plain USB-A-to-USB-C cable — no soldering to the dev board.
- The generic ESP32-S3 board does not appear to have the FireBeetle's integrated Li-ion charger/battery connector.
- Full chain: `cell → HW-373 (charge/protect) → HW-106 (boost to 5 V) → USB-C → ESP32`.
- Never connect battery-range voltage directly to the board's `5V` pin.

### Assembling the battery chain

1. Meter the HW-106 input pads with nothing attached; identify `+` and `−` from the silkscreen, not by guessing.
2. Solder/connect cell `+` → HW-373 `B+`, cell `−` → `B−`. Do this with USB unplugged. Double-check polarity — reversed polarity destroys the TP4056.
3. Connect HW-373 `OUT+` → HW-106 `VIN+`, `OUT−` → `VIN−`.
4. Insert a USB-A-to-USB-C cable into the HW-106 and meter the free end: **`VBUS` to `GND` should read 4.9–5.2 V**.
5. Only then plug into the ESP32 and confirm it boots and the `3V3` rail reads ~3.3 V.

## Safe Test Order

### 1. Identify, do not power unknown wiring

1. Photograph/read all silkscreen on both sides of the ESP32 board, EMG board and charger board; note any model, revision or URL on packaging.
2. Find the exact EMG module manual. Confirm supply pins, supported supply voltage, output type/range and electrode input labels.
3. Read the battery label. Do not use a swollen, damaged, punctured or unidentified cell.
4. With a multimeter, verify charger-board labels and cell polarity before connecting the cell. Confirm the charger current is appropriate for the battery's specification.
5. Confirm the ESP32 board power input. The `5V` pin requires a regulated 5 V source unless its exact board documentation says otherwise.

### 2. Controller-only USB bench check

1. Leave the battery, charger and all body electrodes disconnected.
2. Power the ESP32 board from USB. Use the port identified by the board documentation for programming/serial.
3. Upload a minimal board-identification/serial test. Confirm the ESP32-S3 N16R8 target and verify access to GPIO4/GPIO5.
4. Read ADC1 on GPIO4 and GPIO5 with no sensor attached. Floating-input readings are only an electrical smoke test, not meaningful signal measurements.

### 2b. Firmware: see the signal on the laptop

Follow `firmware/README.md`. Short version:

1. Wire `EMG VCC → 3V3`, `EMG GND → GND`, `EMG OUT → GPIO4`. Electrodes **unconnected**.
2. Arduino IDE: board `ESP32S3 Dev Module`, Flash 16MB, OPI PSRAM, and the correct `USB CDC On Boot` setting for the socket you're using.
3. Upload `firmware/team_mvc/team_mvc.ino`, open Serial Monitor at **115200**.
4. Expect a `# cfg ...` line, the CSV header, then rows. With nothing on the electrode inputs, `filt` is small noise and `clipped` should stay `0`.
5. Live view: `python tools/emg_plot.py --port COMx --out logs/first_test.csv`.

### 3. EMG module electrical check (no person connected)

Proceed only after identifying the module and its power requirements.

1. For a confirmed 3.3 V-compatible Muscle BioAmp Candy-style board, wire one channel: `VCC -> 3V3`, `GND -> GND`, `OUT -> GPIO4/ADC1`. Use the sensor's printed labels, not wire colors.
2. Keep `OUT` within the ESP32-S3 ADC input range. Never connect a possible 5 V output directly to the ADC.
3. With electrode input contacts not attached to a person, observe baseline ADC readings and check for rail clipping, unexpected heating or unstable power. Stop if anything is abnormal.
4. If the module is not confirmed as Candy or its output may exceed 3.3 V, do not connect `OUT` to the ESP32 until a safe level/interface is specified.

### 4. Battery-power gate before any body contact

1. The HW-373/TP4056 board's `OUT+ / OUT-` are not 5 V. Do not feed them directly to the ESP32 `5V` pin.
2. Use the HW-106 boost (or a USB power bank that is not itself charging). Check its output voltage with a meter before connection.
3. Disconnect the ESP32 from a mains-connected computer and disconnect the charger. Do not charge while electrodes are on a person. Prefer BLE to a battery-powered phone for any body-connected telemetry.
4. Obtain required instructor/ethics approval before collecting human data. Start with a short, low-effort voluntary contraction and stop if there is discomfort or skin irritation.

### 5. First one-channel EMG recording

After the power gate passes:

1. Attach the three contacts according to the sensor manual: two differential contacts over the target muscle and the reference contact on the recommended low-activity/bony site. Use gel/coupling material if required.
2. Keep the leads secured so cable motion does not pull the contacts.
3. Capture a quiet baseline, a brief gentle contraction, then rest. Log timestamps and ADC values over BLE or local storage, not through a mains-connected cable.
4. Confirm the output changes repeatably with contraction, stays within ADC range and does not clip. Record sample rate, board/module revision, electrode locations and any filtering/gain settings.
5. If the module is confirmed Candy, its listed fixed 72-720 Hz band means a raw capture target around 2 ksample/s/channel is appropriate for testing, but verify achieved timing and ADC noise. Do not claim conventional 20-450 Hz acquisition or validated spectral fatigue from this sensor.

### 6. Demonstration with one sensor at different sites

One sensor can record **one site at a time**. It cannot measure two muscles simultaneously or distinguish their activity within the same repetition.

1. Decide what “different places” means for the demonstration:
   - **Different electrode placements on the same muscle:** keep muscle, posture and contraction task constant, move the electrode set between marked placements, and show how raw amplitude changes with placement. Recalibrate after each placement; this demonstrates measurement sensitivity, not a stronger/weaker muscle.
   - **Different muscles/sites:** define a safe muscle-specific isometric task and posture for each, and document the site, posture, joint angle and instruction separately. This is more confounded than a same-muscle placement demo.
2. At the first site, record rest, several consistent contractions and a site-specific MVC/reference using the same electrode placement and processing rule. Save the raw envelope/ADC data and note the site.
3. Move the same module/electrode set to the second site, repeat skin prep and placement documentation, then collect that site's own rest and MVC/reference trials. Recheck signal range/clipping after moving the sensor.
4. Show each site's raw amplitude trace and its own task/reference percentage. Its own MVC reference should be around 100% by construction; this is useful for demonstrating calibration, not for ranking muscles.
5. Do not compare the raw MVC amplitudes across sites as force or relative muscle strength. Differences can result from muscle anatomy, electrode geometry, skin contact, tissue and placement. Describe this as a sequential instrumentation/normalization demonstration.
6. If comparing a standardized submaximal task across sites, use a safe task appropriate to each muscle and label the task-specific limitation. Do not describe this as simultaneous co-activation or a helper-muscle ratio.

## Do Not Do

- Do not connect the cell or HW-373 `OUT` directly to the ESP32 `5V` pin.
- Do not connect a 5 V sensor output to an ESP32-S3 ADC input.
- Do not attach a person to electrodes while the board is connected to a mains-powered computer, charger, bench supply or grounded instrument unless proper isolation is established.
- Do not charge the Li-ion cell while electrodes are attached to a person.
- Do not identify sensor lead functions by color; use PCB labels and the correct module manual.
- Do not interpret EMG amplitude as muscle force, correct technique or guaranteed hypertrophy.

## Missing for the Two-Channel Prototype

- A second compatible single-channel EMG module, preferably the same model/revision as the first.
- Three more suitable electrode contacts and the required adhesive/coupling material.
- Confirmed controller pin map and EMG module datasheet/manual.

Already solved: the 5 V rail is covered by the HW-106 boost. The remaining power work is only verification (output voltage, protection ICs on the HW-373, runtime measurement).

## Prompt for a New Session

> Continue the MyoSense prototype from `PROTOTYPE_BENCH_TEST_HANDOFF.md`. First identify the photographed ESP32-S3 N16R8 board, green Muscle BioAmp-style EMG module, HW-373 charger and 3.7 V 1000 mAh battery. Do not assume the sensor is Candy until its marking/manual is verified. Walk me through the disconnected-electrode USB bench test, then check the battery/regulated power path before any electrode-on-person test. Start with one channel on GPIO4/ADC1. Help plan a sequential site-by-site MVC/reference demonstration with that one sensor, clearly labeling that measurements are not simultaneous and that raw amplitudes across sites are not force comparisons. Explain every connection and ask me to confirm meter readings before applying power.
