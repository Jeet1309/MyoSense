# MyoSense Share Pack

**Start with `EMG_WEARABLE_FROM_SCRATCH.pdf`.** It explains the project from the physiology up through the current prototype, MVC calibration, experiment design and limits. `EMG_WEARABLE_FROM_SCRATCH.md` is the accessible source version.

## Pack contents

- `EMG_WEARABLE_FROM_SCRATCH.pdf` — compiled guide for sharing/reading.
- `EMG_WEARABLE_FROM_SCRATCH.md` — source text with citations and links.
- `SHARE_REFERENCES.md` — what is bundled, where each local source came from, and external references.
- `references/` — a curated set of locally held, relevant open-access research PDFs; files are copied unchanged.

## Current design status

The user currently has one generic ESP32-S3 N16R8 development board, a 3.7 V 1000 mAh Li-ion cell, an HW-373/TP4056-style charger board, an HW-106 3.7 V→5 V boost with USB-A output, one single-channel Muscle BioAmp-style EMG board (likely Candy; exact revision unverified), and one three-contact strap/lead set. Acquisition firmware and a live-plot tool are in `../firmware/` and `../tools/`. After identification and a safe power setup, this supports a one-channel bench test and a **sequential site-by-site MVC/reference demonstration**. It does not measure sites simultaneously. **Two-channel testing still needs another front end and electrode set.** The pictured charger is not a 5 V regulator; read `../PROTOTYPE_BENCH_TEST_HANDOFF.md` before attempting battery/body testing.

The older `MyoSense_A2_DH803.docx`, `MyoSense_A2_DH803.pptx` and `EMG Project Communications Subsystem Plan.pdf` are earlier course drafts. Their FireBeetle/SEN0240/20–450 Hz assumptions are not the photographed prototype BOM. They are not reproduced here as current design instructions.

## References and sharing

The complete research archive remains in `../references/pdfs/`. This share pack includes a **curated subset**, not every item. Course slides and other course/team documents remain in their original folders and are cited in the guide rather than copied. Check source licenses before re-hosting the PDF bundle publicly.

Prices and stock are snapshots, not purchase guarantees. Re-check seller listings, exact board/sensor revision, connector and polarity before ordering.
