"""simlib.py -- a strict desktop simulator for MicroPython display kits.

Why this exists: you usually cannot run a new kit on real hardware while you are
writing it. This module lets the REAL lab files, config.py and lib/ modules run
on a laptop against fakes, and it is deliberately STRICT so that bugs which the
real hardware would hide (or silently mis-draw) fail loudly here.

What it fakes
  * machine.Pin (with irq), machine.I2C, machine.SPI
  * gc9a01 (or any display driver you name in install()): a pixel canvas that
    RAISES on drawing outside the screen and on text the real driver would
    silently skip (character outside the font, or a box that runs off the edge)
  * time: a fake clock you control. Every display call costs simulated time
    (COST_MS per call plus a per-pixel cost) so slow redraws delay button
    handling like the real thing. COST_MS is a GUESS, not a measurement.
  * a push button with realistic contact chatter and soft-IRQ latency: the
    handler runs a moment AFTER the edge and reads the CURRENT pin level, which
    is what MicroPython does by default. (An early button.py that read the pin
    inside the handler lost ~40% of presses under this model.)
  * a sensor bus whose bytes you control (World). The default is an SHT40 so the
    example tests run. For another sensor, replace World.i2c_read / i2c_write.

Usage
    export KIT_DIR=/path/to/src/kits/my-kit          # the folder with config.py and lib/
    import simlib; simlib.install(width=240, height=240, circular=True)
    ... run labs with runpy.run_path(...), take snapshots, assert on results ...

Keep it out of the kit: run from a scratch folder, use absolute output paths, and
leave sys.dont_write_bytecode = True (the kit folder must stay free of
__pycache__ and PNGs).
"""
import sys, types, os, math, gc
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

KIT = os.environ.get("KIT_DIR")
if not KIT or not os.path.isdir(KIT):
    raise SystemExit("Set KIT_DIR to the kit folder (the one that holds config.py and lib/).")
sys.path[:0] = [KIT, os.path.join(KIT, "lib")]

COST_MS = 0.3            # simulated cost of one display call (a guess)
PIXEL_MS = 0.00027       # 16 bits per pixel at 60 MHz


class SimDone(KeyboardInterrupt):
    """Raised by sleep_ms when the scripted run reaches CLOCK.end."""


# ------------------------------------------------------------------ clock
class Clock:
    def __init__(self):
        self.now = 0.0
        self.end = None
        self.events = []          # (time, seq, fn)
        self.seq = 0

    def at(self, t, fn):
        self.seq += 1
        self.events.append((t, self.seq, fn))
        self.events.sort(key=lambda e: (e[0], e[1]))

    def advance(self, ms):
        target = self.now + ms
        while self.events and self.events[0][0] <= target:
            t, _, fn = self.events.pop(0)
            if t > self.now:
                self.now = t
            fn()
        self.now = target

    def ms(self):
        return int(self.now)


CLOCK = Clock()


def reset_clock():
    CLOCK.now = 0.0; CLOCK.end = None; CLOCK.events = []; CLOCK.seq = 0
    return CLOCK


# ------------------------------------------------------------------ sensor world
def crc8(data):
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def sht40_frame(t_c, h):
    """EXAMPLE sensor: 6 bytes = temp(2) crc hum(2) crc, as the SHT40 sends them."""
    tt = int(round((t_c + 45.0) * 65535.0 / 175.0)); hh = int(round((h + 6.0) * 65535.0 / 125.0))
    td = bytes([tt >> 8, tt & 255]); hd = bytes([hh >> 8, hh & 255])
    return td + bytes([crc8(td)]) + hd + bytes([crc8(hd)])


class World:
    """What the fake sensor does. Tests set these; replace the two hooks for a new sensor.

    profile(t_ms) -> (temp_c, humidity)      # example sensor values over time
    fail_windows  -> [(start_ms, end_ms)]    # reads raise OSError inside a window
    reset_fails_until                        # a soft reset raises OSError before this time
    """
    profile = staticmethod(lambda t_ms: (22.5, 48.2))
    fail_windows = []
    reset_fails_until = 0
    reads = []                 # times of every successful read

    @staticmethod
    def i2c_write(addr, data):
        if data == bytes([0x94]) and CLOCK.now < World.reset_fails_until:   # SHT40 soft reset
            raise OSError(5)

    @staticmethod
    def i2c_read(addr, n):
        for a, b in World.fail_windows:
            if a <= CLOCK.now < b:
                raise OSError(5)
        t_c, h = World.profile(CLOCK.now)
        World.reads.append(CLOCK.now)
        return sht40_frame(t_c, h)


