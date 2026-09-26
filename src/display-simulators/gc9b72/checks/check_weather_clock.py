"""Lab 09: partial redraws match fresh renders through time and forecast
changes; nothing overlaps; everything is on the glass; and the forecast
refreshes on schedule, retrying after failures."""

import datetime
import sys

from _setup import screen, W, expect, finish, lab_definitions, runner, hardware
import config

D = datetime.datetime


def tup(dt):
    return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0)


# ---- redraw correctness -----------------------------------------------------
print("Redraws")
ns = lab_definitions("09-weather-clock.py")
display = config.init_display()


def reset():
    ns["shown_digits"][:] = [None] * 4
    for k in ("shown_colon", "shown_second", "shown_ampm", "shown_date"):
        ns[k] = None
    ns["shown_weather"][:] = [[ns["UNDRAWN"]] * 4, [ns["UNDRAWN"]] * 4]


def fresh(t, days):
    reset()
    screen.px = [0] * (W * W)
    ns["draw_static"](display)
    ns["update_weather"](display, days)
    ns["update_face"](display, t)
    return list(screen.px)


def snapshot():
    return ([list(ns["shown_digits"]), ns["shown_colon"], ns["shown_second"], ns["shown_ampm"],
             ns["shown_date"], [list(c) for c in ns["shown_weather"]]], list(screen.px))


def restore(snap):
    st, px = snap
    ns["shown_digits"][:] = st[0]
    ns["shown_colon"], ns["shown_second"], ns["shown_ampm"], ns["shown_date"] = st[1:5]
    ns["shown_weather"][:] = [list(c) for c in st[5]]
    screen.px = list(px)


A = [(70, 58, 0), (61, 57, 63)]          # sunny / rain
B = [(75, 60, 2), (28, -5, 73)]          # partly cloudy / snow, negative low
C = [(102, 85, 3), (55, 40, 45)]         # cloudy with a 3-digit high / fog
E = [(9, -12, 95), (0, -20, 1)]          # thunderstorms / sunny
start = D(2026, 9, 25, 12, 59, 50)
steps = [None] * 5 + [A] * 30 + [B] * 20 + [C] * 20 + [E] * 20 + [A] * 10
states = [(tup(start + datetime.timedelta(seconds=i)), days) for i, days in enumerate(steps)]
states += [(tup(D(2026, 9, 30, 23, 59, 59)), A), (tup(D(2026, 10, 1, 0, 0, 0)), B)]
fresh(*states[0])
snap, last_days, bad = snapshot(), states[0][1], 0
for t, days in states[1:]:
    restore(snap)
    ns["update_face"](display, t)
    if days != last_days:
        ns["update_weather"](display, days)
    snap, last_days = snapshot(), days
    bad += snap[1] != fresh(t, days)
expect("%d time and forecast changes (%d mismatched)" % (len(states) - 1, bad), bad == 0)

fresh(tup(D(2026, 9, 25, 10, 31, 7)), A)
screen.written = screen.changed = 0
ns["update_face"](display, tup(D(2026, 9, 25, 10, 31, 8)))
expect("a normal second sends only changed pixels (%d sent, %d changed)"
       % (screen.written, screen.changed), screen.written == screen.changed)

# ---- layout ---------------------------------------------------------------------
print("Layout")
hardware.TRACK_ELEMENTS = True
fresh(tup(D(2026, 9, 30, 12, 58, 58)), None)
screen.touch = {}
ns["draw_static"](display)
for days in (A, B, C, E):
    ns["update_weather"](display, days)
reset()
ns["update_face"](display, tup(D(2026, 9, 30, 12, 58, 58)))
hardware.TRACK_ELEMENTS = False
# draw_degree_sign() draws two circles on purpose, for a thick ring
overlaps, far = runner.check_layout(screen.touch, whole=("draw_degree_sign",))
expect("no elements overlap %s" % (overlaps or ""), not overlaps)
expect("everything on the glass (farthest %.1f px, edge %d)" % (far, config.SAFE_RADIUS),
       far <= config.SAFE_RADIUS)

# ---- forecast schedule ----------------------------------------------------------
print("Forecast schedule")
requests = sys.modules["requests"]
real_get = requests.get
log = []


class Failed:
    status_code = 500

    def close(self):
        pass


def schedule(start, seconds, answers):
    """Run the real lab from `start`; the forecast service answers OK or
    FAIL from `answers` in turn (then OK). Returns (time, answer) for each
    fetch."""
    queue = list(answers)
    log.clear()

    def get(url, timeout=None, **kw):
        ok = queue.pop(0) if queue else True
        log.append(("%02d:%02d:%02d" % runner.localtime()[3:6], "ok" if ok else "FAIL"))
        return real_get(url, timeout) if ok else Failed()
    requests.get = get
    runner.run_lab("09-weather-clock.py", seconds * 1000, start=start)
    requests.get = real_get
    return list(log)


for label, start, seconds, answers, want in (
        ("startup, then :00:30", D(2026, 9, 25, 19, 59, 40), 120, [],
         [("19:59:40", "ok"), ("20:00:30", "ok")]),
        (":30:30 fails -> retry every 5 min", D(2026, 9, 25, 20, 29, 0), 600, [True, False, False],
         [("20:29:00", "ok"), ("20:30:30", "FAIL"), ("20:35:30", "FAIL")]),
        ("startup fails -> retry until it works", D(2026, 9, 25, 20, 1, 0), 720, [False, False],
         [("20:01:00", "FAIL"), ("20:05:30", "FAIL"), ("20:10:30", "ok")]),
        ("midnight moves Tomorrow to Today", D(2026, 9, 25, 23, 59, 0), 120, [],
         [("23:59:00", "ok"), ("00:00:30", "ok")])):
    got = schedule(start, seconds, answers)
    expect("%s %s" % (label, got), got == want)
finish()
