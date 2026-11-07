#!/usr/bin/env python3
"""Regenerate every screen image in docs/kits/mondaine/img from the
kit's real lab code.

    python3 src/display-simulators/gc9b72/render_mondaine_docs.py
    python3 .../render_mondaine_docs.py --only 12 --out /tmp/check

Each image is a lab run on the simulator's fake clock, with scripted
button presses where a lab needs them. Most start at 10:10:25 AM on
Friday, September 25, 2026, the classic clock-advertisement time. The
timing GIFs (labs 11 and 12) start at 10:09:50 so that the red hand
reaches 12 at 10:09:58.5 and the minute rolls over at 10:10:00; their
snapshot times are therefore milliseconds after the start.

Rerun this after changing a lab, then look at the images.

Not made here: the kit photographs, borrowed from the sw-gc9b72 kit's
docs, which uses the same hardware.
"""

import argparse
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from gc9b72_sim import runner, render           # noqa: E402
from gc9b72_sim.hardware import screen          # noqa: E402

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--kit", default=os.path.join(REPO, "src", "kits", "mondaine"))
parser.add_argument("--out", default=os.path.join(REPO, "docs", "kits", "mondaine", "img"))
parser.add_argument("--only", default="", help="only labs whose number starts with this")
args = parser.parse_args()

KIT = runner.use_kit(args.kit)
D = datetime.datetime
CLASSIC = D(2026, 9, 25, 10, 10, 25)


def out(name):
    return os.path.join(args.out, name)


def wanted(number):
    return number.startswith(args.only) or args.only.startswith(number)


def shots(lab, limit, presses=(), at=(), start=CLASSIC):
    """Run a lab; return the screens at the `at` times and the final one."""
    ns, snaps = runner.run_lab(lab, limit, presses, at, start)
    return ns, [snaps[t] for t in sorted(snaps)], list(screen.px)


for number, lab, ms in (("01", "01-hello-display.py", 1500),
                        ("02", "02-dial-dots.py", 1500),
                        ("03", "03-hour-markers.py", 1500),
                        ("04", "04-minute-markers.py", 1500),
                        ("05", "05-black-hands.py", 1500),
                        ("06", "06-red-second-hand.py", 1500),
                        ("07", "07-read-the-time.py", 1500),
                        ("08", "08-wifi-sync-time.py", 3000)):
    if wanted(number):
        _, _, final = shots(lab, ms)
        render.save_png(final, out(lab.replace(".py", ".png")))

if wanted("09"):
    # Four ticks of the red hand, one second apart
    _, s, _ = shots("09-tick-tock.py", 3500, at=[300 + 1000 * k for k in range(4)],
                    start=D(2026, 9, 25, 10, 10, 22))
    render.save_png(s[3], out("09-tick-tock.png"))
    render.save_gif(s, out("09-tick-tock.gif"), 1000)

if wanted("10"):
    # The first second is the lab waiting for the RTC to tick; then a
    # glide, one frame every quarter second.
    _, s, _ = shots("10-smooth-sweep.py", 9000, at=[1100 + 250 * k for k in range(24)],
                    start=D(2026, 9, 25, 10, 10, 20))
    render.save_png(s[16], out("10-smooth-sweep.png"))
    render.save_gif(s, out("10-smooth-sweep.gif"), 250)

# Labs 11, 12, and 15 are shown over the end of a minute. The run starts at
# 10:09:50; the lab waits for the next RTC second (t = 1.0 s), so the red
# hand has been gliding since the minute began, reaches 12 at t = 8.5 s,
# and the minute rolls over at t = 10.0 s.
REST = 8500             # t at which the red hand reaches 12
ROLL = 10000            # t at which the minute rolls over
END_OF_MINUTE = D(2026, 9, 25, 10, 9, 50)

if wanted("11"):
    frames = [REST - 900 + 100 * k for k in range(34)]          # 57.6 s .. 60.9 s
    _, s, _ = shots("11-stop-at-twelve.py", frames[-1] + 100, at=frames, start=END_OF_MINUTE)
    render.save_png(s[11], out("11-stop-at-twelve.png"))      # waiting at 12
    render.save_gif(s, out("11-stop-at-twelve.gif"), 100)

if wanted("12"):
    frames = [REST - 300 + 40 * k for k in range(53)]           # 58.2 s .. 60.3 s
    _, s, _ = shots("12-minute-jump.py", frames[-1] + 100, at=frames, start=END_OF_MINUTE)
    render.save_png(s[22], out("12-minute-jump.png"))         # in mid-hop
    render.save_gif(s, out("12-minute-jump.gif"), 80)          # half speed

    # The storyboard: six moments of the stop-and-go
    from PIL import Image, ImageDraw, ImageFont
    moments = ((REST - 4000, "54.5 s: gliding"), (REST, "58.5 s: arrives at 12"),
               (REST + 330, "58.8 s: the hop begins"), (REST + 700, "59.2 s: mid-hop"),
               (REST + 1000, "59.5 s: landed, still waiting"), (ROLL + 1500, "61.5 s: off again"))
    ns, snaps = runner.run_lab("12-minute-jump.py", ROLL + 1700, (),
                               [t for t, _ in moments], END_OF_MINUTE)
    cell = 260
    font = ImageFont.load_default(size=15)
    sheet = Image.new("RGBA", (3 * cell, 2 * (cell + 26)), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for k, (t, caption) in enumerate(moments):
        im = render.watch_image(snaps[t]).resize((cell, cell), Image.LANCZOS)
        x, y = (k % 3) * cell, (k // 3) * (cell + 26)
        sheet.paste(im, (x, y), im)
        width = draw.textlength(caption, font=font)
        draw.text((x + (cell - width) / 2, y + cell + 2), caption, fill=(30, 30, 30, 255), font=font)
    sheet.convert("RGB").save(out("12-storyboard.png"), optimize=True)
    print("wrote", out("12-storyboard.png"))

if wanted("13"):
    # Nothing held, then MODE, UP, and DOWN in turn
    _, s, _ = shots("13-button-test.py", 5000,
                    [("mode", 2000, 2600), ("up", 3000, 3600), ("down", 4000, 4600)],
                    at=[1500, 2300, 3300, 4300])
    render.save_png(s[2], out("13-button-test.png"))
    render.save_gif(s, out("13-button-test.gif"), 900)

if wanted("14"):
    # Running; set hour (UP twice); set minute (UP three times); running
    _, s, _ = shots("14-set-time.py", 7000,
                    [("mode", 1500, 1580), ("up", 2000, 2080), ("up", 2300, 2380),
                     ("mode", 3000, 3080), ("up", 3500, 3580), ("up", 3800, 3880),
                     ("up", 4100, 4180), ("mode", 5000, 5080)],
                    at=[1400, 2600, 4400, 6000], start=D(2026, 9, 25, 10, 9, 20))
    render.save_png(s[1], out("14-set-time.png"))
    render.save_gif(s, out("14-set-time.gif"), 1200)

if wanted("15"):
    # The finished clock at 10:10:25, and then in SET HOUR
    _, s, _ = shots("15-mondaine-clock.py", 6000, [("mode", 4000, 4100)],
                    at=[3000, 5500])
    render.save_png(s[0], out("15-mondaine-clock.png"))
    render.save_png(s[1], out("15-set-hour.png"))
