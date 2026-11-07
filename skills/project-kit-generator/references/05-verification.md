# 05. Verifying a kit you cannot yet run on hardware

Most of the time you are writing a kit with no board in reach (or with the board reserved for the user).
The rule is: **verify everything you can on a laptop, look at the pictures yourself, and be exact about
what remains unproven.** The SHT40 kit's simulator caught bugs in layout, formatting and state handling
before the user ever saw them, and it also had blind spots that only the real board exposed.

## The simulator (`scripts/simlib.py`)

It runs the **real** lab files, `config.py` and `lib/` modules against fakes:

    export KIT_DIR=/path/to/src/kits/my-kit
    python3 -B my_test.py            # imports simlib, calls simlib.install(), runpy's a lab

- **Strict display**: raises on a draw outside the screen, on a zero-size rectangle, on a character outside the
  font, and on text that would be silently skipped by the real driver. Real hardware hides these; the simulator
  does not.
- **Fake clock with costs**: every draw call advances simulated time (0.3 ms per call, a *guess*), so a slow
  redraw delays the button like the real thing. `sleep_ms` advances the clock and runs scheduled events.
- **Realistic button**: contact chatter on press and release, and soft-IRQ handlers that run after the edge and
  read the *current* level (the model that reproduced the real bug).
- **Fake sensor world**: `World.profile(t_ms)` gives values over time, `World.fail_windows` makes reads fail, and
  `World.reset_fails_until` makes the soft reset fail. Replace `World.i2c_read/i2c_write` for another sensor.
- **Pictures**: `snapshot()` (review) and `round_rgba()` + `grid()` (transparent, for docs and box-cover art).
- **Geometry checks**: `text_box_problems()` (farthest corner beyond the safe radius) and `outside_pixels()`.

Adapt `install(width, height, circular, driver_module, driver_class)` for another display.

## Test layers (all three were needed)

1. **Per-mode/lab unit tests** (`scripts/examples/example_test_modes.py`): each mode against 3-6 readings including
   off-scale ones, fresh context each time; collect draw-call budgets (enter, first update, steady update); render
   a **contact sheet** per mode and **look at it**; run the geometry checks. Zero problems is the goal.
2. **End-to-end script** (`example_test_app.py`): run the real capstone for 30-60 s of simulated time with scripted
   button presses (tap x6 with wrap-around, a bouncy tap, a double tap, a 1 s hold, a 3.2 s hold), a warming
   sensor profile, two sensor outages, a dead sensor at boot, and a second boot that must load saved records.
   Assert the mode order, the LED beat count, read intervals per mode, records file contents, and that the shutdown
   path ran.
3. **Stress test for anything time-sensitive** (`stress_button.py`): random chatter, latency, redraw blind spots.

Also run, every time: `python3 -B -c "import ast..."` over every file, `bash -n upload-code.sh`, `pin_check.py`,
and a check that **the kit folder is clean** (`find kit -name __pycache__ -o -name '*.png'`).

## Real MicroPython, when it is available (found in the skill trials)

`ast.parse` only proves the files are valid **CPython**. A trial that ran the labs under the real MicroPython unix
port, with `time`, `Pin`, `SPI` and `ADC` faked, and compiled every file with `mpy-cross -march=armv6m`, could say "the
syntax and the imports are fine on the Pico's flavour of Python". A trial without them had to list it under
"could not verify". So check first:

```bash
which micropython mpy-cross       # already installed? use them
```

If they are missing, **ask the user before installing anything** (for example
`conda create -p <scratch>/mpy -c conda-forge micropython`, kept in the scratch folder, never in the repo). Then:

- `mpy-cross -march=armv6m <file>.py -o <scratch>/x.mpy` for every kit file (writes only to scratch);
- run a lab with `micropython`, putting a folder of fake `machine`/`utime` modules first on `MICROPYPATH`, and log every
  SPI byte and pin change; replay the bytes through a small model of the display chip to draw the screen.

This is an extra layer on top of `simlib.py`, not a replacement: it proves the language, not the timing or the memory
on the board. Say so.

## Look at the pictures

Numbers and asserts do not tell you a layout is ugly. Render every mode in its normal, extreme and failure
states, put them on one contact sheet, and open the image. Things this caught: text 8 px off centre, a
"cooling" screen still saying "getting warmer", a thin arc leaving a gap. Write down what you saw.

## Keep the scratch out of the kit

The simulator `chdir`s into the kit, so relative output paths and Python's `__pycache__` land **inside the kit**.
This happened once. Prevent it: `sys.dont_write_bytecode = True`, absolute output paths, and run from a scratch
folder. After every run: list the kit folder and delete anything you made. Write scratch to the session's
scratchpad, not `/tmp`, and not the repo.

## Check your expectations, not just the code

Two "failures" in the SHT40 tests were wrong expectations, not bugs: a double tap correctly advances two modes,
and a 526 ms gap between reads was the deliberate "fresh reading after a mode change". Before you "fix" a failing
check, ask which side is wrong.

## The checklist for the human (real hardware)

The simulator cannot prove these. End every report with the ones still open, as a short numbered list the user can
do in five minutes:

1. Run the button/LED test lab; press three times.
2. Run the capstone; tap through every mode and paste the console.
3. Hold about 1 s (units switch) and, in the records mode, 3 s (records clear); unplug and replug to check they persist.
4. Touch the sensor with a warm finger (the "touch it" mode).
5. Pull the SDA wire for a few seconds: expect the red SENSOR FAIL, two quick LED blinks, and recovery.
6. Watch the LED: once per reading, faster in the fast mode.
7. Say what looked or felt wrong (blank areas, leftovers, flicker, a long pause after a tap).

Ask for the console output. It is the fastest evidence you can get: `Free memory: 116288 bytes`, the mode names
in order, the length of every press.

## Reading the user's console log

- `Free memory` after loading everything: compare with what a fresh Pico has; >100 KB is comfortable.
- Each `Mode: values` line is a reading, so lines per mode tell you the read rate.
- `Button: N ms` lines show whether presses register and how long people hold.
- A missing mode name in the sequence means a press was lost.

## Reading a board the user pointed you at

When the user says "there is working code on the Pico", read it **read-only** (`mpremote devs`, `fs ls`, `fs cp
:file local`), copy it to the scratchpad, diff it against the repo, and say exactly what you read and that you wrote
nothing. On the SHT40 board it was older versions of labs 01-04, which still confirmed the wiring and I2C settings
worked. Never upload to the board unless asked.

## Viewing the built docs

Do not start or stop the user's `mkdocs serve`. Use `scripts/scratch_mkdocs_build.py` (repo-clean build), then
`scripts/headless_shot.sh` to render the built page to PNG slices and look at them. See 06-docs-and-lesson.md.
