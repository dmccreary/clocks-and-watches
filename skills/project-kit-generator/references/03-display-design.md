# 03. Designing for a colorful display

Everything here came from building the SHT40 "Mood Ring Thermometer". Reference code lives in
`assets/starter-lib/` (colors, icons, gauges, the mode framework) and `assets/example-modes/`
(six modes). Copy and adapt; do not start from a blank file.

## Rules for a display with no frame buffer

1. **Never wipe the whole screen to update it.** A full fill is tens of thousands of pixels sent
   over the wire and it flashes like a strobe.
2. **Draw the parts that never change once** (ring, labels, divider, bar outline), then every update
   write only the numbers.
3. **Put every changing number in a fixed-width field.** `text()` paints a background colour behind each
   letter, so the new digits land right on top of the old ones. No clear, no flicker, no leftover
   digit when a number gets shorter. `"%5.1f" % x` is always five letters wide.
4. **Bars are two rectangles** (filled part, empty part) so every pixel is repainted each time and
   nothing needs erasing. Guard against a zero-width rectangle (`if filled > 0`), which some
   drivers mis-handle.
5. **Redraw something big only when it changes**, and quantise the trigger: recolour the mood ring
   only when the temperature moves a whole degree, redraw a face only when its band or colour changes.
6. **Never draw with `line()`.** In the GC9A01 driver it costs one call per dot. A sweep graph uses
   one `vline` per new reading; a gauge uses filled polygons; an outline circle costs about 450 calls.

## Geometry on a round screen

- The driver addresses a square; only the inscribed circle is visible. Keep everything inside
  `SAFE_RADIUS` (112 of 120). Check text boxes by their **farthest corner**, not their centre.
- Widest content sits near the middle, narrow items near the top and bottom. Write your layout as a
  table (element, font, x range, y range) and put it in the session log.
- **Centre what the eye sees.** A `"%5.1f"` field has a blank slot on the left for two-digit values,
  which pushes the visible text right by half a slot. Shift the whole line left by half a character
  (8 px for a 16-px font).
- Fonts are ASCII only in these drivers. **Draw the degree symbol** as a tiny ring
  (`shapes.ring`, radius 4, thickness 2) next to the digits.
- Two font sizes is enough: 8x16 for labels, 16x32 for numbers.
- A **bezel of 60 dots** (3x3, with a 5x5 at each "hour") costs 60 rectangle calls and looks like a
  watch rim. A full ring outline costs ~900. Use dots for anything that recolours.
- A row of **page dots** (6 squares, the bright one is the current mode) at y = 216 tells students
  they are in a multi-mode program. Leave room for it: gauges sweep 300 degrees and leave the bottom open.

## Colour and mood

- Colours are RGB565 (5-6-5 bits). Do colour math in 0-255 (r,g,b) and pack at the end
  (`widgets.color565`).
- **Gradient = a list of colour stops and a position from 0.0 to 1.0.** `position = (value - low) /
  (high - low)` is a percent problem students can solve by hand (the lesson does it: 72.5 F on a 50-95
  scale is 0.5, halfway, so green). `widgets.gradient(stops, position)` mixes the two nearest stops.
- **Mood ring** = a gradient (blue cold, cyan, green, orange, red hot) applied everywhere the value is
  shown: the bezel dots, the big number, a face, the graph line, the mercury of a thermometer. One colour
  language across all modes makes the kit feel designed.
- Humidity-style quantities get their own gradient (dry orange, comfy green, damp blue).
- Text on a coloured background: pick dark or light text by brightness (`widgets.text_color_on`).
- Keep the four-band "cool/comfy/warm/hot" colouring in the first, classic mode. It is easy to explain,
  and its thresholds live in `config.py` so a student can change them.

## Icons drawn from primitives

No picture files. They are tiny code and students can read them.

