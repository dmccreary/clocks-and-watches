# Hardware configuration for the Big Round Speaker Clock kit: a Raspberry
# Pi Pico W (the original RP2040 board, not the Pico 2 W) wired to a 2.1"
# 360x360 round GC9B72 SPI display, a MAX98357A I2S amplifier driving a
# small speaker, and three push buttons.
#
# This started as a copy of the Study Buddy kit's config.py. The display
# and buttons are on the same pins; the speaker moved to GP9-GP12. The
# design notes are in docs/kits/big-round-speaker-clock/README.md.
#
# Every program in this folder imports this file instead of repeating pin
# numbers, so the whole kit is described in one place.

from machine import Pin, SPI
import gc9b72
from gc9b72 import color565

WIDTH = 360
HEIGHT = 360

# --- Display: GC9B72 on SPI0 ---------------------------------------------
#
#   Module pin    Pico pin
#   ----------    --------
#   SCL / CLK     GP2        SPI0 clock
#   SDA / DIN     GP3        SPI0 data out (MOSI)
#   RST           GP4
#   DC            GP5        data / command
#   CS            GP6        chip select
#   BL            GP7        backlight -- the driver switches it on
#   VCC           3V3
#   GND           GND
#
# If you ever wire BL straight to 3V3 instead, set BL_PIN to None.
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
RST_PIN = 4
DC_PIN = 5
CS_PIN = 6
BL_PIN = 7

# On a Pico W the onboard LED hangs off the CYW43439 wireless chip, not
# GP25, so always use Pin("LED"). GP23, GP24, GP25 and GP29 belong to the
# wireless chip: don't wire anything to them.
LED_PIN = "LED"

# 24 MHz is the fastest SPI clock MicroPython makes from the 48 MHz
# peripheral clock without rounding down to 12 MHz. Print the SPI object
# to see the rate you really got. Step down to 12_000_000 if you see
# speckled pixels on long or messy wires.
BAUDRATE = 24_000_000

# --- Buttons --------------------------------------------------------------
# Each button has its other leg to GND. PULL_UP holds the pin at 1 until
# a press pulls it to 0, so "pressed" reads as 0.
#
#   MODE   GP13
#   UP     GP14
#   DOWN   GP15
BUTTON_MODE_PIN = 13
BUTTON_INCREMENT_PIN = 14
BUTTON_DECREMENT_PIN = 15

# --- Speaker: MAX98357A I2S amplifier -------------------------------------
#
#   Amp pin   Pico pin   What it does
#   -------   --------   ------------
#   BCLK      GP9        "bit clock": one tick for every bit of audio
#   LRC       GP10       "left/right clock": which channel a sample is
#   DIN       GP11       "data in": the audio itself
#   GAIN      GP12       how loud the amp makes it (see GAIN_DB below)
#   SD        --         not connected (the amp stays switched on)
#   VIN, GND  VBUS (5 V) or 3V3, and GND
#
# THE ONE RULE: MicroPython's I2S on the Pico needs LRC on the pin right
# AFTER BCLK. Here BCLK is GP9 and LRC is GP10, so it works. Swap those
# two wires and I2S() raises an error. 02-probe.py checks the rule.
#
# (The MAX98357A is only an amplifier -- it has no microphone.)
I2S_BCLK_PIN = 9
I2S_LRC_PIN = 10
I2S_DIN_PIN = 11
I2S_GAIN_PIN = 12

# The amplifier's GAIN pin has three settings, chosen by what it is wired
# to. It is wired to a Pico pin, so set_gain() picks one in software:
#
#   GAIN_DB   GAIN pin does this     Pico pin is set to
#   -------   --------------------   -----------------------
#      6      tied to the amp's VIN   output, 1   (high)
#      9      left floating           input       (disconnected)
#     12      tied to GND             output, 0   (low)
#
# The "6" setting only makes sense if the amp's VIN is 3.3 V; with a 5 V
# VIN use 9 or 12.
GAIN_DB = 9

