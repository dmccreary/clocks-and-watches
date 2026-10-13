# Lab 14: Weather Clock
# The time and date at the top, and below them today's and tomorrow's
# forecast: an icon, the high and low temperatures, and a word or two.
# The forecast comes from the internet every half hour (see forecast.py).
# Copy it to the Pico as main.py to make it the clock.
#
# The digits are lab 13's seven-segment digits, smaller. They are not
# built here again: Digit, in lib/watchparts.py, is lab 13's digit
# packaged for any face to use, and TextLine does the same job for a line
# of text. Both follow lab 13's rule: only send the pixels that change.
#
# The weather icons are the new idea here. Each one is built from
# circles, rectangles, and lines -- and while it is being built it would
# flicker if drawn straight to the glass. So each icon is drawn in RAM
# first, in a 32 x 32 frame buffer (2 KB), using MicroPython's framebuf
# module, and then sent to the display in one blit_buffer() call. The
# screen goes straight from the old icon to the new one.
#
# One catch: framebuf stores each RGB565 pixel low byte first, and the
# ST7735S wants the high byte first. So every color drawn into the frame
# buffer goes through swapped() first. Forget it, and the yellow sun
# comes out blue.
#
# Getting the forecast takes a second or two, and the clock stands still
# while it does -- the time catches up when it finishes.

NAME = "14-weather-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import framebuf

import config
import forecast
import wifi_time
from watchparts import Digit, TextLine, DIGITS, BLANK

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

# ---------------------------------------------------------------------
# Layout, top to bottom
# ---------------------------------------------------------------------
DIGIT_WIDTH = 20
DIGIT_HEIGHT = 34        # must be 3 * SEG plus an even number
SEG = 4                  # segment thickness
DIGIT_SPACING = 5
COLON_SPACING = 5
DIGIT_TOP = 2
COLON_DOTS_Y = (DIGIT_TOP + 9, DIGIT_TOP + DIGIT_HEIGHT - 9 - SEG)
# A capital letter's foot is 12 rows below the top of its row of text,
# so this stands AM and PM on the same line as the digits.
AMPM_Y = DIGIT_TOP + DIGIT_HEIGHT - 12
DATE_Y = 40
DATE_CHARS = 17          # "Wed, Sep 30, 2026"

DIVIDER_Y = 57
COLUMN_X = (40, 120)     # centers of the Today and Tomorrow columns
LABEL_Y = 60
ICON_SIZE = 32
ICON_Y = 77
HIGH_Y = ICON_Y          # the high goes beside the icon's top half,
LOW_Y = ICON_Y + 16      # the low beside its bottom half
DESC_Y = 110
DESC_CHARS = 9           # "Pt cloudy", the longest description

# Across a column, measured from its center: the icon, then the two
# temperatures. Each temperature is a 3-character field, right-aligned
# ("%3d" turns 7 into "  7"), with its degree sign at a fixed spot after
# it. Because the field never changes width, a new number always exactly
# covers the old one and the degree sign never has to move.
ICON_X_FROM_CENTER = -32     # the icon's left edge
TEMP_X_FROM_CENTER = 14      # the middle of the 24 px field
DEGREE_X_FROM_CENTER = 26    # the degree sign's left edge

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

display = config.init_display()


# ---------------------------------------------------------------------
# Time and date
# ---------------------------------------------------------------------
def new_digit(x, half=False):
    """One of lab 13's digits, from lib/watchparts.py, with its left
    edge at x."""
    return Digit(display, x, DIGIT_TOP, DIGIT_WIDTH, DIGIT_HEIGHT, SEG,
                 DIGIT_COLOR, GHOST, half)


# Left to right: hour tens, hour ones, the colon, minute tens, minute
# ones, then AM or PM. A 12-hour clock's hour tens is only ever 1 or
# blank: a half digit, one segment wide.
first_width = SEG if TWELVE_HOUR else DIGIT_WIDTH
ampm_width = DIGIT_SPACING + 2 * SMALL.WIDTH if TWELVE_HOUR else 0
row_width = (first_width + 3 * DIGIT_WIDTH + 2 * DIGIT_SPACING
             + 2 * COLON_SPACING + SEG)
x = (config.WIDTH - row_width - ampm_width) // 2
digits = [new_digit(x, TWELVE_HOUR)]
x += first_width + DIGIT_SPACING
digits.append(new_digit(x))
x += DIGIT_WIDTH + COLON_SPACING
COLON_X = x
x += SEG + COLON_SPACING
digits.append(new_digit(x))
x += DIGIT_WIDTH + DIGIT_SPACING
digits.append(new_digit(x))
x += DIGIT_WIDTH + DIGIT_SPACING
ampm = TextLine(display, SMALL, x + SMALL.WIDTH, AMPM_Y, 2, ACCENT)
date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, DATE_CHARS,
                     TEXT_COLOR)

