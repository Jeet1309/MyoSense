# Firmware and first activation test

**The working sketch is `team_mvc/team_mvc.ino`** — the build saved on 18 November that runs on the board. It samples GPIO4 at 2 kHz, removes the DC/mean baseline, computes a 100 ms RMS, and prints `Mean`, `RMS` and `Activation %` at 10 Hz. Press `C` on the serial line to capture a 5-second MVC reference.

**`team_ble/team_ble.ino`** is the same acquisition code with a Bluetooth LE service added, so the values arrive on a phone or laptop instead of a cable. See §7.

Supporting tools:

- `../tools/emg_capture.py` — runs the sketch's output into a CSV log with a summary (auto-detects the port, understands both CSV and `Mean/RMS/Activation` lines).
- `../tools/emg_plot.py` — replays that CSV as a plot (`--replay`), or plots a live CSV stream.
- `../tools/emg_ble.py` — reads the BLE stream into a CSV log with the same kind of summary.

---

## 1. Wiring

| EMG board | ESP32-S3 board |
|---|---|
| `VCC` | `3V3` |
| `GND` | `GND` |
| `OUT` | `GPIO4` |

Electrode inputs `IN+` / `IN−` / `REF` stay **unconnected** for the bench test.

Power the ESP32 from the laptop with a USB **data** cable (not charge-only), using the socket marked **USB** (the native one). The socket marked `UART` needs a CP210x driver that is currently failing to install on this laptop.

## 2. Arduino IDE settings

- Board: **ESP32S3 Dev Module**
- Flash Size: **16MB**, PSRAM: **OPI PSRAM**
- **USB CDC On Boot: Enabled** — without this, the board enumerates but sends nothing over USB
- Port: whichever COM port appears

## 3. Upload and check

1. Open `team_mvc/team_mvc.ino`, upload.
2. Open Serial Monitor at **115200**.
3. Expect:

```
================================
 TEAM KRESIT - CANDY EMG
 ESP32-S3 N16R8
================================
GPIO: 4
Sampling Rate: 2000 Hz
RMS Window: 100 ms
--------------------------------
System ready!
Send C for MVC calibration.
--------------------------------
Mean: 1.62 mV | RMS: 0.481 mV | Activation: 0.0%
```

With the electrode inputs floating, `RMS` is small (roughly 0.1–1 mV) and steady. That proves the ADC and serial path work — it does not prove the sensor works.

## 4. Capture and plot

```
python tools/emg_capture.py --seconds 10 --out logs/bench.csv
python tools/emg_plot.py --replay logs/bench.csv --save-png logs/bench.png
```

`emg_capture.py` prints baseline, peak, drift and clipping at the end.

## 5. Muscle test and the three-press calibration

**Battery power only** — see the safety note in `../PROTOTYPE_BENCH_TEST_HANDOFF.md`.

Apply electrodes first: `IN+`/`IN−` over the muscle belly, `REF` on bone. Then press `C`
three times, once per step. Each step lasts 5 s and the prompt is printed on the serial line.

| Press | Prompt | What you do | What it records |
|---|---|---|---|
| 1 | `STEP 1/3 - REST BASELINE` | stay completely relaxed | **average** RMS over the 5 s → noise floor |
| 2 | `STEP 2/3 - MVC` | contract maximally, hold all 5 s | **peak** 100 ms RMS → MVC |
| 3 | `STEP 3/3 - MVC VERIFY` | contract maximally again | peak of the second trial; the higher one is kept |

After step 3 the line prints `VERIFY RMS: … -> kept: …` and the `MVC/rest` ratio.

`Activation %` is computed with the noise floor removed:

```
signal = sqrt(rms² - rest²)
range  = sqrt(mvc² - rest²)
activation = 100 × signal / range
```

That subtraction is why rest now reads near 0 % instead of 30–40 %. Without a baseline
(press 2 and 3 only) the formula falls back to the plain `rms / mvc`.

Worth knowing:

- The MVC is the **peak window**, so a single noise spike inflates it. That is exactly why
  step 3 exists — repeat the maximal trial and keep the better one.
- `Activation` is **not clamped**, so a value above 100 % means the reference was taken on a
  weaker contraction.
- A healthy result has `MVC/rest` between roughly 8 and 20. Below 5 means poor contact or a
  sub-maximal effort, and every percentage will read too high.
- `RMS` is the standard deviation of the 100 ms window (AC amplitude), not an absolute voltage.
- Calibrate with the **same task you will measure** — calibrate with the grip if you train
  with the grip.
