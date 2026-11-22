# Enclosure Prototype Files

These are early printable-case iterations for the MyoSense electronics. They are design
prototypes, not a verified wearable enclosure; check fit, ventilation, insulation, cable strain
relief and battery retention before wearing the assembly.

## Files

| File | Purpose |
|---|---|
| `box_with_fin.stl` | Open box with fin, 108 × 68 × 44 mm; primary interactive-viewer model |
| `box_with_fin_holes.stl` | Fin variant with mounting holes |
| `box_with_plate.stl` | Box variant with a mounting plate |
| `make_box_stl.py` | Generates the base fin model |
| `make_box_stl_holes.py` | Generates the fin model with holes |
| `make_box_stl_plate.py` | Generates the plate variant |
| `make_box_stl_rounded.py` | Rounded geometry iteration |
| `viewer.html` / `build_viewer.py` | Browser-based interactive preview and its builder |
| `preview_box.py`, `preview_views.py`, `render3d.py` | Local preview/render utilities |
| `draw_plate_views.py`, `draw_rounded_views.py` | Dimensioned-view generators |
| `box_*.png`, `plate_views*.png` | Rendered design previews |

The `box_with_fin_PLA_1h5m.gcode` slicer output is deliberately not published: it is printer-
and profile-specific generated output. Re-slice the STL for the printer/material being used.

## Safety and fit checks

- Keep the battery physically isolated from exposed solder joints and the EMG inputs.
- Add insulation and cable strain relief; the renders do not demonstrate electrical safety.
- Verify the actual board, battery and boost dimensions against the cavity before printing.
- Test closure and access to the USB-C/USB-A connections before a wearable trial.
- Do not wear the prototype while charging.
