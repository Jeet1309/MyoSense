# Battery level and charging — how to wire it

This is the one optional hardware addition to the BLE build. It lets the board report
**how much charge is left**, and roughly **whether the cell is charging**.

Nothing here is needed for the EMG measurement. If you skip it, the firmware runs exactly
the same and the app simply hides the battery pill.

Approximation is fine for this project: the percentage is estimated from the pack voltage,
not measured by a fuel gauge. Expect roughly ±10 % on a resting cell, and less accuracy
while the motor is running.

---

## 1. What the board can and cannot see

| Signal | Available? | How |
|---|---|---|
| Cell voltage | yes | resistor divider into an ADC pin |
| Charge percentage | estimated | Li-ion discharge curve applied to that voltage |
| "Charging" | estimated | pack voltage rising over ~8 s |
| True charge state | only with extra wiring | HW-373 `CHRG` pad, needs a series resistor + a meter check |
| Charge current | no | the TP4056 has no current sense output |

The TP4056 does not report anything digitally. It only has LED pins. That is why charging
state is inferred.

---

## 2. Parts

| Part | Value | Notes |
|---|---|---|
| R1, R2 | **equal**, 100 kΩ preferred (47 kΩ or 10 kΩ also fine) | 1 % metal film if you have them; anything works at this tolerance |
| Wire | 2 short pieces | solid core is easiest |
| Optional R3 | 10 kΩ | only for the true-charging upgrade in §6 |

Two equal resistors keep the maths trivial: the divider halves the voltage, so a fully
charged 4.2 V cell presents 2.1 V to the ADC, well inside the 3.3 V limit.

---

## 3. Where to connect

```
   HW-373                      ESP32-S3
  ┌────────┐
  │  B+ ───┼── cell +                     (charger input side)
  │  B- ───┼── cell −
  │        │
  │ OUT+ ──┼──┬──[ R1 100k ]──●────────── GPIO1
  │ OUT- ──┼──┴── GND ────────┴──[ R2 100k ]── GND
  └────────┘         │
                     └── ESP32 GND  (common ground, mandatory)
```

Rules that matter:

- Tap **`OUT+`** on the HW-373. That node is the protected cell voltage, roughly 3.0–4.2 V.
- **Never** tap the HW-106 boost output (5 V). It would divide to 2.5 V and report a
  meaningless percentage.
- The ESP32 and the battery chain must share a ground. `OUT−` and the ESP32 `GND` are the
  same net once everything is plugged together, but wire the divider's bottom leg to the
  ESP32's own `GND` pin.
- GPIO1 is ADC1 channel 0. Do not move this to an ADC2 pin (GPIO11–GPIO20) — ADC2 is not
  usable while the radio is running.

---

## 4. Assemble, in order

1. Cell disconnected from the HW-373. Solder `R1` from `OUT+` to a free node.
2. Solder `R2` from that node to `OUT−`.
3. Meter between the node and `OUT−`: it must read **exactly half** the pack voltage.
   With a 3.9 V cell, expect 1.95 V ± 0.02 V.
   If it reads the full pack voltage, `R2` is not connected — do not proceed.
4. Meter again with the cell connected: same half-scale reading proves the tap point is right.
5. Only then wire the node to `GPIO1`.
6. Flash `firmware/team_ble/team_ble.ino` and open the app — the pill appears within a second.

---

## 5. What the numbers mean

The firmware (`team_ble.ino`) applies this curve to the smoothed pack voltage:

| Pack voltage | Reported % |
|---|---|
| 4.20 V | 100 |
| 4.10 V | 90 |
| 4.00 V | 80 |
| 3.90 V | 65 |
| 3.80 V | 50 |
| 3.70 V | 35 |
| 3.60 V | 20 |
| 3.50 V | 10 |
| 3.40 V | 5 |
| 3.30 V | 0 |

Values in between are interpolated linearly. This is a resting-voltage curve, so:

