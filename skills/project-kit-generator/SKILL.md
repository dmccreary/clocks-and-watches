---
name: project-kit-generator
description: Turns a boring single-sensor MicroPython lab into a fun, complete, classroom-ready project kit for students - a low-cost (about $5) colorful display as a "window" on the sensor, an incremental ladder of numbered labs (bus scan, single reading, CSV log, Thonny Plotter, display hello, live display, button and LED test, multi-mode capstone), a strict desktop simulator so it is verified before any hardware exists, a friendly 6th-grade lesson and README, docs images, a session log, and a printable box cover (fun name, real photo, QR code). Use this whenever the user wants to make a lab or sensor "more fun", "more colorful" or "more engaging", add a display or a button to a sensor project, create or copy a kit under src/kits or docs/kits, plan the labs for a new kit, write the lesson or README for a kit, design a kit box cover, or says things like "kit", "project kit", "mood ring", "Thonny plotter lab", "GC9A01", "smartwatch display", "TEST PASS labs" - even if they never say "kit generator".
compatibility: Python 3 with numpy and Pillow (simulator and pictures); Google Chrome (page screenshots); mpremote only if the user wants a board read; segno for QR codes; the `mkdocs` conda env for docs builds.
---

# Project Kit Generator

Most sensor labs are boring: a number scrolls past in a console and nothing in the room seems to change. This skill turns one
into a kit students want to build. The recipe, proven on the SHT40 "Mood Ring Thermometer" kit:

> **Put the sensor on a cheap, colourful display so students watch it react to their breath and fingertips; teach it in small
> tested steps; prove it works on a laptop before hardware exists; and wrap it in a lesson and a box cover people want to pick up.**

**Reference implementation** (read it when a detail here is not enough; paths are in the learning-micropython repo):
`src/kits/sht40-temp-display/` (labs, `config.py`, `lib/`), `docs/kits/sht40-temp-display/index.md` (the lesson),
`artwork/thinking-spot/` (box cover art), and `logs/sht-40-temp-display-generation.md` (decisions and mistakes).

## What a finished kit contains

| Deliverable | Where | Made in phase |
|-------------|-------|---------------|
| Hardware plan: parts and prices, confirmed vs assumed, pin table with no conflicts | kit README + session log | 1 |
| Numbered labs `01-...` to `09-...`, each printing `TEST PASS`/`TEST FAIL`; one `config.py`; `lib/`; `upload-code.sh` | `src/kits/<kit>/` | 2-5 |
| Simulator tests, contact sheets, stress tests, a checklist for the human | scratch folder (never the kit) | 6 |
| Kit README and the student lesson with images, quiz, teacher notes | `src/kits/<kit>/README.md`, `docs/kits/<kit>/index.md` | 7 |
| Session log, memory notes, box cover art and HTML, optional commit | `logs/`, `artwork/`, memory | 8 |

## Principles (each one is here because skipping it cost something)

1. **Ask which parts the user really has before designing around them.** A NeoPixel lab was carried into a kit that had no NeoPixel; it
   had to be ripped out with its settings and docs. Ask once, early, about every extra part you assumed.
2. **Copy first, then prove the copy is exact** (`cp -R`, then `diff -r` shows only new files). Parent labs that already read every pin from
   `config` and already end in `TEST PASS`/`TEST FAIL` stay byte-identical. If a parent lab lacks the ending or hard-codes a pin, changing it in
   the new kit is right (the ladder needs one habit), but say so in the report. The parent kit itself is never edited.
3. **One `config.py` holds every pin and setting**; labs never hard-code pins; `import config` must never fail (import drivers inside
   `init_display()`). Run `scripts/pin_check.py` on every change.
4. **Each lab teaches one idea and ends with `TEST PASS`/`TEST FAIL` and a next step.** Test each part alone before combining them.
5. **Read the repo's content guidelines before writing anything a student reads** (reading level, mascot rules, vocabulary).
6. **Buttons are always read with a pin interrupt and a 50 ms debounce**, and the handler never reads the pin to guess press versus release
   (a first version lost about 40% of presses on real contacts).
