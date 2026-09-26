"""Lab 05: every second's partial redraw (erase, repair, redraw) must
leave exactly the pixels a fresh drawing of that time would. Also proves
the check can fail: a minute hand long enough to reach the numerals must
break it."""

import sys

from _setup import screen, expect, finish, lab_definitions
import config


def run_checks(minute_length=None):
    ns = lab_definitions("05-analog-watch-face.py")
    if minute_length:
        ns["MINUTE_LENGTH"] = minute_length
    display = config.init_display()
    ns["draw_dial"](display)
    dial = list(screen.px)

    def fresh(now):
        screen.px = list(dial)
        ns["update_hands"](display, now, None)
        return screen.px

    def mismatches(times):
        screen.px = list(dial)
        ns["update_hands"](display, times[0], None)
        live = screen.px
        bad = 0
        for prev, now in zip(times, times[1:]):
            screen.px = live
            ns["update_hands"](display, now, prev)
            live = screen.px
            bad += fresh(now) != live
            screen.px = live
        return bad

    def seconds(h, m, s, n, step=1):
        out = []
        for i in range(n):
            t = h * 3600 + m * 60 + s + i * step
            out.append(((t // 3600) % 24, (t // 60) % 60, t % 60))
        return out

    return {
        "10:58:00 - 11:01:00, every second": mismatches(seconds(10, 58, 0, 181)),
        "noon rollover": mismatches(seconds(11, 59, 30, 61)),
        "midnight rollover": mismatches(seconds(23, 59, 50, 21)),
        "2 hours in 7 s jumps": mismatches(seconds(7, 0, 0, 1030, 7)),
        "big jumps (a WiFi resync)": mismatches([(3, 0, 0), (9, 41, 17), (21, 5, 59),
                                                 (0, 0, 0), (15, 30, 45)]),
    }


for label, bad in run_checks().items():
    expect("%s (%d mismatched)" % (label, bad), bad == 0)
broken = sum(run_checks(minute_length=120).values())
expect("the check can fail: MINUTE_LENGTH = 120 gives %d mismatches" % broken, broken > 0)
finish()
