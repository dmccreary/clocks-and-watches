# Lab 08: Digital Watch Face
# Big seven-segment digits you can read from across the room, the date
# below them, and a ring of 60 ticks around the rim that fills up as the
# seconds pass. Copy it to the Pico as main.py to make it the watch.
#
# THE RULE FOR THIS FACE: ONLY SEND THE PIXELS THAT CHANGE. There is no
# frame buffer on this display, so anything you clear and redraw blinks.
# This face never clears anything after the first frame:
#
#   - A digit is seven segments, plus the six corners and joints where
#     segments meet, each one either lit or unlit. When the time goes
#     from 12:59 to 1:00, the face works out which pieces switched on or
#     off, and repaints only those. A piece that is lit in both digits is
#     not touched at all.
#   - Unlit segments are not black. They are painted a faint "ghost"
#     color, like the unlit segments on a real LCD watch, so turning a
#     segment off is just repainting it -- never erasing it.
#   - Each second lights exactly one more tick on the seconds ring. At
#     the top of the minute, the ticks that were lit go dark again.
#   - The date is padded with spaces to a fixed width, so every character
#     has a fixed spot. When the date changes, only the characters that
#     differ are repainted -- "Fri, Sep 25" to "Sat, Sep 26" redraws
#     five of them.
#
# In a normal second this face sends two small colon squares and one
# seconds tick -- a few hundred pixels out of the 129,600 on the screen.

NAME = "08-digital-watch-face.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import config
import shapes

# Set the RTC from the internet at power-up and again every night.
# Needs secrets.py (see lab 04).
SYNC_WITH_WIFI = True
RESYNC_HOUR = 3

TWELVE_HOUR = True       # False for a 24-hour clock (13:45 instead of 1:45)
BLINK_COLON = True       # the colon is lit on even seconds, ghosted on odd

# Colors. Set GHOST to config.BLACK to hide the unlit segments entirely.
DIGIT_COLOR = config.WHITE
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
TEXT_COLOR = config.YELLOW
BLACK = config.BLACK

# ---------------------------------------------------------------------
# Seven-segment digits
# ---------------------------------------------------------------------
# Every digit is some combination of these seven segments:
#
#      aaa
#     f   b
#     f   b
#      ggg
#     e   c
#     e   c
#      ddd
#
# Each digit below is a 7-bit number: bit 0 is segment a, bit 1 is b,
# and so on up to bit 6 for g. It is the same information as the
# segmentMapping table in the GC9A01 kit's lab 06, packed into one
# number per digit -- which makes "which segments changed?" a single
# XOR: old ^ new has a 1 bit for every segment that switched.
DIGIT_SEGMENTS = (
    0b0111111,  # 0: a b c d e f
    0b0000110,  # 1: b c
    0b1011011,  # 2: a b d e g
    0b1001111,  # 3: a b c d g
    0b1100110,  # 4: b c f g
    0b1101101,  # 5: a c d f g
    0b1111101,  # 6: a c d e f g
    0b0000111,  # 7: a b c
    0b1111111,  # 8: all seven
    0b1101111,  # 9: a b c d f g
)
BLANK = 0b0000000       # no segments: the leading digit of " 9:41"
ALL_SEGMENTS = 0b1111111

SEG_A, SEG_B, SEG_C, SEG_D, SEG_E, SEG_F, SEG_G = 1, 2, 4, 8, 16, 32, 64

DIGIT_WIDTH = 58
DIGIT_HEIGHT = 114
SEG = 12                # segment thickness
HALF = (DIGIT_HEIGHT - 3 * SEG) // 2     # 39 -- length of a vertical segment
BOTTOM = 2 * SEG + 2 * HALF              # 102 -- top of the bottom row
MIDDLE = SEG + HALF                      # 51 -- top of the middle row
RIGHT = DIGIT_WIDTH - SEG                # 46 -- left edge of the right column