7. **Be exact about what is proven.** The simulator proves logic and layout; only the board proves timing, memory and the interrupt.
   End with the short checklist of what only the user can check. Never let "tests pass" mean more than it does.
8. **Look at your pictures.** Render every state to a contact sheet and open it; numbers do not show an ugly layout.
9. **Keep scratch out of the kit and the repo.** Absolute output paths, no bytecode, run from a scratch folder, list the kit folder afterwards.
10. **Student safety and honesty in the content**: no activity that could make students hyperventilate (no breath races), nothing wet near
    electronics, 3.3 V never 5 V, captions that say a picture is a simulator render, no claim the kit cannot back up.
11. **Do what was asked, then offer.** Do not commit, upload to the board, rename files, edit `mkdocs.yml` or reshape the user's edits unless
    asked; say what you left alone.

## Workflow

Do the phases in order, and show the user a small result at the end of each so they can redirect early. A phase's detail lives in the
reference named next to it; read that file when you start the phase.

### Phase 0. Intake

Read the repo first: `CLAUDE.md` (project and global), the content guidelines, the parent kit (config, labs, upload script, README), any
sibling kit that already runs the display you plan to use (copy its pins), and the user's existing skills for the parts you will need
(see "Companion skills"). Then settle, with the user only where the answer is not in the repo:

- The sensor and the parent lab (or "from scratch"); the audience (default: 10-12 year olds, 90 minutes over two periods, breadboard,
  no soldering); where the kit will live (`src/kits/<name>/`, `docs/kits/<name>/`).
- Which extra parts exist (display, button, LED strip, buzzer). **Confirmed or assumed?** Ask about the assumed ones.
- Scope cuts the user wants (on the SHT40 kit: no pressure; no breath race).
- Whether a board is attached that you may read (read-only, and say so).

### Phase 1. Choose the hardware  ->  `references/01-choosing-hardware.md`

Find the ~$5 colour display (criteria, search terms, driver check, listing screenshot), read its driver (frame buffer? call costs?
font range?), plan pins with `pin_check.py`, write the parts-and-prices table, and pick the hook that makes this sensor visible
(bar, face, graph, gauge, records, touch test). Give the kit a fun name.

### Phase 2. Branch the kit

`cp -R` the parent kit to the new folder, `diff -r` to prove it, then edit. Keep the parent untouched. Remove parts the kit does not have
together with their settings, and refill the lab number instead of leaving a gap. Vendor the display driver, fonts and `shapes.py` into
`lib/` so the kit is self-contained; import them lazily.

### Phase 3. Build the lab ladder  ->  `references/02-lab-ladder.md`

`01` bus/pin scan, `02` one reading, `03` CSV log, `04`/`05` **Thonny Plotter labs (numbers only)**, `06` display hello (no sensor), `07`
first display program, `08` button + LED test, `09` multi-mode capstone that becomes `main.py`. Start from `assets/example-labs/`
and `assets/templates/config.template.py`; `assets/upload-code.sh` uploads `lib/`, config, labs and `main.py`.

### Phase 4. Design the display and its modes  ->  `references/03-display-design.md`

Fixed-width fields and no clearing; layout inside the safe circle; gradients and the mood-ring colour language; icons from circles,
rectangles and triangles (water drop, thermometer); arc gauges; a mode framework (`enter`/`update`/`tick`); a call-cost budget. Copy
from `assets/starter-lib/` and `assets/example-modes/` rather than writing from scratch.

### Phase 5. Buttons, the heartbeat LED, saved records  ->  `references/04-buttons-and-io.md`

`assets/starter-lib/button.py` (interrupt + 50 ms debounce, burst design), `heartbeat.py` (one blink per reading, two on failure),
`records.py` (flash-friendly saves). Run `scripts/stress_button.py` on any change to the button.

### Phase 6. Verify without hardware  ->  `references/05-verification.md`

Set `KIT_DIR`, use `scripts/simlib.py` (strict display, fake clock with costs, chattering button, fake sensor world), write per-mode tests
and an end-to-end script (see `scripts/examples/`), render contact sheets and **open them**, keep budgets, syntax-check everything, confirm
the kit folder is clean. Prepare the numbered checklist for the human and ask for their console log.

