# Lab 13: Weather Forecast Clock
# The time at the top, the temperature and the sky right now under it,
# and two columns at the bottom: today's high, low and weather, and
# tomorrow's. The weather comes from the internet over WiFi, and is
# fetched again every 30 minutes.
#
#   K0 or PUSH    get the weather again now
#
# It needs secrets.py with your WiFi name and password (lab 06), and your
# town's LATITUDE and LONGITUDE in config.py -- it starts out set to
# Minneapolis.
#
# WHERE DOES THE WEATHER COME FROM? Open-Meteo, a free weather service
# that needs no account and no key. forecast.fetch_now() asks it for
# exactly six numbers -- the temperature and weather code now, and a
# high, a low and a code for each of two days -- and it answers with a
# few hundred bytes of JSON. Read forecast.py to see the request.
#
# A "weather code" is a number from the World Meteorological Organization:
# 0 is a clear sky, 3 is overcast, 61 is light rain, 71 is light snow...
# forecast.describe() turns one into a few words for the screen.
#
# The clock stands still for the second or two a download takes, then
# catches up -- the time always comes from the Pico's own clock.

NAME = "13-forecast.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import forecast
import wifi_time
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine, Button

REFRESH_MINUTES = 30     # how old the weather may get
RETRY_MINUTES = 5        # how long to wait after a failed download

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

# ---------------------------------------------------------------------
# Layout, top to bottom. A digit's height must be 3 x its thickness plus
# an even number.
# ---------------------------------------------------------------------
SIZE = (52, 84, 10)      # digit width, height, thickness
DIGIT_TOP = 4
DATE_Y = DIGIT_TOP + SIZE[1] + 4          # 92
NOW_Y = DATE_Y + SMALL.HEIGHT + 4         # 112
DIVIDER_Y = NOW_Y + BIG.HEIGHT + 6        # 150
LABEL_Y = DIVIDER_Y + 4                   # 154
TEMPS_Y = LABEL_Y + SMALL.HEIGHT + 2      # 172
WORDS_Y = TEMPS_Y + BIG.HEIGHT + 2        # 206
STATUS_Y = config.HEIGHT - TINY.HEIGHT - 3   # 229
COLUMN_X = (80, 240)     # the middle of each column

# ---------------------------------------------------------------------
# Set the clock if nobody has, then draw the parts that never change
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(config.BLACK)
a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
push_button = Button(push)

if time.localtime()[0] < 2025:
    print("The clock is not set -- setting it over WiFi.")
    wifi_time.sync_time(display)
    display.fill(config.BLACK)

row = TimeRow(display, SIZE, DIGIT_TOP)
date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 20, DATE_COLOR)
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
    # The high to the left of the slash, the low to the right: three
    # characters each, from cx - 52 to cx + 52.
    columns.append((TextLine(display, BIG, cx - 28, TEMPS_Y, 3, HIGH_COLOR),
                    TextLine(display, BIG, cx + 28, TEMPS_Y, 3, LOW_COLOR),
                    TextLine(display, SMALL, cx, WORDS_Y, 9, WORDS_COLOR)))

# ---------------------------------------------------------------------
# The weather
# ---------------------------------------------------------------------
weather = None           # the last good download, or None
weather_at = 0           # time.ticks_ms() when it came
last_try = None          # time.ticks_ms() of the last attempt


def minutes_old():
    """How old the weather is, in minutes, or None if there is none."""
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
    """Download the weather now. Keeps the old weather if it fails."""
    global weather, weather_at, last_try
    last_try = time.ticks_ms()
    status.show("getting the weather ...")
    new = forecast.fetch_now()
    if new is not None:
        weather = new
        weather_at = time.ticks_ms()
    show_weather()
    show_status()


show_weather()
get_weather()
shown_second = None

while True:
    now = time.ticks_ms()
    if k0_button.pressed(now) or push_button.pressed(now):
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

    time.sleep_ms(20)
