# Lab 05: Analog Watch Face
# A full watch face: 60 minute ticks, 12 hour markers, 12 numerals, and
# hour, minute, and second hands. Copy it to the Pico as main.py and the
# watch starts by itself at power-up -- with SYNC_WITH_WIFI on, it sets
# its own clock from the internet first.
#
# THE HARD PART: THERE IS NO FRAME BUFFER. A framebuf display draws the
# whole face in RAM and sends it with show(). This one draws straight to
# the glass, and redrawing all 360 x 360 pixels every second would flicker
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
# Change the lengths below and you may break those rules. Try it: make
# MINUTE_LENGTH 120 and watch the numerals get chewed up.

NAME = "05-analog-watch-face.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import config
import shapes

# Set the RTC from the internet at power-up and again every night.
# Needs secrets.py (see lab 04). With False, the watch shows whatever the
# RTC already holds -- correct when Thonny started it, not on a battery.
SYNC_WITH_WIFI = True
RESYNC_HOUR = 3          # re-sync at 3:00:00 AM, when no one is looking

BLACK = config.BLACK
WHITE = config.WHITE
HAND_COLOR = WHITE
SECOND_COLOR = config.RED
TICK_COLOR = config.GRAY
NUMERAL_FONT = config.BIG_FONT

CX = config.CENTER_X
CY = config.CENTER_Y
TWO_PI = 2 * math.pi

# Dial geometry, from the rim inward. Every radius is in pixels from the
# center of the screen.
TICK_OUTER = config.SAFE_RADIUS - 6       # 162 -- outer end of every tick
MINUTE_TICK_INNER = TICK_OUTER - 10       # 152
HOUR_MARK_INNER = TICK_OUTER - 20         # 142
HOUR_MARK_HALF_WIDTH = 3                  # hour markers are 7 px wide
NUMERAL_RADIUS = 118                      # center of each numeral
# The 16 x 32 numerals reach from about 96 to 140 px out -- between the
# hands and the hour markers.

SECOND_LENGTH = 138      # past the numerals, short of the hour markers
SECOND_TAIL = 24         # the short end on the far side of the center
MINUTE_LENGTH = 92       # just short of the closest numeral corner (96)
MINUTE_HALF_WIDTH = 6
HOUR_LENGTH = 64
HOUR_HALF_WIDTH = 8
HAND_TAIL = 14
CAP_RADIUS = 7           # the red dot that covers where the hands meet


def point(angle, along, across=0):
    """The screen position `along` pixels out from the center in the
    direction of `angle`, and `across` pixels to the side of that line.

    Angles are clockwise from 12 o'clock, in radians -- the way a watch
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
    display.text(NUMERAL_FONT, label,
                 x - len(label) * NUMERAL_FONT.WIDTH // 2,
                 y - NUMERAL_FONT.HEIGHT // 2,
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
    nearest one can be hit: 2 seconds (12 degrees) off a numeral the hand
    still clips its box, but 3 seconds (18 degrees) off it clears it."""
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
    config.centered_text(display, config.BIG_FONT, "Setting clock", 130)
    if not wifi_time.sync_time(display):
        # Keep going on whatever time the RTC has -- a watch that is
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