### Phase 7. Write the docs  ->  `references/06-docs-and-lesson.md`

Fill `assets/templates/lesson-template.md` and `kit-readme-template.md` from real lab outputs; render docs pictures from the simulator;
test every challenge; run `scripts/check_lesson.py`; build with `scripts/scratch_mkdocs_build.py`; look at the page with
`scripts/headless_shot.sh`. Offer the nav lines for `mkdocs.yml` (never `navigation.tabs`). Swap in the user's real photo when it arrives.

### Phase 8. Launch  ->  `references/07-launch-and-box-cover.md`

Session log from `assets/templates/session-log-template.md`; memory notes for durable preferences; the **box cover** (fun name, real photo,
simulator hero strip, 18 chips, mascot, QR) via `make_qr_symbol.py`, `fill_box_cover.py` and `headless_shot.sh`; commit and push only if asked,
staging only your files.

## When time is short

Cut in this order, and tell the user what you cut: modes 5 and 6 (finger test, records), then the character mode and gauges, then the box cover, then
the extension step in the lesson. Never cut the `TEST PASS` ladder, the pin check, the simulator run, the honest verification statement, or the guideline
check on student-facing text.

## Bundled resources

| Path | Use |
|------|-----|
| `references/01..07-*.md` | the detail for each phase (read on demand) |
| `assets/starter-lib/` | `button.py`, `heartbeat.py`, `records.py`, `widgets.py` (colours, gradients, icons, arc gauge), `display_ctx.py` (Context + Mode), `sensor_example_sht40.py` (rename to your sensor) |
| `assets/example-modes/` | six SHT40 modes as patterns: classic, Buddy face, live graph, ring gauges, finger test, hi/lo records |
| `assets/example-labs/` | proven labs 01, 02, 04, 05, 06, 08 and the capstone 09 (`09-display-modes-capstone.py`, expects `lib/sht40.py`) |
| `assets/upload-code.sh` | uploader with `MAIN_LAB` |
| `assets/templates/` | `config.template.py`, `lesson-template.md`, `kit-readme-template.md`, `session-log-template.md`, `box-cover-template.html` |
| `scripts/simlib.py` | the strict simulator (needs `KIT_DIR`) |
| `scripts/stress_button.py` | chatter/latency stress test for a button implementation |
| `scripts/pin_check.py` | duplicate and invalid pin finder; prints the physical-pin table |
| `scripts/check_lesson.py` | mechanical writing-rule checker for a lesson |
| `scripts/scratch_mkdocs_build.py`, `scripts/headless_shot.sh` | repo-clean docs build; page/cover screenshots in slices |
| `scripts/make_qr_symbol.py`, `scripts/fill_box_cover.py` | QR symbol and verified box-cover fill |
| `scripts/examples/` | example per-mode test, end-to-end test and docs-image maker (the SHT40 versions) |

The example modes and labs are SHT40-specific (they use `ctx.temp_f` and `ctx.humidity`). Keep their structure and rename the values for the new
sensor. The example tests run against a kit assembled from these assets plus the display driver files, which proves the bundle is consistent.

## Companion skills (use them when present)

`kit-box-cover-generator` (robot-faces house-style cover), `purchasing-guide-generator` (classroom parts page), `circuit-diagram-generator` and
`breadboard-sim-generator` (wiring diagrams: the SHT40 lesson still has none, which the repo's contributing rules want), `hands-on-lab-evaluator`
(score the finished lab against the rubric), `challenge-card` (printable challenge cards), `micropython-oled-render` (preview mono OLED code),
`microsim-generator` (an interactive simulator page), `skill-creator` (improve this skill after each kit).

## If you catch yourself

- writing a lab that reads a pin number literally -> put it in `config.py` and run `pin_check.py`;
- clearing the screen to update a number -> use a fixed-width field;
- reading a pin inside an interrupt handler -> use the burst design in `button.py`;
- saying "it works" after only a simulator run -> say what was and was not run;
- writing student text before reading the guidelines -> stop and read them;
- leaving files in the kit folder from a test -> list the folder and clean it;
- adding a part, lab or mode the user did not ask for -> ask, or say you assumed;
- about to commit everything in the working tree -> stage only your files.