# A digit is built from 13 rectangles (x, y, width, height), measured
# from its top-left corner. Rectangles are the cheapest thing this driver
# draws: one window, one run of pixels.
#
# The first seven are the segments a-g, in bit order. The last six are
# the square corners and joints where segments meet. On a real LCD those
# are left dark, but at this size that makes a digit look like seven
# loose sticks. Here a joint lights up whenever ANY segment touching it
# is lit, so a lit digit is one solid stroke:
#
#     1--a--2        1: a f     2: a b
#     f     b        3: f g e   4: b g c
#     3--g--4        5: e d     6: c d
#     e     c
#     5--d--6
PIECES = (
    (SEG, 0, DIGIT_WIDTH - 2 * SEG, SEG),        # a
    (RIGHT, SEG, SEG, HALF),                     # b
    (RIGHT, MIDDLE + SEG, SEG, HALF),            # c
    (SEG, BOTTOM, DIGIT_WIDTH - 2 * SEG, SEG),   # d
    (0, MIDDLE + SEG, SEG, HALF),                # e
    (0, SEG, SEG, HALF),                         # f
    (SEG, MIDDLE, DIGIT_WIDTH - 2 * SEG, SEG),   # g
    (0, 0, SEG, SEG),                            # joint 1, top-left
    (RIGHT, 0, SEG, SEG),                        # joint 2, top-right
    (0, MIDDLE, SEG, SEG),                       # joint 3, middle-left
    (RIGHT, MIDDLE, SEG, SEG),                   # joint 4, middle-right
    (0, BOTTOM, SEG, SEG),                       # joint 5, bottom-left
    (RIGHT, BOTTOM, SEG, SEG),                   # joint 6, bottom-right
)

# Which segments meet at each joint, in the same order as PIECES.
JOINTS = (
    SEG_A | SEG_F,
    SEG_A | SEG_B,
    SEG_F | SEG_G | SEG_E,
    SEG_B | SEG_G | SEG_C,
    SEG_E | SEG_D,
    SEG_C | SEG_D,
)


def pieces(segments):
    """Turn 7 segment bits into 13 piece bits: the segments themselves,
    then one bit per joint, set if any segment touching that joint is set."""
    bits = segments
    for j in range(6):
        if segments & JOINTS[j]:
            bits |= 1 << (7 + j)
    return bits


# THE LEFTMOST DIGIT OF A 12-HOUR CLOCK IS ONLY EVER "1" OR BLANK -- the
# hour is 1 to 12. So it only needs segments b and c (and their joints),
# and gets drawn as a narrow half digit: just the right-hand column.
# Drawing the other five segments, even as ghosts, would suggest it could
# show digits it never will. A 24-hour clock needs 0, 1, and 2 there, so
# it keeps a full digit.
if TWELVE_HOUR:
    FIRST_DIGIT_SEGMENTS = SEG_B | SEG_C
    first_width = SEG
else:
    FIRST_DIGIT_SEGMENTS = ALL_SEGMENTS
    first_width = DIGIT_WIDTH
# The pieces each digit actually has.
DIGIT_PIECES = (pieces(FIRST_DIGIT_SEGMENTS), pieces(ALL_SEGMENTS),
                pieces(ALL_SEGMENTS), pieces(ALL_SEGMENTS))

# Layout: the digits and the colon, as one row centered on the screen.
DIGIT_SPACING = 10      # between the two hour digits, and the two minutes
COLON_SPACING = 12      # on each side of the colon
_row_width = (first_width + 3 * DIGIT_WIDTH + 2 * DIGIT_SPACING
              + 2 * COLON_SPACING + SEG)
_x = (config.WIDTH - _row_width) // 2
# A half digit is only its right-hand column, so its "top-left corner"
# sits off to the left of where its pixels actually start.
_first_x = _x - (DIGIT_WIDTH - first_width)
_x += first_width + DIGIT_SPACING
_second_x = _x
_x += DIGIT_WIDTH + COLON_SPACING
COLON_X = _x
_x += SEG + COLON_SPACING
_third_x = _x
_x += DIGIT_WIDTH + DIGIT_SPACING
DIGIT_X = (_first_x, _second_x, _third_x, _x)

