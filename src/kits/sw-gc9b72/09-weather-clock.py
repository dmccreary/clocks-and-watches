# Lab 09: Weather Clock
# The time and date at the top, and below them today's and tomorrow's
# forecast: an icon, the high and low temperatures, and a word or two.
# The forecast comes from the internet every half hour (see forecast.py).
# Copy it to the Pico as main.py to make it the watch.
#
# The digits are the same seven-segment digits as lab 08, just smaller,
# and they follow the same rule: only send the pixels that change.
#
# The weather icons are the new idea here. Each one is built from
# circles, polygons, and lines -- and while it is being built it would
# flicker if drawn straight to the glass. So each icon is drawn in RAM
# first, in a 64 x 64 frame buffer (8 KB), using MicroPython's framebuf
# module, and then sent to the display in one blit_buffer() call. The
# screen goes straight from the old icon to the new one.
#
# One catch: framebuf stores each RGB565 pixel low byte first, and the
# GC9B72 wants the high byte first. So every color drawn into the frame
# buffer goes through swapped() first. Forget it, and red comes out as
# a murky green.
#
# Getting the forecast takes a second or two, and the clock stands still
# while it does -- the seconds catch up when it finishes.

NAME = "09-weather-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time
from array import array

import framebuf

import config
import forecast
import shapes
import wifi_time

# Set the RTC from the internet at power-up and again every night.
SYNC_WITH_WIFI = True
RESYNC_HOUR = 3
FORECAST_MINUTES = 30    # get a new forecast every half hour

TWELVE_HOUR = True       # False for a 24-hour clock
BLINK_COLON = True

BLACK = config.BLACK
DIGIT_COLOR = config.WHITE
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TEXT_COLOR = config.YELLOW
LABEL_COLOR = config.color565(170, 170, 170)
LINE_COLOR = config.color565(60, 60, 70)
HIGH_COLOR = config.color565(255, 150, 40)
LOW_COLOR = config.color565(90, 170, 255)
SUN_COLOR = config.color565(255, 200, 0)
CLOUD_COLOR = config.color565(225, 225, 235)
DARK_CLOUD_COLOR = config.color565(150, 150, 165)
RAIN_COLOR = config.color565(80, 160, 255)
SNOW_COLOR = config.WHITE

SMALL = config.SMALL_FONT
BIG = config.BIG_FONT
TWO_PI = 2 * math.pi

# ---------------------------------------------------------------------
# Seven-segment digits -- lab 08's, at 72 px tall instead of 114
# ---------------------------------------------------------------------
DIGIT_SEGMENTS = (
    0b0111111,  # 0
    0b0000110,  # 1
    0b1011011,  # 2
    0b1001111,  # 3
    0b1100110,  # 4
    0b1101101,  # 5
    0b1111101,  # 6
    0b0000111,  # 7
    0b1111111,  # 8
    0b1101111,  # 9
)
BLANK = 0b0000000
ALL_SEGMENTS = 0b1111111
SEG_A, SEG_B, SEG_C, SEG_D, SEG_E, SEG_F, SEG_G = 1, 2, 4, 8, 16, 32, 64

DIGIT_WIDTH = 38
DIGIT_HEIGHT = 72
SEG = 8
HALF = (DIGIT_HEIGHT - 3 * SEG) // 2     # 24
BOTTOM = 2 * SEG + 2 * HALF
MIDDLE = SEG + HALF
RIGHT = DIGIT_WIDTH - SEG

# Segments a-g, then the six joints where they meet (see lab 08).
PIECES = (
    (SEG, 0, DIGIT_WIDTH - 2 * SEG, SEG),        # a
    (RIGHT, SEG, SEG, HALF),                     # b
    (RIGHT, MIDDLE + SEG, SEG, HALF),            # c
    (SEG, BOTTOM, DIGIT_WIDTH - 2 * SEG, SEG),   # d
    (0, MIDDLE + SEG, SEG, HALF),                # e
    (0, SEG, SEG, HALF),                         # f
    (SEG, MIDDLE, DIGIT_WIDTH - 2 * SEG, SEG),   # g
    (0, 0, SEG, SEG),                            # joint: a f
    (RIGHT, 0, SEG, SEG),                        # joint: a b
    (0, MIDDLE, SEG, SEG),                       # joint: f g e
    (RIGHT, MIDDLE, SEG, SEG),                   # joint: b g c
    (0, BOTTOM, SEG, SEG),                       # joint: e d
    (RIGHT, BOTTOM, SEG, SEG),                   # joint: c d
)
JOINTS = (SEG_A | SEG_F, SEG_A | SEG_B, SEG_F | SEG_G | SEG_E,
          SEG_B | SEG_G | SEG_C, SEG_E | SEG_D, SEG_C | SEG_D)


