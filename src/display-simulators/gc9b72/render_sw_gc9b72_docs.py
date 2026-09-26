#!/usr/bin/env python3
"""Regenerate every screen image in docs/kits/sw-gc9b72/img from the
kit's real lab code.

    python3 src/display-simulators/gc9b72/render_sw_gc9b72_docs.py
    python3 .../render_sw_gc9b72_docs.py --only 05 --out /tmp/check

Each image is a lab run on the simulator's fake clock, starting Friday,
September 25, 2026, around 10:09 AM, with scripted button presses where a
lab needs them. Rerun this after changing a lab, then look at the images.

Not made here: img/social-card.jpg (a crop of the kit photo) and the
lab 00 GIF (a real photo, in docs/img).
"""

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from gc9b72_sim import runner, render, pico2w  # noqa: E402
from gc9b72_sim.hardware import screen          # noqa: E402

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--kit", default=os.path.join(REPO, "src", "kits", "sw-gc9b72"))
parser.add_argument("--out", default=os.path.join(REPO, "docs", "kits", "sw-gc9b72", "img"))
parser.add_argument("--only", default="", help="only labs whose number starts with this")
args = parser.parse_args()

KIT = runner.use_kit(args.kit)
D = datetime.datetime


def out(name):
    return os.path.join(args.out, name)


def wanted(number):
    return number.startswith(args.only) or args.only.startswith(number)


def shots(lab, limit, presses=(), at=(), start=None):
    """Run a lab; return the screens at the `at` times and the final one."""
    ns, snaps = runner.run_lab(lab, limit, presses, at, start)
    return ns, [snaps[t] for t in sorted(snaps)], list(screen.px)


if wanted("02"):
    _, _, final = shots("02-hello.py", 2000)
    render.save_png(final, out("02-hello.png"))

if wanted("03"):
    _, s, _ = shots("03-digital-clock.py", 1500, at=[1400])
    render.save_png(s[0], out("03-digital-clock.png"))

if wanted("04"):
    _, _, final = shots("04-wifi-sync-time.py", 3000)
    render.save_png(final, out("04-wifi-sync-time.png"))

if wanted("05"):
    # A few seconds just after 10:10, the classic watch-advert time
    _, s, _ = shots("05-analog-watch-face.py", 16000,
                    at=[10000 + 1000 * k for k in range(6)],
                    start=D(2026, 9, 25, 10, 9, 58))
    render.save_png(s[2], out("05-analog-watch-face.png"))
    render.save_gif(s, out("05-analog-watch-face.gif"), 1000)

if wanted("06"):
    # Nothing held, then MODE, UP, and DOWN in turn
    _, s, _ = shots("06-button-test.py", 5000,
                    [("mode", 2000, 2600), ("up", 3000, 3600), ("down", 4000, 4600)],
                    at=[1500, 2300, 3300, 4300])
    render.save_png(s[2], out("06-button-test.png"))
    render.save_gif(s, out("06-button-test.gif"), 900)

if wanted("07"):
    # Running; set hour (UP twice); set minute (UP three times); running
    _, s, _ = shots("07-set-time.py", 7000,
                    [("mode", 1500, 1580), ("up", 2000, 2080), ("up", 2300, 2380),
                     ("mode", 3000, 3080), ("up", 3500, 3580), ("up", 3800, 3880),
                     ("up", 4100, 4180), ("mode", 5000, 5080)],
                    at=[1400, 2600, 4400, 6000])
    render.save_png(s[1], out("07-set-time.png"))
    render.save_gif(s, out("07-set-time.gif"), 1200)

if wanted("08"):
    _, s, _ = shots("08-digital-watch-face.py", 5000, at=[3200, 4200],
                    start=D(2026, 9, 25, 10, 9, 38))
    render.save_png(s[0], out("08-digital-watch-face.png"))
    render.save_gif(s, out("08-digital-watch-face.gif"), 1000)

if wanted("09"):
    # The simulator's canned forecast: partly cloudy today, rain tomorrow
    _, s, _ = shots("09-weather-clock.py", 4000, at=[3500])
    render.save_png(s[0], out("09-weather-clock.png"))
    render_icons = True
else:
    render_icons = False

if wanted("10"):
    # Laps of 2.00, 1.50, and 2.00 s, so lap 2 is the fastest (green)
    laps = [("up", 1000, 1080), ("mode", 3000, 3080), ("mode", 4500, 4580),
            ("mode", 6500, 6580)]
    _, s, _ = shots("10-stopwatch.py", 8000, laps,
                    at=[6900 + 100 * k for k in range(10)])
    render.save_png(s[0], out("10-stopwatch.png"))
    render.save_gif(s, out("10-stopwatch.gif"), 100)

