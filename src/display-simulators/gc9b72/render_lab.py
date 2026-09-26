#!/usr/bin/env python3
"""Render one GC9B72 lab to a PNG or an animated GIF.

    # the final screen of a lab that finishes by itself
    python3 render_lab.py --kit src/kits/sw-gc9b72 02-hello.py -o hello.png

    # the screen 3 seconds in
    python3 render_lab.py --kit src/kits/sw-gc9b72 03-digital-clock.py --at 3000 -o clock.png

    # an animation: one frame a second, pressing MODE at 1.5 s
    python3 render_lab.py --kit ../robot-faces/src/kits/sw-gc9b72 13-blink.py \\
        --at 1000 --at 2000 --at 3000 --press a:1500-1600 -o blink.gif --frame-ms 600

Times are milliseconds on the simulator's fake clock, which starts at
Friday, September 25, 2026, 10:09:20 AM unless --start says otherwise.
Button names are mode/up/down for a kit with three buttons and a/b for
two (use --buttons to name them yourself).
"""

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gc9b72_sim import runner, render           # noqa: E402
from gc9b72_sim.hardware import screen          # noqa: E402

parser = argparse.ArgumentParser(
    description="Render one GC9B72 lab to a PNG or animated GIF.",
    formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
parser.add_argument("lab", help="the lab's file name, inside the kit folder")
parser.add_argument("--kit", required=True, help="the kit folder (holds config.py and lib/)")
parser.add_argument("-o", "--out", required=True, help="output .png or .gif")
parser.add_argument("--at", type=int, action="append", default=[],
                    help="capture the screen at this time (ms); repeat for more frames")
parser.add_argument("--press", action="append", default=[],
                    help="hold a button: NAME:START-END in ms, e.g. mode:1000-1100")
parser.add_argument("--limit", type=int, help="stop the lab at this time (ms)")
parser.add_argument("--start", help='calendar start, e.g. "2026-12-24 18:30:00"')
parser.add_argument("--buttons", help="names for config.init_buttons() pins, e.g. a,b")
parser.add_argument("--frame-ms", type=int, default=800, help="GIF frame length (ms)")
parser.add_argument("--real-timeout", type=int, default=runner.REAL_TIMEOUT_S,
                    help="stop a lab that uses this many REAL seconds (default %(default)s)")
parser.add_argument("--plain", action="store_true",
                    help="save the plain square screen, without the watch bezel")
args = parser.parse_args()

runner.REAL_TIMEOUT_S = args.real_timeout
runner.use_kit(args.kit, args.buttons.split(",") if args.buttons else None)
presses = []
for spec in args.press:
    name, span = spec.split(":")
    start, end = span.split("-")
    presses.append((name, int(start), int(end)))
start = datetime.datetime.fromisoformat(args.start) if args.start else None
limit = args.limit or (max(args.at) + 100 if args.at else 3000)

runner.run_lab(args.lab, limit, presses, args.at, start)
frames = [runner.state["snaps"][t] for t in sorted(runner.state["snaps"])]
if not frames:
    frames = [list(screen.px)]

if args.out.lower().endswith(".gif"):
    render.save_gif(frames, args.out, args.frame_ms)
elif args.plain:
    render.screen_image(frames[0]).save(args.out)
    print("wrote", args.out)
else:
    render.save_png(frames[0], args.out)
