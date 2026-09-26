"""CPython stand-ins for the MicroPython modules a GC9B72 kit imports.

Importing this module installs fake `machine`, `micropython`, `ustruct`,
`framebuf`, `network`, `ntptime`, `requests`, and `secrets` modules, plus
the MicroPython-only `time.ticks_*` functions and `gc.mem_free()`.

The important fake is the SPI bus. It decodes the GC9B72's CASET, RASET,
and RAMWR command stream into a 360 x 360 array of RGB565 pixels, so the
kit's REAL driver (its own lib/gc9b72.py) is what runs: every picture this
simulator makes shows exactly the pixels the program would send to the
panel.

The data/command (DC) line is found by watching the driver itself (see
runner.use_kit()), so a kit may wire DC to any pin.
"""

import gc
import math
import struct
import sys
import time
import types

W = H = 360


class Screen:
    """The panel's memory, plus counters used by the checks."""

    def __init__(self):
        self.clear()

    def clear(self):
        self.px = [0] * (W * H)     # one RGB565 value per pixel
        self.dc_pin = None          # the Pin the driver uses for DC
        self.cmd = None
        self.args = b""
        self.x0 = self.x1 = self.y0 = self.y1 = 0
        self.x = self.y = 0
        self.pending = b""
        self.written = 0            # pixels sent over SPI
        self.changed = 0            # pixels whose color actually changed
        self.label = None           # which element is drawing right now
        self.touch = {}             # label -> set of pixel indexes it wrote


screen = Screen()

# When True, every pixel write is tagged with the element that drew it
# (see element_label()), for overlap and visibility checks. Off by
# default, because walking the call stack slows rendering down.
TRACK_ELEMENTS = False
KIT = None                          # set by runner.use_kit()


class Pin:
    OUT, IN, PULL_UP, PULL_DOWN = 1, 0, 2, 3
    IRQ_FALLING, IRQ_RISING = 4, 8

    def __init__(self, id, mode=None, pull=None, value=None):
        self.id = id
        self.v = 1 if value is None else value
        self.handler = None

    def irq(self, trigger=None, handler=None, **kwargs):
        self.handler = handler

    def set_level(self, v):
        """Drive an input, firing the falling-edge interrupt like a Pico."""
        if self.v == 1 and v == 0 and self.handler:
            self.handler(self)
        self.v = v

    def value(self, v=None):
        if v is None:
            return self.v
        self.v = v

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def high(self):
        self.value(1)

    def low(self):
        self.value(0)

    def toggle(self):
        self.value(1 - self.v)

    def __call__(self, v=None):
        return self.value(v)


class SPI:
    def __init__(self, *args, **kwargs):
        self.baudrate = kwargs.get("baudrate", 0)

    def __repr__(self):
        # MicroPython's SPI repr carries the real rate; the probe parses it.
        return "SPI(0, baudrate=%d, polarity=0, phase=0)" % self.baudrate

    def write(self, data):
        s = screen
        data_mode = s.dc_pin.v if s.dc_pin is not None else 1
        if data_mode == 0:                      # a command byte
            s.cmd = data[0]
            s.args = b""
            if s.cmd == 0x2C:                   # RAMWR: start of pixels
                s.x, s.y = s.x0, s.y0
                s.pending = b""
            return
        if s.cmd in (0x2A, 0x2B):               # CASET / RASET
            s.args += bytes(data)
            if len(s.args) == 4:
                a, b = struct.unpack(">HH", s.args)
                if s.cmd == 0x2A:
                    s.x0, s.x1 = a, b
                else:
                    s.y0, s.y1 = a, b
        elif s.cmd == 0x2C:                     # pixel data, high byte first
            if TRACK_ELEMENTS:
                s.label = element_label()
            buf = s.pending + bytes(data)
            n = len(buf) // 2
            for i in range(n):
                if not (0 <= s.x < W and 0 <= s.y < H):
                    raise AssertionError("pixel off screen at %d,%d" % (s.x, s.y))
                idx = s.y * W + s.x
                val = (buf[2 * i] << 8) | buf[2 * i + 1]
                s.written += 1
                s.changed += s.px[idx] != val
                s.px[idx] = val
                if s.label is not None:
                    s.touch.setdefault(s.label, set()).add(idx)
                s.x += 1
                if s.x > s.x1:
                    s.x = s.x0
                    s.y += 1
            s.pending = buf[2 * n:]


class RTC:
    """Replaced by the runner's settable clock (runner.RTC)."""

    def datetime(self, t=None):
        return (2026, 9, 25, 4, 10, 0, 0, 0)


# ---------------------------------------------------------------------------
# Element labels, for checks
# ---------------------------------------------------------------------------
_HELPERS = ("gc9b72.py", "shapes.py", "config.py")
_KEYS = ("i", "column", "second", "x", "y")


def element_label():
    """Name the element drawing right now, from the call stack: the
    innermost frame in the kit that isn't a drawing helper.

    watchparts objects are named by object (one Digit, TextLine, ...), and
    TickRing ticks by second. Anything else is (file, function, line, and
    a few telling local variables), so two calls from the same line with
    different arguments count as different elements."""
    f = sys._getframe(2)
    while f is not None:
        path = f.f_code.co_filename
        name = path.rsplit("/", 1)[-1]
        if KIT and path.startswith(KIT) and name not in _HELPERS:
            if name == "watchparts.py":
                me = f.f_locals.get("self")
                if type(me).__name__ == "TickRing":
                    return ("TickRing", f.f_locals.get("second"))
                if me is not None:
                    return (type(me).__name__, id(me))
            else:
                func = f.f_code.co_name
                keys = ()
                if func != "<module>":
                    keys = tuple(f.f_locals.get(k) for k in _KEYS
                                 if isinstance(f.f_locals.get(k), int))
                return (name, func, f.f_lineno) + keys
        f = f.f_back
    return None


