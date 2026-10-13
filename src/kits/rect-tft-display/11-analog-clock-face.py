# Lab 11: Analog Clock Face
# A full clock face: 60 minute ticks, 12 hour markers, 12 numerals, and
# hour, minute, and second hands. Copy it to the Pico as main.py and the
# clock starts by itself at power-up -- with SYNC_WITH_WIFI on, it sets
# its own time from the internet first.
#
# THE HARD PART: THERE IS NO FRAME BUFFER. A framebuf display draws the
# whole face in RAM and sends it with show(). This one draws straight to
# the glass, and redrawing all 160 x 128 pixels every second would flicker
# badly. So the face is drawn ONCE, and each second only the hands move:
#
#   1. erase the old second hand by drawing it again in black
#   2. if the minute changed, erase the old minute and hour hands too
#   3. repair whatever the erased second hand cut through
#   4. draw all three hands in their new positions
#
# Step 3 is the interesting one. Erasing a hand in black also erases
# anything it was lying on top of. The dial is laid out so that the list
# of things a hand can damage stays short:
#
#   - the ticks sit OUTSIDE the longest hand, so they are never touched
#   - the numerals sit outside the minute and hour hands, so only the
#     second hand ever crosses one -- and at most one at a time, the
#     numeral nearest to where it was
#   - the hour and minute hands are redrawn every second anyway
#
# The screen is only 128 pixels tall, so the dial is 124 across. The
# numerals use the smallest font, 8 x 8 -- the only one that fits all
# twelve on a dial this size and still leaves room for the hands.
#
# Change the lengths below and you may break those rules. Try it: make
# SECOND_LENGTH 60 and watch the second hand chew up the ticks.

NAME = "11-analog-clock-face.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import config
import shapes

# Set the RTC from the internet at power-up and again every night.
# Needs secrets.py (see lab 10). With False, the clock shows whatever the
# RTC already holds -- correct when Thonny started it, not when the Pico
# powers up on its own.
SYNC_WITH_WIFI = True
RESYNC_HOUR = 3          # re-sync at 3:00:00 AM, when no one is looking

BLACK = config.BLACK
WHITE = config.WHITE
HAND_COLOR = WHITE
SECOND_COLOR = config.RED
TICK_COLOR = config.GRAY
NUMERAL_FONT = config.TINY_FONT

CX = config.CENTER_X
CY = config.CENTER_Y
TWO_PI = 2 * math.pi

# Dial geometry, from the rim inward. Every radius is in pixels from the
# center of the screen.
TICK_OUTER = config.CENTER_Y - 2          # 62 -- outer end of every tick
MINUTE_TICK_INNER = TICK_OUTER - 3        # 59
HOUR_MARK_INNER = TICK_OUTER - 7          # 55
HOUR_MARK_HALF_WIDTH = 1                  # hour markers are 3 px wide
NUMERAL_RADIUS = 46                       # center of each numeral
# The 8 x 8 numerals reach from about 37 to 54 px out -- between the
# hands and the hour markers.

SECOND_LENGTH = 52       # across the numerals, short of the hour markers
SECOND_TAIL = 9          # the short end on the far side of the center
MINUTE_LENGTH = 35       # just short of the closest numeral corner (37)
MINUTE_HALF_WIDTH = 3
HOUR_LENGTH = 24
HOUR_HALF_WIDTH = 4
HAND_TAIL = 5
CAP_RADIUS = 3           # the red dot that covers where the hands meet


def point(angle, along, across=0):
    """The screen position `along` pixels out from the center in the
    direction of `angle`, and `across` pixels to the side of that line.

    Angles are clockwise from 12 o'clock, in radians -- the way a clock
    measures them, not the way a math book does. Screen y grows DOWNWARD,
    which is why y subtracts the cosine."""
    s = math.sin(angle)
    c = math.cos(angle)
    return (round(CX + along * s + across * c),
            round(CY - along * c + across * s))


def quad(p0, p1, p2, p3):
    """Four points packed the way shapes.poly() wants them."""
    return array('h', [p0[0], p0[1], p1[0], p1[1],
                       p2[0], p2[1], p3[0], p3[1]])


