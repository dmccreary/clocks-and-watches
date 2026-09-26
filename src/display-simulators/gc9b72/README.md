# GC9B72 Display Simulator

A desktop simulator for the **GC9B72 2.1" 360×360 round display**. It runs
a kit's real MicroPython programs in ordinary Python, through the kit's
own `lib/gc9b72.py` driver, and captures every pixel the driver sends.
Use it to:

- **make documentation images**: a still or an animated GIF of any lab, drawn as a
  round watch
- **check labs without a board**: redraw correctness, overlaps, button
  handling, timing logic

**Projects that use the GC9B72 display should use this simulator to
generate their documentation images**, so every kit's pictures come from
its real code, the same way. It works on any kit folder that has a
`config.py` with `init_display()` and a `lib/gc9b72.py`, such as the
robot-faces and stem-robots kits as well as this one.

It lives outside the kit folder on purpose: `upload-code.sh` only copies
files from inside `src/kits/sw-gc9b72`, so none of this ever lands on a
Pico.

## Requirements

Python 3.10 or newer and [Pillow](https://pypi.org/project/pillow/)
(`pip install pillow`). No MicroPython, no board.

## Quick start

From the repository root:

```bash
# Regenerate every screen image in docs/kits/sw-gc9b72/img
python3 src/display-simulators/gc9b72/render_sw_gc9b72_docs.py

# ...or just one lab's, into a scratch folder to look at first
python3 src/display-simulators/gc9b72/render_sw_gc9b72_docs.py --only 08 --out /tmp/check

# Run all the checks (about 35 seconds)
python3 src/display-simulators/gc9b72/checks/run_all.py
```

## Rendering one lab: `render_lab.py`

Works on any kit. Times are milliseconds on the simulator's fake clock.

```bash
# The final screen of a lab that finishes by itself
python3 render_lab.py --kit ../../kits/sw-gc9b72 02-hello.py -o hello.png

# The screen 3 seconds in
python3 render_lab.py --kit ../../kits/sw-gc9b72 03-digital-clock.py --at 3000 -o clock.png

# An animated GIF: three frames, pressing button A at 1.5 s
python3 render_lab.py --kit ~/projects/robot-faces/src/kits/sw-gc9b72 13-blink.py \
    --at 1000 --at 1700 --at 2400 --press a:1500-1600 -o blink.gif --frame-ms 600

# A different date and time
python3 render_lab.py --kit ../../kits/sw-gc9b72 05-analog-watch-face.py \
    --start "2026-12-24 18:30:00" --at 12000 -o evening.png
```

| Option | Meaning |
|---|---|
| `--at MS` | Capture the screen at this time. Repeat it for GIF frames. Without it, the final screen is saved. |
| `--press NAME:START-END` | Hold a button, e.g. `mode:1000-1100`. Each press bounces for its first 20 ms, like real contacts. |
| `--buttons a,b` | Names for the pins `config.init_buttons()` returns. The default is `mode,up,down` for three buttons and `a,b` for two. |
| `--start "YYYY-MM-DD HH:MM:SS"` | Where the calendar starts. The default is Friday, September 25, 2026, 10:09:20 AM. |
| `--limit MS` | Stop the lab here. The default is just after the last `--at`. |
| `-o FILE` | `.png` for a still, `.gif` for an animation (`--frame-ms` per frame). |
| `--plain` | Save the square screen without the watch bezel. |

## Using it from Python

```python
import sys
sys.path.insert(0, "src/display-simulators/gc9b72")
from gc9b72_sim import runner, render

runner.use_kit("src/kits/sw-gc9b72")
ns, snaps = runner.run_lab("10-stopwatch.py", 7000,
                           presses=[("up", 1000, 1080), ("mode", 3000, 3080)],
                           snap_at=[6900])
render.save_png(snaps[6900], "stopwatch.png")
print(ns["laps"])           # the lab's own variables, after the run
```

- `runner.use_kit(path)` points the simulator at a kit folder. Switching
  kits in one process forgets the old kit's modules.
- `runner.run_lab(lab, limit_ms, presses, snap_at, start)` runs a lab.
  It returns the lab's globals and a `{time: pixels}` dict. The final
  screen is left in `runner.screen.px`, one RGB565 value per pixel.
- `render.save_png()`, `render.save_gif()`, `render.watch_image()`, and
  `render.screen_image()` turn pixels into pictures.
- `hardware.FORECAST` is the answer every web request gets (a two-day
  Open-Meteo forecast). Replace it to render other weather.
- `pico2w.pretend()` makes board-inspecting programs (like `01-probe.py`)
  see a real Pico 2 W's memory, flash, and temperature, with a made-up ID
  and MAC address.
- `hardware.TRACK_ELEMENTS = True` tags every pixel with the element that
  drew it (`screen.touch`), and `runner.check_layout()` then reports
  overlapping elements and pixels outside the visible glass.

## How it works

**The real driver runs.** A fake `machine.SPI` decodes the GC9B72's
`CASET`, `RASET`, and `RAMWR` commands into a 360×360 array, exactly as
the panel would. So a picture shows the pixels the program really sends,
and the checks can count pixels sent against pixels changed. The
simulator learns which pin is the data/command line by watching the
kit's driver being created, so a kit may wire DC to any pin.

**A fake clock.** `time.sleep()` and `sleep_ms()` move a fake clock
instead of waiting, so a 90-second run takes a moment and is exactly
repeatable. `time.localtime()`, `time.time()`, and `machine.RTC` all
follow the fake calendar, and a lab can set the RTC. Two safeguards
cover labs that never sleep:
- **Busy-waiting:** a lab that reads `time.ticks_ms()` more than 50 times
  in a row without sleeping (pacing itself with the clock) moves the
  clock 1 ms per read.
- **Watchdog:** a lab that neither sleeps nor reads the clock is stopped
  after 120 real seconds, with a warning.

**Buttons, including interrupts.** Scripted presses drive the pins the
kit's `init_buttons()` returns, and falling edges fire any `Pin.irq()`
handler, like a real Pico.

**No network, ever.** WiFi, NTP, and web requests are stand-ins: WiFi
always connects, and every request gets `hardware.FORECAST`. A fake
`secrets` module means a kit's real `secrets.py` is never read.

**Stand-ins for MicroPython.** The simulator supplies `micropython.const`,
`framebuf` (with pixels stored low byte first, like the real one), and
the old `u`-names (`utime`, `ustruct`, `ujson`, and others).

## Limits

- **Speed isn't simulated.** Drawing costs nothing on the fake clock.
  Measure timing on real hardware; `01-probe.py` and the labs' comments
  record the real numbers.
- **`framebuf` curves are close, not exact.** Icons drawn with
  `framebuf.ellipse()` or `poly()` may differ from a real Pico by a pixel
  here and there. Everything drawn through the GC9B72 driver is exact.
- **Nothing is read back from the panel,** and there is no real WiFi, so
  anything about the physical board (colors on the glass, the bezel's
  exact edge, button wiring) still needs the real kit.
- **The fakes are process-wide.** Importing `gc9b72_sim` replaces
  `machine`, `time.ticks_ms`, and friends for the whole Python process.
  Run it on its own, not inside other code. `checks/run_all.py` runs each
  check in its own process for this reason.

## What's in this folder

| Path | What it is |
|---|---|
| `gc9b72_sim/hardware.py` | The fake `machine`, SPI decoder, `framebuf`, network, and `time` functions |
| `gc9b72_sim/runner.py` | `use_kit()`, `run_lab()`, the fake clock and calendar, scripted buttons, `check_layout()` |
| `gc9b72_sim/render.py` | Pixels to PNG and GIF, drawn as a round watch |
| `gc9b72_sim/pico2w.py` | A real Pico 2 W's answers, for programs that inspect the board |
| `render_lab.py` | Command line: one lab to a PNG or GIF, for any kit |
| `render_sw_gc9b72_docs.py` | Regenerates every image in `docs/kits/sw-gc9b72/img` |
| `checks/` | Verification of the sw-gc9b72 labs: `run_all.py` runs them all. Set `GC9B72_KIT` to check another kit's copies of the same labs. |

## For another kit's documentation

1. Make sure the kit folder has `config.py` (with `init_display()`, and
   `init_buttons()` if it has buttons) and `lib/gc9b72.py`.
2. Try a lab: `python3 render_lab.py --kit /path/to/your/kit 01-hello.py -o hello.png`.
3. Write a `render_<your-kit>_docs.py` like `render_sw_gc9b72_docs.py`: one
   `run_lab()` per image, with the times and button presses that show
   each lab at its best. Keeping the script means the pictures can be
   regenerated whenever a lab changes.
