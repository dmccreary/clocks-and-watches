# mode_weather.py -- the weather clock of lab 09, as a mode for
# 12-main-template.py. Lab 09 explains the forecast, the icons, and why
# each icon is drawn in a small frame buffer first.
#
# New here: stop() hands back the last forecast, and start() gets it
# again the next time this mode is shown. If it is less than
# FORECAST_MINUTES old and from today, it is used as it is -- no waiting
# for WiFi every time you press MODE past the weather.
#
# Every mode has the same four functions -- see 12-main-template.py.

import math
import time
from array import array

import framebuf

import config
import forecast
import shapes
from watchparts import Digit, TextLine, DIGITS, BLANK

TWELVE_HOUR = True
BLINK_COLON = True
FORECAST_MINUTES = 30

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

# Layout, the same as lab 09.
DIGIT_W, DIGIT_H, DIGIT_T = 38, 72, 8
PAIR_GAP = 7
COLON_GAP = 8
DIGIT_TOP = 48
DATE_Y = DIGIT_TOP + DIGIT_H + 10
DIVIDER_Y = 158
COLUMN_X = (120, 240)
LABEL_Y = 168
ICON_SIZE = 64
ICON_Y = 188
TEMP_Y = 258
DESC_Y = 296
DESC_CHARS = 9

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# ---------------------------------------------------------------------
# Weather icons, drawn in a 64 x 64 frame buffer, then sent in one blit
# ---------------------------------------------------------------------
def swapped(color):
    """framebuf stores RGB565 low byte first; the display wants high byte
    first."""
    return ((color & 0xFF) << 8) | (color >> 8)


def draw_sun(canvas, cx, cy, radius, ray_length):
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
        canvas.poly(0, 0, array('h', corners), color, True)
    canvas.ellipse(cx, cy, radius, radius, color, True)


def draw_cloud(canvas, left, bottom, color):
    c = swapped(color)
    canvas.ellipse(left + 10, bottom - 10, 10, 10, c, True)
    canvas.ellipse(left + 24, bottom - 18, 14, 14, c, True)
    canvas.ellipse(left + 36, bottom - 10, 10, 10, c, True)
    canvas.fill_rect(left + 10, bottom - 10, 27, 11, c)


def draw_snowflake(canvas, x, y, color):
    canvas.hline(x - 4, y, 9, color)
    canvas.vline(x, y - 4, 9, color)
    canvas.line(x - 3, y - 3, x + 3, y + 3, color)
    canvas.line(x - 3, y + 3, x + 3, y - 3, color)


def render_icon(icon):
    canvas = icon_canvas
    canvas.fill(0)
    if icon == forecast.SUNNY:
        draw_sun(canvas, 32, 32, 12, 9)
    elif icon == forecast.PARTLY_CLOUDY:
        draw_sun(canvas, 23, 23, 9, 6)
        draw_cloud(canvas, 15, 55, CLOUD_COLOR)
    elif icon == forecast.CLOUDY:
        draw_cloud(canvas, 9, 48, CLOUD_COLOR)
    elif icon == forecast.RAIN:
        draw_cloud(canvas, 9, 40, DARK_CLOUD_COLOR)
        drop = swapped(RAIN_COLOR)
        for x in (18, 29, 40, 51):
            canvas.line(x, 46, x - 5, 60, drop)
            canvas.line(x + 1, 46, x - 4, 60, drop)
    elif icon == forecast.SNOW:
        draw_cloud(canvas, 9, 40, DARK_CLOUD_COLOR)
        flake = swapped(SNOW_COLOR)
        for x, y in ((17, 50), (32, 57), (47, 50)):
            draw_snowflake(canvas, x, y, flake)


