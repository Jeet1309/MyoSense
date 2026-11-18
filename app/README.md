# Meter — live muscle-activation feedback

A single-file web app that connects to the board over Bluetooth LE and turns the raw
`mean,rms,activation` stream into something you can actually train with.

## What it does

| Element | Meaning |
|---|---|
| Big number + bar | Activation as a percentage of the calibrated MVC |
| Bar colour | Amber below the target zone, green inside it, red above |
| Blue band | Your target zone (adjustable, default 60–80 %) |
| RMS | Raw 100 ms RMS in mV, the underlying signal |
| MVC reference | The mV value behind 100 %, derived from the calibration |
| Reps | Counted when activation rises past the high value and falls below the low one |
| Time in zone | How long the last rep was held inside the band |
| Battery pill | Pack voltage and percentage, with `CHG` while charging (needs the divider in `firmware/README.md` §8) |
| Session card | Duration, reps, peak, total time in zone |
| Save CSV | Downloads the session plus a summary block |

Buttons:

- **Calibrate MVC** — sends `C`; the firmware records the peak 100 ms window for 5 s.
  Contract as hard as you can for the whole window.
- **Reset** — sends `R`, clears the reference; activation returns to 0 %.
- **Save CSV** — exports the session for plotting or the report.

## Running it

Web Bluetooth needs a secure context, so `file://` will not work reliably.

**On the laptop:**

```
python -m http.server 8000
```

then open <http://localhost:8000/app/meter.html> in Chrome or Edge.

**On a phone:** serve the page over HTTPS — the simplest way is GitHub Pages on this
repository (Settings → Pages → Deploy from branch → `main` → `/` root). The page is then
at `https://<user>.github.io/MyoSense/app/meter.html`.

## Browser support

| Browser | Works |
|---|---|
| Chrome / Edge, desktop | yes |
| Chrome, Android | yes |
| Safari, iOS | no — use the **Bluefy** browser |
| Firefox | no |

## Notes

- The board serves one BLE client at a time. Disconnect the phone before connecting the
  laptop, and close any other app holding the device.
- The first click on **Connect** must be a user gesture; browsers block background scans.
- Calibration is per muscle and per electrode placement. Re-calibrate whenever the
  electrodes move, and remember the reference is that muscle's own maximum, not an
  absolute force.
- Activation above 100 % is shown as a number above 100 but the bar saturates, so an
  over-range reading never looks like a perfect contraction.
