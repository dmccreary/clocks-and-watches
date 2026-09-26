"""Lab 12: MODE steps through the modes and unloads each one; the timer
is set with a long press; a background timer wakes the watch for its
alarm; a background stopwatch keeps running; the weather reuses its
forecast; and no mode draws on the mode dots."""

import datetime
import sys

from _setup import screen, W, expect, finish, runner, hardware

LAB = "12-main-template.py"


def tap(t):
    return ("mode", t, t + 100)


session = [tap(2000), tap(3000), tap(4000),        # weather -> analog -> digital -> stopwatch
           ("up", 4500, 4580),                     # start the stopwatch
           tap(5000),                              # -> timer
           ("mode", 6000, 7300),                   # hold MODE: set
           ("down", 7500, 8430),                   # 5:00 -> 0:00
           tap(8600),                              # -> seconds
           ("up", 8800, 8880), ("up", 9000, 9080), ("up", 9200, 9280),   # 0:03
           tap(9400),                              # done setting -> READY
           ("up", 9600, 9680),                     # start: ends at about 12.6 s
           tap(10000),                             # -> weather; the timer runs on
           ("up", 13500, 13580),                   # stop the alarm
           tap(14000), tap(15000), tap(15500), tap(16000)]   # ... back to the stopwatch
START = datetime.datetime(2026, 9, 25, 10, 0, 0)


def at(ms):
    hardware.FETCHES.clear()
    ns, _ = runner.run_lab(LAB, ms, session, start=START)
    return ns


def mode(ns):
    return ns["MODES"][ns["mode_index"]][1]


def loaded():
    return sorted(m for m in sys.modules if m.startswith("mode_"))


ns = at(1900)
expect("starts in Weather; one forecast fetched", mode(ns) == "Weather" and len(hardware.FETCHES) == 1)
ns = at(2500)
expect("MODE -> Analog; only mode_analog loaded %s" % loaded(),
       mode(ns) == "Analog" and loaded() == ["mode_analog"])
expect("  the forecast module went with the weather mode", "forecast" not in sys.modules)
ns = at(4400)
expect("MODE, MODE -> Stopwatch", mode(ns) == "Stopwatch")
ns = at(7200)
tm = sys.modules["mode_timer"]
expect("holding MODE in Timer sets it, without switching modes",
       mode(ns) == "Timer" and tm.state == tm.SET_MINUTES)
ns = at(9580)
tm = sys.modules["mode_timer"]
expect("set to 00:03 with the buttons", tm.state == tm.READY
       and (tm.set_minutes, tm.set_seconds) == (0, 3))
ns = at(11000)
expect("MODE while timing -> Weather; the timer is kept with a wake_at",
       mode(ns) == "Weather" and "wake_at" in ns["saved"]["mode_timer"])
expect("  the weather reused its saved forecast", len(hardware.FETCHES) == 1)
ns = at(12900)
tm = sys.modules["mode_timer"]
expect("at zero the watch jumps to the timer: TIME'S UP, LED on",
       mode(ns) == "Timer" and tm.state == tm.DONE and tm.led.v == 1)
ns = at(13700)
tm = sys.modules["mode_timer"]
expect("UP stops the alarm", tm.state == tm.READY and tm.led.v == 0)
ns = at(16500)
sw = sys.modules["mode_stopwatch"]
elapsed = sw.elapsed_ms(runner.state["ms"])
expect("back to the stopwatch: still running, %.2f s (started at 4.5 s)" % (elapsed / 1000),
       mode(ns) == "Stopwatch" and sw.state == sw.RUNNING
       and abs(elapsed - (runner.state["ms"] - 4500)) <= 20)

# ---- no mode draws on the dots ------------------------------------------------
source_path = runner.KIT + "/" + LAB
original = open(source_path).read()
for k, name in enumerate(("Weather", "Analog", "Digital", "Stopwatch", "Timer")):
    patched = original.replace("START_MODE = 0 ", "START_MODE = %d " % k)
    hardware.TRACK_ELEMENTS = True
    screen.clear()
    runner.forget_modes()
    runner.state.update(ms=0, limit=40000, snaps={}, snap_at=[],
                        base=datetime.datetime(2026, 9, 25, 10, 58, 25),   # crosses :30
                        rtc_offset=datetime.timedelta(0),
                        presses=[("up", 2000, 2080)] if name in ("Stopwatch", "Timer") else [])
    try:
        exec(compile(patched, source_path, "exec"), {"__name__": "__main__"})
    except runner.Stop:
        pass
    runner.state["limit"] = None
    hardware.TRACK_ELEMENTS = False
    # Only what the modes and the dots draw: not full clears or boot messages
    touch = {key: px for key, px in screen.touch.items()
             if len(px) < W * W and key[1] != "<module>"}
    dots = set().union(*[px for key, px in touch.items() if key[1] == "draw_dots"])
    others = set().union(*[px for key, px in touch.items() if key[1] != "draw_dots"])
    expect("%-9s draws nothing on the mode dots" % name, dots and not (dots & others))
finish()
