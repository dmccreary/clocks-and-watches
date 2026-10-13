# ST7735S Display Simulator (rect-tft-display kit)

Runs the [rect-tft-display kit](../../kits/rect-tft-display)'s real
MicroPython labs in ordinary Python, through the kit's own
`lib/st7735s.py` driver, and captures every pixel the driver sends. Use
it to:

- **make documentation images**: a still or an animated GIF of any lab
- **check labs without a board**: redraw correctness, the knob and
  buttons, timing logic

It is a thin layer over the [GC9B72 simulator](../gc9b72) next door,
which supplies the fake Pico, the fake clock, the SPI decoder, and the
stand-ins for WiFi and `framebuf`. Read that folder's README for how
those work and what their limits are. This layer changes only what is
different about this kit: a 160 × 128 rectangular screen, the ST7735S
driver, and a rotary knob.

## Requirements

Python 3.10 or newer and [Pillow](https://pypi.org/project/pillow/)
(`pip install pillow`). No MicroPython, no board.

## Regenerating the documentation images

From the repository root:

```bash
# Every screen image in docs/kits/rect-tft-display/img
python3 src/display-simulators/st7735s/render_rect_tft_docs.py

# ...or just one lab's, into a scratch folder to look at first
python3 src/display-simulators/st7735s/render_rect_tft_docs.py --only 11 --out /tmp/check
```

Rerun it after changing a lab, then look at the pictures.

## Using it from Python

```python
import sys
sys.path.insert(0, "src/display-simulators/st7735s")
import st7735s_sim as sim

sim.use_kit("src/kits/rect-tft-display")
ns, shots, final = sim.shots("12-set-time.py", 3000,
                             presses=[("push", 1000, 1100)],
                             turns=[(1500, 3)], at=[2500])
sim.save_png(shots[0], "set-hour.png")
print(ns["mode"])           # the lab's own variables, after the run
```

- `presses` are `(button, start_ms, end_ms)`. The buttons are `"push"`
  (pressing the knob) and `"k0"`.
- `turns` are `(start_ms, clicks)`. Positive is clockwise. Each click is
  two steps of the knob's A and B lines, like the real knob.
- `at` lists the fake-clock times at which to copy the screen.

## Limits

- **Speed isn't simulated.** Drawing costs nothing on the fake clock.
- **Colors are ideal.** The real screen's colors and viewing angle are
  not copied.
- **The backlight isn't simulated.** Lab 08's picture shows the screen
  lit.
- **No network, ever.** WiFi always connects, and every web request gets
  the GC9B72 simulator's canned forecast. The kit's real `secrets.py` is
  never read.
