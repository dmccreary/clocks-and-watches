# Lab 13: Digital Clock Face
# Big seven-segment digits you can read from across the room, the date
# below them, and 60 ticks around the edge of the screen that light up
# one by one as the seconds pass. Copy it to the Pico as main.py to make
# it the clock.
#
# THE RULE FOR THIS FACE: ONLY SEND THE PIXELS THAT CHANGE. There is no
# frame buffer on this display, so anything you clear and redraw blinks.
# Lab 09 cleared a whole digit and drew it again every time it changed.
# This face never clears anything after the first frame:
#
#   - A digit is seven segments, plus the six corners and joints where
#     segments meet, each one either lit or unlit. When the time goes
#     from 12:59 to 1:00, the face works out which pieces switched on or
#     off, and repaints only those. A piece that is lit in both digits is
#     not touched at all.
#   - Unlit segments are not black. They are painted a faint "ghost"
#     color, like the unlit segments on a real LCD clock, so turning a
#     segment off is just repainting it -- never erasing it.
#   - Each second lights exactly one more tick on the edge of the screen.
#     At the top of the minute, the ticks that were lit go dark again.
#   - The date is padded with spaces to a fixed width, so every character
#     has a fixed spot. When the date changes, only the characters that
#     differ are repainted -- "Fri, Sep 25" to "Sat, Sep 26" redraws
#     four of them.
#
# In a normal second this face sends two small colon squares and one
# seconds tick -- fewer than 100 pixels out of the 20,480 on the screen.

NAME = "13-digital-clock-face.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config

# Set the RTC from the internet at power-up and again every night.
# Needs secrets.py (see lab 10).
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
# and so on up to bit 6 for g. It is the same information as the DIGITS
# table of segment letters in lab 09, packed into one number per digit
# -- which makes "which segments changed?" a single XOR: old ^ new has
# a 1 bit for every segment that switched.
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

DIGIT_WIDTH = 29
DIGIT_HEIGHT = 57
SEG = 5                 # segment thickness
HALF = (DIGIT_HEIGHT - 3 * SEG) // 2     # 21 -- length of a vertical segment
BOTTOM = 2 * SEG + 2 * HALF              # 52 -- top of the bottom row
MIDDLE = SEG + HALF                      # 26 -- top of the middle row
RIGHT = DIGIT_WIDTH - SEG                # 24 -- left edge of the right column

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
# The row is 119 pixels wide, or 143 with four full digits -- which only
# just fits between the ticks on the left and right edges.
DIGIT_SPACING = 5       # between the two hour digits, and the two minutes
COLON_SPACING = 6       # on each side of the colon
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

# Top to bottom: AM or PM, the digits, the date. The seconds ticks use
# the outer 6 pixels of the screen, so everything else stays at least 7
# pixels in from every edge.
AMPM_Y = 12
DIGIT_TOP = 34
DATE_Y = 98
COLON_DOTS_Y = (DIGIT_TOP + DIGIT_HEIGHT // 3 - SEG // 2,
                DIGIT_TOP + 2 * DIGIT_HEIGHT // 3 - SEG // 2)
DATE_CHARS = 17          # "Wed, Sep 30, 2026" -- the longest date there is

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# ---------------------------------------------------------------------
# Seconds ticks
# ---------------------------------------------------------------------
# A round watch has a ring of 60 ticks around its rim. This screen is a
# rectangle, so the ring is bent to fit it: the ticks sit along the four
# edges, evenly spaced, starting at the middle of the top and running
# clockwise. Tick 15 lands at the middle of the right side, 30 at the
# bottom and 45 on the left -- the same places as 3, 6 and 9 o'clock.
TICK_LENGTH = 5          # along the edge
TICK_DEPTH = 3           # in from the edge
TICK_DEPTH_FIVE = 6      # every fifth tick reaches further in

# How far it is around the edge from the middle of the top, clockwise,
# to each corner. All the way around is 2 * (160 + 128) = 576 pixels.
TOP_RIGHT = config.WIDTH // 2                # 80
BOTTOM_RIGHT = TOP_RIGHT + config.HEIGHT     # 208
BOTTOM_LEFT = BOTTOM_RIGHT + config.WIDTH    # 368
TOP_LEFT = BOTTOM_LEFT + config.HEIGHT       # 496
ALL_AROUND = TOP_LEFT + config.WIDTH // 2    # 576


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


def tick_rect(second):
    """Work out the rectangle (x, y, width, height) of one seconds tick.
    Walk `d` pixels around the edge from the middle of the top, see which
    side of the screen that lands on, and center the tick there."""
    d = second * ALL_AROUND // 60
    deep = TICK_DEPTH_FIVE if second % 5 == 0 else TICK_DEPTH
    half_length = TICK_LENGTH // 2
    if d < TOP_RIGHT:                   # along the top, right of the middle
        x, y = config.CENTER_X + d - half_length, 0
        w, h = TICK_LENGTH, deep
    elif d < BOTTOM_RIGHT:              # down the right side
        x, y = config.WIDTH - deep, d - TOP_RIGHT - half_length
        w, h = deep, TICK_LENGTH
    elif d < BOTTOM_LEFT:               # back along the bottom
        x = config.WIDTH - (d - BOTTOM_RIGHT) - half_length
        y = config.HEIGHT - deep
        w, h = TICK_LENGTH, deep
    elif d < TOP_LEFT:                  # up the left side
        x, y = 0, config.HEIGHT - (d - BOTTOM_LEFT) - half_length
        w, h = deep, TICK_LENGTH
    else:                               # along the top, left of the middle
        x, y = d - TOP_LEFT - half_length, 0
        w, h = TICK_LENGTH, deep
    return x, y, w, h


# EACH TICK IS ONE RECTANGLE. The ticks on a round watch all point at the
# center, each at its own angle, and working out the pixels of a slanted
# shape takes sines, cosines, and a lot of short lines. The edges of this
# screen are straight, so a tick here is just a little rectangle 5 pixels
# long and 3 or 6 deep: one fill_rect(), 15 or 30 pixels. The rectangles
# never change, so work them all out here, once, at startup.
TICKS = [tick_rect(second) for second in range(60)]


def draw_tick(display, second, lit):
    """Paint one seconds tick, lit or unlit. Both use exactly the same
    pixels, so switching a tick only ever repaints its own pixels."""
    x, y, w, h = TICKS[second]
    display.fill_rect(x, y, w, h, ACCENT if lit else TICK_OFF)


def update_ticks(display, second, last):
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

    update_ticks(display, second, shown_second)
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
    config.centered_text(display, config.SMALL_FONT, "Setting clock", 24)
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