- Reading the level **immediately after** a charge shows an optimistically high number.
- Reading it **under load** (ESP32 + BLE + EMG) shows slightly low.
- The pack is treated as empty at 3.30 V, but the HW-373's DW01 protection typically cuts
  the load near 2.5–3.0 V, so a true 0 % reading means "stop using it".

Two firmware constants control this:

```cpp
#define BATT_PIN 1              // ADC1_CH0 = GPIO1
const float BATT_DIVIDER = 2.0f;   // (R1 + R2) / R2
```

If your resistors are not equal, set `BATT_DIVIDER` to `(R1 + R2) / R2`. Example: 47 kΩ and
100 kΩ → `(47 + 100) / 100 = 1.47`.

Below 2.6 V the firmware treats the reading as "no sensor fitted" and sends 0, so a floating
pin never shows a false 0 %.

---

## 6. Optional: true charging state

The HW-373 `CHRG` pad pulls low while a charge is in progress and is released when the
charge completes, which is exactly the bit you want. Two problems:

- The pad sits behind an LED tied to the 5 V rail, so its "high" state is **not** 3.3 V.
- The ESP32 GPIO is not 5 V tolerant.

Safe method:

1. Solder a 10 kΩ resistor in series from the `CHRG` pad to the GPIO you intend to use.
2. Charge the cell and measure the pad: with the series resistor in place, the GPIO side
   must stay below 3.3 V in both states.
3. Add a 10 kΩ pull-up from that GPIO to `3V3` so the released state reads clean high.
4. In `team_ble.ino`, set `#define CHRG_PIN 2` (GPIO2 is ADC1_CH1, but used here as a plain
   digital input) and rebuild.

With `CHRG_PIN -1` (the default), the firmware infers charging from the pack voltage rising
more than about 20 mV over eight seconds. It works from mid-charge upward, lags by a few
seconds, and cannot tell "charging" from "just stopped and recovering its open-circuit
voltage" — an acceptable approximation for a demo, not a charge controller.

---

## 7. App behaviour

| Situation | What the app shows |
|---|---|
| Divider fitted, pack 3.9 V | pill with `65% · 3.90V`, amber |
| Voltage rising | same pill with `CHG` |
| Above 50 % | pill in green |
| Below 20 % | pill in red |
| No divider / floating pin | pill hidden, everything else normal |
| Old firmware without battery fields | pill hidden (the parser only reads what is sent) |

The CSV includes `batt_mV`, `batt_pct` and `charging` per row, plus a `# session summary`
block at the end, so a charge-level-over-time plot comes straight out of the log.

---

## 8. Safety

- **Measure before connecting.** Never put more than 3.3 V on a GPIO.
- Cell polarity first, always. Reversed polarity destroys the TP4056.
- Do not charge the cell while electrodes are on a person, and do not have the laptop USB
  and the boost converter connected to the board at the same time.
- The HW-373's default charge current is set by its `Rprog` resistor, typically 1 A. That is
  1C for a 1000 mAh cell — acceptable but warm. If it gets hot, change `Rprog` to 2.4 kΩ for
  about 500 mA.
- Keep the divider's resistors away from the cell's terminals' exposed metal; a short across
  the cell is a fire risk.

---

## 9. Troubleshooting

| Symptom | Cause |
|---|---|
| Pill never appears | node not on GPIO1, divider not connected, or `BATT_PIN` changed without rebuilding |
| Reads about half the real voltage | you forgot the divider is 2:1 — check `BATT_DIVIDER` |
| Reads ~0 % at 3.8 V | tapping after the boost (5 V) instead of `OUT+`, or a 1:1 divider on the wrong node |
| Percentage jumps around | long unshielded wires to the divider; keep them short, and the 1 s averaging will settle it |
| Always shows `CHG` | inferred flag stuck on a slowly rising voltage; visible only while the level climbs |
| Number drifts while flexing | expected: the load modulates the pack voltage slightly; the curve is coarse by design |
