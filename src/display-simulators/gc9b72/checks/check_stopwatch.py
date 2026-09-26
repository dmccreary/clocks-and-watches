"""Lab 10: start, stop, resume, laps, reset, the fastest-lap highlight, and
the best/average line, all driven by scripted (bouncing) button presses;
plus a layout check."""

from _setup import screen, expect, finish, runner, hardware
import config

GREEN, YELLOW = config.GREEN, config.YELLOW
LAB = "10-stopwatch.py"


def rows(ns):
    return [(line.shown.strip(), line.shown_color) for line in ns["lap_lines"]]


def stats(ns):
    return ns["best_line"].shown.strip(), ns["average_line"].shown.strip()


session = [("up", 1000, 1100),      # start
           ("mode", 3000, 3080),    # lap 1: 2.00 s
           ("mode", 4500, 4580),    # lap 2: 1.50 s
           ("down", 5000, 5080),    # DOWN while running: ignored
           ("up", 6000, 6100),      # stop at 5.00 s
           ("mode", 6500, 6580),    # MODE while stopped: ignored
           ("up", 7000, 7080),      # resume
           ("mode", 7500, 7580),    # lap 3: 2.00 s (it spans the stop)
           ("up", 8000, 8080),      # stop at 6.00 s
           ("down", 9000, 9080)]    # reset

hardware.TRACK_ELEMENTS = True
ns, _ = runner.run_lab(LAB, 8500, session)
hardware.TRACK_ELEMENTS = False
laps = ns["laps"]
expect("stopped at 6.00 s with laps 2.00, 1.50, 2.00 (%d ms, %s)" % (ns["banked_ms"], laps),
       ns["state"] == ns["STOPPED"] and abs(ns["banked_ms"] - 6000) <= 10
       and [round(x, -1) for x in laps] == [2000, 1500, 2000])
r = rows(ns)
expect("newest lap yellow, fastest (lap 2) green", r[0][1] == YELLOW and r[1][1] == GREEN)
expect("Best 00:01.50, Avg 00:01.83 %s" % (stats(ns),), stats(ns) == ("Best 00:01.50", "Avg 00:01.83"))
overlaps, far = runner.check_layout(screen.touch)
expect("no elements overlap %s" % (overlaps or ""), not overlaps)
expect("everything on the glass (farthest %.1f px)" % far, far <= config.SAFE_RADIUS)

ns, _ = runner.run_lab(LAB, 9500, session)
expect("DOWN while stopped resets everything",
       ns["state"] == ns["READY"] and ns["banked_ms"] == 0 and ns["laps"] == []
       and all(t == "" for t, _ in rows(ns)) and stats(ns) == ("", ""))

ns, _ = runner.run_lab(LAB, 3500, [("up", 1000, 1080), ("mode", 3000, 3080)])
expect("one lap: no green row, no Best/Avg", all(c != GREEN for _, c in rows(ns))
       and stats(ns) == ("", ""))

five = [("up", 1000, 1080), ("mode", 3000, 3080), ("mode", 4000, 4080), ("mode", 6500, 6580),
        ("mode", 9500, 9580), ("mode", 11700, 11780)]
ns, _ = runner.run_lab(LAB, 12000, five)
expect("five laps: the fastest scrolled off, so no green row", all(c != GREEN for _, c in rows(ns)))
expect("...but Best still shows it %s" % (stats(ns),), stats(ns) == ("Best 00:01.00", "Avg 00:02.14"))

three = [("up", 1000, 1080), ("mode", 3000, 3080), ("mode", 4500, 4580), ("mode", 6500, 6580),
         ("mode", 7300, 7380)]           # lap 4: 0.80 s, a new fastest
ns, _ = runner.run_lab(LAB, 7600, three)
r = rows(ns)
expect("a new fastest lap takes the green from the old one",
       r[0][1] == GREEN and r[2][1] not in (GREEN, YELLOW) and stats(ns)[0] == "Best 00:00.80")
finish()
