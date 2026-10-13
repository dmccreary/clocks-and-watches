#!/usr/bin/env python3
"""Regenerate every screen image in docs/kits/rect-tft-display/img from
the kit's real lab code.

    python3 src/display-simulators/st7735s/render_rect_tft_docs.py
    python3 .../render_rect_tft_docs.py --only 11 --out /tmp/check

Each image is a lab run on the simulator's fake clock, starting Sunday,
October 11, 2026, around 10:09 AM, with scripted button presses and knob
turns where a lab needs them. Rerun this after changing a lab, then look
at the images.

Not made here: the photos of the real kit, img/social-card.jpg (a crop
of the kit photo), and the lab 01 GIF (a real photo, in docs/img).
"""

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import st7735s_sim as sim                      # noqa: E402
from st7735s_sim import hardware, pico2w       # noqa: E402

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--kit", default=os.path.join(REPO, "src", "kits", "rect-tft-display"))
parser.add_argument("--out", default=os.path.join(REPO, "docs", "kits", "rect-tft-display", "img"))
parser.add_argument("--only", default="", help="only labs whose number starts with this")
args = parser.parse_args()

KIT = sim.use_kit(args.kit)
D = datetime.datetime
START = D(2026, 10, 11, 10, 9, 20)


def out(name):
    return os.path.join(args.out, name)


def wanted(number):
    return number.startswith(args.only) or args.only.startswith(number)


def shots(lab, limit, presses=(), turns=(), at=(), start=START):
    return sim.shots(lab, limit, presses, turns, at, start)


if wanted("03"):
    _, _, final = shots("03-hello-world.py", 2000)
    sim.save_png(final, out("03-hello-world.png"))

if wanted("07"):
    # Nothing touched; K0 held; the knob pressed; five clicks clockwise
    _, s, _ = shots("07-controls-display-test.py", 6000,
                    [("k0", 2000, 2600), ("push", 3000, 3600)], [(4000, 5)],
                    at=[1500, 2300, 3300, 4600])
    sim.save_png(s[3], out("07-controls-display-test.png"))
    sim.save_gif(s, out("07-controls-display-test.gif"), 900)

if wanted("08"):
    # Taken once the display has started; the backlight is not simulated
    _, s, _ = shots("08-backlight-test.py", 3000, at=[1500])
    sim.save_png(s[0], out("08-backlight-test.png"))

if wanted("09"):
    _, s, _ = shots("09-digital-clock.py", 1500, at=[1400])
    sim.save_png(s[0], out("09-digital-clock.png"))

if wanted("10"):
    _, _, final = shots("10-wifi-sync-time.py", 3000)
    sim.save_png(final, out("10-wifi-sync-time.png"))

if wanted("11"):
    # A few seconds just after 10:10, the classic clock-advert time
    _, s, _ = shots("11-analog-clock-face.py", 16000,
                    at=[10000 + 1000 * k for k in range(6)],
                    start=D(2026, 10, 11, 10, 9, 58))
    sim.save_png(s[2], out("11-analog-clock-face.png"))
    sim.save_gif(s, out("11-analog-clock-face.gif"), 1000)

if wanted("12"):
    # Running; set hour (two clicks); set minute (three clicks); running
    _, s, _ = shots("12-set-time.py", 7000,
                    [("push", 1500, 1580), ("push", 3000, 3080), ("push", 5000, 5080)],
                    [(2000, 2), (3500, 3)],
                    at=[1400, 2600, 4400, 6000])
    sim.save_png(s[1], out("12-set-time.png"))
    sim.save_gif(s, out("12-set-time.gif"), 1200)

if wanted("13"):
    _, s, _ = shots("13-digital-clock-face.py", 5000, at=[3200, 4200],
                    start=D(2026, 10, 11, 10, 9, 38))
    sim.save_png(s[0], out("13-digital-clock-face.png"))
    sim.save_gif(s, out("13-digital-clock-face.gif"), 1000)

