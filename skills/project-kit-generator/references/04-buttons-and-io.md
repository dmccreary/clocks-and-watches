# 04. Buttons, the heartbeat LED, and saving data

## The standing rule

**Every push button is read with a pin interrupt (IRQ) and a 50 millisecond debounce.** Do not switch
to polling in the main loop, and do not lower the debounce. (`BUTTON_DEBOUNCE_MS = 50` in `config.py`;
`assets/starter-lib/button.py` implements it.) Interrupts also connect the kit to the textbook's chapter
on digital input, so students meet the idea for real.

Wiring: one leg to GP15 (physical pin 20), the other leg to GND (pin 18). No resistor: the program turns on
the Pico's internal `Pin.PULL_UP`, so the pin reads 1 normally and 0 while pressed.

## Why the first version lost about 40% of presses (and what to copy instead)

The obvious handler reads the pin inside the interrupt:

    def handler(pin):
        if pin.value() == 0: pressed()
        else: released()

On real hardware that is wrong twice over. Contacts **chatter** for a few milliseconds, and MicroPython
runs a soft IRQ handler **a moment after the edge**. By then the pin may have bounced to the opposite
level, so a press is misread as a release and lost, and the debounce window then ignores the rest of the
chatter. The user noticed ("I had to press the button a few times") on the very first hardware run,
because the simulator had delivered perfect edges. `scripts/simlib.py` now models chatter and IRQ latency, and
the old handler loses ~40% of presses under it.

**The design that works** (`button.py`):

1. The handler only records **when** something changed: if this edge is at least `debounce_ms` after
   the previous one it starts a new **burst** (store the time, count it); it never reads the pin and
   allocates nothing. One physical push is one burst of many edges.
2. The main loop calls `next_press()` often. When the pin has been **quiet for `debounce_ms`**, it reads
   where the button ended up. Now the level is stable, so it is the truth.
3. Bursts are transitions that take turns (press, release, ...). If the burst count fits the level, replay
   them from the stored timestamps. This is how a whole tap that happened while the screen was busy
   redrawing is still counted, with an accurate length.
4. If the count does not fit (electrical noise, lost edges), trust the level. A guessed **release** has
   no trustworthy length, so it is **dropped**: a missed tap is better than a fake long press that flips
   units or clears records.
5. Remember 16 changes, not 8. The 8-entry version turned a long redraw with 4 taps into a bogus 2.7 s hold.
6. A press held at boot is ignored until released.

Trade-off to tell the user: taps shorter than 50 ms are ignored as bounce. Normal taps are 80-200 ms.

`scripts/stress_button.py` runs the button against chatter, late handlers, long redraws, long holds, quick
double taps and stray glitches and reports missed / extra / bogus-long presses. Run it whenever `button.py`
changes. It must report 0 problems.

## What a press means

Decide the meaning on release (the length is known then):

| Press | Action |
|-------|--------|
| tap (< 800 ms) | next mode |
| hold (800 ms to 3 s) | switch units (F/C) |
| long hold (>= 3 s), only in the records mode | clear the records |

Known weakness: with release-based decisions there is no feedback while you hold, so a long hold looks like
nothing happened for a second. Offer the user "switch at the 0.8 s mark while still holding" as an
improvement (records mode would keep its 3 s hold). Print each press to the console (`Button: 169 ms`) so
they can see on the real board what the button reported; that one line settled two debugging questions.

## Heartbeat LED (`heartbeat.py`)

The Pico's LED blinks once per **sensor reading**, two quick blinks on a failed read. The blink rate
*is* the reading rate, and a solid LED means the program stopped: a free crash detector for a classroom.

- Find the LED with `Pin("LED", Pin.OUT)` and fall back to `Pin(25, ...)` (`onboard_led()`); the name works on a plain Pico and a Pico W.
- Time blinks with `ticks_ms()` and a small step list, never `sleep()`, so blinking never blocks anything.
- Point out that a mode with a faster reading rate blinks faster.

## Saving data (`records.py`)

- One small text file (`78.42 66.10 62.30 31.00`), parsed with `split()` and `float()`; a missing or broken file
  starts fresh.
- Flash memory wears out: **save at most once a minute** (`RECORDS_SAVE_SECONDS`) and on Ctrl-C, and only
  when something changed. Tell the user the cost: unplugging right after a new record can lose it.
- Track in every mode and start again from the current reading after a clear.
- A warm finger or a breath sets records too; say so in the docs so nobody is surprised.

## MicroPython gotchas collected on the way

- No `str.center/ljust/rjust` on some builds: pad with your own helper (`widgets.pad_center`) or `"%-8s" %`.
- IRQ handlers must not allocate: no floats, no new objects, no string formatting, no `max()`.
- Do not use f-strings or the walrus operator in student code (the repo style is `%` and `.format`).
- `hasattr(mode, "cleared")` is a fine way for the main loop to ask a mode if it can handle a special action.
- The board string in the REPL banner (e.g. "Raspberry Pi Pico with RP2040", MicroPython v1.29.0) tells you
  Pico versus Pico W; put it in the memory file for the user's setup.
