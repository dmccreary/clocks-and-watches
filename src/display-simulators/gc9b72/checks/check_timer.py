"""Lab 11: setting the time with hold-to-repeat, start, pause, reset, the
red warning, and the flashing alarm with the LED -- driven by scripted
(bouncing) button presses; plus a layout check."""

from _setup import screen, expect, finish, runner, hardware
import config
from watchparts import DIGITS, pieces

LAB = "11-countdown-timer.py"
session = [("mode", 1000, 1080),                   # -> SET MINUTES
           ("down", 1200, 2130),                   # held: 1 + 4 repeats: 5:00 -> 0:00
           ("mode", 2400, 2480),                   # -> SET SECONDS
           ("up", 2600, 2680), ("up", 2800, 2880), ("up", 3000, 3080),   # 0:03
           ("mode", 3200, 3280),                   # -> READY
           ("up", 3400, 3480),                     # start: ends at 6400
           ("up", 4400, 4480),                     # pause with 2.0 s left
           ("down", 4800, 4880),                   # reset -> READY 0:03
           ("up", 5000, 5080),                     # start: ends at 8000
           ("mode", 9600, 9680)]                   # stop the alarm


def at(ms, track=False):
    hardware.TRACK_ELEMENTS = track
    ns, _ = runner.run_lab(LAB, ms, session)
    hardware.TRACK_ELEMENTS = False
    return ns, [d.shown for d in ns["digits"]]


ns, _ = at(3300)
expect("set to 00:03 with the buttons, back to READY",
       ns["state"] == ns["READY"] and (ns["set_minutes"], ns["set_seconds"]) == (0, 3))
ns, _ = at(4600)
expect("paused with 2000 ms left (%d)" % ns["remaining_ms"],
       ns["state"] == ns["PAUSED"] and abs(ns["remaining_ms"] - 2000) <= 15)
ns, _ = at(4900)
expect("DOWN while paused resets to 00:03", ns["state"] == ns["READY"] and ns["remaining_ms"] == 3000)
ns, _ = at(7000)
expect("last 10 seconds: digits red (%d ms left)" % ns["remaining_ms"],
       ns["state"] == ns["RUNNING"] and all(d.shown_color == config.RED for d in ns["digits"]))
ns, d = at(8250, track=True)
expect("zero: TIME'S UP, 00:00 lit, LED on",
       ns["state"] == ns["DONE"] and d == [pieces(DIGITS[0])] * 4 and ns["led"].v == 1)
overlaps, far = runner.check_layout(screen.touch)
expect("no elements overlap %s" % (overlaps or ""), not overlaps)
expect("everything on the glass (farthest %.1f px)" % far, far <= config.SAFE_RADIUS)
ns, d = at(8750)
expect("the alarm flashes: digits blank, LED off", d == [0] * 4 and ns["led"].v == 0)
ns, _ = at(9800)
expect("any button stops it: READY 00:03, LED off",
       ns["state"] == ns["READY"] and ns["remaining_ms"] == 3000 and ns["led"].v == 0)
finish()
