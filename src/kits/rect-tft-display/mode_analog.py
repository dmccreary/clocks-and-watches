# mode_analog.py -- the analog clock face of lab 11, as a mode for
# 17-main-template.py. Lab 11 explains how it moves the hands without
# redrawing the whole face.
#
# One change from lab 11: a mode only gets rows 0 to 119 of the screen,
# because the mode dots go below. So the dial is 8 px smaller across and
# sits 4 rows higher, and the hands are shorter to match.
#
# Every mode has the same four functions -- see 17-main-template.py.

import math
import time
from array import array

import config
import shapes

BLACK = config.BLACK
WHITE = config.WHITE
HAND_COLOR = WHITE
SECOND_COLOR = config.RED
TICK_COLOR = config.GRAY
NUMERAL_FONT = config.TINY_FONT

FACE_HEIGHT = 120        # rows 0 to 119
CX = config.CENTER_X
CY = FACE_HEIGHT // 2
TWO_PI = 2 * math.pi

TICK_OUTER = CY - 2                       # 58
MINUTE_TICK_INNER = TICK_OUTER - 3        # 55
HOUR_MARK_INNER = TICK_OUTER - 7          # 51
HOUR_MARK_HALF_WIDTH = 1
NUMERAL_RADIUS = 42

SECOND_LENGTH = 48       # lab 11 uses 52
SECOND_TAIL = 9
MINUTE_LENGTH = 30       # lab 11 uses 35
MINUTE_HALF_WIDTH = 3
HOUR_LENGTH = 21         # lab 11 uses 24
HOUR_HALF_WIDTH = 4
HAND_TAIL = 5
CAP_RADIUS = 3


def point(angle, along, across=0):
    """`along` px out from the center at `angle` (clockwise from 12), and
    `across` px to the side."""
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
    _display.text(NUMERAL_FONT, label,
                  x - (len(label) * NUMERAL_FONT.WIDTH - 1) // 2,
                  y - (NUMERAL_FONT.HEIGHT - 1) // 2, WHITE, BLACK)


def draw_dial():
    _display.fill_rect(0, 0, config.WIDTH, FACE_HEIGHT, BLACK)
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
    """The one numeral the second hand can be lying across."""
    return ((second + 2) // 5) % 12 or 12


def start(display, k0, push, saved):
    global _display, last
    _display = display
    draw_dial()
    last = None


def update(now):
    global last
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


def stop():
    return None
