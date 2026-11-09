# app_analog.py -- lab 11's analog clock, as a mode for 20-mode-main.py.
#
#   K0 (short press)   the tick-tock sound on / off
#
# Read lab 11 for how the hands move without redrawing the face: the old
# hands are drawn again in black, and the one numeral the second hand
# was lying across is put back.
#
# The chime on the hour is 20-mode-main.py's job, so it sounds in every
# mode. Whether the ticking is on is kept by stop(), so it is still on
# when you come back. See 20-mode-main.py for the three functions every
# mode has.

import math
import time
from array import array

import config
import shapes
import sound

BLACK = config.BLACK
WHITE = config.WHITE
HAND_COLOR = WHITE
SECOND_COLOR = config.RED
TICK_COLOR = config.GRAY
CORNER_COLOR = config.YELLOW
DIM = config.color565(110, 110, 110)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

CX = config.CENTER_X
CY = config.CENTER_Y
TWO_PI = 2 * math.pi

TICK_OUTER = CY - 4                       # 116
MINUTE_TICK_INNER = TICK_OUTER - 7        # 109
HOUR_MARK_INNER = TICK_OUTER - 15         # 101
HOUR_MARK_HALF_WIDTH = 2
NUMERAL_RADIUS = 88

SECOND_LENGTH = 104
SECOND_TAIL = 18
MINUTE_LENGTH = 72
MINUTE_HALF_WIDTH = 5
HOUR_LENGTH = 48
HOUR_HALF_WIDTH = 7
HAND_TAIL = 10
CAP_RADIUS = 5

MARGIN = 4

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def point(angle, along, across=0):
    s = math.sin(angle)
    c = math.cos(angle)
    return (round(CX + along * s + across * c),
            round(CY - along * c + across * s))


def quad(p0, p1, p2, p3):
    return array('h', [p0[0], p0[1], p1[0], p1[1],
                       p2[0], p2[1], p3[0], p3[1]])


def hand_shape(angle, length, half_width):
    return quad(point(angle, length), point(angle, 0, half_width),
                point(angle, -HAND_TAIL), point(angle, 0, -half_width))


def draw_numeral(hour):
    label = str(hour)
    x, y = point(hour * TWO_PI / 12, NUMERAL_RADIUS)
    _display.text(SMALL, label, x - (len(label) * SMALL.WIDTH - 1) // 2,
                  y - (SMALL.HEIGHT - 1) // 2, WHITE, BLACK)


def draw_dial():
    _display.fill(BLACK)
    for i in range(60):
        angle = i * TWO_PI / 60
        if i % 5 == 0:
            w = HOUR_MARK_HALF_WIDTH
            shapes.poly(_display, 0, 0,
                        quad(point(angle, HOUR_MARK_INNER, -w),
                             point(angle, TICK_OUTER, -w),
                             point(angle, TICK_OUTER, w),
                             point(angle, HOUR_MARK_INNER, w)),
                        WHITE, config.FILL)
        else:
            x0, y0 = point(angle, MINUTE_TICK_INNER)
            x1, y1 = point(angle, TICK_OUTER)
            _display.line(x0, y0, x1, y1, TICK_COLOR)
    for hour in range(1, 13):
        draw_numeral(hour)


def draw_hour_hand(hour, minute, color):
    angle = ((hour % 12) + minute / 60) * TWO_PI / 12
    shapes.poly(_display, 0, 0,
                hand_shape(angle, HOUR_LENGTH, HOUR_HALF_WIDTH),
                color, config.FILL)


def draw_minute_hand(minute, color):
    shapes.poly(_display, 0, 0,
                hand_shape(minute * TWO_PI / 60, MINUTE_LENGTH,
                           MINUTE_HALF_WIDTH),
                color, config.FILL)


def draw_second_hand(second, color):
    angle = second * TWO_PI / 60
    x0, y0 = point(angle, -SECOND_TAIL)
    x1, y1 = point(angle, SECOND_LENGTH)
    _display.line(x0, y0, x1, y1, color)


def numeral_under(second):
    return ((second + 2) // 5) % 12 or 12


def draw_corners(weekday, month, day, hour):
    right = config.WIDTH - MARGIN
    _display.text(BIG, DAYS[weekday], MARGIN, MARGIN, CORNER_COLOR, BLACK)
    _display.text(BIG, "%2d" % day, right - 2 * BIG.WIDTH, MARGIN,
                  CORNER_COLOR, BLACK)
    _display.text(SMALL, MONTHS[month - 1], right - 3 * SMALL.WIDTH,
                  MARGIN + BIG.HEIGHT + 2, CORNER_COLOR, BLACK)
    _display.text(BIG, "AM" if hour < 12 else "PM", MARGIN,
                  config.HEIGHT - MARGIN - BIG.HEIGHT, DIM, BLACK)


def draw_tick_label():
    _display.text(SMALL, "tick" if tick_sound else "    ",
                  config.WIDTH - MARGIN - 4 * SMALL.WIDTH,
                  config.HEIGHT - MARGIN - SMALL.HEIGHT, DIM, BLACK)


def tick(second):
    sound.tone(1500 if second % 2 == 0 else 1100, 8, wave=sound.SQUARE,
               level=0.15, attack=1, release=4)


def start(display, k0, push, knob, saved):
    global _display, _k0, tick_sound, last, shown_corners
    _display = display
    _k0 = k0
    tick_sound = saved["tick_sound"] if saved else False
    draw_dial()
    draw_tick_label()
    last = None
    shown_corners = None


def update(now):
    global tick_sound, last, shown_corners
    if _k0.pressed(now):
        tick_sound = not tick_sound
        draw_tick_label()

    t = time.localtime()
    current = (t[3], t[4], t[5])
    if current == last:
        return
    hour, minute, second = current
    if last is not None:
        last_hour, last_minute, last_second = last
        draw_second_hand(last_second, BLACK)
        if (hour, minute) != (last_hour, last_minute):
            draw_minute_hand(last_minute, BLACK)
            draw_hour_hand(last_hour, last_minute, BLACK)
        draw_numeral(numeral_under(last_second))
    draw_hour_hand(hour, minute, HAND_COLOR)
    draw_minute_hand(minute, HAND_COLOR)
    draw_second_hand(second, SECOND_COLOR)
    shapes.circle(_display, CX, CY, CAP_RADIUS, SECOND_COLOR, config.FILL)
    last = current

    corners = (t[6], t[1], t[2], hour < 12)
    if corners != shown_corners:
        draw_corners(t[6], t[1], t[2], hour)
        shown_corners = corners

    # No tick at the top of the hour: that is the chime's moment.
    if tick_sound and not (minute == 0 and second == 0):
        tick(second)


def stop():
    return {"tick_sound": tick_sound}