- **Water drop** = a circle plus a triangle. The tip is two radii above the centre; the triangle base
  sits half a radius above the centre where its sides just touch the circle (tangent points at +-0.87 r).
- **Thermometer** = a rectangle with a round top, a circle for the bulb, and an inner fill drawn as two
  rectangles (empty, liquid). Keep the tube width odd so the round cap matches. `widgets.Thermometer` draws the
  outline once and `set_level()` repaints only the inside.
- **Faces** = filled circles and half-ellipses (`shapes.ellipse` with a quadrant mask). A thick smile is
  the same arc drawn 3-4 times with a slightly smaller radius. Eyes in round glasses give a character.
- **Arc gauges** = 30 filled polygons ("blocks") between two radii, each in its own gradient colour, lit or
  dim. Only blocks whose state changed are repainted, so updates cost 4-50 calls.

## The mode framework (`display_ctx.py`)

A `Context` holds the display, the latest reading, the unit, a history buffer and the records; a `Mode`
has three jobs:

    enter(ctx)       wipe the screen and draw the fixed parts (and the page dots and bezel)
    update(ctx)      draw the numbers; called after every new reading
    tick(ctx, now)   optional small animation (a blink, a flashing message)

The main loop (`assets/example-labs/09-display-modes-capstone.py`) owns three things and nothing else does:
the button, the sensor schedule and the LED. Design consequences that mattered:

- **Per-mode read interval** (`READ_MS`). A "touch it" mode reads faster (300 ms) so it feels quick; the
  heartbeat LED then blinks faster, which is a nice thing to point out. Watch for sensors that heat when
  read too fast.
- **Record and log in every mode**, not just the mode that displays them (`ctx.add_reading`,
  `records.update` in the main loop). Switching to the history mode then shows the past at once.
- **Unit toggle** (F/C) is a `ctx` method (`in_unit`, `unit`) so every mode converts at display time.
- **Sensor failure banner**: each mode has a `TITLE` line near the top; on failure it becomes a red
  `SENSOR FAIL` (padded to the same width so nothing needs clearing) and returns when a reading succeeds.
- **Re-enter on a mode or unit change**, drawing the mode and then the latest reading. Process all queued
  button presses first and redraw once, so a double tap skips two modes without two heavy redraws.
- Give a mode its **own "start over"** in `enter()` (the touch test re-measures the room each time).

## Modes that worked (with the reasons)

| Mode | Design notes |
|------|--------------|
| Classic | the numbers, the other unit, a bar; the easiest thing to explain in Step 6 |
| Buddy face | whole face = mood colour; band from thresholds; caption from band and humidity; blink every 4 s by redrawing only the eyes |
| Live graph | one `vline` per reading, a thin cursor column, auto-rescale when a value leaves the range or the range is 2.5x too loose; redraws the whole recent history when you enter |
| Ring gauges | two 300-degree arcs of 30 blocks; big numbers and icons in the middle; off-scale values clamp |
| Finger test | baseline = mean of the first 5 readings; baseline only ever drifts DOWN; climb = (t - baseline) / max(target - baseline, min span); smoothing; messages by state, "Cooling off..." whenever the level is falling |
| Hi/Lo records | tracked always; saved to a text file at most once a minute (flash wear) and on Ctrl-C; loaded at boot; a long hold clears them and shows "RECORDS CLEARED" for 2 s |

## Performance budget (measured in the simulator, cost per call is a guess)

Aim for **steady-state updates under about 60 calls** (a number in a fixed field is 2-6 calls) and accept
big costs only at mode entry, a mood change or a graph rescale. SHT40 numbers: Classic enter 910, first Ring
update 1,060, Buddy full face 500-700, Live rescale 330 (median update 4). The simulator prints these; re-check
after any layout change, and time the heaviest transition on real hardware.

## Sensor placement and the display

Both the Pico and the display make a little heat. Tell students to keep the sensor a few holes away from both.
Say it as a tip, not a measured claim, unless you measured it.