def pieces(segments):
    """7 segment bits -> 13 piece bits: the segments, then each joint
    that touches a lit segment."""
    bits = segments
    for j in range(6):
        if segments & JOINTS[j]:
            bits |= 1 << (7 + j)
    return bits


# A 12-hour clock's leftmost digit is only ever 1 or blank: a half digit.
if TWELVE_HOUR:
    FIRST_DIGIT_SEGMENTS = SEG_B | SEG_C
    first_width = SEG
    ampm_width = 6 + 2 * SMALL.WIDTH     # AM/PM sits just right of the time
else:
    FIRST_DIGIT_SEGMENTS = ALL_SEGMENTS
    first_width = DIGIT_WIDTH
    ampm_width = 0
DIGIT_PIECES = (pieces(FIRST_DIGIT_SEGMENTS), pieces(ALL_SEGMENTS),
                pieces(ALL_SEGMENTS), pieces(ALL_SEGMENTS))

DIGIT_SPACING = 7
COLON_SPACING = 8
_row_width = (first_width + 3 * DIGIT_WIDTH + 2 * DIGIT_SPACING
              + 2 * COLON_SPACING + SEG)
_x = (config.WIDTH - _row_width - ampm_width) // 2
_first_x = _x - (DIGIT_WIDTH - first_width)
_x += first_width + DIGIT_SPACING
_second_x = _x
_x += DIGIT_WIDTH + COLON_SPACING
COLON_X = _x
_x += SEG + COLON_SPACING
_third_x = _x
_x += DIGIT_WIDTH + DIGIT_SPACING
DIGIT_X = (_first_x, _second_x, _third_x, _x)
AMPM_X = _x + DIGIT_WIDTH + 6

