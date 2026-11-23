#!/usr/bin/env python
"""Small regression tests for BLE payload parsing and session CSV analysis."""

from __future__ import annotations

import importlib.util
import csv
import statistics
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


emg_ble = load_module("emg_ble", ROOT / "tools" / "emg_ble.py")
plot_session = load_module("plot_session", ROOT / "tools" / "plot_session.py")


class BlePayloadTests(unittest.TestCase):
    def test_full_payload_preserves_battery_calibration_and_rate(self):
        row = emg_ble.parse_payload("1655,2.50,33.3,0,3830,55,1,0,0.31,12.4,1998", 100.0)
        self.assertEqual(row["batt_mV"], 3830)
        self.assertEqual(row["batt_pct"], 55)
        self.assertEqual(row["charging"], 1)
        self.assertEqual(row["rest_mV"], 0.31)
        self.assertEqual(row["mvc_mV"], 12.4)
        self.assertEqual(row["acq_hz"], 1998)

    def test_older_short_payload_keeps_compatible_defaults(self):
        row = emg_ble.parse_payload("1655,2.50,33.3,0", 100.0)
        self.assertEqual(row["activation"], 33.3)
        self.assertEqual(row["batt_mV"], 0.0)
        self.assertEqual(row["acq_hz"], 0.0)


class SessionCsvTests(unittest.TestCase):
    def test_app_export_and_summary_comments(self):
        content = (
            "t_s,mean_mV,rms_mV,activation_pct,calibrating,batt_mV,batt_pct,charging,rest_mV,mvc_mV\n"
            "0.0,1650,0.3,2,0,3830,55,0,0.3,12\n"
            "0.1,1650,9,85,0,3830,55,0,0.3,12\n"
            "0.2,1650,0.3,2,0,3829,55,0,0.3,12\n"
            "# session summary\n# reps,1\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "app.csv"
            path.write_text(content, encoding="utf-8")
            rows, _ = plot_session.load(str(path))
        result = plot_session.stats(rows, 60, 80)
        self.assertEqual(result["reps"], 1)
        self.assertAlmostEqual(result["rest"], 0.3)
        self.assertAlmostEqual(result["batt_start"], 3830)

    def test_serial_ble_logger_export_and_milliseconds(self):
        content = (
            "t_ms,mean_mV,rms_mV,activation,calibrating,batt_mV,batt_pct,charging,flags,rest_mV,mvc_mV,acq_hz\n"
            "1000,1650,0.3,2,0,3830,55,0,0,0.3,12,1998\n"
            "1100,1650,9,75,0,3830,55,0,0,0.3,12,1998\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ble.csv"
            path.write_text(content, encoding="utf-8")
            rows, _ = plot_session.load(str(path))
        self.assertAlmostEqual(rows[0]["t"], 1.0)
        self.assertEqual(rows[0]["batt"], 3830)
        self.assertEqual(rows[1]["mvc"], 12)


class PreliminaryReportTests(unittest.TestCase):
    def test_source_values_and_descriptive_means(self):
        path = ROOT / "data" / "form_comparison_2026-11-22.csv"
        with path.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 24)

        def mean(exercise_part: str, muscle: str, form: str) -> float:
            values = [
                float(r["activation_pct"])
                for r in rows
                if exercise_part in r["exercise"]
                and r["muscle"] == muscle
                and r["form_label"] == form
            ]
            return statistics.mean(values)

        self.assertAlmostEqual(mean("Lat", "Latissimus dorsi", "good"), 72.6667, places=3)
        self.assertAlmostEqual(mean("Lat", "Latissimus dorsi", "bad"), 58.6667, places=3)
        self.assertAlmostEqual(mean("Lat", "Biceps brachii", "good"), 33.3333, places=3)
        self.assertEqual(mean("Lat", "Biceps brachii", "bad"), 56.0)
        self.assertAlmostEqual(mean("Chest press", "Pectoralis major", "good"), 65.0)
        self.assertAlmostEqual(mean("Chest press", "Triceps brachii", "bad"), 67.0)
        l3 = [r for r in rows if r["pair_id"] == "L3"]
        self.assertEqual(len(l3), 4)
        self.assertTrue(all("user identifies as participant 3" in r["source"] for r in l3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
