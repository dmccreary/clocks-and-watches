# Lab 11: Analog Clock
# A round clock face as tall as the screen: 60 ticks, 12 numerals, an
# hour hand, a minute hand, and a thin red second hand. The day sits in
# the top-left corner, the date in the top-right, and AM or PM bottom
# left -- the corners a round face leaves empty on a rectangular screen.
#
#   K0    (GP11)  the ticking sound on / off
#
# Turn the ticking on and the speaker goes "tick ... tock" once a second,
# like a wind-up clock. At the top of every hour it plays a chime.
#
# HOW THE HANDS MOVE WITHOUT REDRAWING THE FACE. There is no frame
# buffer, so the whole dial cannot be redrawn every second -- it would
# flicker. Instead, each second:
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
# WHERE IS A POINT ON THE DIAL? Angles on a clock start at 12 and go
# clockwise, but the screen's y goes DOWN. So a point `along` pixels out
# from the center at angle a is
#
#     x = CX + along * sin(a)
#     y = CY - along * cos(a)
#
# point() below does that, and also steps `across` pixels to the side,
# which is how a hand gets its width.

NAME = "11-analog.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import config
import shapes
import sound
from watchparts import Button

TICK_SOUND = False           # K0 turns it on and off
CHIME_ON_THE_HOUR = True

BLACK = config.BLACK
WHITE = config.WHITE
HAND_COLOR = WHITE
SECOND_COLOR = config.RED
TICK_COLOR = config.GRAY
CORNER_COLOR = config.YELLOW
DIM = config.color565(110, 110, 110)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

CX = config.CENTER_X              # 160
CY = config.CENTER_Y              # 120
TWO_PI = 2 * math.pi

# Every size is a distance from the center, in pixels.
TICK_OUTER = CY - 4                       # 116
MINUTE_TICK_INNER = TICK_OUTER - 7        # 109
HOUR_MARK_INNER = TICK_OUTER - 15         # 101
HOUR_MARK_HALF_WIDTH = 2
NUMERAL_RADIUS = 88

SECOND_LENGTH = 104      # stops short of the ticks
SECOND_TAIL = 18
MINUTE_LENGTH = 72       # stops short of the numerals
MINUTE_HALF_WIDTH = 5
HOUR_LENGTH = 48
HOUR_HALF_WIDTH = 7
HAND_TAIL = 10
CAP_RADIUS = 5

MARGIN = 4               # the corner text, in from the screen's edges

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

display = config.init_display()
a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
sound.init()


def point(angle, along, across=0):
    """`along` px out from the center at `angle` (radians clockwise from
    12), and `across` px to the side."""
    s = math.sin(angle)
    c = math.cos(angle)
    return (round(CX + along * s + across * c),
            round(CY - along * c + across * s))


def quad(p0, p1, p2, p3):
    """Four corners in the flat array shapes.poly() wants."""
    return array('h', [p0[0], p0[1], p1[0], p1[1],
                       p2[0], p2[1], p3[0], p3[1]])


def hand_shape(angle, length, half_width):
    """A long thin diamond: the tip, one side, the tail, the other side."""
    return quad(point(angle, length), point(angle, 0, half_width),
                point(angle, -HAND_TAIL), point(angle, 0, -half_width))


def draw_numeral(hour):
    label = str(hour)
    x, y = point(hour * TWO_PI / 12, NUMERAL_RADIUS)
    display.text(SMALL, label, x - (len(label) * SMALL.WIDTH - 1) // 2,
                 y - (SMALL.HEIGHT - 1) // 2, WHITE, BLACK)


def draw_dial():
    display.fill(BLACK)
    for i in range(60):
        angle = i * TWO_PI / 60
        if i % 5 == 0:
            w = HOUR_MARK_HALF_WIDTH
            shapes.poly(display, 0, 0,
                        quad(point(angle, HOUR_MARK_INNER, -w),
                             point(angle, TICK_OUTER, -w),
                             point(angle, TICK_OUTER, w),
                             point(angle, HOUR_MARK_INNER, w)),
                        WHITE, config.FILL)
        else:
            x0, y0 = point(angle, MINUTE_TICK_INNER)
            x1, y1 = point(angle, TICK_OUTER)
            display.line(x0, y0, x1, y1, TICK_COLOR)
    for hour in range(1, 13):
        draw_numeral(hour)


def draw_hour_hand(hour, minute, color):
    angle = ((hour % 12) + minute / 60) * TWO_PI / 12
    shapes.poly(display, 0, 0,
                hand_shape(angle, HOUR_LENGTH, HOUR_HALF_WIDTH),
                color, config.FILL)


def draw_minute_hand(minute, color):
    shapes.poly(display, 0, 0,
                hand_shape(minute * TWO_PI / 60, MINUTE_LENGTH,
                           MINUTE_HALF_WIDTH),
                color, config.FILL)


def draw_second_hand(second, color):
    angle = second * TWO_PI / 60
    x0, y0 = point(angle, -SECOND_TAIL)
    x1, y1 = point(angle, SECOND_LENGTH)
    display.line(x0, y0, x1, y1, color)


def numeral_under(second):
    """The one numeral the second hand can be lying across."""
    return ((second + 2) // 5) % 12 or 12


def draw_corners(weekday, month, day, hour):
    """Day top left; date top right; AM/PM bottom left. Each is padded to
    the same width every time, so new text covers the old."""
    right = config.WIDTH - MARGIN
    display.text(BIG, DAYS[weekday], MARGIN, MARGIN, CORNER_COLOR, BLACK)
    display.text(BIG, "%2d" % day, right - 2 * BIG.WIDTH, MARGIN,
                 CORNER_COLOR, BLACK)
    display.text(SMALL, MONTHS[month - 1], right - 3 * SMALL.WIDTH,
                 MARGIN + BIG.HEIGHT + 2, CORNER_COLOR, BLACK)
    display.text(BIG, "AM" if hour < 12 else "PM", MARGIN,
                 config.HEIGHT - MARGIN - BIG.HEIGHT, DIM, BLACK)


def draw_tick_label():
    """"tick" in the bottom-right corner while the ticking is on."""
    display.text(SMALL, "tick" if tick_sound else "    ",
                 config.WIDTH - MARGIN - 4 * SMALL.WIDTH,
                 config.HEIGHT - MARGIN - SMALL.HEIGHT, DIM, BLACK)


def tick(second):
    """A soft click, high on even seconds and low on odd ones."""
    sound.tone(1500 if second % 2 == 0 else 1100, 8, wave=sound.SQUARE,
               level=0.15, attack=1, release=4)


if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 06 to set it over WiFi.")

draw_dial()
tick_sound = TICK_SOUND
draw_tick_label()
last = None              # (hour, minute, second) the hands show
shown_corners = None

while True:
    if k0_button.pressed():
        tick_sound = not tick_sound
        draw_tick_label()
        print("ticking", "on" if tick_sound else "off")

    t = time.localtime()
    current = (t[3], t[4], t[5])
    if current != last:
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
        shapes.circle(display, CX, CY, CAP_RADIUS, SECOND_COLOR, config.FILL)
        last = current

        corners = (t[6], t[1], t[2], hour < 12)
        if corners != shown_corners:
            draw_corners(t[6], t[1], t[2], hour)
            shown_corners = corners

        if CHIME_ON_THE_HOUR and minute == 0 and second == 0:
            sound.play("chime")
        elif tick_sound:
            tick(second)

    time.sleep_ms(20)