# ---------------------------------------------------------------------------
# framebuf, storing RGB565 LOW byte first like MicroPython's
# ---------------------------------------------------------------------------
class FrameBuffer:
    """Close to MicroPython's framebuf, in pure Python. Curves may differ
    from the real one by a pixel here and there."""

    def __init__(self, buf, w, h, fmt=None, stride=None):
        self.buf, self.w, self.h = buf, w, h

    def pixel(self, x, y, c=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = 2 * (y * self.w + x)
            if c is None:
                return self.buf[i] | (self.buf[i + 1] << 8)
            self.buf[i] = c & 0xFF
            self.buf[i + 1] = (c >> 8) & 0xFF

    def fill_rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, c)

    def fill(self, c):
        self.fill_rect(0, 0, self.w, self.h, c)

    def rect(self, x, y, w, h, c, f=False):
        if f:
            self.fill_rect(x, y, w, h, c)
        else:
            self.hline(x, y, w, c)
            self.hline(x, y + h - 1, w, c)
            self.vline(x, y, h, c)
            self.vline(x + w - 1, y, h, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.pixel(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, x, y, xr, yr, c, f=False, m=15):
        for dy in range(-yr, yr + 1):
            half = (int(xr * math.sqrt(max(0.0, 1 - (dy / yr) ** 2)) + 0.5)
                    if yr else xr)
            if f:
                self.hline(x - half, y + dy, 2 * half + 1, c)
            else:
                self.pixel(x - half, y + dy, c)
                self.pixel(x + half, y + dy, c)

    def poly(self, x, y, coords, c, f=False):
        pts = [(x + coords[i], y + coords[i + 1])
               for i in range(0, len(coords), 2)]
        for row in range(min(p[1] for p in pts), max(p[1] for p in pts) + 1):
            xs = []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if y0 != y1 and min(y0, y1) <= row < max(y0, y1):
                    xs.append(int(x0 + (row - y0) * (x1 - x0) / (y1 - y0) + 0.5))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(xs[i], row, xs[i + 1] - xs[i] + 1, c)


# ---------------------------------------------------------------------------
# Network stand-ins: no real WiFi, NTP, or web requests, ever
# ---------------------------------------------------------------------------
class WLAN:
    NETWORKS = [(b"MyHomeWiFi", b"", 6, -59, 3, 0),
                (b"Neighbor-5G", b"", 11, -82, 3, 0)]

    def __init__(self, *args):
        self._on = False
        self._up = False

    def active(self, on=None):
        if on is not None:
            self._on = on
        return self._on

    def isconnected(self):
        return self._up

    def connect(self, ssid, password):
        self._up = True

    def disconnect(self):
        self._up = False

    def status(self):
        return 3

    def ifconfig(self):
        return ("10.0.0.99", "255.255.255.0", "10.0.0.1", "10.0.0.1")

    def config(self, *args, **kwargs):
        return bytes.fromhex("28cdc1000000")

    def scan(self):
        return list(self.NETWORKS)


# The answer every forecast request gets: partly cloudy today, rain
# tomorrow. Replace it to render other weather.
FORECAST = {"daily": {"time": ["2026-09-25", "2026-09-26"],
                      "weather_code": [2, 63],
                      "temperature_2m_max": [70.3, 61.0],
                      "temperature_2m_min": [58.1, 56.8]}}
FETCHES = []                                   # every URL requested


class _Response:
    status_code = 200

    def json(self):
        return FORECAST

    def close(self):
        pass


def _get(url, timeout=None, **kwargs):
    FETCHES.append(url)
    return _Response()


# ---------------------------------------------------------------------------
# Install everything
# ---------------------------------------------------------------------------
def _module(name, **attrs):
    m = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(m, key, value)
    sys.modules[name] = m
    return m


machine = _module("machine", Pin=Pin, SPI=SPI, RTC=RTC,
                  freq=lambda *a: 150_000_000)
_module("micropython", const=lambda x: x)

# MicroPython's older "u" names, which many labs still use. utime is the
# same (patched) time module, so `from utime import sleep` gets the fake
# clock too.
import array, binascii, collections, hashlib, io, json, os, random, re  # noqa: E401,E402
for _u, _real in (("utime", time), ("ustruct", struct), ("uos", os), ("ujson", json),
                  ("urandom", random), ("ubinascii", binascii), ("uarray", array),
                  ("ucollections", collections), ("uio", io), ("ure", re),
                  ("uhashlib", hashlib)):
    sys.modules[_u] = _real
_module("framebuf", FrameBuffer=FrameBuffer, RGB565=1)
_module("network", STA_IF=0, AP_IF=1, WLAN=WLAN)
_module("ntptime", host="pool.ntp.org", timeout=1, settime=lambda: None)
_module("requests", get=_get)
_module("urequests", get=_get)
# Fake credentials, so a kit's real secrets.py is never read.
_module("secrets", wifi_ssid="MyHomeWiFi", wifi_pass="not-a-real-password")

time.sleep_ms = lambda ms: None
time.sleep_us = lambda us: None
time.ticks_ms = lambda: int(time.monotonic() * 1000)
time.ticks_us = lambda: int(time.monotonic() * 1_000_000)
time.ticks_diff = lambda a, b: a - b
time.ticks_add = lambda a, b: a + b

gc.mem_free = lambda: 431_616          # what a Pico 2 W reports at boot
gc.mem_alloc = lambda: 15_040