shown_second = None
shown_colon = None


def update_face(t):
    """Bring the time and date up to date. Every part repaints only what
    changed, so in most seconds nothing is sent but the colon."""
    global shown_second, shown_colon
    year, month, day, hour, minute, second, weekday = t[:7]
    shown_second = second

    shown_hour = (hour % 12 or 12) if TWELVE_HOUR else hour
    tens = shown_hour // 10
    first = DIGITS[tens] if (tens or not TWELVE_HOUR) else BLANK
    for digit, pattern in zip(digits, (first, DIGITS[shown_hour % 10],
                                       DIGITS[minute // 10],
                                       DIGITS[minute % 10])):
        digit.show(pattern)

    colon = (second % 2 == 0) if BLINK_COLON else True
    if colon != shown_colon:
        for y in COLON_DOTS_Y:
            display.fill_rect(COLON_X, y, SEG, SEG,
                              DIGIT_COLOR if colon else GHOST)
        shown_colon = colon

    if TWELVE_HOUR:
        ampm.show("AM" if hour < 12 else "PM")
    date_line.show("%s, %s %d, %d" % (DAYS[weekday], MONTHS[month - 1],
                                      day, year))


# ---------------------------------------------------------------------
# Weather icons, drawn off-screen in a 32 x 32 frame buffer
# ---------------------------------------------------------------------
icon_buffer = bytearray(ICON_SIZE * ICON_SIZE * 2)
icon_canvas = framebuf.FrameBuffer(icon_buffer, ICON_SIZE, ICON_SIZE,
                                   framebuf.RGB565)


def swapped(color):
    """framebuf keeps each pixel's two bytes low byte first; the display
    wants high byte first. Swapping them in the color fixes it."""
    return ((color & 0xFF) << 8) | (color >> 8)


def draw_sun(cx, cy, radius, ray_length):
    """A filled circle with eight rays, each ray 3 px wide."""
    color = swapped(SUN_COLOR)
    icon_canvas.ellipse(cx, cy, radius, radius, color, True)
    near = radius + 3                 # where a ray starts...
    far = near + ray_length - 1       # ...and where it ends
    # The rays that point up, down, left, and right are rectangles.
    icon_canvas.fill_rect(cx - 1, cy - far, 3, ray_length, color)
    icon_canvas.fill_rect(cx - 1, cy + near, 3, ray_length, color)
    icon_canvas.fill_rect(cx - far, cy - 1, ray_length, 3, color)
    icon_canvas.fill_rect(cx + near, cy - 1, ray_length, 3, color)
    # A diagonal ray is three lines side by side. To be just as far from
    # the center, it goes 0.7 times as far across and 0.7 times as far
    # up or down.
    near = round(near * 0.7)
    far = round(far * 0.7)
    for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1)):
        x0, y0 = cx + sx * near, cy + sy * near
        x1, y1 = cx + sx * far, cy + sy * far
        icon_canvas.line(x0, y0, x1, y1, color)
        icon_canvas.line(x0 + sx, y0, x1, y1 - sy, color)
        icon_canvas.line(x0, y0 + sy, x1 - sx, y1, color)


def draw_cloud(left, bottom, color):
    """Three puffs on a flat base: 28 px wide, 19 px tall, with its
    bottom-left corner at (left, bottom)."""
    c = swapped(color)
    icon_canvas.ellipse(left + 6, bottom - 6, 6, 6, c, True)
    icon_canvas.ellipse(left + 14, bottom - 10, 8, 8, c, True)
    icon_canvas.ellipse(left + 21, bottom - 6, 6, 6, c, True)
    icon_canvas.fill_rect(left + 6, bottom - 6, 16, 7, c)


def draw_snowflake(x, y, color):
    icon_canvas.hline(x - 3, y, 7, color)
    icon_canvas.vline(x, y - 3, 7, color)
    icon_canvas.line(x - 2, y - 2, x + 2, y + 2, color)
    icon_canvas.line(x - 2, y + 2, x + 2, y - 2, color)


