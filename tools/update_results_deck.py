#!/usr/bin/env python
"""Update the final MyoSense presentation with the 2026-11-22 pilot readings.

    python tools/update_results_deck.py MyoSense_final_web_photo_schematic.pptx MyoSense_final_results.pptx

Requires python-pptx. The original deck is left untouched.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


NAVY = RGBColor(12, 28, 52)
ROW = RGBColor(25, 43, 68)
WHITE = RGBColor(241, 244, 251)
PALE = RGBColor(220, 228, 242)
AMBER = RGBColor(251, 191, 36)
GREEN = RGBColor(52, 211, 153)
CORAL = RGBColor(248, 113, 113)


def set_text(shape, text: str, *, size: float | None = None,
             color: RGBColor | None = None, bold: bool | None = None) -> None:
    shape.text = text
    if not shape.has_text_frame:
        return
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if size is not None:
                run.font.size = Pt(size)
            if color is not None:
                run.font.color.rgb = color
            if bold is not None:
                run.font.bold = bold


def format_cell(cell, text: str, *, fill: RGBColor, color: RGBColor,
                size: float = 10, bold: bool = False,
                align=PP_ALIGN.CENTER) -> None:
    cell.text = text
    cell.fill.solid()
    cell.fill.fore_color.rgb = fill
    cell.margin_left = Inches(0.05)
    cell.margin_right = Inches(0.05)
    cell.margin_top = Inches(0.04)
    cell.margin_bottom = Inches(0.04)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for paragraph in cell.text_frame.paragraphs:
        paragraph.alignment = align
        for run in paragraph.runs:
            run.font.name = "Aptos"
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color


def add_results_table(slide) -> None:
    data = [
        ["Lat pulldown / lat", "68, 78, 72", "72.7", "54, 63, 59", "58.7", "+14.0"],
        ["Lat pulldown / biceps", "27, 33, 40", "33.3", "44, 53, 71", "56.0", "−22.7"],
        ["Bench press / chest", "66, 69, 60", "65.0", "59, 59, 55", "57.7", "+7.3"],
        ["Bench press / triceps", "55, 53, 50", "52.7", "65, 66, 70", "67.0", "−14.3"],
    ]
    headers = ["Exercise / site", "Good readings (%)", "Mean", "Bad readings (%)", "Mean", "Good−bad (pp)"]
    table_shape = slide.shapes.add_table(
        rows=len(data) + 1,
        cols=len(headers),
        left=Inches(0.6),
        top=Inches(1.65),
        width=Inches(7.5),
        height=Inches(3.75),
    )
    table = table_shape.table
    widths = [1.65, 1.22, 0.72, 1.22, 0.72, 1.97]
    for col, width in enumerate(widths):
        table.columns[col].width = Inches(width)

    for col, header in enumerate(headers):
        format_cell(table.cell(0, col), header, fill=NAVY, color=WHITE,
                    size=9, bold=True,
                    align=PP_ALIGN.LEFT if col == 0 else PP_ALIGN.CENTER)

    for r, values in enumerate(data, start=1):
        for c, value in enumerate(values):
            color = PALE
            bold = False
            if c == 2:
                color, bold = GREEN, True
            elif c == 4:
                color, bold = CORAL, True
            elif c == 5:
                color, bold = AMBER, True
            format_cell(table.cell(r, c), value, fill=ROW, color=color,
                        size=10 if c != 0 else 9.5, bold=bold,
                        align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)

    note = slide.shapes.add_textbox(Inches(0.62), Inches(5.53), Inches(7.45), Inches(0.88))
    tf = note.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = (
        "Report: three participants per exercise group; L1/L2 lat pairs are in the PDF. L3 values "
        "(from slides 13–14) are user-identified participant 3; original slide footers call them "
        "illustrative. PDF and deck remain unchanged. Descriptive only."
    )
    run.font.name = "Aptos"
    run.font.size = Pt(10)
    run.font.color.rgb = PALE

    # Reuse the intentionally blank right-hand card on the results slide.
    panel = next(
        s for s in slide.shapes
        if s.has_text_frame and s.left > Inches(8) and s.width > Inches(3)
    )
    panel.text_frame.clear()
    panel.text_frame.word_wrap = True
    panel.text_frame.margin_left = Inches(0.24)
    panel.text_frame.margin_right = Inches(0.24)
    panel.text_frame.margin_top = Inches(0.20)
    panel.text_frame.margin_bottom = Inches(0.16)
    panel.text_frame.vertical_anchor = MSO_ANCHOR.TOP

    blocks = [
        ("Observed pattern", AMBER, True),
        ("Good-labelled readings were higher for lat (+14.0 pp) and chest (+7.3 pp). "
         "Bad-labelled readings were higher for biceps (22.7 pp) and triceps (14.3 pp).", PALE, False),
        ("Limits", AMBER, True),
        ("Three participants per exercise group in the report. L3 is supplemented from slide "
         "readouts per user confirmation; no independent form scoring.", PALE, False),
        ("Interpretation", AMBER, True),
        ("These are activation readings, not force or a validated form verdict. "
         "They do not show that a muscle took over.", PALE, False),
    ]
    for i, (text, color, bold) in enumerate(blocks):
        p = panel.text_frame.paragraphs[0] if i == 0 else panel.text_frame.add_paragraph()
        p.text = text
        p.space_after = Pt(5 if bold else 10)
        for run in p.runs:
            run.font.name = "Aptos"
            run.font.size = Pt(14 if bold else 12)
            run.font.bold = bold
            run.font.color.rgb = color


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    prs = Presentation(args.input)
    if len(prs.slides) < 17:
        raise SystemExit("expected the 20-slide MyoSense deck")

    # Slide 4: qualify the cross-session claim and distinguish target from measurement.
    slide4 = prs.slides[3]
    set_text(slide4.shapes[7],
             "ESP32-S3 targets 2 kHz; prior BLE build measured 1888 Hz (retest after notify-path fix)")
    set_text(slide4.shapes[13],
             "MVC = Maximum Voluntary Contraction\nEach user calibrates to their own maximum. "
             "Values remain sensitive to electrode site, placement, preparation and task; "
             "cross-session comparisons require those to be repeatable.")

    # Slide 7: report the measured rate honestly, not just the configured target.
    slide7 = prs.slides[6]
    text7 = slide7.shapes[4].text
    text7 = text7.replace(
        "samples at 2000 Hz, 12-bit resolution",
        "targets 2000 Hz (1888 Hz measured on prior BLE build; retest pending), 12-bit resolution",
    )
    set_text(slide7.shapes[4], text7, size=12, color=PALE)
    set_text(slide7.shapes[5],
             "2 kHz target · 1888 Hz prior-build measurement · 100 ms window · 10 Hz BLE · 12-bit ADC",
             size=12, color=PALE)

    # Slide 11: match the procedure to the actual dry-metal strap hardware.
    slide11 = prs.slides[10]
    set_text(slide11.shapes[3],
             "Use the in-hand 3-contact metal band. Place the two active contacts along the "
             "forearm muscle fibres, over the muscle belly (not the wrist tendons); put REF on "
             "a bony landmark. Record exact placement and whether Ten20 paste was used.", size=12, color=PALE)

    slide9 = prs.slides[8]
    set_text(slide9.shapes[7],
             "Key points\nEvery user calibrates to their own reference\n"
             "Current cycle: rest baseline + two maximal efforts; higher peak is retained\n"
             "Formal MVC repeatability across sessions is not measured\n"
             "Re-calibrate if electrodes move\nRest baseline is subtracted in quadrature → rest near 0 %",
             size=12, color=PALE)

    # Slides 13–14: replace the old illustrative single-clip values with the reported trials.
    slide13 = prs.slides[12]
    set_text(slide13.shapes[0], "LAT PULLDOWN  ·  L1–L3")
    set_text(slide13.shapes[1], "Latissimus activation: good vs bad condition")
    set_text(slide13.shapes[7], "58.7 %")
    set_text(slide13.shapes[8], "mean activation · n=3")
    set_text(slide13.shapes[9], "Pairs L1–L3: 54 %, 63 %, 59 %")
    set_text(slide13.shapes[14], "72.7 %")
    set_text(slide13.shapes[15], "mean activation · n=3")
    set_text(slide13.shapes[16], "Pairs L1–L3: 68 %, 78 %, 72 %")
    set_text(slide13.shapes[17],
             "L3 comes from the unchanged slide readout; user identifies it as participant 3. See provenance note.")

    slide14 = prs.slides[13]
    set_text(slide14.shapes[0], "LAT PULLDOWN  ·  L1–L3")
    set_text(slide14.shapes[1], "Biceps activation: good vs bad condition")
    set_text(slide14.shapes[7], "33.3 %")
    set_text(slide14.shapes[8], "mean activation · n=3")
    set_text(slide14.shapes[9], "Pairs L1–L3: 27 %, 33 %, 40 %")
    set_text(slide14.shapes[14], "56.0 %")
    set_text(slide14.shapes[15], "mean activation · n=3")
    set_text(slide14.shapes[16], "Pairs L1–L3: 44 %, 53 %, 71 %")
    set_text(slide14.shapes[17],
             "L3 comes from the unchanged slide readout; user identifies it as participant 3. See provenance note.")

    # Slide 15 was blank apart from its title and a reserved note card.
    slide15 = prs.slides[14]
    set_text(slide15.shapes[1], "User-reported activation readings by condition")
    add_results_table(slide15)

    # Slide 16: these software/reporting items are complete; standardised re-testing remains.
    slide16 = prs.slides[15]
    set_text(slide16.shapes[3],
             " \nPilot report: 3 participants/group\nL1/L2 lat pairs in PDF; L3 supplemental from slides\n"
             "CSV preserves pair IDs and source\nPrior BLE run: 1888 Hz; repeat after notify fix\n"
             "Standardise load, tempo, placement and MVC\nRepeat trials and verify rep counts", size=12, color=PALE)
    set_text(slide16.shapes[7],
             "Small pilot; L3 is slide-derived per user confirmation and not in the PDF tables. "
             "Repeat with fixed load, tempo, range, placement and cue; report all trials.", size=12, color=PALE)

    # Slide 17: preliminary observations exist, but they are not validation.
    slide17 = prs.slides[16]
    set_text(slide17.shapes[12], "MVC protocol implemented; repeatability across visits is not measured.")
    set_text(slide17.shapes[15], "Pilot values from three participants per group; no controlled accuracy or validation study.")
    set_text(slide17.shapes[17], "Pilot data; validation pending")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
