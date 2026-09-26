"""Run a GC9B72 kit's real programs on a simulated Pico.

    from gc9b72_sim import runner
    runner.use_kit("/path/to/src/kits/sw-gc9b72")
    ns, snaps = runner.run_lab("05-analog-watch-face.py", 12000,
                               snap_at=[10000, 11000])

A lab runs until its time limit, measured on a FAKE clock that only moves
when the lab sleeps, so a run is exactly repeatable and takes no real time
waiting. Button presses are scripted as (button, start_ms, end_ms), and
every press bounces for its first 20 ms, like real contacts.

The calendar starts at START (Friday, September 25, 2026, 10:09:20 AM)
unless run_lab() is given another start. time.localtime(), time.time(),
and the RTC all agree with it, and the RTC can be set by the lab.
"""

import calendar
import datetime
import math
import os
import signal
import sys
import time

from . import hardware
from .hardware import screen, W

START = datetime.datetime(2026, 9, 25, 10, 9, 20)
UTC_OFFSET_HOURS = -5      # the fake calendar is US Central daylight time

KIT = None


class Stop(Exception):
    """Raised inside the lab when its time limit is reached."""


class RealTimeout(Stop):
    """Raised when a lab uses too much REAL time: it never sleeps and
    never checks the clock, so its fake clock can't reach the limit."""


# A program that reads ticks_ms() this many times in a row without
# sleeping is busy-waiting on the clock (pacing with ticks_ms instead of
# sleep, like robot-faces' 15-no-blocking.py). From then on, each read
# moves the fake clock 1 ms, so time passes for it too. Programs that
# sleep every pass never get here, so their timing is unchanged.
BUSY_READS = 50
REAL_TIMEOUT_S = 120        # real seconds before a run is stopped anyway
_busy = [0]


state = {"ms": 0, "limit": None, "presses": [], "pins": {}, "snaps": {},
         "snap_at": [], "base": START, "rtc_offset": datetime.timedelta(0)}


# ---------------------------------------------------------------------------
# The fake clock
# ---------------------------------------------------------------------------
def _tick():
    t = state["ms"]
    for name, pin in state["pins"].items():
        down = any(b == name and s <= t < e for b, s, e in state["presses"])
        bouncing = any(b == name and s <= t < s + 20 and (t - s) % 20 == 10
                       for b, s, e in state["presses"])
        pin.set_level(1 if (not down or bouncing) else 0)
    for when in list(state["snap_at"]):
        if t >= when:
            state["snaps"][when] = list(screen.px)
            state["snap_at"].remove(when)


def _advance(ms):
    for _ in range(int(ms)):            # 1 ms steps, so presses land precisely
        state["ms"] += 1
        _tick()
    # Only a lab started by run_lab() has a time limit; outside one (a
    # check drawing directly, say), sleeping just moves the clock.
    if state["limit"] is not None and state["ms"] >= state["limit"]:
        raise Stop


def sleep_ms(ms):
    _busy[0] = 0
    _advance(ms)


def ticks_ms():
    _busy[0] += 1
    if _busy[0] > BUSY_READS:
        _advance(1)
    return state["ms"]


def _now():
    return (state["base"] + datetime.timedelta(milliseconds=state["ms"])
            + state["rtc_offset"])


def localtime(secs=None):
    """MicroPython's localtime(): an 8-tuple, weekday 0 = Monday. With an
    argument it converts seconds, as MicroPython does, with no time zone."""
    if secs is not None:
        return time.gmtime(secs)[:8]
    d = _now()
    return (d.year, d.month, d.day, d.hour, d.minute, d.second, d.weekday(),
            d.timetuple().tm_yday)


class RTC:
    """A real-time clock the lab can set (lab 07 does)."""

    def datetime(self, t=None):
        now = localtime()
        if t is None:
            return (now[0], now[1], now[2], now[6], now[3], now[4], now[5], 0)
        wanted = datetime.datetime(t[0], t[1], t[2], t[4], t[5], t[6])
        state["rtc_offset"] += wanted - datetime.datetime(*now[:6])


time.sleep_ms = sleep_ms
time.sleep = lambda s: sleep_ms(int(s * 1000))
time.ticks_ms = ticks_ms
time.localtime = localtime
# MicroPython's mktime() takes an 8-tuple and has no time zone.
time.mktime = lambda t: calendar.timegm(tuple(t[:6]) + (0, 0, 0))
time.time = lambda: calendar.timegm(
    (_now() - datetime.timedelta(hours=UTC_OFFSET_HOURS)).timetuple())
hardware.machine.RTC = RTC


