#!/usr/bin/env python3
"""Regenerate every screen image in docs/kits/big-round-speaker-clock/img
from the kit's real code.

    python3 src/display-simulators/gc9b72/render_big_round_speaker_clock_docs.py
    python3 .../render_big_round_speaker_clock_docs.py --only modes --out /tmp/check

Each image is a program run on the simulator's fake clock, with scripted
button presses where it needs them. Runs start at 10:09:20 AM on Friday,
September 25, 2026 unless noted. The simulator has no sound and only one
core, so sound.py runs on core 0 and the speaker stays silent; the
pictures are exactly what the programs draw.

Labs 01, 02, 03, 05 and 06 only print to Thonny's shell, so they have no
screen image. Their pages show the shell output instead.

Rerun this after changing a program, then look at the images.
"""

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from gc9b72_sim import runner, render, hardware   # noqa: E402
from gc9b72_sim.hardware import screen            # noqa: E402

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--kit", default=os.path.join(REPO, "src", "kits", "big-round-speaker-clock"))
parser.add_argument("--out", default=os.path.join(REPO, "docs", "kits", "big-round-speaker-clock", "img"))
parser.add_argument("--only", default="", help="04, 07, big, modes, or alarm")
args = parser.parse_args()

KIT = runner.use_kit(args.kit)
D = datetime.datetime

# Open-Meteo's answer, with the "current" block that modes 1 and 2 read:
# 64 F and partly cloudy now, rain tomorrow.
hardware.FORECAST = {
    "current": {"temperature_2m": 63.6, "weather_code": 2},
    "daily": {"time": ["2026-09-25", "2026-09-26"],
              "weather_code": [2, 63],
              "temperature_2m_max": [70.3, 61.0],
              "temperature_2m_min": [58.1, 56.8]}}

MODE_NAMES = ("big", "temp", "forecast", "alarm", "timer", "stopwatch",
              "analog", "railway", "phrase", "calendar")


def out(name):
    return os.path.join(args.out, name)


def wanted(key):
    return not args.only or key.startswith(args.only)


def tap(button, at, ms=80):
    return (button, at, at + ms)


if wanted("04"):
    runner.run_lab("04-display-test.py", 2000)
    render.save_png(list(screen.px), out("04-display-test.png"))

if wanted("07"):
    runner.run_lab("07-get-time.py", 4000)
    render.save_png(list(screen.px), out("07-get-time.png"))

if wanted("big"):
    # The Big Clock: a still, and a GIF of the second ring filling
    _, snaps = runner.run_lab("main-template.py", 9000, (),
                              [3000 + 1000 * k for k in range(6)])
    frames = [snaps[t] for t in sorted(snaps)]
    render.save_png(frames[0], out("08-big-clock.png"))
    render.save_gif(frames, out("08-big-clock.gif"), 1000)

if wanted("modes"):
    # All ten modes: tap MODE every 2.5 s, look just before the next tap.
    # Mode 4 (Timer) and 5 (Stopwatch) are started with UP so they move.
    step = 2500
    presses, at = [], []
    for k in range(10):
        shown = 3000 + step * k
        at.append(shown + step - 300)
        presses.append(tap("mode", shown + step))
    presses += [tap("up", 3000 + step * 5 + 300)]           # start the stopwatch
    _, snaps = runner.run_lab("mode-template.py", 3000 + step * 10 + 500,
                              presses, at)
    frames = [snaps[t] for t in sorted(snaps)]
    for k, px in enumerate(frames):
        render.save_png(px, out("09-mode-%d-%s.png" % (k, MODE_NAMES[k])))
    render.save_gif(frames, out("09-all-modes.gif"), 1500)

    # One sheet of all ten, captioned, for the overview page
    from PIL import Image, ImageDraw, ImageFont
    titles = ("0 Big Clock", "1 Temperature", "2 Forecast", "3 Alarm",
              "4 Timer", "5 Stopwatch", "6 Analog", "7 Railway",
              "8 Phrase", "9 Holidays")
    cell, cols = 220, 5
    font = ImageFont.load_default(size=16)
    sheet = Image.new("RGBA", (cols * cell, 2 * (cell + 28)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(sheet)
    for k, px in enumerate(frames):
        im = render.watch_image(px).resize((cell, cell), Image.LANCZOS)
        x, y = (k % cols) * cell, (k // cols) * (cell + 28)
        sheet.paste(im, (x, y), im)
        width = draw.textlength(titles[k], font=font)
        draw.text((x + (cell - width) / 2, y + cell + 4), titles[k],
                  fill=(110, 110, 120, 255), font=font)
    sheet.save(out("09-ten-modes.png"), optimize=True)
    print("wrote", out("09-ten-modes.png"))

if wanted("alarm"):
    # Setting the alarm: go to mode 3, hold MODE, then step with UP.
    presses = [tap("mode", 2000), tap("mode", 2400), tap("mode", 2800),
               ("mode", 4000, 5200),                      # hold: set the alarm
               tap("up", 6000), tap("up", 6300)]
    _, snaps = runner.run_lab("mode-template.py", 7500, presses, [3800, 7000])
    frames = [snaps[t] for t in sorted(snaps)]
    render.save_png(frames[1], out("09-alarm-setting.png"))