def hand_shape(angle, length, half_width):
    """A kite-shaped hand: a sharp tip, widest at the center, and a short
    tail behind it."""
    return quad(point(angle, length),
                point(angle, 0, half_width),
                point(angle, -HAND_TAIL),
                point(angle, 0, -half_width))


def draw_numeral(display, hour):
    """Draw one numeral (1-12), centered on its spot on the dial."""
    label = str(hour)
    x, y = point(hour * TWO_PI / 12, NUMERAL_RADIUS)
    # The last column and the bottom row of every 8 x 8 character are
    # blank, so the -1 centers the part you can see.
    display.text(NUMERAL_FONT, label,
                 x - (len(label) * NUMERAL_FONT.WIDTH - 1) // 2,
                 y - (NUMERAL_FONT.HEIGHT - 1) // 2,
                 WHITE, BLACK)


def draw_dial(display):
    """Everything that never moves. Drawn once."""
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
        draw_numeral(display, hour)


def hour_angle(hour, minute):
    # The hour hand creeps forward as the minutes pass: at 3:30 it points
    # halfway between the 3 and the 4.
    return ((hour % 12) + minute / 60) * TWO_PI / 12


def minute_angle(minute):
    return minute * TWO_PI / 60


def draw_hour_hand(display, hour, minute, color):
    shapes.poly(display, 0, 0,
                hand_shape(hour_angle(hour, minute), HOUR_LENGTH,
                           HOUR_HALF_WIDTH),
                color, config.FILL)


def draw_minute_hand(display, minute, color):
    shapes.poly(display, 0, 0,
                hand_shape(minute_angle(minute), MINUTE_LENGTH,
                           MINUTE_HALF_WIDTH),
                color, config.FILL)


def draw_second_hand(display, second, color):
    angle = second * TWO_PI / 60
    x0, y0 = point(angle, -SECOND_TAIL)
    x1, y1 = point(angle, SECOND_LENGTH)
    display.line(x0, y0, x1, y1, color)


def numeral_under(second):
    """The numeral the second hand lies across at this second. Only the
    nearest one can be hit: 1 second (6 degrees) off a numeral the hand
    still clips its box, but 2 seconds (12 degrees) off it clears it."""
    return ((second + 2) // 5) % 12 or 12


def update_hands(display, now, last):
    """Move the hands from `last` (hour, minute, second) to `now`.
    `last` is None the first time, when there is nothing to erase."""
    hour, minute, second = now
    if last is not None:
        last_hour, last_minute, last_second = last
        draw_second_hand(display, last_second, BLACK)
        if (hour, minute) != (last_hour, last_minute):
            draw_minute_hand(display, last_minute, BLACK)
            draw_hour_hand(display, last_hour, last_minute, BLACK)
        draw_numeral(display, numeral_under(last_second))

    draw_hour_hand(display, hour, minute, HAND_COLOR)
    draw_minute_hand(display, minute, HAND_COLOR)
    draw_second_hand(display, second, SECOND_COLOR)
    shapes.circle(display, CX, CY, CAP_RADIUS, SECOND_COLOR, config.FILL)


display = config.init_display()

if SYNC_WITH_WIFI:
    import wifi_time
    display.fill(BLACK)
    config.centered_text(display, config.SMALL_FONT, "Setting clock", 24)
    if not wifi_time.sync_time(display):
        # Keep going on whatever time the RTC has -- a clock that is
        # wrong is more useful than one that shows an error forever.
        time.sleep(3)

draw_dial(display)
last = None

while True:
    t = time.localtime()
    now = (t[3], t[4], t[5])
    if now != last:
        update_hands(display, now, last)
        last = now
        if SYNC_WITH_WIFI and now == (RESYNC_HOUR, 0, 0):
            # No display argument: status messages go to the shell only,
            # so they don't scribble over the face. The hands jump to the
            # corrected time on the next pass, erasing the old ones first.
            wifi_time.sync_time()
    time.sleep_ms(20)
