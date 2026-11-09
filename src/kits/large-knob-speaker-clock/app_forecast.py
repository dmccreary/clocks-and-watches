# app_forecast.py -- lab 13's weather clock, as a mode for 20-mode-main.py.
#
#   K0 (short press) or PUSH   get the weather again now
#
# The time, the weather now, and today's and tomorrow's forecast from
# Open-Meteo -- read lab 13 and forecast.py for how it is fetched. It is
# fetched again when it is more than REFRESH_MINUTES old, but only while
# this mode is on the screen.
#
# stop() keeps the last download, so coming back here shows it straight
# away instead of joining WiFi again. See 20-mode-main.py for the three
# functions every mode has.

import time

import config
import forecast
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine

REFRESH_MINUTES = 30
RETRY_MINUTES = 5

DATE_COLOR = config.YELLOW
NOW_COLOR = config.WHITE
LABEL_COLOR = config.color565(170, 170, 170)
LINE_COLOR = config.color565(60, 60, 70)
HIGH_COLOR = config.color565(255, 150, 40)
LOW_COLOR = config.color565(90, 170, 255)
WORDS_COLOR = config.YELLOW
DIM = config.color565(110, 110, 110)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT
TINY = config.TINY_FONT

# Lab 13's layout.
SIZE = (52, 84, 10)
DIGIT_TOP = 4
DATE_Y = DIGIT_TOP + SIZE[1] + 4          # 92
NOW_Y = DATE_Y + SMALL.HEIGHT + 4         # 112
DIVIDER_Y = NOW_Y + BIG.HEIGHT + 6        # 150
LABEL_Y = DIVIDER_Y + 4                   # 154
TEMPS_Y = LABEL_Y + SMALL.HEIGHT + 2      # 172
WORDS_Y = TEMPS_Y + BIG.HEIGHT + 2        # 206
STATUS_Y = config.HEIGHT - TINY.HEIGHT - 3   # 229
COLUMN_X = (80, 240)


def start(display, k0, push, knob, saved):
    global _k0, _push, row, date_line, now_line, status, columns
    global weather, weather_at, last_try, shown_second, fetch_due
    _k0 = k0
    _push = push
    display.fill(config.BLACK)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 20,
                         DATE_COLOR)
    now_line = TextLine(display, BIG, config.CENTER_X, NOW_Y, 14, NOW_COLOR)
    status = TextLine(display, TINY, config.CENTER_X, STATUS_Y, 38, DIM)
    display.hline(16, DIVIDER_Y, config.WIDTH - 32, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 6,
                  WORDS_Y + SMALL.HEIGHT - DIVIDER_Y - 6, LINE_COLOR)
    columns = []
    for cx, label in zip(COLUMN_X, ("Today", "Tomorrow")):
        display.text(SMALL, label, cx - len(label) * SMALL.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, config.BLACK)
        display.text(SMALL, "/", cx - SMALL.WIDTH // 2, TEMPS_Y + 8,
                     LABEL_COLOR, config.BLACK)
        columns.append((TextLine(display, BIG, cx - 28, TEMPS_Y, 3,
                                 HIGH_COLOR),
                        TextLine(display, BIG, cx + 28, TEMPS_Y, 3,
                                 LOW_COLOR),
                        TextLine(display, SMALL, cx, WORDS_Y, 9,
                                 WORDS_COLOR)))
    if saved is None:
        weather, weather_at, last_try = None, 0, None
    else:
        weather = saved["weather"]
        weather_at = saved["weather_at"]
        last_try = saved["last_try"]
    shown_second = None
    show_weather()
    show_status()
    age = minutes_old()
    # Fetch on the first update(), once the screen is drawn.
    fetch_due = age is None or age >= REFRESH_MINUTES


def minutes_old():
    if weather is None:
        return None
    return time.ticks_diff(time.ticks_ms(), weather_at) // 60_000


def show_weather():
    unit = forecast.unit_letter()
    if weather is None:
        now_line.show("no weather", DIM)
        for high, low, words in columns:
            high.show(" --")
            low.show("-- ")
            words.show("")
        return
    now_line.show("{}{} {}".format(weather["temp"], unit,
                                   forecast.describe(weather["code"])[1]),
                  NOW_COLOR)
    for (high, low, words), day in zip(columns, weather["days"]):
        high.show("%3d" % day[0])
        low.show("%-3d" % day[1])
        words.show(forecast.describe(day[2])[1])


def show_status():
    age = minutes_old()
    if age is None:
        status.show("no weather yet -- is the WiFi on?")
    elif age == 0:
        status.show("updated just now")
    else:
        status.show("updated {} min ago   PUSH: now".format(age))


def get_weather():
    global weather, weather_at, last_try
    last_try = time.ticks_ms()
    status.show("getting the weather ...")
    new = forecast.fetch_now()
    if new is not None:
        weather = new
        weather_at = time.ticks_ms()
    show_weather()
    show_status()


def update(now):
    global shown_second, fetch_due
    if _k0.pressed(now) or _push.pressed(now) or fetch_due:
        fetch_due = False
        get_weather()

    t = time.localtime()
    if t[5] != shown_second:
        shown_second = t[5]
        hour, minute, second = t[3], t[4], t[5]
        row.show(hour, minute, colon=second % 2 == 0)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        date_line.show(text)

        if second == 0:
            show_status()
            age = minutes_old()
            stale = age is None or age >= REFRESH_MINUTES
            waited = (last_try is None or time.ticks_diff(
                now, last_try) >= RETRY_MINUTES * 60_000)
            if stale and waited:
                get_weather()


def stop():
    """Keep the weather, so coming back does not fetch it again."""
    return {"weather": weather, "weather_at": weather_at,
            "last_try": last_try}
