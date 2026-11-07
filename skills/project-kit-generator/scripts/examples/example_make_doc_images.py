import sys, os, math, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import simlib
simlib.install()
from simlib import CLOCK, Display, rgb565_array
import numpy as np
from PIL import Image
import config
from display_ctx import Context
from records import Records
os.chdir(tempfile.mkdtemp())
DOCS = os.environ.get("DOCS_DIR", os.getcwd())      # where the docs pictures are written

from mode_classic import ClassicMode
from mode_buddy import BuddyMode
from mode_live import LiveMode
from mode_ring import RingMode
from mode_finger import FingerMode
from mode_hilo import HiLoMode


def make_ctx(index):
    if os.path.exists(config.RECORDS_FILE):
        os.remove(config.RECORDS_FILE)
    ctx = Context(Display(), Records(config.RECORDS_FILE, 60), 6)
    ctx.mode_index = index
    return ctx


def feed(ctx, t, h):
    ctx.add_reading((t - 32.0) * 5.0 / 9.0, h)
    ctx.records.update(ctx.temp_f, ctx.humidity)


def round_rgba(display, scale=2):
    img = rgb565_array(display.px)
    big = np.array(Image.fromarray(img).resize((240 * scale, 240 * scale), Image.NEAREST).convert("RGBA"))
    yy, xx = np.mgrid[0:240 * scale, 0:240 * scale]
    dist = np.hypot(xx - (120 * scale - 0.5), yy - (120 * scale - 0.5))
    big[..., 3] = (np.clip(120 * scale - dist + 0.5, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(big)


def grid(tiles, cols, path, gap=24):
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (w + gap), (i // cols) * (h + gap)), t)
    sheet.save(path)
    print(path, sheet.size, os.path.getsize(path) // 1024, "KB")


tiles = []
# 1 Watch
ctx = make_ctx(0); m = ClassicMode(); m.enter(ctx); feed(ctx, 72.5, 48.2); m.update(ctx); tiles.append(round_rgba(ctx.display))
# 2 Buddy
ctx = make_ctx(1); m = BuddyMode(); m.enter(ctx); feed(ctx, 72.5, 48.2); m.update(ctx); tiles.append(round_rgba(ctx.display))
# 3 Live: about two minutes of gently warming air
ctx = make_ctx(2); m = LiveMode(); m.enter(ctx)
for i in range(125):
    feed(ctx, 72.0 + 1.6 * math.sin(i / 12.0) + 0.02 * i, 48.0); m.update(ctx)
tiles.append(round_rgba(ctx.display))
# 4 Ring
ctx = make_ctx(3); m = RingMode(); m.enter(ctx); feed(ctx, 72.5, 48.2); m.update(ctx); tiles.append(round_rgba(ctx.display))
# 5 Finger: a finger warming the sensor, half way to the goal
ctx = make_ctx(4); m = FingerMode(); m.enter(ctx)
seq = [72.0, 72.1, 71.9, 72.0, 72.1] + [72 + 21 * (1 - math.exp(-k / 6.0)) for k in range(1, 40)]
for t in seq:
    feed(ctx, t, 50.0); m.update(ctx)
    if m.level >= 0.5:
        break
tiles.append(round_rgba(ctx.display))
# 6 Hi/Lo
ctx = make_ctx(5); m = HiLoMode(); m.enter(ctx)
for t, h in ((70.0, 40.0), (78.4, 62.0), (66.1, 31.0), (74.0, 48.0)):
    feed(ctx, t, h)
CLOCK.now = 8115000.0          # pretend the watch has been running for 2 hours 15 minutes
m.update(ctx); tiles.append(round_rgba(ctx.display))
grid(tiles, 3, os.path.join(DOCS, "smartwatch-modes.png"))

# Buddy's moods
moods = []
for t, h in ((45.0, 40.0), (60.0, 40.0), (72.5, 48.0), (72.5, 20.0), (84.0, 50.0), (95.0, 85.0)):
    ctx = make_ctx(1); m = BuddyMode(); m.enter(ctx); feed(ctx, t, h); m.update(ctx); moods.append(round_rgba(ctx.display))
grid(moods, 3, os.path.join(DOCS, "buddy-moods.png"))