- Re-run all three presses whenever the electrodes move.
- `R` clears both values and returns the cycle to step 1.

## 6. Troubleshooting

| Symptom | Likely cause |
|---|---|
| No COM port | Charge-only cable, or the `UART` socket without its driver |
| Port exists, Serial Monitor blank | `USB CDC On Boot` is Disabled |
| Upload fails to connect | Hold **BOOT**, tap **RESET**, release, upload |
| Garbage characters | Not 115200 baud |
| `Mean` pinned at 0 or ~3.3 V | Front-end output at a rail — check module supply |
| Envelope never changes | `OUT` not on GPIO4, or module unpowered |
| Envelope huge at rest | Poor electrode contact or floating input — re-prep and re-zero |

## 7. Bluetooth (BLE) stream

Upload `team_ble/team_ble.ino` with the same IDE settings as above. The USB serial output stays identical, so you can watch both paths at once.

**Device name:** `MyoSense-EMG`
**Service:** Nordic UART (`6E400001-B5A3-F393-E0A9-E50E24DCCA9E`)

| Characteristic | UUID suffix | Direction |
|---|---|---|
| TX (notify) | `6E400003-…` | board → phone/laptop, payload `mean,rms,activation,calibrating` |
| RX (write) | `6E400002-…` | phone/laptop → board, send `C` to calibrate or `R` to reset |

Payload example: `1665,54.47,0.0,0,3980,72,1,0,0.31,12.40,1999` — mean mV, RMS mV, activation %, calibrating, battery mV, battery %, charging, flags, rest baseline mV, MVC mV, achieved acquisition rate in Hz. One line every 100 ms. Flags is a bit field: bit 0 = front end at a rail, bits 1–2 = the next calibration step (0 rest, 1 MVC, 2 verify). The line is longer than a default 20-byte BLE packet, so the firmware splits it and the client reassembles on the newline.

The acquisition rate is counted from real `analogReadMilliVolts()` calls once a second, so it measures what the loop actually achieved, not the configured 2000 Hz. The previous BLE build measured 1888 Hz in one short capture. The current notify path sends a negotiated-MTU payload in one notification without a per-line delay; flash this revision and remeasure before claiming a restored 2 kHz rate.

### From a phone

1. Install **nRF Connect for Mobile** (Android / iOS, free).
2. Scan; `MyoSense-EMG` appears.
3. Connect → expand the Nordic UART service → tap the TX characteristic (three arrows) → **subscribe**.
4. Values stream in. To calibrate, open the RX characteristic, choose **UTF-8**, type `C`, send.

Only one client at a time — disconnect the phone before connecting from the laptop.

### From the laptop

```
python -m pip install bleak
python tools/emg_ble.py --list
python tools/emg_ble.py --seconds 15 --out logs/ble.csv
python tools/emg_ble.py --calibrate --seconds 20 --out logs/ble_mvc.csv
```

Notes:

- BLE must be on, and the laptop must not be connected to the board from the phone.
- Throughput is comfortable: ~17 bytes at 10 Hz.
- The radio runs on core 0 and the sampling loop on core 1, so the 2 kHz cadence is unaffected, but expect a few dropped samples when a client connects.

## 8. Battery and charging telemetry

The board cannot see its own battery until you give it a divider. Two resistors of the **same value** (100 kΩ is ideal; 47 kΩ or 10 kΩ work too).

```
HW-373 OUT+ ──[ R1 ]──●──[ R2 ]── GND
                      │
                    GPIO1
```

| | |
|---|---|
| Tap point | HW-373 `OUT+` (that is the cell, not the boost output) |
| Ratio | `(R1 + R2) / R2` — with two equal resistors that is **2.0** |
| At 4.2 V pack | 2.1 V at the pin (safe; the ADC limit is 3.3 V) |
| Firmware constant | `BATT_DIVIDER` in `team_ble.ino` |

**Before connecting the pin**, meter the divider node: it must read exactly half the pack voltage. If it reads higher, stop — the GPIO would see more than 3.3 V.

What you get:

- Pack voltage mapped to a percentage through a Li-ion discharge curve (3.30 V = 0 %, 4.20 V = 100 %).
- A charging flag. With `CHRG_PIN -1` it is inferred from a rising pack voltage over roughly 8 s; charging shows up once the level has climbed about 20 mV.
- A rail flag so the app can warn you that the front end is pinned.

Leaving `BATT_PIN` unconnected is harmless: the readings sit near 0 V and the app simply hides the battery pill. Do not wire the divider to the 5 V boost output — that would read 2.5 V and report nonsense.
