# Notes for Teachers

These notes are for teachers, parents, and anyone who wants the technical
story behind the [Railway Clock Kit](index.md): which idea each lab teaches,
how the face is drawn without flicker, how the stop-and-go is timed, and
what has and has not been tested on real hardware. The lab pages themselves
are written for students around 11 years old.

!!! note "What has been tested"
    Every screen picture in the lab pages was made by running that lab's
    real code in a desktop simulator of the GC9B72 display. The simulator
    runs the kit's own `lib/gc9b72.py` driver, decodes the SPI commands it
    sends, and keeps the pixels, so the pictures show exactly what the
    program draws. The checks listed [at the end of this page](#checks-and-pictures)
    run all sixteen labs and test the timing and the drawing.

    **What the simulator cannot tell you is how fast a real board draws.**
    The wiring, the display driver (`lib/gc9b72.py`, unchanged),
    `wifi_time.py`, and lab 00 come from the
    [Chrono Smart Clock Kit](../sw-gc9b72/teacher-notes.md), whose labs
    have run on a real Pico 2 W and panel. The new code in this kit
    (`lib/mondaine.py` and labs 01 to 15) has been run in the simulator, but
    **not yet on a board**. Run lab 10 on yours: its "frames a second" line
    is the first real measurement of how the face performs.

## Sourcing Parts

The parts are the same as the Chrono Smart Clock Kit, wired the same way,
so everything on its
[sourcing page](../sw-gc9b72/teacher-notes.md#sourcing-parts) applies:
where to buy the Pico, the display, the cable, and the buttons. The kit
works with a **Pico W** or a **Pico 2 W**. It needs the **W** for WiFi, but
not the 2. See [Pico W or Pico 2 W?](#pico-w-or-pico-2-w) below for the
difference you may notice.

## The Lab Sequence

Each lab adds one idea to the ones before it. The first column links to
the student page.

| Lab | File | New idea | What students see |
|---|---|---|---|
| [00](00-blink-onboard-led.md) | `00-blink-onboard-led.py` | `import`, `Pin`, `while True`, `sleep` | The onboard LED blinks |
| [01](01-hello-display.md) | `01-hello-display.py` | Modules, function calls, screen coordinates (y points down) | Text, a dot, and a ring on white |
| [02](02-dial-dots.md) | `02-dial-dots.py` | Variables, `for` and `range`, sine and cosine | Twelve dots in a circle |
| [03](03-hour-markers.md) | `03-hour-markers.py` | Writing functions with `def`, a design unit | Twelve heavy bars |
| [04](04-minute-markers.md) | `04-minute-markers.py` | `%` (remainder), `if / else` | The full 60-bar dial |
| [05](05-black-hands.md) | `05-black-hands.py` | Time to angles, tuples, many-argument functions | Black hands at 10:10 |
| [06](06-red-second-hand.md) | `06-red-second-hand.py` | Draw order (layers) | The finished face, frozen |
| [07](07-read-the-time.md) | `07-read-the-time.py` | `time.localtime()`, tuple unpacking, using a module | The face at the real time |
| [08](08-wifi-sync-time.md) | `08-wifi-sync-time.py` | WiFi, NTP, time zones, secrets kept out of code | The time, set from the internet |
| [09](09-tick-tock.md) | `09-tick-tock.py` | `while` loop, "only act on change" | A ticking red hand |
| [10](10-smooth-sweep.md) | `10-smooth-sweep.py` | `ticks_ms`, `ticks_diff`, fractions, pacing a loop | A gliding red hand, and a frame rate |
| [11](11-stop-at-twelve.md) | `11-stop-at-twelve.py` | Phases of a cycle, named constants | The red hand waits at 12 |
| [12](12-minute-jump.md) | `12-minute-jump.py` | Easing, clamping with `min` / `max`, returning values | The minute hand hops during the wait |
| [13](13-button-test.md) | `13-button-test.py` | Digital inputs, pull-ups, a list of tuples | Three circles that fill when pressed |
| [14](14-set-time.md) | `14-set-time.py` | Classes, debounce, hold-to-repeat, program modes | Setting the time by hand |
| [15](15-mondaine-clock.md) | `15-mondaine-clock.py` | Assembling parts, housekeeping, `main.py` | The finished clock |

Labs 02 to 06 each carry their own copy of the small functions they use
(`point()`, `bar()`, `hand()`), so a student can read and change a single
file. From lab 07 on, the finished face lives in `lib/mondaine.py`, and the
labs `import` it. That mirrors how the Chrono kit packages its watch parts,
and it keeps labs 09 to 15 short enough to read in one sitting.

## The Design

The face follows the proportions of the Swiss Federal Railways (SBB)
station clock. Every size is a multiple of one unit, *a*, equal to 1/100 of
the dial's diameter, so the whole face scales by changing one number.

| Part | Size in *a* |
|---|---|
| Five-minute bar (12 of them) | from 36.5 to 48.5 out, 3.5 wide |
| Minute bar (48 of them) | from 45 to 48.5 out, 1.4 wide |
| Hour hand | 32 forward, 12 behind; 5.2 wide at the tip, 6.4 at the tail |
| Minute hand | 46 forward, 12 behind; 3.6 wide at the tip, 5.2 at the tail |
| Second hand stem | 1.4 wide; from 16.5 behind the pin to 31.25 out |
| Second hand disc | 10.5 across, centered 31.25 out |

Three relationships make the face fit together, and students can spot them
in the pictures:

- The disc's outer edge is 31.25 + 5.25 = **36.5** *a* out, exactly where
  the five-minute bars start. The disc touches a bar when it points at one.
- The minute hand's tip reaches 46 *a*, overlapping the outer bars so the
  tip and a bar read as one black stroke.
- The disc is three times as wide as a five-minute bar (10.5 = 3 × 3.5).

The kit uses **A = 3.4 pixels**, which puts the outer end of the bars at
48.5 × 3.4 = 165 px. The glass is visible out to `SAFE_RADIUS = 168`, so
the bars sit just inside the bezel. The whole screen is painted white, so
the dial looks as if it fills the glass. The second hand's red is
`color565(235, 0, 0)`, a traffic-sign red, set as `RAIL_RED` in
`config.py`. Pure RED (`0xF800`) glows too harshly against white.

The face has no logo, and the code makes no use of any brand name. See
[About the Design](index.md#about-the-design).

## The Stop-and-Go Timing

Each minute is 60,000 ms long:

| Milliseconds into the minute | Red hand | Minute and hour hands |
|---|---|---|
| 0 to 58,500 | glides 0° to 360° at a steady 6.15° a second | at rest |
| 58,500 to 58,650 | at 12 | at rest |
| 58,650 to 59,370 | at 12 | the **hop**: one minute (6°) and half a degree, eased |
| 59,370 to 60,000 | at 12 | at rest |

The constants are `SWEEP_MS`, `ADVANCE_START_MS`, and `ADVANCE_MS` in
`lib/mondaine.py`. The pause is not a separate setting: it is whatever is
left of the minute after `SWEEP_MS`.

The hop uses `smootherstep(x) = 6x⁵ − 15x⁴ + 10x³` (Ken Perlin's
improvement on the older `3x² − 2x³` smoothstep). It has zero speed *and*
zero acceleration at both ends, so the hand starts and lands without a
visible jolt. The minute hand and the hour hand share the same eased
progress, so they stay in proportion all the way through.

The hands are continuous across the top of the minute: at 59,999 ms the
minute hand is at `(minute + 1) × 6` degrees, and at 0 ms of the next
minute it is at the same angle. `check_mondaine.py` tests this at several
hour boundaries, including 11:59 to 12:00 and 23:59 to 00:00.

### Counting milliseconds

The Pico's real-time clock (RTC) only counts whole seconds, so
`mondaine.SweepClock` makes finer time:

1. `sync()` waits for the RTC's seconds to change, then reads
   `time.ticks_ms()`. Now it knows the millisecond counter's value at the
   start of a known second.
2. `now()` adds `ticks_diff(ticks_ms(), tick0)` to that second, and carries
   over into minutes and hours.

The RTC and the millisecond counter should both run from the board's
crystal, so they stay in step to within a few milliseconds a minute. To be
sure no error ever builds up, lab 12 and lab 15 call `sync()` once a minute,
at 59,400 ms, when every hand is at rest. `sync()` waits for the *next* RTC
tick, which is the top of the minute, so the red hand sets off exactly
when the RTC rolls over. If the RTC is changed (lab 14's set modes, or a
nightly WiFi sync), the next `sync()` simply follows it. No special case is
needed, because the hands are always computed from the hour and minute the
clock reports plus the milliseconds into the minute.

## How the Face Moves Without Flicker

This display has **no frame buffer**: every pixel drawn is sent over SPI, and
every drawing command has a fixed cost on top of its pixels (the driver sets
a window, then sends the pixels). On the Pico 2 W, a full-screen fill takes
about 131 ms, so redrawing the whole face more than seven times a second is
out of the question, and it would flicker anyway.

The Chrono kit's analog face avoids flicker by erasing a hand in the
background color and then repairing whatever the erase cut through. That
works there because the dial is laid out so that only a few things can be
damaged. It does **not** work here: the red hand lies on top of both black
hands, and the black hands lie on top of the outer bars. Erasing any one
of them would cut a hole in the others.

So `Face.show()` never erases. It works in three steps:

1. **Find what changed.** Each hand is stored as a shape: the left and right
   pixel edge on each row it covers. For each hand that moved, compare the
   old and new edges row by row. A hand that moved less than one pixel
   has an identical shape and costs nothing. A row whose edges did not change
   is skipped.
2. **Decide the color of every changed pixel** by looking at the *whole scene*
   from the bottom up: white dial, the 60 bars, the hour hand, the minute
   hand, the red stem, the red disc. The topmost thing that covers a pixel
   wins. Bars are only checked on rows near the rim, because nothing else
   can reach them.
3. **Send the changed pixels in bands.** A drawing command costs about the
   same whether it carries 10 pixels or 600. So rows that changed are
   grouped, 16 at a time, into a rectangle that is filled in a scratch
   buffer and sent with one `blit_buffer()` call.

Every pixel is therefore written once, with the color it should end up
with.

### What it costs

Measured in the simulator, counting the commands the driver is asked to
send:

| Operation | Drawing commands | Pixels sent |
|---|---|---|
| `draw_dial()`: fill, then 60 bars | 914 lines, plus one fill | 9,610 in the bars |
| First draw of the three hands | 413 | about 8,100 |
| Worst frame of the red hand's sweep (any angle) | 12 | about 6,000 |
| Worst frame of the minute hop (14 steps) | 13 | about 3,800 |

Drawing one row at a time, the same sweep frame costs about 340 commands.
Banding is why the hands can be redrawn many times a second.

`check_mondaine.py` proves the result is exact. It moves the hands through
more than 1,100 frames (full laps of the red hand, the hop through all 60
minutes, 80 random jumps, and the disc passing every five-minute bar) and
compares the screen with one drawn from scratch at the same angles. They
are identical, pixel for pixel.

### Pico W or Pico 2 W?

Both work. The pin layout is the same. The difference is speed: the
Pico 2 W's RP2350 chip has hardware floating-point math and runs at
150 MHz, while the Pico W's RP2040 does floating-point in software at
133 MHz. Most of the time in a frame is spent in Python working out edges
and colors, not on the SPI wire, so **expect the Pico W to reach a lower
frame rate than the Pico 2 W**. Neither has been measured yet (see the note
at the top).

The program never depends on the frame rate. Each frame asks the clock
where the hands should be *right now*, so a slower board shows bigger steps,
never a hand that runs late. Lab 10 prints the rate every five seconds. If it
is low and you want smoother motion, these are the dials, in order of effect:

- `BAUDRATE` in `config.py` only matters if the display shows specks;
  see the Chrono notes on SPI speed.
- `BAND` in `lib/mondaine.py` (16 rows). Smaller bands send fewer pixels
  per command but need more commands. Larger bands do the opposite.
- `FRAME_MS` in labs 10, 11, 12, and 15 (50 ms). It is a *target*; a board
  that cannot keep up simply runs flat out.

### Memory

`Face` keeps a scratch buffer of `BAND × 360 × 2` = 11,520 bytes, three
rows of 720 bytes (one per color) to copy pixels from, four corner points
for each of the 60 bars, and the row edges of the four moving shapes.
That is a small fraction of a Pico 2 W's 436 KB of heap. A Pico W has 264 KB
of RAM in all, and it should still fit with room to spare. If you ever see
a `MemoryError`, lower `BAND` to 8, which halves the scratch buffer.

## Buttons and Modes

Lab 14 builds its own small `Button` class so students can see bounce and
hold-to-repeat solved. Lab 15 uses `lib/buttons.py`, the same class plus two
more tricks it needs: **interrupts**, so a quick tap is not lost while the
loop is busy drawing, and `short_or_long()`, so one button can do two
jobs. The class is copied from the Chrono kit's `watchparts.py`.

| Button | Run mode | Set hour / set minute |
|---|---|---|
| MODE, short press | next mode | next mode |
| MODE, hold 1 s | set the clock from the internet | (ignored) |
| UP | (nothing) | forward one step; hold to repeat |
| DOWN | (nothing) | back one step; hold to repeat |

Entering a set mode freezes the display at the RTC's hour and minute, with
the red hand parked at 12 and a yellow label below the center. Changing the
minute zeroes the seconds. Leaving set mode repaints the dial (which wipes
the label), re-syncs the sweep clock to the RTC, and the clock runs again.

## Making the Clock Start by Itself

Lab 15 is the whole clock. Save a copy of it on the Pico as `main.py`, and
the Pico runs it every time it is powered. `upload-code.sh` copies the
`lib` folder, `config.py`, `secrets.py` (if you made one), and every lab to
the Pico. It does not copy the simulator, which lives outside the kit
folder.

!!! warning "Quit Thonny before running `upload-code.sh`"
    Only one program can use the Pico's serial port at a time. If Thonny is
    connected, `mpremote` fails with a message that the port is in use.

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Screen stays dark | Wiring, or VCC on a 5 V pin | Check the table in [How It Is Wired](index.md#how-it-is-wired). Run lab 00 first to prove the board works. |
| Ring or bars cut off at the edge | The bezel covers more of your glass | Lower `SAFE_RADIUS` in `config.py`, and `UNIT` in `lib/mondaine.py` (try 3.2) |
| Specks, or torn frames | Long or messy display wires | Set `BAUDRATE = 12_000_000` in `config.py` |
| Red hand moves in big steps | A low frame rate (see lab 10's report) | Normal on a Pico W; see [Pico W or Pico 2 W?](#pico-w-or-pico-2-w). The hand is still in the right place. |
| `MemoryError` on a Pico W | Too little free RAM | Set `BAND = 8` in `lib/mondaine.py`; remove labs you don't need from the board |
| Red hand does not stop at 12 | The Pico's time is wrong, or the program is an older copy | Check the `NAME vX.Y` line in the shell; run lab 08 |
| The minute hand hops at the wrong moment | The RTC was changed while running | It re-aligns itself within one minute, at the next rest |
| Time off by exactly one hour | Time zone or daylight saving | Check `TIMEZONE_HOURS` and `USE_US_DST` in `config.py` |
| Time starts at midnight | The Pico lost power, and no WiFi sync ran | Run lab 08, or lab 15 with `SYNC_WITH_WIFI = True` |
| `WiFi failed` | Wrong name or password, or a 5 GHz network | Check `secrets.py`; use a 2.4 GHz network |
| One press moves the hand more than once | Contact bounce | Check that lab 14's `DEBOUNCE_MS` is 40 and that the button leg touches GND |
| The SET HOUR label is still showing | The program is stuck in a set mode | Press MODE until the label disappears |

## Checks and Pictures

The simulator is in the repository at
[`src/display-simulators/gc9b72`](https://github.com/dmccreary/clocks-and-watches/tree/main/src/display-simulators/gc9b72).
Two scripts there belong to this kit:

- `checks/check_mondaine.py` runs all sixteen labs, tests the face's
  geometry and the stop-and-go timing, proves that incremental repainting
  matches a full redraw, and reports the cost of each frame in drawing
  commands.
- `render_mondaine_docs.py` regenerates every picture in this kit's `img`
  folder from the labs' own code. Run it after changing a lab, then look at
  the results.

Both run with only Python 3.10 or newer and Pillow. No board is needed.
