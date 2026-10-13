# mode_weather.py -- the weather clock of lab 14, as a mode for
# 17-main-template.py. Lab 14 explains the forecast, the icons, and why
# each icon is drawn in a small frame buffer first.
#
# New here: stop() hands back the last forecast, and start() gets it
# again the next time this mode is shown. If it is less than
# FORECAST_MINUTES old and from today, it is used as it is -- no waiting
# for WiFi every time you turn the knob past the weather.
#
# Every mode has the same four functions -- see 17-main-template.py. A
# mode only gets rows 0 to 119 of the screen, because the mode dots go
# below, so the digits are 2 rows shorter than lab 14's and the rows
# under them sit closer together.

import time

import framebuf

import config
import forecast
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

# Layout: lab 14's, moved up to end at row 119.
MODE_ROWS = 120         # rows 0 to 119
DIGIT_W, DIGIT_H, DIGIT_T = 20, 32, 4
PAIR_GAP = 5
COLON_GAP = 5
DIGIT_TOP = 1
COLON_DOTS_Y = (DIGIT_TOP + 9, DIGIT_TOP + DIGIT_H - 9 - DIGIT_T)
AMPM_Y = DIGIT_TOP + DIGIT_H - 12
DATE_Y = 37
DIVIDER_Y = 54
COLUMN_X = (40, 120)
LABEL_Y = 56
ICON_SIZE = 32
ICON_Y = 72
HIGH_Y = ICON_Y
LOW_Y = ICON_Y + 16
DESC_Y = 104
DESC_CHARS = 9
ICON_X_FROM_CENTER = -32
TEMP_X_FROM_CENTER = 14
DEGREE_X_FROM_CENTER = 26

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# ---------------------------------------------------------------------
# Weather icons, drawn in a 32 x 32 frame buffer, then sent in one blit
# ---------------------------------------------------------------------
def swapped(color):
    """framebuf stores RGB565 low byte first; the display wants high byte
    first."""
    return ((color & 0xFF) << 8) | (color >> 8)


def draw_sun(canvas, cx, cy, radius, ray_length):
    color = swapped(SUN_COLOR)
    canvas.ellipse(cx, cy, radius, radius, color, True)
    near = radius + 3
    far = near + ray_length - 1
    canvas.fill_rect(cx - 1, cy - far, 3, ray_length, color)
    canvas.fill_rect(cx - 1, cy + near, 3, ray_length, color)
    canvas.fill_rect(cx - far, cy - 1, ray_length, 3, color)
    canvas.fill_rect(cx + near, cy - 1, ray_length, 3, color)
    near = round(near * 0.7)
    far = round(far * 0.7)
    for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1)):
        x0, y0 = cx + sx * near, cy + sy * near
        x1, y1 = cx + sx * far, cy + sy * far
        canvas.line(x0, y0, x1, y1, color)
        canvas.line(x0 + sx, y0, x1, y1 - sy, color)
        canvas.line(x0, y0 + sy, x1 - sx, y1, color)


def draw_cloud(canvas, left, bottom, color):
    c = swapped(color)
    canvas.ellipse(left + 6, bottom - 6, 6, 6, c, True)
    canvas.ellipse(left + 14, bottom - 10, 8, 8, c, True)
    canvas.ellipse(left + 21, bottom - 6, 6, 6, c, True)
    canvas.fill_rect(left + 6, bottom - 6, 16, 7, c)


def draw_snowflake(canvas, x, y, color):
    canvas.hline(x - 3, y, 7, color)
    canvas.vline(x, y - 3, 7, color)
    canvas.line(x - 2, y - 2, x + 2, y + 2, color)
    canvas.line(x - 2, y + 2, x + 2, y - 2, color)


def render_icon(icon):
    canvas = icon_canvas
    canvas.fill(0)
    if icon == forecast.SUNNY:
        draw_sun(canvas, 16, 16, 7, 5)
    elif icon == forecast.PARTLY_CLOUDY:
        draw_sun(canvas, 11, 11, 5, 4)
        draw_cloud(canvas, 4, 29, CLOUD_COLOR)
    elif icon == forecast.CLOUDY:
        draw_cloud(canvas, 2, 25, CLOUD_COLOR)
    elif icon == forecast.RAIN:
        draw_cloud(canvas, 2, 18, DARK_CLOUD_COLOR)
        drop = swapped(RAIN_COLOR)
        for x in (6, 13, 20, 27):
            canvas.line(x, 21, x - 3, 30, drop)
            canvas.line(x + 1, 21, x - 2, 30, drop)
    elif icon == forecast.SNOW:
        draw_cloud(canvas, 2, 18, DARK_CLOUD_COLOR)
        flake = swapped(SNOW_COLOR)
        for x, y in ((7, 24), (16, 28), (25, 24)):
            draw_snowflake(canvas, x, y, flake)


def draw_degree_sign(x, y, color):
    _display.hline(x + 1, y, 2, color)
    _display.hline(x + 1, y + 3, 2, color)
    _display.vline(x, y + 1, 2, color)
    _display.vline(x + 3, y + 1, 2, color)


# ---------------------------------------------------------------------
# The mode
# ---------------------------------------------------------------------
def start(display, k0, push, saved):
    global _display, digits, colon_x, ampm, date_line
    global icon_buffer, icon_canvas, columns, shown_icons
    global days, fetched_at, fetched_day, fetch_now, forecast_due
    global shown_second, shown_colon
    _display = display
    display.fill_rect(0, 0, config.WIDTH, MODE_ROWS, BLACK)

    # Time: the same row of digits as lab 14, AM/PM just to the right.
    first_width = DIGIT_T if TWELVE_HOUR else DIGIT_W
    ampm_width = PAIR_GAP + 2 * SMALL.WIDTH if TWELVE_HOUR else 0
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
    ampm = TextLine(display, SMALL, x + SMALL.WIDTH, AMPM_Y, 2, ACCENT)
    date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 17,
                         TEXT_COLOR)

    # The forecast columns: the parts that never change...
    display.hline(8, DIVIDER_Y, config.WIDTH - 16, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 6,
                  DESC_Y + SMALL.HEIGHT - DIVIDER_Y - 6, LINE_COLOR)
    columns = []
    for column, label in enumerate(("Today", "Tomorrow")):
        cx = COLUMN_X[column]
        display.text(SMALL, label, cx - len(label) * SMALL.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, BLACK)
        draw_degree_sign(cx + DEGREE_X_FROM_CENTER, HIGH_Y + 2, HIGH_COLOR)
        draw_degree_sign(cx + DEGREE_X_FROM_CENTER, LOW_Y + 2, LOW_COLOR)
        # ...and the parts that do: each temperature is a 3-character
        # field, right-aligned, so a new number covers the old one.
        columns.append((TextLine(display, SMALL, cx + TEMP_X_FROM_CENTER,
                                 HIGH_Y, 3, HIGH_COLOR),
                        TextLine(display, SMALL, cx + TEMP_X_FROM_CENTER,
                                 LOW_Y, 3, LOW_COLOR),
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
                                 COLUMN_X[column] + ICON_X_FROM_CENTER,
                                 ICON_Y, ICON_SIZE, ICON_SIZE)
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
            for y in COLON_DOTS_Y:
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
