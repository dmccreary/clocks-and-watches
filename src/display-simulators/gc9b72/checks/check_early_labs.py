"""Labs 02, 03, 04, 06, and 07 run and draw; lab 07's buttons really set
the clock; and wifi_time's US daylight-saving edges are right."""

import calendar

from _setup import screen, W, expect, finish, runner, hardware


def lit():
    return sum(1 for p in screen.px if p)


for lab, ms in (("02-hello.py", 2000), ("03-digital-clock.py", 2500),
                ("04-wifi-sync-time.py", 3000), ("06-button-test.py", 1200)):
    runner.run_lab(lab, ms)
    expect("%s runs and draws (%d lit pixels)" % (lab, lit()), lit() > 1000)

# Lab 07: MODE, UP UP (hour 10 -> 12), MODE, UP x3 (min 09 -> 12), MODE
runner.run_lab("07-set-time.py", 7000,
               [("mode", 1500, 1580), ("up", 2000, 2080), ("up", 2300, 2380),
                ("mode", 3000, 3080), ("up", 3500, 3580), ("up", 3800, 3880),
                ("up", 4100, 4180), ("mode", 5000, 5080)])
t = runner.localtime()
expect("lab 07 set the clock to 12:12 with the buttons (%02d:%02d)" % (t[3], t[4]),
       (t[3], t[4]) == (12, 12))

import wifi_time                                          # noqa: E402


def utc(*t):
    return calendar.timegm(t + (0, 0, 0))


cases = [(utc(2026, 3, 8, 7, 59, 59), -6, False), (utc(2026, 3, 8, 8, 0, 0), -6, True),
         (utc(2026, 11, 1, 6, 59, 59), -6, True), (utc(2026, 11, 1, 7, 0, 0), -6, False),
         (utc(2027, 3, 14, 7, 59, 59), -6, False), (utc(2027, 3, 14, 8, 0, 0), -6, True),
         (utc(2027, 11, 7, 6, 59, 59), -6, True), (utc(2027, 11, 7, 7, 0, 0), -6, False),
         (utc(2026, 3, 8, 6, 59, 0), -5, False), (utc(2026, 3, 8, 7, 0, 0), -5, True)]
wrong = [c for c in cases if wifi_time.is_us_dst(c[0], c[1]) != c[2]]
expect("US daylight saving edges, 2026 and 2027, Central and Eastern (%d wrong)" % len(wrong),
       not wrong)
finish()