# ------------------------------------------------------------------ fake machine
class Pin:
    IN, OUT, PULL_UP = 0, 1, 2
    IRQ_FALLING, IRQ_RISING = 4, 8
    instances = {}
    IRQ_LATENCY = (0.05, 2.0)       # ms between an edge and the soft handler running (a guess)
    SCHED_DEPTH = 8                 # MicroPython's scheduler queue depth
    rng = None                      # set to random.Random(seed) for random latency

    def __init__(self, ident, mode=None, pull=None):
        self.ident = ident
        self.level = 1 if pull == Pin.PULL_UP else 0
        self.handler = None
        self.trigger = 0
        self.writes = []
        self.pending = 0
        self.scheduled = False
        self.dropped = 0
        Pin.instances[ident] = self

    def irq(self, handler=None, trigger=0, hard=False):
        self.handler = handler; self.trigger = trigger

    def edge(self, level):
        """The real pin changes level NOW. The handler runs a little later."""
        if level == self.level:
            return
        self.level = level
        if not self.handler:
            return
        if self.pending < Pin.SCHED_DEPTH:
            self.pending += 1
        else:
            self.dropped += 1
        if not self.scheduled:
            self.scheduled = True
            lo, hi = Pin.IRQ_LATENCY
            r = Pin.rng.uniform(lo, hi) if Pin.rng else lo
            CLOCK.at(CLOCK.now + r, self._run)

    def _run(self):
        n, self.pending, self.scheduled = self.pending, 0, False
        for _ in range(n):
            self.handler(self)          # every call sees the level as it is right now

    def value(self, v=None):
        if v is None:
            return self.level
        self.level = v
        self.writes.append((CLOCK.now, v))     # LED writes end up here: use it to check the heartbeat

    def on(self): self.value(1)
    def off(self): self.value(0)


class I2C:
    def __init__(self, *a, **k): pass
    def writeto(self, addr, data): return World.i2c_write(addr, data)
    def readfrom(self, addr, n): return World.i2c_read(addr, n)
    def scan(self): return [0x44]


class SPI:
    def __init__(self, *a, **k): pass


def chatter(rng, t0, final_level):
    """Edges for ONE button transition ending at final_level: the first edge, then an
    even number of extra flickers (up to ~12 ms of them), like real contacts."""
    edges = [(t0, final_level)]
    t, level = t0, final_level
    for _ in range(rng.choice([0, 2, 2, 4, 6, 8])):
        t += rng.uniform(0.02, 2.5)
        level = 1 - level
        edges.append((t, level))
    return edges


def press(t, hold_ms, bounce=True, pin=15, seed=None):
    """Schedule a press: down at t, up at t + hold_ms, with contact chatter."""
    import random
    rng = random.Random(seed if seed is not None else int(t * 7 + hold_ms))
    down = chatter(rng, t, 0) if bounce else [(t, 0)]
    up = chatter(rng, t + hold_ms, 1) if bounce else [(t + hold_ms, 1)]
    for when, level in down + up:
        CLOCK.at(when, lambda lv=level: Pin.instances[pin].edge(lv))


# ------------------------------------------------------------------ strict display
class StrictError(AssertionError):
    pass


