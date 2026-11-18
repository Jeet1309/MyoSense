#!/usr/bin/env python
"""Read the EMG stream from team_ble.ino over Bluetooth LE.

    python tools/emg_ble.py --list
    python tools/emg_ble.py --seconds 15 --out logs/ble.csv
    python tools/emg_ble.py --calibrate --seconds 20 --out logs/ble_mvc.csv

Requires: pip install bleak   (Windows 10/11 with Bluetooth on)
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import statistics
import sys
import time

DEVICE_NAME = "MyoSense-EMG"

# Nordic UART Service, as used by team_ble.ino
TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

FIELDS = ["t_ms", "mean_mV", "rms_mV", "activation", "calibrating"]


def parse_payload(text: str, t_ms: float) -> dict | None:
    """Payload is 'mean,rms,activation,calibrating'."""
    parts = text.strip().split(",")
    if len(parts) < 3:
        return None
    try:
        return {
            "t_ms": t_ms,
            "mean_mV": float(parts[0]),
            "rms_mV": float(parts[1]),
            "activation": float(parts[2]),
            "calibrating": int(float(parts[3])) if len(parts) > 3 else 0,
        }
    except ValueError:
        return None


async def list_devices(timeout: float) -> int:
    from bleak import BleakScanner

    print(f"scanning {timeout:.0f} s ...")
    devices = await BleakScanner.discover(timeout=timeout, return_adv=True)

    rows = []
    for device, adv in devices.values():
        rows.append((device.name or "", device.address, adv.rssi))

    if not rows:
        print("No BLE devices found. Is Bluetooth turned on?", file=sys.stderr)
        return 1

    for name, address, rssi in sorted(rows):
        mark = "  <-- MyoSense" if DEVICE_NAME in name else ""
        print(f"  {name or '(unnamed)':30s} {address}  {rssi:4d} dBm{mark}")
    return 0


async def capture(args) -> int:
    from bleak import BleakClient, BleakScanner

    device = await BleakScanner.find_device_by_filter(
        lambda d, adv: (d.name or adv.local_name or "") == DEVICE_NAME,
        timeout=args.scan_timeout,
    )

    if device is None:
        print(f"Could not find a device named {DEVICE_NAME}.", file=sys.stderr)
        print("Check: board powered, sketch uploaded, Bluetooth on, in range.", file=sys.stderr)
        return 2

    print(f"connecting to {device.name or DEVICE_NAME} ({device.address})")

    buffer = ""
    rows: list[dict] = []
    t_start = time.time()
    last_report = 0.0

    def on_notify(_handle, data: bytearray) -> None:
        nonlocal buffer
        buffer += data.decode("utf-8", errors="replace")
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            row = parse_payload(line, (time.time() - t_start) * 1000.0)
            if row is not None:
                rows.append(row)

    try:
        async with BleakClient(device, timeout=args.connect_timeout) as client:

            print(f"connected, mtu={getattr(client, 'mtu_size', 'n/a')}")
            await client.start_notify(TX_UUID, on_notify)
            print("subscribed to TX characteristic")

            if args.reset:
                await client.write_gatt_char(RX_UUID, b"R", response=False)
                print("sent R (reset calibration)")
                await asyncio.sleep(0.5)

            if args.calibrate:
                await asyncio.sleep(1.0)
                await client.write_gatt_char(RX_UUID, b"C", response=False)
                print("sent C (calibrate now - contract hard for 5 s)")

            deadline = time.time() + args.seconds
            while time.time() < deadline:
                await asyncio.sleep(0.1)
                if time.time() - last_report > 1.0 and rows:
                    last_report = time.time()
                    r = rows[-1]
                    flag = " CAL" if r["calibrating"] else ""
                    print(
                        f"  rms={r['rms_mV']:7.2f} mV  "
                        f"act={r['activation']:6.1f}%{flag}  rows={len(rows)}"
                    )

            await client.stop_notify(TX_UUID)

    except Exception as exc:  # noqa: BLE001 - surface the real BLE error
        print(f"BLE error: {exc}", file=sys.stderr)
        print("If the board is connected to the phone, disconnect there first.", file=sys.stderr)
        return 3

    print(f"\ndata rows: {len(rows)}")
    if not rows:
        print("No data. Confirm the sketch is team_ble.ino and TX notifications are enabled.")
        return 1

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            for r in rows:
                w.writerow([r[k] for k in FIELDS])
        print(f"wrote {args.out}")

    rms = [r["rms_mV"] for r in rows]
    acts = [r["activation"] for r in rows]
    dur = (rows[-1]["t_ms"] - rows[0]["t_ms"]) / 1000.0
    ordered = sorted(rms)
    n = len(ordered)

    print("\n--- capture summary ---")
    print(f"duration        : {dur:.1f} s at {len(rows) / max(dur, 1e-6):.1f} rows/s")
    print(f"rms median      : {statistics.median(rms):.2f} mV")
    print(f"rms range       : {ordered[0]:.2f} .. {ordered[-1]:.2f} mV")
    print(f"rms p05 / p95   : {ordered[max(0, int(0.05 * (n - 1)))]:.2f} / "
          f"{ordered[int(0.95 * (n - 1))]:.2f} mV")
    if max(acts) > 0:
        print(f"activation      : median {statistics.median(acts):.1f}%  max {max(acts):.1f}%")

    print("\n--- reading it ---")
    rest = statistics.median(acts) if max(acts) > 0 else 0.0
    if max(acts) > 0 and rest > 20:
        print(f"Rest activation is {rest:.0f}% - the MVC reference is low or the noise floor is high.")
    elif max(acts) > 0:
        print(f"Rest activation {rest:.0f}% looks healthy.")
    if ordered[-1] < 1.0:
        print("Signal is flat - check the Candy connection and that OUT is on GPIO4.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Read the EMG stream over BLE.")
    ap.add_argument("--list", action="store_true", help="scan and list BLE devices")
    ap.add_argument("--seconds", type=float, default=15.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--calibrate", action="store_true", help="send C after connecting")
    ap.add_argument("--reset", action="store_true", help="send R to clear the MVC reference")
    ap.add_argument("--scan-timeout", type=float, default=15.0)
    ap.add_argument("--connect-timeout", type=float, default=20.0)
    args = ap.parse_args()

    try:
        import bleak  # noqa: F401
    except ImportError:
        print("bleak is not installed. Run:  python -m pip install bleak", file=sys.stderr)
        return 2

    if args.list:
        return asyncio.run(list_devices(args.scan_timeout))

    return asyncio.run(capture(args))


if __name__ == "__main__":
    raise SystemExit(main())