# Default loudness, 0 (silent) to 100. Keep it low while testing: a
# speaker an inch from your ear is louder than you expect.
VOLUME = 40

# --- Colors (RGB565) ------------------------------------------------------
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F
GRAY = color565(110, 110, 110)
RAIL_RED = color565(235, 0, 0)      # the railway clock's second hand (lib/mondaine.py)

# Fill flags for shapes.ellipse() / shapes.poly().
NO_FILL = 0
FILL = 1

# --- Round-screen geometry ------------------------------------------------
# The driver addresses a 360x360 square, but only the inscribed circle is
# visible. SAFE_RADIUS is the largest circle you can see all of; it was
# confirmed on the Study Buddy's panel. If your bezel cuts a ring off,
# make it smaller.
CENTER_X = WIDTH // 2       # 180
CENTER_Y = HEIGHT // 2      # 180
RADIUS = WIDTH // 2         # 180
SAFE_RADIUS = 168

# --- Location and time ----------------------------------------------------
# NTP servers only hand out UTC, so the clock needs your time zone.
#   Eastern -5, Central -6, Mountain -7, Pacific -8
TIMEZONE_HOURS = -6
# True to apply US daylight saving time (second Sunday in March to the
# first Sunday in November). False for Arizona, Hawaii, or anywhere that
# does not change its clocks.
USE_US_DST = True

# Where you are, for the weather-clock modes that come later. The city
# name is only for display; the forecast is looked up by latitude and
# longitude. North and east are positive, so the United States has a
# NEGATIVE longitude.
CITY = "Minneapolis"
LATITUDE = 44.98
LONGITUDE = -93.27
TEMPERATURE_UNIT = "fahrenheit"      # or "celsius"

# 12-hour (True) or 24-hour (False) digits on every digital face.
TWELVE_HOUR = True

# Fonts live in lib/ with the driver. The GC9B72 driver has no built-in
# font -- text() takes a font MODULE as its first argument.
import vga1_8x16 as SMALL_FONT       # 8 x 16
import vga1_bold_16x32 as BIG_FONT   # 16 x 32

_backlight = None


def init_display():
    """Start the SPI bus and the GC9B72. Returns the display object."""
    global _backlight
    spi = SPI(SPI_ID, baudrate=BAUDRATE,
              sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
    _backlight = None if BL_PIN is None else Pin(BL_PIN, Pin.OUT)
    return gc9b72.GC9B72(
        spi,
        dc=Pin(DC_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        reset=Pin(RST_PIN, Pin.OUT),
        backlight=_backlight,
        rotation=0)


def set_backlight(on):
    """Turn the backlight on or off (does nothing if BL_PIN is None)."""
    if _backlight is not None:
        _backlight.value(1 if on else 0)


def init_buttons():
    """Set up the three buttons. Returns (mode, up, down) Pins.

    Each pin idles at 1 and reads 0 while its button is held down."""
    mode = Pin(BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
    up = Pin(BUTTON_INCREMENT_PIN, Pin.IN, Pin.PULL_UP)
    down = Pin(BUTTON_DECREMENT_PIN, Pin.IN, Pin.PULL_UP)
    return mode, up, down


def set_gain(db=None):
    """Set the amplifier's GAIN pin for 6, 9, or 12 dB (default GAIN_DB).
    Returns the Pin."""
    db = GAIN_DB if db is None else db
    if db == 9:
        return Pin(I2S_GAIN_PIN, Pin.IN)             # floating
    if db == 12:
        return Pin(I2S_GAIN_PIN, Pin.OUT, value=0)   # tied to GND
    if db == 6:
        return Pin(I2S_GAIN_PIN, Pin.OUT, value=1)   # tied high
    raise ValueError("GAIN_DB must be 6, 9, or 12, not {}".format(db))


def centered_text(display, font, text, y, color=WHITE, background=BLACK):
    """Draw text centered left-to-right on the screen at row y."""
    x = (WIDTH - len(text) * font.WIDTH) // 2
    display.text(font, text, x, y, color, background)