# ---------------------------------------------------------------------
# Layout, top to bottom
# ---------------------------------------------------------------------
DIGIT_TOP = 48
COLON_DOTS_Y = (DIGIT_TOP + DIGIT_HEIGHT // 3 - SEG // 2,
                DIGIT_TOP + 2 * DIGIT_HEIGHT // 3 - SEG // 2)
AMPM_Y = DIGIT_TOP + DIGIT_HEIGHT - SMALL.HEIGHT   # level with the digits' feet
DATE_Y = DIGIT_TOP + DIGIT_HEIGHT + 10
DATE_CHARS = 17

DIVIDER_Y = 158
COLUMN_X = (120, 240)        # centers of the Today and Tomorrow columns
LABEL_Y = 168
ICON_SIZE = 64
ICON_Y = 188
TEMP_Y = 258
DESC_Y = 296
DESC_CHARS = 9               # "Pt cloudy", the longest description

# Each temperature is a 3-character field, right-aligned ("%3d" turns 7
# into "  7"), with its degree sign at a fixed spot after it. Because the
# field never changes width, a new number always exactly covers the old
# one and the degree sign never has to move.
HIGH_X_FROM_CENTER = -58     # high: 48 px field, degree sign at -6
LOW_X_FROM_CENTER = 2        # low: 48 px field, degree sign at +54

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# ---------------------------------------------------------------------
# Time and date
# ---------------------------------------------------------------------
def draw_digit(display, i, new, old):
    """Repaint only the pieces of digit i that changed (see lab 08)."""
    lit = pieces(new)
    changed = DIGIT_PIECES[i] if old is None else lit ^ pieces(old)
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
    if TWELVE_HOUR:
        hour = hour % 12 or 12
    tens = hour // 10
    first = DIGIT_SEGMENTS[tens] if (tens or not TWELVE_HOUR) else BLANK
    return (first, DIGIT_SEGMENTS[hour % 10],
            DIGIT_SEGMENTS[minute // 10], DIGIT_SEGMENTS[minute % 10])


def padded(text, width):
    """Center text in exactly `width` characters, padding with spaces."""
    pad = width - len(text)
    return " " * (pad // 2) + text + " " * (pad - pad // 2)


def draw_changed_chars(display, font, new, old, x, y, color):
    """Draw a line of text, repainting only the characters that differ
    from `old` (None the first time). Both strings are the same length."""
    for i in range(len(new)):
        if old is None or old[i] != new[i]:
            display.text(font, new[i], x + i * font.WIDTH, y, color, BLACK)


# What is on the glass right now. None means "never drawn".
shown_digits = [None, None, None, None]
shown_colon = None
shown_second = None
shown_ampm = None
shown_date = None


def update_face(display, t):
    """Bring the time and date up to date, repainting only what changed."""
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
    shown_second = second

    if TWELVE_HOUR:
        ampm = "AM" if hour < 12 else "PM"
        if ampm != shown_ampm:
            draw_changed_chars(display, SMALL, ampm, shown_ampm,
                               AMPM_X, AMPM_Y, ACCENT)
            shown_ampm = ampm

    date = padded("%s, %s %d, %d" % (DAYS[weekday], MONTHS[month - 1],
                                     day, year), DATE_CHARS)
    if date != shown_date:
        x = (config.WIDTH - DATE_CHARS * SMALL.WIDTH) // 2
        draw_changed_chars(display, SMALL, date, shown_date, x, DATE_Y,
                           TEXT_COLOR)
        shown_date = date


# ---------------------------------------------------------------------
# Weather icons, drawn off-screen in a 64 x 64 frame buffer
# ---------------------------------------------------------------------
icon_buffer = bytearray(ICON_SIZE * ICON_SIZE * 2)
icon_canvas = framebuf.FrameBuffer(icon_buffer, ICON_SIZE, ICON_SIZE,
                                   framebuf.RGB565)


def swapped(color):
    """framebuf keeps each pixel's two bytes low byte first; the display
    wants high byte first. Swapping them in the color fixes it."""
    return ((color & 0xFF) << 8) | (color >> 8)


def draw_sun(cx, cy, radius, ray_length):
    """A filled circle with eight rays, each ray a thin filled polygon."""
    color = swapped(SUN_COLOR)
    for i in range(8):
        angle = i * TWO_PI / 8
        s = math.sin(angle)
        c = math.cos(angle)
        inner = radius + 3
        outer = inner + ray_length
        corners = []
        for along, across in ((inner, -1.5), (outer, -1.5),
                              (outer, 1.5), (inner, 1.5)):
            corners.append(round(cx + along * s + across * c))
            corners.append(round(cy - along * c + across * s))
        icon_canvas.poly(0, 0, array('h', corners), color, True)
    icon_canvas.ellipse(cx, cy, radius, radius, color, True)


def draw_cloud(left, bottom, color):
    """Three puffs on a flat base: 47 px wide, 33 px tall, with its
    bottom-left corner at (left, bottom)."""
    c = swapped(color)
    icon_canvas.ellipse(left + 10, bottom - 10, 10, 10, c, True)
    icon_canvas.ellipse(left + 24, bottom - 18, 14, 14, c, True)
    icon_canvas.ellipse(left + 36, bottom - 10, 10, 10, c, True)
    icon_canvas.fill_rect(left + 10, bottom - 10, 27, 11, c)


def draw_snowflake(x, y, color):
    icon_canvas.hline(x - 4, y, 9, color)
    icon_canvas.vline(x, y - 4, 9, color)
    icon_canvas.line(x - 3, y - 3, x + 3, y + 3, color)
    icon_canvas.line(x - 3, y + 3, x + 3, y - 3, color)


def render_icon(icon):
    """Draw one icon into icon_buffer. None leaves it blank."""
    icon_canvas.fill(0)
    if icon == forecast.SUNNY:
        draw_sun(32, 32, 12, 9)
    elif icon == forecast.PARTLY_CLOUDY:
        draw_sun(23, 23, 9, 6)            # the sun first...
        draw_cloud(15, 55, CLOUD_COLOR)   # ...so the cloud covers part of it
    elif icon == forecast.CLOUDY:
        draw_cloud(9, 48, CLOUD_COLOR)
    elif icon == forecast.RAIN:
        draw_cloud(9, 40, DARK_CLOUD_COLOR)
        drop = swapped(RAIN_COLOR)
        for x in (18, 29, 40, 51):        # slanted raindrops, 2 px wide
            icon_canvas.line(x, 46, x - 5, 60, drop)
            icon_canvas.line(x + 1, 46, x - 4, 60, drop)
    elif icon == forecast.SNOW:
        draw_cloud(9, 40, DARK_CLOUD_COLOR)
        flake = swapped(SNOW_COLOR)
        for x, y in ((17, 50), (32, 57), (47, 50)):
            draw_snowflake(x, y, flake)


# ---------------------------------------------------------------------
# The forecast columns
# ---------------------------------------------------------------------
UNDRAWN = object()      # matches nothing, so the first draw always happens
shown_weather = [[UNDRAWN] * 4, [UNDRAWN] * 4]   # high, low, icon, words


def temp_text(temp):
    return " --" if temp is None else "%3d" % temp


def draw_degree_sign(display, x, y, color):
    shapes.circle(display, x, y, 3, color)
    shapes.circle(display, x, y, 2, color)


def draw_static(display):
    """The parts of the forecast that never change. Drawn once."""
    display.hline(60, DIVIDER_Y, 240, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 8,
                  DESC_Y + SMALL.HEIGHT - DIVIDER_Y - 8, LINE_COLOR)
    for column, label in enumerate(("Today", "Tomorrow")):
        cx = COLUMN_X[column]
        display.text(SMALL, label, cx - len(label) * SMALL.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, BLACK)
        draw_degree_sign(display, cx - 6, TEMP_Y + 5, HIGH_COLOR)
        draw_degree_sign(display, cx + 54, TEMP_Y + 5, LOW_COLOR)


def show_day(display, column, high, low, icon, words):
    """Update one forecast column, repainting only the parts that changed."""
    shown = shown_weather[column]
    cx = COLUMN_X[column]
    if icon != shown[2]:
        render_icon(icon)
        display.blit_buffer(icon_buffer, cx - ICON_SIZE // 2, ICON_Y,
                            ICON_SIZE, ICON_SIZE)
    if high != shown[0]:
        display.text(BIG, temp_text(high), cx + HIGH_X_FROM_CENTER, TEMP_Y,
                     HIGH_COLOR, BLACK)
    if low != shown[1]:
        display.text(BIG, temp_text(low), cx + LOW_X_FROM_CENTER, TEMP_Y,
                     LOW_COLOR, BLACK)
    if words != shown[3]:
        display.text(SMALL, padded(words, DESC_CHARS),
                     cx - DESC_CHARS * SMALL.WIDTH // 2, DESC_Y,
                     TEXT_COLOR, BLACK)
    shown[:] = [high, low, icon, words]


def update_weather(display, days):
    """days is forecast.fetch()'s answer, or None before the first one."""
    for column in range(2):
        if days is None:
            show_day(display, column, None, None, None, "")
        else:
            high, low, code = days[column]
            icon, words = forecast.describe(code)
            show_day(display, column, high, low, icon, words)


# ---------------------------------------------------------------------
# Start up, then run
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)
config.centered_text(display, BIG, "Weather clock", 130)

# One WiFi connection does both jobs: the forecast leaves it on, and the
# time sync reuses it and then turns it off.
days = forecast.fetch(display, disconnect=not SYNC_WITH_WIFI)
if SYNC_WITH_WIFI and not wifi_time.sync_time(display):
    time.sleep(3)    # keep going on whatever time the RTC has

display.fill(BLACK)
draw_static(display)
update_weather(display, days)
forecast_due = days is None

while True:
    t = time.localtime()
    if t[5] != shown_second:
        update_face(display, t)
        hour, minute, second = t[3], t[4], t[5]

        # At :00:30 and :30:30 get a new forecast -- the one just after
        # midnight also moves "Tomorrow" over to "Today". If it fails,
        # keep showing the old one and try again every 5 minutes.
        if second == 30:
            if minute % FORECAST_MINUTES == 0:
                forecast_due = True
            if forecast_due and minute % 5 == 0:
                new_days = forecast.fetch()
                if new_days is not None:
                    days = new_days
                    forecast_due = False
                    update_weather(display, days)

        if SYNC_WITH_WIFI and (hour, minute, second) == (RESYNC_HOUR, 0, 0):
            wifi_time.sync_time()
    time.sleep_ms(20)
