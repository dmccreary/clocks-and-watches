# ST7789 Display Simulator (large-knob-speaker-clock kit)

Runs the [large-knob-speaker-clock kit](../../kits/large-knob-speaker-clock)'s
real MicroPython labs in ordinary Python, through the kit's own
`lib/st7789.py` driver, and captures every pixel the driver sends.

It is a copy of the [ST7735S simulator](../st7735s) with three changes:
a 320 × 240 screen, the ST7789 driver, and pictures at 1× scale. Both
are thin layers over the [GC9B72 simulator](../gc9b72), which supplies
the fake Pico, the fake clock, the SPI decoder, the silent I2S
amplifier, and the stand-ins for WiFi and `framebuf`. Read that folder's
README for how those work and what their limits are.

## Requirements

Python 3.10 or newer and [Pillow](https://pypi.org/project/pillow/)
(`pip install pillow`). No MicroPython, no board.

## Using it from Python

From the repository root:

```python
import sys
sys.path.insert(0, "src/display-simulators/st7789")
import st7789_sim as sim

sim.use_kit("src/kits/large-knob-speaker-clock")
ns, shots, final = sim.shots("16-main-template.py", 12000,
                             turns=[(8000, 1)], at=[7500, 11000])
sim.save_png(shots[0], "weather.png")
sim.save_png(shots[1], "analog.png")
```

- `presses` are `(button, start_ms, end_ms)`. The buttons are `"push"`
  (pressing the knob) and `"k0"`.
- `turns` are `(start_ms, clicks)`. Positive is clockwise. Each click is
  two steps of the knob's A and B lines.
- `at` lists the fake-clock times at which to copy the screen.

## Limits

- **Sound is silent, and there is one core.** `sound.py` falls back to
  its core-0 interrupt path. What a program plays can be checked by
  wrapping `sound.tone()` and `sound.play()`.
- **`02-probe.py` needs help.** Call `pico2w.pretend()` and set
  `hardware.machine.mem32 = {0x40000000: 0x20004927}` first, as
  `../st7735s/render_rect_tft_docs.py` does. Its I2S timing warning in
  the simulator is not real: `pretend()` replaces `ticks_us()` to time
  the screen fill, which also upsets the probe's audio timing.
- **Scripted knob turns are not reliable.** In lab 04 the step counts
  came out wrong for some `turns`, and this hasn't been tracked down.
  Check knob behavior on the real board.
- **A lab takes about 600 ms of fake time to start**, mostly drawing the
  first screen. A press scripted before then is missed.
- **Speed, colors and the backlight aren't simulated.** The settings in
  `config.py` that depend on the real panel (`ROTATION`, `BGR`,
  `INVERT`) still need the real board.
