# 02. The lab ladder: incremental labs that each prove one thing

Students (and you) should never debug three new things at once. The ladder adds one part or one
idea per lab, and every lab ends with a line a beginner can act on: `TEST PASS` or `TEST FAIL`.

## The ladder (SHT40 kit as the worked example)

| # | Lab | Teaches | Needs | Ends with |
|---|-----|---------|-------|-----------|
| 01 | Bus scanner | "is the part even there?" (I2C scan; for an analog sensor, read the ADC; for a digital pin, read the pin) | sensor | list of addresses, `TEST PASS` |
| 02 | One reading | send a command, wait, read bytes, check the checksum, convert units | sensor | the numbers, `TEST PASS` |
| 03 | CSV logging | a loop, min/max, Ctrl-C summary | sensor | CSV rows, summary, `TEST PASS` |
| 04 | Thonny Plotter, all values | a live graph with no display hardware | sensor | numbers only |
| 05 | Thonny Plotter, one value | the same, one line, friendlier unit (F) | sensor | numbers only |
| 06 | Display hello | the screen works and x/y positions make sense | display (no sensor!) | `TEST PASS` + "look at the screen" |
| 07 | First real display program | fixed-width fields, no flicker, colour bands, sensor-fail banner | both | a live reading per second |
| 08 | Button and LED test | interrupt, debounce, heartbeat | button | `TEST PASS` after 3 presses |
| 09 | Multi-mode capstone | modes, gauges, graphs, records | everything | becomes `main.py` |

Adapt the rungs to the sensor, but keep the order of *risk*: bus/pin test, then a single reading,
then continuous data, then the screen alone, then screen plus sensor, then extras, then the
capstone. Rungs 04 and 05 are the "Thonny plotting" step and are cheap wins: they need no display
and show the sensor's speed and precision immediately.

**Do not leave a numbering gap.** When the NeoPixel lab was removed, lab 05 became a new
temperature-only plot rather than leaving 04 -> 06. A gap makes students think a file is missing.

## Rules every lab follows

1. **One idea per lab.** If a lab teaches display setup, a sensor read and error handling at once, split it
   (lab 06 exists so lab 07 does not have to teach "does the screen work").
2. **Header comment first**: what it does, what to run before it, the wiring (with pin names), and what
   the student should see. Written for a 10-year-old, in plain words.
3. **Pins and constants come from `config.py`.** No `Pin(15)` in a lab. Add a `_PIN` setting instead so
   `pin_check.py` sees it.
4. **Print `TEST PASS` / `TEST FAIL`** with a next step on failure ("Run 01-i2c-scanner.py to check the
   wiring"). Tests that cannot truly verify (a write-only display) must say so: the display hello lab
   prints "Look at the display. Do you see Hello World?" before `TEST PASS`.
5. **Give the sensor a clean start**: send the soft reset, and if it does not answer print the
   "unplug and replug" advice and `raise SystemExit`. (The capstone is different: it shows SENSOR FAIL
   and keeps retrying so the watch recovers by itself.)
6. **Labs 01-08 are self-contained**: they carry their own small helper (crc8, read function). A student
   reads one file top to bottom. Only the capstone, which needs the same code in six modes, moves it into
   `lib/` (sht40.py). Say so in the capstone's header. Trade-off: repeated code, but each lab stays readable.
7. **`%` formatting for fixed-width numbers on the display** (`"%5.1f" % x`), as a nested `str.format`
   width has been unreliable on some builds. Text labs may use `.format`.
8. **Ctrl-C is a clean exit** where the lab draws or writes: turn the LED off, show "Stopped", save records.

## Thonny Plotter labs (04 and 05)

The Plotter graphs every number it sees, so the lab prints **only numbers**:

- one line per reading: `26.94 50.32` (or one number for the single-value lab);
- **no heading, no summary, no "TEST PASS"**: a stray word draws junk or a bogus point;
- a failed reading prints **nothing** (a catch that passes) and the loop tries again; say in a
  comment: "if the graph freezes, stop and run the scanner";
- state the units in the header comment; the single-value lab converts to the friendlier unit
  (Fahrenheit for a US classroom) and tells the reader how to get the other one;
- prefer a temperature-only lab that checks **only the temperature checksum**, so a scrambled
  humidity half does not throw away a good temperature (say so in a comment).

Header tells the student: open the file, View > Plotter, Run, then "breathe / touch the sensor and watch
the line move".

## The display hello lab (06)

Needs no sensor. Draws one line of big text centered, prints the coordinates it used, and works
the arithmetic in comments so the lesson can repeat it: 12 letters x 16 dots = 192 dots, half is 96,
centre 120 - 96 gives x = 24; the 32-dot font gives y = 120 - 16 = 104. The lesson prints these numbers
in a puzzle table that matches the lab's output exactly.

## Copy the parent kit, then branch (when extending an existing kit)

1. `cp -R` the parent kit to the new folder **and run `diff -r` before you edit anything**. It should show
   only the new files. This proves the copy is exact (the user asked for an "exact copy"), and every
   unchanged lab stays byte-identical to the original so a fix in one place is easy to port.
2. Edit `config.py`, add the new labs, add `lib/`, update the README and upload script.
3. If a parent lab uses a part this kit does not have, delete the lab **and** its settings (grep for each
   name first: only delete a setting if nothing else uses it) and refill the number.
4. Keep the parent kit untouched. `git status` should show only the new folder.

## The upload script

Start from `assets/upload-code.sh`. It: finds the board with `mpremote devs` (skipping Bluetooth
ports), refuses when two boards are found and prints the `PORT=... ./upload-code.sh` retry, checks the
port is free (Thonny holds it), uploads `lib/` first, then `config.py`, then every `NN-*.py`, and
finally copies the capstone to `:main.py`. `MAIN_LAB` is a variable at the top, so nobody keeps a
duplicate `main.py` in the repo that can drift. The final "Uploaded N files" count is printed, so the
lesson's number must be the real one: count `lib/*.py` + `config.py` + labs + 1.

`main.py` runs at power-up, so Thonny can look stuck. Tell students: click Stop first.

## Testing the ladder without hardware

See 05-verification.md. Each lab's expected output in the docs is copied from a simulator run, so it is
exact, and every lab must survive the failure cases (sensor dead at start, read errors mid-run, values at
the extremes, Ctrl-C).
