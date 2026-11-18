#!/usr/bin/env python
"""Plot a captured EMG log.

Capture first with emg_capture.py, then plot or replay it here.

Examples
--------
List ports:
    python tools/emg_plot.py --list

Replay a saved log:
    python tools/emg_plot.py --replay logs/rest_and_flex.csv

Save a PNG instead of opening a window:
    python tools/emg_plot.py --replay logs/rest_and_flex.csv --save-png out.png

Live CSV stream straight from the board (CSV sketches only):
    python tools/emg_plot.py --port COM5 --out logs/rest_and_flex.csv
"""

from __future__ import annotations

import argparse
import collections
import csv
import os
import sys
import time

FIELDS = ["t_ms", "raw", "filt", "rms", "rms_mV", "peak", "clipped"]


def list_ports() -> None:
    from serial.tools import list_ports as lp

    found = list(lp.comports())
    if not found:
        print("No serial ports found.")
        return
    for p in found:
        print(f"{p.device:<10} {p.description}")
    print("\nTip: unplug/replug the board and run this again to see which port appears.")


class SerialSource:
    def __init__(self, port: str, baud: int):
        import serial  # pyserial

        self.ser = serial.Serial(port, baud, timeout=0.05)
        time.sleep(0.5)
        self.ser.reset_input_buffer()

    def readline(self) -> str | None:
        line = self.ser.readline()
        if not line:
            return None
        return line.decode("utf-8", errors="replace").strip()

    def close(self) -> None:
        try:
            self.ser.close()
        except Exception:
            pass


class FileSource:
    def __init__(self, path: str):
        self.fh = open(path, "r", encoding="utf-8", errors="replace")

    def readline(self) -> str | None:
        line = self.fh.readline()
        if not line:
            return None
        return line.strip()

    def close(self) -> None:
        self.fh.close()


def parse_row(line: str) -> dict | None:
    if not line or line.startswith("#"):
        return None
    parts = line.split(",")
    if len(parts) < len(FIELDS):
        return None
    try:
        row = {k: float(v) for k, v in zip(FIELDS, parts[: len(FIELDS)])}
    except ValueError:
        return None
    return row


def summarize(rows: list[dict]) -> None:
    if not rows:
        print("No data rows parsed.")
        return
    env = sorted(r["rms_mV"] for r in rows)
    clipped = sum(1 for r in rows if r["clipped"] >= 1)
    duration = (rows[-1]["t_ms"] - rows[0]["t_ms"]) / 1000.0
    p10 = env[max(0, int(0.10 * (len(env) - 1)))]
    p99 = env[int(0.99 * (len(env) - 1))]

    print("\n--- summary ---")
    print(f"rows          : {len(rows)}  ({duration:.1f} s)")
    print(f"baseline (p10): {p10:.2f} mV")
    print(f"peak (p99)    : {p99:.2f} mV")
    print(f"max envelope  : {env[-1]:.2f} mV")
    print(f"clipped rows  : {clipped}")
    if p10 > 0:
        print(f"peak/baseline : {p99 / p10:.1f}x")


def run(args: argparse.Namespace) -> None:
    if args.replay:
        source = FileSource(args.replay)
    else:
        source = SerialSource(args.port, args.baud)

    out_fh = None
    writer = None
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        out_fh = open(args.out, "w", newline="", encoding="utf-8")
        writer = csv.writer(out_fh)
        writer.writerow(FIELDS)

    rows: list[dict] = []

    def consume(line: str | None) -> dict | None:
        if line is None:
            return None
        if line.startswith("#"):
            if not args.quiet:
                print(line)
            return None
        if line.startswith("t_ms"):
            return None
        row = parse_row(line)
        if row is None:
            return None
        rows.append(row)
        if writer is not None:
            writer.writerow([row[k] for k in FIELDS])
        return row

    try:
        if args.no_plot:
            last = time.time()
            while True:
                line = source.readline()
                if line is None:
                    if isinstance(source, FileSource) and source.fh.tell() == os.path.getsize(args.replay):
                        break
                    time.sleep(0.01)
                    continue
                row = consume(line)
                if row and not args.quiet and time.time() - last > 0.5:
                    last = time.time()
                    print(
                        f"raw={row['raw']:6.0f}  filt={row['filt']:6.0f}  "
                        f"rms={row['rms_mV']:6.2f} mV  peak={row['peak']:5.0f}  "
                        f"clip={int(row['clipped'])}"
                    )
        elif args.save_png:
            static_plot(source, consume, args)
        else:
            plot_live(source, consume, args)
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        source.close()
        if out_fh is not None:
            out_fh.close()
            print(f"wrote {args.out}")

    summarize(rows)


