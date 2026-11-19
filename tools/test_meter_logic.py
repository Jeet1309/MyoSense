#!/usr/bin/env python
"""Headless test for the logic inside app/meter.html.

Extracts the page's <script>, runs it under Node with a small DOM stub, then feeds
synthetic BLE payloads and asserts the resulting UI state:

    python tools/test_meter_logic.py

Requires Node on PATH. The firmware sends lines shaped like
`mean,rms,activation,calibrating,batt_mV,batt_pct,charging,flags,rest_mV,mvc_mV`
where flags is bit 0 = front end at a rail, bits 1-2 = next calibration step.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "app" / "meter.html"

PRELUDE = r"""
function makeEl(id) {
  return {
    id, style: {}, className: "", textContent: "", innerHTML: "",
    value: id === "lo" ? "60" : id === "hi" ? "80" : "",
    disabled: false, addEventListener() {}, appendChild() {}, removeChild() {},
  };
}
const ELS = {};
globalThis.document = {
  getElementById(id) { if (!ELS[id]) ELS[id] = makeEl(id); return ELS[id]; },
  createElement() { return makeEl("tmp"); },
  body: { appendChild() {}, removeChild() {} },
};
Object.defineProperty(globalThis, "navigator", { value: {}, writable: true, configurable: true });
// Controllable clock so link timing can be tested deterministically.
let __now = 0;
globalThis.__clock = {
  advance(ms) { __now += ms; },
  get now() { return __now; },
};
Object.defineProperty(globalThis, "performance", {
  value: { now: () => __now }, writable: true, configurable: true,
});
globalThis.URL = { createObjectURL: () => "blob:x", revokeObjectURL() {} };
globalThis.Blob = class { constructor() {} };
"""

TESTS = r"""
const __ui = ELS;
let __pass = 0, __fail = 0;

function check(name, cond, extra) {
  if (cond) { __pass++; console.log("  PASS  " + name); }
  else { __fail++; console.log("  FAIL  " + name + (extra !== undefined ? "   got: " + extra : "")); }
}

function feed(line, stepMs) {
  __clock.advance(stepMs === undefined ? 100 : stepMs);
  const bytes = new TextEncoder().encode(line);
  handleNotification({ target: { value: new DataView(bytes.buffer) } });
}

console.log("[A] idle sample with a battery present");
feed("1655,250.00,0.0,0,3830,55,0,0,0.00,0.00\n");
check("label is step 1", __ui.btnCal.textContent.includes("1/3"), __ui.btnCal.textContent);
check("activation 0", __ui.actVal.textContent === "0", __ui.actVal.textContent);
check("pill visible", __ui.battPill.style.display === "inline-flex", __ui.battPill.style.display);
check("pill shows 55%", __ui.battText.textContent.includes("55%"), __ui.battText.textContent);
check("pill green", __ui.battPill.className === "battery ok", __ui.battPill.className);

console.log("[B] rest baseline returned -> step 2");
feed("1655,1.20,0.0,0,3830,55,0,2,0.31,0.00\n");
check("label is step 2", __ui.btnCal.textContent.includes("2/3"), __ui.btnCal.textContent);
check("rest shown", __ui.mvcRef.textContent.includes("0.31"), __ui.mvcRef.textContent);

console.log("[C] MVC returned -> step 3");
feed("1655,1.10,1.5,0,3830,55,0,4,0.31,12.40\n");
check("label is step 3", __ui.btnCal.textContent.includes("3/3"), __ui.btnCal.textContent);
check("mvc shown", __ui.mvcRef.textContent.includes("12.4"), __ui.mvcRef.textContent);

console.log("[D] verify returned -> cycle restarts");
feed("1655,1.10,1.5,0,3830,55,0,0,0.31,12.40\n");
check("label back to step 1", __ui.btnCal.textContent.includes("1/3"), __ui.btnCal.textContent);

console.log("[E] rep counting, target band 60-80");
state.reps = 0;
state.inRep = false;
__ui.reps.textContent = "0";
feed("1655,10.0,10.0,0,3830,55,0,0,0.31,12.40\n");
check("no rep below the band", __ui.reps.textContent === "0", __ui.reps.textContent);
feed("1655,90.0,90.0,0,3830,55,0,0,0.31,12.40\n");
check("crossing high does not count yet", __ui.reps.textContent === "0", __ui.reps.textContent);
feed("1655,70.0,70.0,0,3830,55,0,0,0.31,12.40\n");
feed("1655,20.0,20.0,0,3830,55,0,0,0.31,12.40\n");
check("dropping below counts one rep", __ui.reps.textContent === "1", __ui.reps.textContent);