DIGIT_TOP = config.CENTER_Y - DIGIT_HEIGHT // 2
COLON_DOTS_Y = (DIGIT_TOP + DIGIT_HEIGHT // 3 - SEG // 2,
                DIGIT_TOP + 2 * DIGIT_HEIGHT // 3 - SEG // 2)

AMPM_Y = DIGIT_TOP - 32
DATE_Y = DIGIT_TOP + DIGIT_HEIGHT + 20
DATE_CHARS = 17          # "Wed, Sep 30, 2026" -- the longest date there is

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# ---------------------------------------------------------------------
# Seconds ring
# ---------------------------------------------------------------------
TICK_OUTER = config.SAFE_RADIUS - 2       # 166
TICK_INNER = TICK_OUTER - 8               # 158
TICK_INNER_FIVE = TICK_OUTER - 14         # 152 -- every fifth tick is longer
TICK_HALF_WIDTH = 2
TWO_PI = 2 * math.pi


def draw_digit(display, i, new, old):
    """Repaint only the pieces of digit i that changed. `new` and `old`
    are segment bits; `old` is None the first time, when every piece the
    digit has must be painted once."""
    lit = pieces(new)
    if old is None:
        changed = DIGIT_PIECES[i]
    else:
        changed = lit ^ pieces(old)
    for bit in range(13):
        if changed & (1 << bit):
            px, py, w, h = PIECES[bit]
            color = DIGIT_COLOR if lit & (1 << bit) else GHOST
            display.fill_rect(DIGIT_X[i] + px, DIGIT_TOP + py, w, h, color)


def draw_colon(display, lit):
    color = DIGIT_COLOR if lit else GHOST
    for y in COLON_DOTS_Y:
        display.fill_rect(COLON_X, y, SEG, SEG, color)


def time_digits(hour, minute):
    """The four digit patterns for this time."""
    if TWELVE_HOUR:
        hour = hour % 12 or 12
    tens = hour // 10
    # A 12-hour clock shows " 9:41", not "09:41".
    first = DIGIT_SEGMENTS[tens] if (tens or not TWELVE_HOUR) else BLANK
    return (first, DIGIT_SEGMENTS[hour % 10],
            DIGIT_SEGMENTS[minute // 10], DIGIT_SEGMENTS[minute % 10])


class _RunRecorder:
    """Stands in for the display while shapes.poly() works out a shape.
    poly() fills a shape one horizontal run at a time with hline(); this
    keeps the runs instead of sending them anywhere."""

    def __init__(self):
        self.runs = []

    def hline(self, x, y, length, color):
        self.runs.append((x, y, length))


def tick_runs(second):
    """Work out the pixels of one seconds tick: a thin 4-sided shape
    pointing at the center. Returns its horizontal runs (x, y, length)."""
    angle = second * TWO_PI / 60
    inner = TICK_INNER_FIVE if second % 5 == 0 else TICK_INNER
    s = math.sin(angle)
    c = math.cos(angle)
    corners = []
    for along, across in ((inner, -TICK_HALF_WIDTH), (TICK_OUTER, -TICK_HALF_WIDTH),
                          (TICK_OUTER, TICK_HALF_WIDTH), (inner, TICK_HALF_WIDTH)):
        corners.append(round(config.CENTER_X + along * s + across * c))
        corners.append(round(config.CENTER_Y - along * c + across * s))
    recorder = _RunRecorder()
    shapes.poly(recorder, 0, 0, array('h', corners), 0, config.FILL)
    return recorder.runs


# COMPUTE ONCE, DRAW MANY TIMES. Working out a tick's shape takes sines,
# cosines, and a scanline fill -- about 7 ms on the Pico 2 W. At the top
# of every minute 59 ticks go dark at once, and doing that math 59 times
# made the ring take 0.4 s to clear. The shapes never change, so work
# them all out here, once, at startup. After that a tick is just a
# handful of hline() calls.
TICK_RUNS = [tick_runs(second) for second in range(60)]


def draw_tick(display, second, lit):
    """Paint one seconds tick, lit or unlit. Both use exactly the same
    pixels, so switching a tick only ever repaints its own pixels."""
    color = ACCENT if lit else TICK_OFF
    for x, y, length in TICK_RUNS[second]:
        display.hline(x, y, length, color)


def update_ring(display, second, last):
    """Ticks 0 through `second` are lit. Moving from `last` to `second`,
    repaint only the ticks whose state changed."""
    if last is None:
        for i in range(60):
            draw_tick(display, i, i <= second)
    elif second > last:
        for i in range(last + 1, second + 1):   # normally just one tick
            draw_tick(display, i, True)
    elif second < last:
        # A new minute (or the clock was set back): everything after
        # `second` goes dark. Ticks 0..second were already lit.
        for i in range(second + 1, last + 1):
            draw_tick(display, i, False)


def draw_changed_chars(display, new, old, y, color):
    """Draw a centered line of small-font text, repainting only the
    characters that differ from `old` (None the first time). Both strings
    must be the same length, so each character keeps its spot on the line.
    text() paints a character's background along with it, so the new
    character covers the old one completely -- nothing to clear first."""
    font = config.SMALL_FONT
    x = (config.WIDTH - len(new) * font.WIDTH) // 2
    for i in range(len(new)):
        if old is None or old[i] != new[i]:
            display.text(font, new[i], x + i * font.WIDTH, y, color, BLACK)


def date_text(year, month, day, weekday):
    """The date, padded with spaces to exactly DATE_CHARS characters."""
    text = "%s, %s %d, %d" % (DAYS[weekday], MONTHS[month - 1], day, year)
    pad = DATE_CHARS - len(text)
    return " " * (pad // 2) + text + " " * (pad - pad // 2)


def ampm_text(hour):
    if not TWELVE_HOUR:
        return "  "
    return "AM" if hour < 12 else "PM"


# What is on the glass right now. None means "never drawn".
shown_digits = [None, None, None, None]
shown_colon = None
shown_second = None
shown_ampm = None
shown_date = None


def update_face(display, t):
    """Bring the glass up to date for time.localtime() tuple t, repainting
    only the parts that differ from what is already shown."""
    global shown_colon, shown_second, shown_ampm, shown_date
    year, month, day, hour, minute, second, weekday = t[:7]

    digits = time_digits(hour, minute)
    for i in range(4):
        if digits[i] != shown_digits[i]:
            draw_digit(display, i, digits[i], shown_digits[i])
            shown_digits[i] = digits[i]

    colon = (second % 2 == 0) if BLINK_COLON else True
    if colon != shown_colon:
        draw_colon(display, colon)
        shown_colon = colon

    update_ring(display, second, shown_second)
    shown_second = second

    ampm = ampm_text(hour)
    if ampm != shown_ampm:
        draw_changed_chars(display, ampm, shown_ampm, AMPM_Y, ACCENT)
        shown_ampm = ampm

    date = date_text(year, month, day, weekday)
    if date != shown_date:
        draw_changed_chars(display, date, shown_date, DATE_Y, TEXT_COLOR)
        shown_date = date


display = config.init_display()

if SYNC_WITH_WIFI:
    import wifi_time
    display.fill(BLACK)
    config.centered_text(display, config.BIG_FONT, "Setting clock", 130)
    if not wifi_time.sync_time(display):
        time.sleep(3)   # keep going on whatever time the RTC has

display.fill(BLACK)

while True:
    t = time.localtime()
    if t[5] != shown_second:
        update_face(display, t)
        if SYNC_WITH_WIFI and t[3:6] == (RESYNC_HOUR, 0, 0):
            # Status goes to the shell only, not over the face.
            wifi_time.sync_time()
    time.sleep_ms(20)