# ---------------------------------------------------------------------
# The mode
# ---------------------------------------------------------------------
def start(display, up, down, saved):
    global _display, digits, colon_x, colon_y, ampm, date_line
    global icon_buffer, icon_canvas, columns, shown_icons
    global days, fetched_at, fetched_day, fetch_now, forecast_due
    global shown_second, shown_colon
    _display = display
    display.fill(BLACK)

    # Time: the same row of digits as lab 09, AM/PM just to the right.
    first_width = DIGIT_T if TWELVE_HOUR else DIGIT_W
    ampm_width = 6 + 2 * SMALL.WIDTH if TWELVE_HOUR else 0
    row = first_width + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
    x = (config.WIDTH - row - ampm_width) // 2
    digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                    DIGIT_COLOR, GHOST, half=TWELVE_HOUR)]
    x += first_width + PAIR_GAP
    digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                        DIGIT_COLOR, GHOST))
    x += DIGIT_W + COLON_GAP
    colon_x = x
    x += DIGIT_T + COLON_GAP
    for _ in range(2):
        digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                            DIGIT_COLOR, GHOST))
        x += DIGIT_W + PAIR_GAP
    colon_y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
               DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)
    ampm = TextLine(display, SMALL, x - PAIR_GAP + 6 + SMALL.WIDTH,
                    DIGIT_TOP + DIGIT_H - SMALL.HEIGHT, 2, ACCENT)
    date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 17,
                         TEXT_COLOR)

    # The forecast columns: the parts that never change...
    display.hline(60, DIVIDER_Y, 240, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 8,
                  DESC_Y + SMALL.HEIGHT - DIVIDER_Y - 8, LINE_COLOR)
    columns = []
    for column, label in enumerate(("Today", "Tomorrow")):
        cx = COLUMN_X[column]
        display.text(SMALL, label, cx - len(label) * SMALL.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, BLACK)
        for x, color in ((cx - 6, HIGH_COLOR), (cx + 54, LOW_COLOR)):
            shapes.circle(display, x, TEMP_Y + 5, 3, color)   # degree signs
            shapes.circle(display, x, TEMP_Y + 5, 2, color)
        # ...and the parts that do: each temperature is a 3-character
        # field, right-aligned, so a new number covers the old one.
        columns.append((TextLine(display, BIG, cx - 34, TEMP_Y, 3, HIGH_COLOR),
                        TextLine(display, BIG, cx + 26, TEMP_Y, 3, LOW_COLOR),
                        TextLine(display, SMALL, cx, DESC_Y, DESC_CHARS,
                                 TEXT_COLOR)))
    icon_buffer = bytearray(ICON_SIZE * ICON_SIZE * 2)
    icon_canvas = framebuf.FrameBuffer(icon_buffer, ICON_SIZE, ICON_SIZE,
                                       framebuf.RGB565)
    shown_icons = [0, 0]      # 0 matches no icon, so the first draw happens

    # Use the forecast from last time if it is still fresh.
    days = None
    fetched_at = 0
    fetched_day = 0
    today = time.localtime()[2]
    if (saved is not None and saved["day"] == today
            and time.ticks_diff(time.ticks_ms(), saved["fetched_at"])
            < FORECAST_MINUTES * 60_000):
        days = saved["days"]
        fetched_at = saved["fetched_at"]
        fetched_day = saved["day"]
    show_weather()
    # Otherwise get one on the first update() -- after the face is drawn,
    # so the screen does not sit black while the WiFi connects.
    fetch_now = days is None
    forecast_due = fetch_now
    shown_second = None
    shown_colon = None


def show_weather():
    for column in range(2):
        high_line, low_line, words_line = columns[column]
        if days is None:
            high = low = None
            icon, words = None, ""
        else:
            high, low, code = days[column]
            icon, words = forecast.describe(code)
        if icon != shown_icons[column]:
            render_icon(icon)
            _display.blit_buffer(icon_buffer,
                                 COLUMN_X[column] - ICON_SIZE // 2, ICON_Y,
                                 ICON_SIZE, ICON_SIZE)
            shown_icons[column] = icon
        high_line.show(" --" if high is None else "%3d" % high)
        low_line.show(" --" if low is None else "%3d" % low)
        words_line.show(words)


def get_forecast():
    """Fetch a forecast. The clock stands still for the second or two
    this takes, then catches up."""
    global days, fetched_at, fetched_day, forecast_due
    new_days = forecast.fetch()
    if new_days is not None:
        days = new_days
        fetched_at = time.ticks_ms()
        fetched_day = time.localtime()[2]
        forecast_due = False
        show_weather()


def update(now):
    global shown_second, shown_colon, fetch_now, forecast_due
    year, month, day, hour, minute, second, weekday = time.localtime()[:7]
    if second != shown_second:
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
            for y in colon_y:
                _display.fill_rect(colon_x, y, DIGIT_T, DIGIT_T,
                                   DIGIT_COLOR if colon else GHOST)
            shown_colon = colon
        if TWELVE_HOUR:
            ampm.show("AM" if hour < 12 else "PM")
        date_line.show("%s, %s %d, %d" % (DAYS[weekday], MONTHS[month - 1],
                                          day, year))

        # At :00:30 and :30:30 get a new forecast (the one after midnight
        # moves Tomorrow to Today). If one fails, retry every 5 minutes.
        if second == 30:
            if minute % FORECAST_MINUTES == 0:
                forecast_due = True
            if forecast_due and minute % 5 == 0:
                get_forecast()

    if fetch_now:
        fetch_now = False
        get_forecast()


def stop():
    """Keep the forecast for the next time this mode is shown."""
    if days is None:
        return None
    return {"days": days, "fetched_at": fetched_at, "day": fetched_day}