if wanted("11"):
    _, s, _ = shots("11-countdown-timer.py", 2000,
                    [("mode", 1000, 1080), ("mode", 1400, 1480)], at=[1900])
    render.save_png(s[0], out("11-timer-setting.png"))
    _, s, _ = shots("11-countdown-timer.py", 93500, [("up", 1000, 1080)], at=[92400])
    render.save_png(s[0], out("11-timer-running.png"))
    # A 0:05 timer counting down to its alarm
    five = ([("mode", 1000, 1080), ("down", 1200, 2130), ("mode", 2400, 2480)]
            + [("up", 2600 + 200 * k, 2680 + 200 * k) for k in range(5)]
            + [("mode", 3800, 3880), ("up", 4000, 4080)])
    _, s, _ = shots("11-countdown-timer.py", 11000, five,
                    at=[4500 + 1000 * k for k in range(5)] + [9250, 9750, 10250, 10750])
    render.save_gif(s, out("11-countdown-timer.gif"), 700)

if wanted("12"):
    # One MODE tap every 2.5 s: weather, analog, digital, stopwatch, timer
    taps = [("mode", t, t + 100) for t in (4000, 6500, 9000, 11500)]
    _, s, _ = shots("12-main-template.py", 14000, taps,
                    at=[3900, 6400, 8900, 11400, 13900])
    for name, px in zip(("weather", "analog", "digital", "stopwatch", "timer"), s):
        render.save_png(px, out("12-mode-%s.png" % name))
    render.save_gif(s, out("12-main-template.gif"), 1500)

if render_icons:
    # The five weather icons, from lab 09's own drawing code
    from PIL import Image, ImageDraw, ImageFont
    import forecast
    path = os.path.join(KIT, "09-weather-clock.py")
    source = open(path).read()
    ns = {"__name__": "icons"}
    exec(compile(source[:source.index("display = config.init_display()")], path, "exec"), ns)
    icons = [(forecast.SUNNY, "Sunny"), (forecast.PARTLY_CLOUDY, "Partly cloudy"),
             (forecast.CLOUDY, "Cloudy"), (forecast.RAIN, "Rain"), (forecast.SNOW, "Snow")]
    cell = 150
    font = ImageFont.load_default(size=17)
    strip = Image.new("RGBA", (cell * 5, cell + 14), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    for k, (icon, label) in enumerate(icons):
        ns["render_icon"](icon)
        buf = ns["icon_buffer"]
        # framebuf keeps each pixel low byte first, holding the swapped color
        px = [buf[2 * i] | (buf[2 * i + 1] << 8) for i in range(64 * 64)]
        px = [((p & 0xFF) << 8) | (p >> 8) for p in px]
        img = Image.new("RGB", (64, 64))
        img.putdata(render.to_rgb(px))
        x = k * cell
        draw.rounded_rectangle((x + 8, 4, x + cell - 8, cell + 8), 14, fill=(15, 15, 18, 255))
        strip.paste(img.resize((128, 128), Image.NEAREST), (x + 11, 10))
        width = draw.textlength(label, font=font)
        draw.text((x + (cell - width) / 2, cell - 20), label, fill=(255, 224, 0, 255), font=font)
    strip.save(out("09-weather-icons.png"))
    print("wrote", out("09-weather-icons.png"))

if wanted("01"):
    # The probe inspects the board itself: give it a real Pico 2 W's
    # answers (with a made-up ID and MAC), and the board's real 131 ms
    # full-screen fill time. It checks for kit files by relative path.
    pico2w.pretend(fill_us=131_300)
    here = os.getcwd()
    os.chdir(KIT)
    try:
        _, _, final = shots("01-probe.py", 5000)
    finally:
        os.chdir(here)
    render.save_png(final, out("01-probe.png"))

if not args.only:
    # A banner of five faces for the kit's home page
    from PIL import Image
    names = ["05-analog-watch-face.png", "08-digital-watch-face.png", "09-weather-clock.png",
             "10-stopwatch.png", "11-timer-running.png"]
    banner = Image.new("RGBA", (5 * 220, 220), (0, 0, 0, 0))
    for k, name in enumerate(names):
        im = Image.open(out(name)).resize((210, 210), Image.LANCZOS)
        banner.paste(im, (k * 220 + 5, 5), im)
    banner.save(out("kit-banner.png"), optimize=True)
    print("wrote", out("kit-banner.png"))