# ---------------------------------------------------------------------------
# Choosing a kit
# ---------------------------------------------------------------------------
def use_kit(path, button_names=None):
    """Point the simulator at a kit folder: its labs, config.py, and lib/.

    Any modules already loaded from another kit are forgotten, so each
    kit uses its own driver, fonts, and config. button_names names the
    pins config.init_buttons() returns, in order; the default is
    (mode, up, down) for three buttons and (a, b) for two."""
    global KIT
    path = os.path.abspath(path)
    if not os.path.exists(os.path.join(path, "lib", "gc9b72.py")):
        raise FileNotFoundError("no lib/gc9b72.py in " + path)
    if KIT:
        for p in (KIT, os.path.join(KIT, "lib")):
            while p in sys.path:
                sys.path.remove(p)
        for name, module in list(sys.modules.items()):
            origin = getattr(module, "__file__", None) or ""
            if origin.startswith(KIT):
                del sys.modules[name]
    KIT = hardware.KIT = path
    sys.path[:0] = [path, os.path.join(path, "lib")]

    # Watch the driver to learn which pin is its DC line.
    import gc9b72
    real_init = gc9b72.GC9B72.__init__

    def init(self, spi=None, dc=None, *args, **kwargs):
        screen.dc_pin = dc
        real_init(self, spi, dc, *args, **kwargs)
    gc9b72.GC9B72.__init__ = init

    # Watch config.init_buttons() to learn which pin is which button.
    import config
    if hasattr(config, "init_buttons"):
        real_buttons = config.init_buttons

        def init_buttons(*args, **kwargs):
            pins = real_buttons(*args, **kwargs)
            names = button_names or (("mode", "up", "down") if len(pins) == 3
                                     else ("a", "b", "c", "d")[:len(pins)])
            state["pins"].update(zip(names, pins))
            return pins
        config.init_buttons = init_buttons
    return path


def forget_modes():
    """Unload modules a lab loads on demand (lab 12's modes, forecast),
    so the next run starts them fresh."""
    for name in list(sys.modules):
        if name.startswith("mode_") or name == "forecast":
            del sys.modules[name]


# ---------------------------------------------------------------------------
# Running a lab
# ---------------------------------------------------------------------------
def _out_of_real_time(signum, frame):
    raise RealTimeout("stopped after %d s of real time: the lab never slept "
                      "or read the clock, so its fake clock could not advance"
                      % REAL_TIMEOUT_S)


def run_lab(lab, limit_ms, presses=(), snap_at=(), start=None):
    """Run a lab's real code until limit_ms on the fake clock.

    presses: (button, start_ms, end_ms) tuples.
    snap_at: fake-clock times at which to copy the screen.
    Returns (the lab's globals, {time: pixels}). The final screen is
    left in hardware.screen.px."""
    if KIT is None:
        raise RuntimeError("call use_kit() first")
    forget_modes()
    dc_pin = screen.dc_pin
    screen.clear()
    screen.dc_pin = dc_pin
    state.update(ms=0, limit=limit_ms, presses=list(presses), snaps={},
                 snap_at=sorted(snap_at), base=start or START,
                 rtc_offset=datetime.timedelta(0))
    path = os.path.join(KIT, lab)
    ns = {"__name__": "__main__", "__file__": path}
    _busy[0] = 0
    watchdog = hasattr(signal, "setitimer")          # not on Windows
    if watchdog:
        signal.signal(signal.SIGALRM, _out_of_real_time)
        signal.setitimer(signal.ITIMER_REAL, REAL_TIMEOUT_S)
    try:
        exec(compile(open(path).read(), path, "exec"), ns)
    except RealTimeout as stopped:
        print("WARNING: %s: %s" % (lab, stopped), file=sys.stderr)
    except Stop:
        pass
    finally:
        if watchdog:
            signal.setitimer(signal.ITIMER_REAL, 0)
        state["limit"] = None
    return ns, state["snaps"]


run = run_lab       # the short name the checks use


def check_layout(touch, whole=()):
    """Given hardware.screen.touch, return (pairs of elements that drew on
    the same pixel, the farthest drawn pixel from the center). Full-screen
    clears are ignored: they are not elements.

    whole: names of functions that build ONE element from several drawing
    calls that overlap on purpose (a thick ring drawn as two circles, say).
    Their calls are counted as one element instead of one per line."""
    merged = {}
    for k, v in touch.items():
        if len(v) >= W * W:
            continue
        if len(k) >= 3 and k[1] in whole:
            k = k[:2] + k[3:]               # drop the line number
        merged.setdefault(k, set()).update(v)
    touch = merged
    names = list(touch)
    overlaps = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]
                if touch[a] & touch[b]]
    far = max((math.hypot(i % W + 0.5 - W / 2, i // W + 0.5 - W / 2)
               for px in touch.values() for i in px), default=0)
    return overlaps, far