def static_plot(source, consume, args: argparse.Namespace) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ts, env, raw = [], [], []
    t0 = None
    while True:
        line = source.readline()
        if line is None:
            break
        row = consume(line)
        if row is None:
            continue
        if t0 is None:
            t0 = row["t_ms"]
        ts.append((row["t_ms"] - t0) / 1000.0)
        env.append(row["rms_mV"])
        raw.append(row["filt"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(ts, raw, lw=0.6, color="#1f77b4")
    ax2.plot(ts, env, lw=1.4, color="#d62728")
    ax1.set_ylabel("filtered (counts)")
    ax2.set_ylabel("envelope (mV)")
    ax2.set_xlabel("time (s)")
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    ax1.set_title("EMG envelope — rest should sit low, contraction should rise")
    fig.tight_layout()
    fig.savefig(args.save_png, dpi=130)
    print(f"wrote {args.save_png}")


def plot_live(source, consume, args: argparse.Namespace) -> None:
    import matplotlib.pyplot as plt

    win = int(args.window * 100)  # 100 rows/second
    t_buf: collections.deque = collections.deque(maxlen=win)
    e_buf: collections.deque = collections.deque(maxlen=win)
    r_buf: collections.deque = collections.deque(maxlen=win)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    fig.canvas.manager.set_window_title("MyoSense live view")
    (line_raw,) = ax1.plot([], [], lw=0.6, color="#1f77b4")
    (line_env,) = ax2.plot([], [], lw=1.4, color="#d62728")
    ax1.set_ylabel("filtered (counts)")
    ax2.set_ylabel("envelope (mV)")
    ax2.set_xlabel("time (s)")
    ax1.grid(alpha=0.3)
    ax2.grid(alpha=0.3)
    ax1.set_title("Rest, then flex — envelope should rise and return")

    t0 = None

    def update(_frame):
        nonlocal t0
        for _ in range(400):
            line = source.readline()
            if line is None:
                break
            row = consume(line)
            if row is None:
                continue
            if t0 is None:
                t0 = row["t_ms"]
            t = (row["t_ms"] - t0) / 1000.0
            t_buf.append(t)
            e_buf.append(row["rms_mV"])
            r_buf.append(row["filt"])

        if not t_buf:
            return line_raw, line_env

        line_raw.set_data(t_buf, r_buf)
        line_env.set_data(t_buf, e_buf)
        ax1.set_xlim(max(0.0, t_buf[-1] - args.window), max(args.window, t_buf[-1]))
        rmax = max(50.0, max(abs(v) for v in r_buf) * 1.2)
        ax1.set_ylim(-rmax, rmax)
        ax2.set_ylim(0, max(1.0, max(e_buf) * 1.25))
        return line_raw, line_env

    import matplotlib.animation as animation

    ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
    try:
        plt.tight_layout()
        plt.show()
    finally:
        del ani


def main() -> int:
    ap = argparse.ArgumentParser(description="EMG log viewer for team_mvc.ino captures")
    ap.add_argument("--list", action="store_true", help="list serial ports and exit")
    ap.add_argument("--port", default="COM5", help="serial port, e.g. COM5")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--replay", default=None, help="read a CSV log instead of a port")
    ap.add_argument("--out", default=None, help="write CSV log here")
    ap.add_argument("--window", type=float, default=8.0, help="plot window in seconds")
    ap.add_argument("--no-plot", action="store_true", help="print stats only")
    ap.add_argument("--save-png", default=None, help="save figure instead of showing it")
    ap.add_argument("--quiet", action="store_true", help="suppress firmware # lines")
    args = ap.parse_args()

    if args.list:
        list_ports()
        return 0
    if not args.replay and not args.port:
        print("Need --port (or --replay).", file=sys.stderr)
        return 2

    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
