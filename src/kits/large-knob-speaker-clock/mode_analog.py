# mode_analog.py -- an analog clock face, as a mode for 16-main-template.py.
#
# A round dial with 60 ticks and 12 numerals, an hour hand, a minute hand,
# and a thin red second hand, with the day and the date in the top
# corners beside it.
#
# HOW THE HANDS MOVE WITHOUT REDRAWING THE FACE. There is no frame buffer,
# so the whole dial cannot be redrawn every second -- it would flicker.
# Instead, each second:
#
#   1. the old second hand is drawn again in BLACK, which erases it
#   2. the old minute and hour hands too, but only when the minute changed
#   3. the one numeral the old second hand was lying across is redrawn,
#      because erasing the hand took a bite out of it
#   4. the hands are drawn in their new places
#
# The hands are kept shorter than the ring of numerals, and the second
# hand shorter than the ticks, so the only part of the dial a hand can
# ever cover is one numeral.
#
# Every mode has the same four functions -- see 16-main-template.py. A
# mode only gets rows 0 to 219 of the screen, because the mode dots go
# below.

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
TEXT_COLOR = config.YELLOW
NUMERAL_FONT = config.SMALL_FONT

FACE_HEIGHT = 220        # rows 0 to 219
CX = config.CENTER_X
CY = FACE_HEIGHT // 2
TWO_PI = 2 * math.pi

TICK_OUTER = CY - 4                       # 106
MINUTE_TICK_INNER = TICK_OUTER - 6        # 100
HOUR_MARK_INNER = TICK_OUTER - 13         # 93
HOUR_MARK_HALF_WIDTH = 2
NUMERAL_RADIUS = 79

SECOND_LENGTH = 92
SECOND_TAIL = 16
MINUTE_LENGTH = 64
MINUTE_HALF_WIDTH = 5
HOUR_LENGTH = 42
HOUR_HALF_WIDTH = 7
HAND_TAIL = 9
CAP_RADIUS = 5

CORNER_Y = 8             # the day (top left) and the date (top right)
CORNER_CHARS = 6

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


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
    """A long thin diamond: the tip, one side, the tail, the other side."""
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


def draw_corners(weekday, month, day):
    """The day name top left, the month and day top right."""
    font = config.SMALL_FONT
    left = "{:<6}".format(DAYS[weekday])
    right = "{:>6}".format("%s %d" % (MONTHS[month - 1], day))
    _display.text(font, left, 6, CORNER_Y, TEXT_COLOR, BLACK)
    _display.text(font, right, config.WIDTH - 6 - CORNER_CHARS * font.WIDTH,
                  CORNER_Y, TEXT_COLOR, BLACK)


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
    global _display, last, shown_day
    _display = display
    draw_dial()
    last = None
    shown_day = None


def update(now):
    global last, shown_day
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

    if t[2] != shown_day:
        draw_corners(t[6], t[1], t[2])
        shown_day = t[2]


def stop():
    return None
