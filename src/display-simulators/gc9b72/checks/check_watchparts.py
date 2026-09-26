"""lib/watchparts.py: Digit and TextLine repaint correctly, digit pieces
tile without overlap, and Button handles bounce, quick taps, and short
and long presses."""

import random
import time

from _setup import screen, W, expect, finish, hardware
import config
from watchparts import (Digit, TextLine, Button, DIGITS, BLANK, ALL_SEGMENTS,
                        SHORT, LONG)

display = config.init_display()
random.seed(7)
COLORS = (0xFFFF, 0xF800, 0xFFE0, 0x07FF)


def repaints_match(make, values):
    """After each show(), the screen must equal a fresh part showing the
    same value on a blank screen."""
    bad = 0
    screen.px = [0] * (W * W)
    part = make()
    for v in values:
        part.show(*v)
        live = list(screen.px)
        screen.px = [0] * (W * W)
        make().show(*v)
        bad += screen.px != live
        screen.px = live
    return bad


print("Digit and TextLine")
patterns = [random.choice(DIGITS + (BLANK, ALL_SEGMENTS, random.randrange(128)))
            for _ in range(300)]
bad = repaints_match(lambda: Digit(display, 100, 100, 40, 71, 9, 0xFFFF, 0x18C3),
                     [(p, random.choice(COLORS)) for p in patterns])
expect("Digit: 300 random patterns and colors (%d mismatched)" % bad, bad == 0)
bad = repaints_match(lambda: Digit(display, 100, 100, 58, 114, 12, 0xFFFF, 0x18C3, half=True),
                     [(random.choice((DIGITS[1], BLANK)), random.choice(COLORS))
                      for _ in range(100)])
expect("Digit, half width: 1 or blank (%d mismatched)" % bad, bad == 0)
words = ["", "Lap   1 00:02.00", "READY", "RUNNING", "Lap 100 99:59.99", "a", "TIME'S UP!"]
bad = repaints_match(lambda: TextLine(display, config.SMALL_FONT, 180, 200, 16, 0xFFFF),
                     [(random.choice(words), random.choice(COLORS)) for _ in range(60)])
expect("TextLine: random text and colors (%d mismatched)" % bad, bad == 0)
for w, h, t in ((40, 71, 9), (22, 40, 6), (58, 114, 12), (38, 72, 8)):
    cells = {}
    for x, y, rw, rh in Digit(display, 0, 0, w, h, t, 1, 0).rects:
        for yy in range(y, y + rh):
            for xx in range(x, x + rw):
                cells[(xx, yy)] = cells.get((xx, yy), 0) + 1
    over = sum(1 for c in cells.values() if c > 1)
    expect("Digit %dx%d, %d thick: pieces don't overlap (%d)" % (w, h, t, over), over == 0)
try:
    Digit(display, 0, 0, 40, 70, 9, 1, 0)
    expect("Digit rejects a height that doesn't divide evenly", False)
except ValueError:
    expect("Digit rejects a height that doesn't divide evenly", True)

print("Button")
clock = [1000]
time.ticks_ms = lambda: clock[0]


def bounce(pin, final):
    for level in (final, 1 - final, final, 1 - final, final):   # rattling contacts
        pin.set_level(level)
        clock[0] += 1


pin = hardware.Pin(13)
b = Button(pin)
clock[0] = 2000
bounce(pin, 0)
r = [b.pressed(clock[0])]
clock[0] += 100
r.append(b.pressed(clock[0]))
bounce(pin, 1)
clock[0] += 5
r.append(b.pressed(clock[0]))
for _ in range(2):
    clock[0] += 60
    r.append(b.pressed(clock[0]))
expect("a normal press counts once; release bounce adds nothing",
       r == [True, False, False, False, False])

clock[0] = 5000
bounce(pin, 0)
clock[0] += 90
bounce(pin, 1)              # down and up again before the loop looks
clock[0] += 150
taps = [b.pressed(clock[0])]
for _ in range(5):
    clock[0] += 10
    taps.append(b.pressed(clock[0]))
expect("a quick tap during a busy loop counts exactly once", taps == [True] + [False] * 5)

p2 = hardware.Pin(14)
m = Button(p2)
clock[0] = 10000


def events(ms, step=10):
    found = []
    for _ in range(ms // step):
        clock[0] += step
        e = m.short_or_long(clock[0])
        if e:
            found.append(e)
    return found


bounce(p2, 0)
e = events(300)
bounce(p2, 1)
e += events(300)
expect("short press -> SHORT once, when let go", e == [SHORT])
bounce(p2, 0)
e = events(1500)
bounce(p2, 1)
e += events(300)
expect("held 1.5 s -> LONG once at 1 s, nothing when let go", e == [LONG])
clock[0] += 500
bounce(p2, 0)
clock[0] += 80
bounce(p2, 1)
clock[0] += 200
expect("quick tap while busy -> SHORT", events(300) == [SHORT])
finish()
