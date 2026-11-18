#!/usr/bin/env python
"""Fixed-duration capture from team_mvc.ino, with a stats summary.

    python tools/emg_capture.py --seconds 10 --out logs/bench.csv
    python tools/emg_capture.py --port COM7 --seconds 10

Auto-detects the ESP32 port when --port is omitted.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import statistics
import sys
import time

FIELDS = ["t_ms", "raw", "filt", "rms", "rms_mV", "peak", "clipped", "activation"]

# "Mean: 1.23 mV | RMS: 4.56 mV | Activation: 12.3%"
_RE_MEAN = re.compile(r"Mean:\s*(-?\d+(?:\.\d+)?)")
_RE_RMS = re.compile(r"RMS:\s*(-?\d+(?:\.\d+)?)")
_RE_ACT = re.compile(r"Activation:\s*(-?\d+(?:\.\d+)?)")


def parse_line(text: str, t_ms: float) -> dict | None:
    """Accept both the CSV sketch and the 'Mean/RMS/Activation' sketch."""
    if text.startswith("t_ms"):
        return None
    parts = text.split(",")
    if len(parts) >= 6:
        try:
            row = {k: float(v) for k, v in zip(FIELDS, parts[: len(FIELDS)])}
            row.setdefault("activation", 0.0)
            return row
        except ValueError:
            pass

    m_rms = _RE_RMS.search(text)
    if m_rms:
        m_mean = _RE_MEAN.search(text)
        m_act = _RE_ACT.search(text)
        return {
            "t_ms": t_ms,
            "raw": 0.0,
            "filt": 0.0,
            "rms": 0.0,
            "rms_mV": float(m_rms.group(1)),
            "peak": 0.0,
            "clipped": 0.0,
            "activation": float(m_act.group(1)) if m_act else 0.0,
            "mean_mV": float(m_mean.group(1)) if m_mean else 0.0,
        }
    return None


def candidate_ports() -> list[tuple[str, str]]:
    from serial.tools import list_ports as lp

    out = []
    for p in lp.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").upper()
        score = 0
        if "303A" in hwid:           # Espressif native USB / JTAG
            score += 3
        if "usb serial" in desc or "usb-serial" in desc:
            score += 2
        if any(k in desc for k in ("cp210", "ch340", "ch343", "ft232", "silicon")):
            score += 2
        if "bluetooth" in desc:
            score -= 5
        out.append((score, p.device, p.description))
    out.sort(key=lambda r: r[0], reverse=True)
    return [(d, desc) for score, d, desc in out if score > 0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=None)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-reset", action="store_true", help="hold DTR/RTS low on open")
    args = ap.parse_args()

    import serial

    port = args.port
    if port is None:
        cands = candidate_ports()
        if not cands:
            print("No ESP32-like serial port found.", file=sys.stderr)
            print("Ports seen:", file=sys.stderr)
            from serial.tools import list_ports as lp

            for p in lp.comports():
                print(f"  {p.device}  {p.description}  [{p.hwid}]", file=sys.stderr)
            return 2
        port, desc = cands[0]
        print(f"auto-selected {port} ({desc})")

    ser = serial.Serial()
    ser.port = port
    ser.baudrate = args.baud
    ser.timeout = 0.2
    if args.no_reset:
        ser.dtr = False
        ser.rts = False
    try:
        ser.open()
    except serial.SerialException as exc:
        print(f"Could not open {port}: {exc}", file=sys.stderr)
        print("If Arduino IDE's Serial Monitor is open, close it first.", file=sys.stderr)
        return 2

    rows: list[dict] = []
    header_seen = False
    t_start = time.time()
    deadline = t_start + args.seconds
    last_report = 0.0
    lines_total = 0

    print(f"listening on {port} for {args.seconds:.0f} s — do not touch the sensor")

    while time.time() < deadline:
        line = ser.readline()
        if not line:
            continue
        text = line.decode("utf-8", errors="replace").strip()
        if not text:
            continue
        lines_total += 1
        if text.startswith("t_ms"):
            header_seen = True
            continue
        if text.startswith("#"):
            print(f"  board: {text}")
            continue
        row = parse_line(text, (time.time() - t_start) * 1000.0)
        if row is None:
            if lines_total <= 12:
                print(f"  board: {text[:110]}")
            continue
        rows.append(row)
        if time.time() - last_report > 1.0:
            last_report = time.time()
            print(
                f"  raw={row['raw']:6.0f} filt={row['filt']:6.0f} "
                f"env={row['rms_mV']:7.2f} mV peak={row['peak']:5.0f} "
                f"clip={int(row['clipped'])} rows={len(rows)}"
            )

    ser.close()

    print(f"\nlines received: {lines_total}, data rows: {len(rows)}, header seen: {header_seen}")
    if not rows:
        print("No CSV data. Check: USB CDC On Boot setting, baud rate, and that the sketch uploaded.")
        return 1

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            for r in rows:
                w.writerow([r[k] for k in FIELDS])
        print(f"wrote {args.out}")

    env = [r["rms_mV"] for r in rows]
    raw = [r["raw"] for r in rows]
    acts = [r.get("activation", 0.0) for r in rows]
    dur = (rows[-1]["t_ms"] - rows[0]["t_ms"]) / 1000.0
    clipped = sum(1 for r in rows if r["clipped"] >= 1)
    env_sorted = sorted(env)
    n = len(env_sorted)
    med = statistics.median(env)
    p05 = env_sorted[max(0, int(0.05 * (n - 1)))]
    p95 = env_sorted[int(0.95 * (n - 1))]
    head = env[: max(1, n // 10)]
    tail = env[-max(1, n // 10) :]

    print("\n--- capture summary ---")
    print(f"duration        : {dur:.1f} s at {len(rows) / max(dur, 1e-6):.1f} rows/s")
    print(f"envelope median : {med:.2f} mV   (p05 {p05:.2f} / p95 {p95:.2f})")
    print(f"envelope max    : {max(env):.2f} mV")
    print(f"envelope sd     : {statistics.pstdev(env):.2f} mV")
    print(f"drift head→tail : {statistics.median(head):.2f} → {statistics.median(tail):.2f} mV")
    if max(raw) > 0:
        print(f"raw range       : {min(raw):.0f} .. {max(raw):.0f}  (mean {statistics.mean(raw):.0f})")
    if any(acts):
        print(f"activation      : median {statistics.median(acts):.1f}%  max {max(acts):.1f}%")
    print(f"clipped rows    : {clipped}")

    print("\n--- reading it ---")
    if clipped > len(rows) * 0.3:
        print("Output is pinned at a rail. Check sensor supply and that OUT is on GPIO4.")
    elif max(raw) >= 4090 or min(raw) <= 5:
        print("Occasional rail hits — the front end output is close to a supply rail.")
    if max(env) < 1.0:
        print("Envelope is essentially flat/very low.")
    if med > 0 and (max(env) / med) < 1.5:
        print("Envelope is steady (expected with nothing on the electrode inputs).")
    if abs(statistics.median(tail) - statistics.median(head)) > max(3.0, 0.5 * med):
        print("Noticeable baseline drift across the capture — re-zero with 'z' before trials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
