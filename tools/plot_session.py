#!/usr/bin/env python
"""Plot a MyoSense session and print its statistics.

Accepts either CSV:

  * the browser app's "Save CSV" export
    (t_s, mean_mV, rms_mV, activation_pct, calibrating, batt_mV, batt_pct, charging, ...)
  * the serial capture from tools/emg_capture.py
    (t_ms, raw, filt, rms, rms_mV, peak, clipped, activation)

    python tools/plot_session.py logs/session.csv --save-png logs/session.png
    python tools/plot_session.py logs/session.csv --lo 60 --hi 80
    python tools/plot_session.py logs/session.csv --show

Panels, when the data is present: activation against the target band, RMS envelope,
battery voltage. Reps are counted with the same hysteresis the app uses.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import statistics
import sys

APP_COLUMNS = {
    "t": "t_s",
    "rms": "rms_mV",
    "act": "activation_pct",
    "batt": "batt_mV",
    "rest": "rest_mV",
    "mvc": "mvc_mV",
}

SERIAL_COLUMNS = {
    "t": "t_ms",
    "rms": "rms_mV",
    "act": "activation",
    "batt": None,
    "rest": None,
    "mvc": None,
}


def load(path: str) -> tuple[list[dict], dict]:
    """Return (rows, column map) for either format."""
    with io.open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]

    if not lines:
        raise SystemExit(f"{path} has no data rows")

    header = [h.strip() for h in lines[0].strip().split(",")]
    if "activation_pct" in header:
        mapping = APP_COLUMNS
    elif "t_ms" in header and "rms_mV" in header:
        mapping = SERIAL_COLUMNS
        mapping = dict(mapping, t_scale=0.001)
    else:
        raise SystemExit(
            "unrecognised CSV - expected the app export or the serial capture header"
        )

    rows: list[dict] = []
    for line in lines[1:]:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        try:
            record = {}
            for key, column in mapping.items():
                if key in ("t_scale",):
                    continue
                if column is None or column not in header:
                    record[key] = None
                    continue
                value = parts[header.index(column)]
                record[key] = float(value) if value not in ("", "nan") else None
            rows.append(record)
        except (ValueError, IndexError):
            continue

    if not rows:
        raise SystemExit("no parsable rows")

    scale = mapping.get("t_scale", 1.0)
    if scale != 1.0:
        for r in rows:
            if r["t"] is not None:
                r["t"] *= scale

    return rows, mapping


def count_reps(times: list[float], acts: list[float], lo: float, hi: float) -> list[float]:
    reps = []
    inside = False
    for t, a in zip(times, acts):
        if not inside and a > hi:
            inside = True
        elif inside and a < lo:
            inside = False
            reps.append(t)
    return reps


def stats(rows: list[dict], lo: float, hi: float) -> dict:
    times = [r["t"] for r in rows if r["t"] is not None]
    acts = [r["act"] for r in rows if r["act"] is not None]
    rms = [r["rms"] for r in rows if r["rms"] is not None]

    reps_at = count_reps(times, acts, lo, hi)

    in_zone = 0.0
    for i in range(1, len(times)):
        if lo <= acts[i] <= hi:
            dt = times[i] - times[i - 1]
            if 0 < dt < 1.0:
                in_zone += dt

    rest = next((r["rest"] for r in rows if r.get("rest")), None)
    mvc = next((r["mvc"] for r in rows if r.get("mvc")), None)

    batt = [r["batt"] for r in rows if r.get("batt") and r["batt"] > 2600]

    return {
        "duration": times[-1] - times[0] if times else 0.0,
        "rows": len(rows),
        "peak": max(acts) if acts else 0.0,
        "median": statistics.median(acts) if acts else 0.0,
        "p95": sorted(acts)[int(0.95 * (len(acts) - 1))] if acts else 0.0,
        "rms_median": statistics.median(rms) if rms else 0.0,
        "rms_max": max(rms) if rms else 0.0,
        "reps": len(reps_at),
        "rep_times": reps_at,
        "in_zone": in_zone,
        "rest": rest,
        "mvc": mvc,
        "batt_start": batt[0] if batt else None,
        "batt_end": batt[-1] if batt else None,
    }


def print_stats(s: dict, lo: float, hi: float) -> None:
    print(f"duration        : {s['duration']:.1f} s over {s['rows']} samples")
    print(f"activation      : median {s['median']:.1f}%   p95 {s['p95']:.1f}%   peak {s['peak']:.1f}%")
    print(f"target band     : {lo:.0f}-{hi:.0f}%   time in band {s['in_zone']:.1f} s")
    print(f"reps detected   : {s['reps']}")
    print(f"rms             : median {s['rms_median']:.2f} mV   max {s['rms_max']:.2f} mV")
    if s["rest"]:
        print(f"rest baseline   : {s['rest']:.2f} mV")
    if s["mvc"]:
        print(f"mvc reference   : {s['mvc']:.2f} mV", end="")
        if s["rest"]:
            print(f"   ({s['mvc'] / s['rest']:.1f}x noise floor)")
        else:
            print()
    if s["batt_start"]:
        print(f"battery         : {s['batt_start'] / 1000:.2f} V -> {s['batt_end'] / 1000:.2f} V")


def draw(rows: list[dict], s: dict, lo: float, hi: float, out: str | None, show: bool) -> None:
    import matplotlib

    if out and not show:
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    times = [r["t"] for r in rows if r["t"] is not None]
    acts = [r["act"] for r in rows if r["act"] is not None]
    rms = [r["rms"] for r in rows if r["rms"] is not None]
    batt_rows = [r for r in rows if r.get("batt") and r["batt"] > 2600]

    panels = 1 + (1 if len(rms) == len(times) else 0) + (1 if batt_rows else 0)
    fig, axes = plt.subplots(panels, 1, sharex=True, figsize=(10, 2.6 * panels), squeeze=False)
    axes = [ax for row in axes for ax in row]

    ax = axes[0]
    ax.plot(times, acts, color="#3d7eff", linewidth=1.1)
    ax.axhspan(lo, hi, color="#3d7eff", alpha=0.12, label=f"target {lo:.0f}-{hi:.0f}%")
    ax.axhline(100, color="#e8595a", linestyle="--", linewidth=0.8, label="MVC (100%)")
    if s["rest"] and s["mvc"]:
        ax.axhline(0, color="#2ecc71", linewidth=0.8)
    for rt in s["rep_times"]:
        ax.axvline(rt, color="#8b98a9", linestyle=":", linewidth=0.8)
    ax.set_ylabel("activation (%)")
    ax.set_title("MyoSense session")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.15)

    idx = 1
    if len(rms) == len(times):
        ax = axes[idx]
        ax.plot(times, rms, color="#f2b134", linewidth=0.9)
        if s["rest"]:
            ax.axhline(s["rest"], color="#2ecc71", linestyle="--", linewidth=0.8, label="rest baseline")
            ax.legend(loc="upper right", fontsize=8)
        ax.set_ylabel("RMS (mV)")
        ax.grid(alpha=0.15)
        idx += 1

    if batt_rows:
        ax = axes[idx]
        ax.plot([r["t"] for r in batt_rows], [r["batt"] / 1000 for r in batt_rows],
                color="#2ecc71", linewidth=1.0)
        ax.set_ylabel("battery (V)")
        ax.set_xlabel("time (s)")
        ax.grid(alpha=0.15)
    else:
        axes[-1].set_xlabel("time (s)")

    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)

    fig.tight_layout()
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        fig.savefig(out, dpi=140)
        print(f"wrote {out}")
    if show:
        plt.show()
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot and summarise a MyoSense session.")
    ap.add_argument("csv", help="session CSV (app export or serial capture)")
    ap.add_argument("--lo", type=float, default=60.0, help="target band low %%")
    ap.add_argument("--hi", type=float, default=80.0, help="target band high %%")
    ap.add_argument("--save-png", default=None)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    rows, _ = load(args.csv)
    summary = stats(rows, args.lo, args.hi)
    print_stats(summary, args.lo, args.hi)

    if args.save_png or args.show:
        draw(rows, summary, args.lo, args.hi, args.save_png, args.show)
    elif not args.save_png:
        print("\n(add --save-png out.png or --show to draw the plot)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