if wanted("14"):
    # The simulator's canned forecast: partly cloudy today, rain tomorrow
    ns, s, _ = shots("14-weather-clock.py", 4000, at=[3500])
    sim.save_png(s[0], out("14-weather-clock.png"))

    # The five weather icons, from lab 14's own drawing code
    from PIL import Image, ImageDraw, ImageFont
    import forecast
    icons = [(forecast.SUNNY, "Sunny"), (forecast.PARTLY_CLOUDY, "Partly cloudy"),
             (forecast.CLOUDY, "Cloudy"), (forecast.RAIN, "Rain"), (forecast.SNOW, "Snow")]
    size = ns["ICON_SIZE"]
    cell = 150
    font = ImageFont.load_default(size=17)
    strip = Image.new("RGBA", (cell * 5, cell + 14), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    for k, (icon, label) in enumerate(icons):
        ns["render_icon"](icon)
        buf = ns["icon_buffer"]
        # framebuf keeps each pixel low byte first, holding the swapped color
        px = [buf[2 * i] | (buf[2 * i + 1] << 8) for i in range(size * size)]
        px = [((p & 0xFF) << 8) | (p >> 8) for p in px]
        img = Image.new("RGB", (size, size))
        img.putdata(sim.to_rgb(px))
        x = k * cell
        draw.rounded_rectangle((x + 8, 4, x + cell - 8, cell + 8), 14, fill=(15, 15, 18, 255))
        strip.paste(img.resize((128, 128), Image.NEAREST), (x + 11, 6))
        width = draw.textlength(label, font=font)
        draw.text((x + (cell - width) / 2, cell - 18), label, fill=(255, 224, 0, 255), font=font)
    strip.save(out("14-weather-icons.png"))
    print("wrote", out("14-weather-icons.png"))

if wanted("15"):
    # Laps of 2.00, 1.50, and 2.00 s, so lap 2 is the fastest (green)
    laps = [("k0", 1000, 1080), ("push", 3000, 3080), ("push", 4500, 4580),
            ("push", 6500, 6580)]
    _, s, _ = shots("15-stopwatch.py", 8000, laps,
                    at=[6900 + 100 * k for k in range(10)])
    sim.save_png(s[0], out("15-stopwatch.png"))
    sim.save_gif(s, out("15-stopwatch.gif"), 100)

if wanted("16"):
    _, s, _ = shots("16-countdown-timer.py", 2000, [("push", 1000, 1080)], at=[1900])
    sim.save_png(s[0], out("16-timer-setting.png"))
    _, s, _ = shots("16-countdown-timer.py", 93500, [("k0", 1000, 1080)], at=[92400])
    sim.save_png(s[0], out("16-timer-running.png"))
    # A 0:05 timer counting down to its alarm: minutes 05 -> 00, seconds
    # 00 -> 05, then start
    _, s, _ = shots("16-countdown-timer.py", 11000,
                    [("push", 1000, 1080), ("push", 2400, 2480), ("push", 3800, 3880),
                     ("k0", 4000, 4080)],
                    [(1300, -5), (2700, 5)],
                    at=[4500 + 1000 * k for k in range(5)] + [9250, 9750, 10250, 10750])
    sim.save_gif(s, out("16-countdown-timer.gif"), 700)

if wanted("17"):
    # One click of the knob every 2.5 s: weather, analog, digital,
    # stopwatch, timer
    _, s, _ = shots("17-main-template.py", 14000,
                    turns=[(t, 1) for t in (4000, 6500, 9000, 11500)],
                    at=[3900, 6400, 8900, 11400, 13900])
    for name, px in zip(("weather", "analog", "digital", "stopwatch", "timer"), s):
        sim.save_png(px, out("17-mode-%s.png" % name))
    sim.save_gif(s, out("17-main-template.gif"), 1500)

if wanted("02"):
    # The probe inspects the board itself: give it a real Pico 2 W's
    # answers (with a made-up ID and MAC), the chip ID a real RP2350
    # reports, and the board's real 37 ms full-screen fill time.
    pico2w.pretend(fill_us=37_300)
    hardware.machine.mem32 = {0x40000000: 0x20004927}
    _, _, final = shots("02-probe.py", 5000)
    sim.save_png(final, out("02-probe.png"))

if not args.only:
    # A banner of five faces for the kit's home page
    from PIL import Image
    names = ["11-analog-clock-face.png", "13-digital-clock-face.png", "14-weather-clock.png",
             "15-stopwatch.png", "16-timer-running.png"]
    tiles = [Image.open(out(name)) for name in names]
    w, h = tiles[0].size
    gap = 10
    banner = Image.new("RGBA", (5 * w + 6 * gap, h + 2 * gap), (0, 0, 0, 0))
    for k, tile in enumerate(tiles):
        banner.paste(tile, (gap + k * (w + gap), gap))
    banner.save(out("kit-banner.png"), optimize=True)
    print("wrote", out("kit-banner.png"))