def render_icon(icon):
    """Draw one icon into icon_buffer. None leaves it blank."""
    icon_canvas.fill(0)
    if icon == forecast.SUNNY:
        draw_sun(16, 16, 7, 5)
    elif icon == forecast.PARTLY_CLOUDY:
        draw_sun(11, 11, 5, 4)            # the sun first...
        draw_cloud(4, 29, CLOUD_COLOR)    # ...so the cloud covers part of it
    elif icon == forecast.CLOUDY:
        draw_cloud(2, 25, CLOUD_COLOR)
    elif icon == forecast.RAIN:
        draw_cloud(2, 18, DARK_CLOUD_COLOR)
        drop = swapped(RAIN_COLOR)
        for x in (6, 13, 20, 27):         # slanted raindrops, 2 px wide
            icon_canvas.line(x, 21, x - 3, 30, drop)
            icon_canvas.line(x + 1, 21, x - 2, 30, drop)
    elif icon == forecast.SNOW:
        draw_cloud(2, 18, DARK_CLOUD_COLOR)
        flake = swapped(SNOW_COLOR)
        for x, y in ((7, 24), (16, 28), (25, 24)):
            draw_snowflake(x, y, flake)


# ---------------------------------------------------------------------
# The forecast columns
# ---------------------------------------------------------------------
columns = []            # for each column: its high, its low, and its words
for cx in COLUMN_X:
    columns.append((TextLine(display, SMALL, cx + TEMP_X_FROM_CENTER,
                             HIGH_Y, 3, HIGH_COLOR),
                    TextLine(display, SMALL, cx + TEMP_X_FROM_CENTER,
                             LOW_Y, 3, LOW_COLOR),
                    TextLine(display, SMALL, cx, DESC_Y, DESC_CHARS,
                             TEXT_COLOR)))
shown_icons = [0, 0]    # 0 matches no icon, so the first draw happens


def temp_text(temp):
    return " --" if temp is None else "%3d" % temp


def draw_degree_sign(x, y, color):
    """A ring 4 px across. The font has no degree sign of its own."""
    display.hline(x + 1, y, 2, color)
    display.hline(x + 1, y + 3, 2, color)
    display.vline(x, y + 1, 2, color)
    display.vline(x + 3, y + 1, 2, color)


def draw_static():
    """The parts of the forecast that never change. Drawn once."""
    display.hline(8, DIVIDER_Y, config.WIDTH - 16, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 6,
                  DESC_Y + SMALL.HEIGHT - DIVIDER_Y - 6, LINE_COLOR)
    for column, label in enumerate(("Today", "Tomorrow")):
        cx = COLUMN_X[column]
        display.text(SMALL, label, cx - len(label) * SMALL.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, BLACK)
        # + 2 because the digits start 2 rows down in their row of text.
        draw_degree_sign(cx + DEGREE_X_FROM_CENTER, HIGH_Y + 2, HIGH_COLOR)
        draw_degree_sign(cx + DEGREE_X_FROM_CENTER, LOW_Y + 2, LOW_COLOR)


def update_weather(days):
    """days is forecast.fetch()'s answer, or None before the first one.
    An icon is drawn again only if it changed, and TextLine does the
    same for each character of the numbers and the words."""
    for column in range(2):
        if days is None:
            high = low = icon = None
            words = ""
        else:
            high, low, code = days[column]
            icon, words = forecast.describe(code)
        if icon != shown_icons[column]:
            render_icon(icon)
            display.blit_buffer(icon_buffer,
                                COLUMN_X[column] + ICON_X_FROM_CENTER,
                                ICON_Y, ICON_SIZE, ICON_SIZE)
            shown_icons[column] = icon
        high_line, low_line, words_line = columns[column]
        high_line.show(temp_text(high))
        low_line.show(temp_text(low))
        words_line.show(words)


# ---------------------------------------------------------------------
# Start up, then run
# ---------------------------------------------------------------------
display.fill(BLACK)
config.centered_text(display, SMALL, "Weather clock", 24)

# One WiFi connection does both jobs: the forecast leaves it on, and the
# time sync reuses it and then turns it off.
days = forecast.fetch(display, disconnect=not SYNC_WITH_WIFI)
if SYNC_WITH_WIFI and not wifi_time.sync_time(display):
    time.sleep(3)    # keep going on whatever time the RTC has

display.fill(BLACK)
draw_static()
update_weather(days)
forecast_due = days is None

while True:
    t = time.localtime()
    if t[5] != shown_second:
        update_face(t)
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
                    update_weather(days)

        if SYNC_WITH_WIFI and (hour, minute, second) == (RESYNC_HOUR, 0, 0):
            wifi_time.sync_time()
    time.sleep_ms(20)