console.log("[F] activation above 100 %");
feed("1655,15.0,125.0,0,3830,55,0,0,0.31,12.40\n");
check("number not clamped", __ui.actVal.textContent === "125", __ui.actVal.textContent);
check("bar capped", __ui.fill.style.width === "100%", __ui.fill.style.width);

console.log("[G] no divider fitted");
feed("1655,15.0,20.0,0,0,-1,0,0,0.31,12.40\n");
check("pill hidden", __ui.battPill.style.display === "none", __ui.battPill.style.display);

console.log("[H] rail flag");
feed("3200,15.0,20.0,0,3830,55,0,1,0.31,12.40\n");
check("warning shown", __ui.quality.textContent.length > 10, __ui.quality.textContent);
feed("1655,15.0,20.0,0,3830,55,0,0,0.31,12.40\n");
check("warning cleared", __ui.quality.textContent === "", __ui.quality.textContent);

console.log("[I] calibrating flag");
feed("1655,15.0,0.0,1,3830,55,0,2,0.31,12.40\n");
check("status is calibrating", __ui.statusText.textContent.includes("calibrating"), __ui.statusText.textContent);
feed("1655,15.0,20.0,0,3830,55,0,4,0.31,12.40\n");
check("status back to connected", __ui.statusText.textContent === "connected", __ui.statusText.textContent);

console.log("[J] out-of-range step bits are ignored");
feed("1655,15.0,20.0,0,3830,55,0,6,0.31,12.40\n");
check("label stays valid",
      ["1/3", "2/3", "3/3"].some(s => __ui.btnCal.textContent.includes(s)),
      __ui.btnCal.textContent);

console.log("[K] acquisition rate and MVC/rest ratio");
feed("1655,15.0,20.0,0,3830,55,0,0,0.31,12.40,1998\n");
check("acquisition shown", __ui.acq.innerHTML.includes("1998"), __ui.acq.innerHTML);
check("ratio shown", __ui.mvcRef.textContent.includes("40\u00d7"), __ui.mvcRef.textContent);

console.log("[L] link rate and drops");
state.arrivals = [];
state.drops = 0;
for (let i = 0; i < 11; i++) feed("1655,15.0,20.0,0,3830,55,0,0,0.31,12.40,1998\n");
check("link near 10 Hz", __ui.link.innerHTML.startsWith("10"), __ui.link.innerHTML);
check("no drops at 100 ms spacing", __ui.drops.textContent === "0", __ui.drops.textContent);
feed("1655,15.0,20.0,0,3830,55,0,0,0.31,12.40,1998\n", 800);
check("gap counted as a drop", __ui.drops.textContent === "1", __ui.drops.textContent);

console.log("[M] weak MVC reference is flagged");
feed("1655,6.0,20.0,0,3830,55,0,0,3.00,6.00,1998\n");
check("weak reference warning", __ui.quality.textContent.includes("Weak reference"), __ui.quality.textContent);

console.log("[N] acquisition below target is flagged");
feed("1655,6.0,20.0,0,3830,55,0,0,0.31,12.40,1500\n");
check("slow acquisition warning", __ui.quality.textContent.includes("2 kHz"), __ui.quality.textContent);

console.log("[O] low battery warning");
feed("1655,6.0,20.0,0,3450,10,0,0,0.31,12.40,1998\n");
check("low battery warning", __ui.quality.textContent.includes("Battery low"), __ui.quality.textContent);

console.log("\n" + __pass + " passed, " + __fail + " failed");
if (__fail > 0) process.exitCode = 1;
"""


def main() -> int:
    if not HTML.exists():
        print(f"missing {HTML}", file=sys.stderr)
        return 2

    html = HTML.read_text(encoding="utf-8")
    match = re.search(r"<script>(.*?)</script>", html, re.S)
    if not match:
        print("no <script> block found", file=sys.stderr)
        return 2

    bundle = PRELUDE + match.group(1) + TESTS
    with tempfile.TemporaryDirectory() as tmp:
        target = pathlib.Path(tmp) / "meter_test.mjs"
        target.write_text(bundle, encoding="utf-8")
        try:
            result = subprocess.run(
                ["node", str(target)], capture_output=True, text=True
            )
        except FileNotFoundError:
            print("node is not installed or not on PATH", file=sys.stderr)
            return 2

    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
