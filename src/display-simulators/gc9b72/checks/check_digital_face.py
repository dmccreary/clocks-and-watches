"""Lab 08, in 12-hour and 24-hour mode: every partial redraw matches a
fresh render; a second, minute, or hour change sends exactly the pixels
that change; nothing overlaps; everything is on the visible glass."""

import datetime
import math

from _setup import screen, W, expect, finish, lab_definitions, runner
import config

D = datetime.datetime


def tup(dt):
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0)


def check(twelve_hour):
    print("TWELVE_HOUR =", twelve_hour)
    ns = lab_definitions("08-digital-watch-face.py", replace=() if twelve_hour else
                         (("TWELVE_HOUR = True", "TWELVE_HOUR = False"),))
    display = config.init_display()

    def reset():
        ns["shown_digits"][:] = [None] * 4
        for k in ("shown_colon", "shown_second", "shown_ampm", "shown_date"):
            ns[k] = None

    def fresh(t):
        reset()
        screen.px = [0] * (W * W)
        ns["update_face"](display, t)
        return list(screen.px)

    def state():
        return (list(ns["shown_digits"]), ns["shown_colon"], ns["shown_second"],
                ns["shown_ampm"], ns["shown_date"])

    def restore(st, px):
        ns["shown_digits"][:] = st[0]
        ns["shown_colon"], ns["shown_second"], ns["shown_ampm"], ns["shown_date"] = st[1:]
        screen.px = list(px)

    def mismatches(times):
        live = fresh(times[0])
        st = state()
        bad = 0
        for t in times[1:]:
            restore(st, live)
            ns["update_face"](display, t)
            live, st = list(screen.px), state()
            bad += fresh(t) != live
        return bad

    def run(start, n, step=1):
        return [tup(start + datetime.timedelta(seconds=i * step)) for i in range(n)]

    for label, times in (
            ("12:58 -> 1:01 PM", run(D(2026, 9, 25, 12, 58, 0), 181)),
            ("11:59:30 AM -> 12:00:30 PM", run(D(2026, 9, 25, 11, 59, 30), 61)),
            ("midnight, Sep 30 -> Oct 1", run(D(2026, 9, 30, 23, 59, 50), 21)),
            ("an hour in 7 s jumps", run(D(2026, 9, 25, 7, 0, 0), 520, 7)),
            ("clock set backward and forward",
             [tup(D(2026, 9, 25, 10, 30, 45)), tup(D(2026, 9, 25, 10, 30, 12)),
              tup(D(2026, 1, 1, 0, 0, 0)), tup(D(2026, 12, 31, 23, 59, 59)),
              tup(D(2026, 9, 25, 9, 5, 5))])):
        bad = mismatches(times)
        expect("%s (%d mismatched)" % (label, bad), bad == 0)

    for label, a, b in (("a normal second", D(2026, 9, 25, 10, 31, 7), D(2026, 9, 25, 10, 31, 8)),
                        ("a new minute", D(2026, 9, 25, 10, 31, 59), D(2026, 9, 25, 10, 32, 0)),
                        ("12:59:59 -> 1:00", D(2026, 9, 25, 12, 59, 59), D(2026, 9, 25, 13, 0, 0))):
        fresh(tup(a))
        screen.written = screen.changed = 0
        ns["update_face"](display, tup(b))
        expect("%s sends only changed pixels (%d sent, %d changed)"
               % (label, screen.written, screen.changed), screen.written == screen.changed)

    # Every element at its largest, each tagged by hand
    reset()
    screen.px = [0] * (W * W)
    screen.touch = {}
    for i in range(4):
        screen.label = "digit%d" % i
        ns["draw_digit"](display, i, ns["FIRST_DIGIT_SEGMENTS"] if i == 0 else 0b1111111, None)
    screen.label = "colon"
    ns["draw_colon"](display, True)
    screen.label = "ticks"
    for s in range(60):
        ns["draw_tick"](display, s, True)
    screen.label = "ampm"
    config.centered_text(display, config.SMALL_FONT, "PM", ns["AMPM_Y"])
    screen.label = "date"
    config.centered_text(display, config.SMALL_FONT, "Wed, Sep 30, 2026", ns["DATE_Y"])
    screen.label = None
    overlaps, far = runner.check_layout(screen.touch)
    expect("no elements overlap %s" % (overlaps or ""), not overlaps)
    expect("everything on the glass (farthest %.1f px, edge %d)" % (far, config.SAFE_RADIUS),
           far <= config.SAFE_RADIUS)
    ticks = [(i % W, i // W) for i in screen.touch["ticks"]]
    edge = [(i % W, i // W) for k, v in screen.touch.items() if k != "ticks" for i in v
            if math.hypot(i % W - 180, i // W - 180) > 120]
    gap = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in edge for b in ticks)
    expect("seconds ring clears the digits (%.1f px)" % gap, gap >= 5)


check(True)
check(False)
finish()