class Display:
    """A canvas that behaves like a no-frame-buffer SPI display driver, but strictly."""
    WIDTH = 240
    HEIGHT = 240
    CIRCULAR = True
    last = None

    def __init__(self, spi=None, dc=None, cs=None, reset=None, rotation=0, **kwargs):
        self.width, self.height = Display.WIDTH, Display.HEIGHT
        self.px = np.zeros((self.height, self.width), dtype=np.uint16)
        self.calls = 0
        self.by_kind = {}
        self.text_boxes = []
        Display.last = self

    def _count(self, kind, pixels=0, blits=1):
        self.calls += 1
        self.by_kind[kind] = self.by_kind.get(kind, 0) + 1
        CLOCK.advance(COST_MS * blits + PIXEL_MS * pixels)

    def fill_rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            raise StrictError("fill_rect non-positive size %r" % ((x, y, w, h),))
        if x < 0 or y < 0 or x + w > self.width or y + h > self.height:
            raise StrictError("fill_rect outside the canvas %r" % ((x, y, w, h),))
        self.px[y:y + h, x:x + w] = c
        self._count("rect", w * h)

    def fill(self, c): self.fill_rect(0, 0, self.width, self.height, c)
    def hline(self, x, y, l, c): self.fill_rect(x, y, l, 1, c)
    def vline(self, x, y, l, c): self.fill_rect(x, y, 1, l, c)

    def rect(self, x, y, w, h, c):
        self.hline(x, y, w, c); self.vline(x, y, h, c)
        self.vline(x + w - 1, y, h, c); self.hline(x, y + h - 1, w, c)

    def pixel(self, x, y, c):
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise StrictError("pixel outside the canvas %r" % ((x, y),))
        self.px[y, x] = c
        self._count("pixel", 1)        # a pixel costs about as much as a whole rectangle

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.pixel(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def text(self, font, s, x0, y0, color=0xFFFF, background=0x0000):
        w, h = font.WIDTH, font.HEIGHT
        for i, ch in enumerate(s):
            o = ord(ch)
            if not (font.FIRST <= o < font.LAST):
                raise StrictError("character %r is not in the font (text %r)" % (ch, s))
            if x0 + i * w < 0 or x0 + (i + 1) * w > self.width or y0 < 0 or y0 + h > self.height:
                raise StrictError("text would be skipped by the real driver: %r at %r" % (s, (x0, y0)))
        self.text_boxes.append((x0, y0, len(s) * w, h, s))
        bpr = w // 8
        for i, ch in enumerate(s):
            base = (ord(ch) - font.FIRST) * h * bpr
            for row in range(h):
                for byte in range(bpr):
                    bits = font.FONT[base + row * bpr + byte]
                    for bit in range(8):
                        xx = x0 + i * w + byte * 8 + bit
                        self.px[y0 + row, xx] = color if bits & (0x80 >> bit) else background
        blits = 2 if h == 16 else 4
        self._count("text", len(s) * w * h, blits * len(s))


def install(width=240, height=240, circular=True, driver_module="gc9a01", driver_class="GC9A01"):
    """Put the fakes in sys.modules. Call once, before importing anything from the kit."""
    Display.WIDTH, Display.HEIGHT, Display.CIRCULAR = width, height, circular
    m = types.ModuleType("machine")
    m.Pin, m.I2C, m.SPI = Pin, I2C, SPI
    sys.modules["machine"] = m
    d = types.ModuleType(driver_module); setattr(d, driver_class, Display); sys.modules[driver_module] = d
    import time as _t
    _t.ticks_ms = lambda: CLOCK.ms()
    _t.ticks_diff = lambda a, b: a - b
    _t.ticks_add = lambda a, b: a + b

    def sleep_ms(ms):
        CLOCK.advance(ms)
        if CLOCK.end is not None and CLOCK.now >= CLOCK.end:
            raise SimDone()
    _t.sleep_ms = sleep_ms
    _t.sleep = lambda s: sleep_ms(int(s * 1000))
    gc.mem_free = lambda: 123456


# ------------------------------------------------------------------ pictures and geometry checks
def rgb565_array(px):
    r = ((px >> 11) & 31) * 255 // 31
    g = ((px >> 5) & 63) * 255 // 63
    b = (px & 31) * 255 // 31
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def round_rgba(display, scale=2):
    """The screen as an RGBA image. Round screens get a soft transparent corner area,
    so the picture looks like the real glass. Use this for docs and box-cover art."""
    img = rgb565_array(display.px)
    big = np.array(Image.fromarray(img).resize((display.width * scale, display.height * scale),
                                               Image.NEAREST).convert("RGBA"))
    if display.CIRCULAR:
        yy, xx = np.mgrid[0:display.height * scale, 0:display.width * scale]
        r = display.width * scale / 2
        dist = np.hypot(xx - (r - 0.5), yy - (display.height * scale / 2 - 0.5))
        big[..., 3] = (np.clip(r - dist + 0.5, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(big)


def snapshot(display, path, scale=2):
    """Save a review picture (on a grey table so black and transparent are distinguishable)."""
    im = round_rgba(display, scale)
    bg = Image.new("RGBA", im.size, (70, 70, 78, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(path)


def grid(tiles, cols, path, gap=24):
    """Paste several RGBA screens into one transparent picture (docs grids, hero art)."""
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w + (cols - 1) * gap, rows * h + (rows - 1) * gap), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (w + gap), (i // cols) * (h + gap)), t)
    sheet.save(path)
    return sheet.size


def outside_pixels(display, radius=None):
    """Count lit pixels outside the visible glass (round screens). Should be 0."""
    if not display.CIRCULAR:
        return 0
    radius = radius or display.width / 2 - 4
    yy, xx = np.mgrid[0:display.height, 0:display.width]
    outside = (xx - (display.width - 1) / 2) ** 2 + (yy - (display.height - 1) / 2) ** 2 > radius ** 2
    return int(((display.px != 0) & outside).sum())


def text_box_problems(display, limit=None):
    """Text boxes whose farthest corner is beyond the safe radius (round screens)."""
    if not display.CIRCULAR:
        return []
    limit = limit or display.width / 2 - 10
    cx, cy = (display.width - 1) / 2, (display.height - 1) / 2
    bad = []
    for (x, y, w, h, s) in display.text_boxes:
        worst = max(math.hypot(px - cx, py - cy)
                    for px, py in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)))
        if worst > limit:
            bad.append((s, round(worst, 1)))
    return bad
