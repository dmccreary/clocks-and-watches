# Hardware configuration for the mondaine kit: a Raspberry Pi Pico W (or
# Pico 2 W) wired to a 2.1" 360x360 round GC9B72 SPI smartwatch display.
#
# Every lab in this folder imports this file instead of repeating pin
# numbers, so the whole kit only needs to be described in one place. The
# wiring is identical to the sw-gc9b72 (Chrono Smart Clock) kit, so a board
# wired for one runs the other.
#
# The display's silkscreen reads "Driver IC: GC9B72, Resolution: 360x360" --
# the 640x640 figure on some AliExpress listings for this panel is wrong.

from machine import Pin, SPI
import gc9b72
from gc9b72 import color565

WIDTH = 360
HEIGHT = 360

# Pico W / Pico 2 W + bare GC9B72 module, on SPI0.
#
# The 10-pad breakout reads (left to right): GND VCC SCL SDA RST DC CS BL
# SDO TE. Only 8 of those are wired -- SDO (read-back) and TE (frame
# tearing sync) are not used by this driver and left unconnected.
#
#   Module pin   Pico pin   Wire color
#   ----------   --------   ----------
#   SCL / CLK    GP2        orange
#   SDA / MOSI   GP3        yellow
#   RST          GP4        green
#   DC           GP5        blue
#   CS           GP6        purple
#   BL           GP7        gray
#   VCC          3V3        red
#   GND          GND        black
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
RST_PIN = 4
DC_PIN = 5
CS_PIN = 6
BL_PIN = 7

# On a Pico W or Pico 2 W the onboard LED is NOT wired to GP25 the way it
# is on a plain Pico -- it hangs off the wireless chip. MicroPython hides
# that behind the pin name "LED", so always use Pin("LED"), never Pin(25).
#
# GP23, GP24, GP25 and GP29 belong to the wireless chip on these boards.
# Don't wire anything to them.
LED_PIN = "LED"

# 24 MHz is what the sw-gc9b72 kit ships at, confirmed on real hardware
# with 20 cm ribbon cables and no speckling or tearing.
#
# THE NUMBER YOU ASK FOR IS NOT ALWAYS THE NUMBER YOU GET. MicroPython
# divides a fixed peripheral clock down to make the SPI clock, and rounds
# DOWN to the nearest rate it can make. Print the SPI object to see the
# rate you really got:
#
#     from machine import Pin, SPI
#     print(SPI(0, baudrate=24_000_000, sck=Pin(2), mosi=Pin(3)))
#
# If you see speckled pixels or torn frames on long or messy wiring,
# step down to 12_000_000. The sweeping second hand will redraw a little
# slower, but it will still look smooth.
BAUDRATE = 24_000_000

# Three push buttons, each with its other leg to GND. PULL_UP holds the
# pin at 1 until a press pulls it to 0, so "pressed" reads as 0.
#
#   Mode       GP13   step through what the up/down buttons change
#   Increment  GP14   the current setting goes up
#   Decrement  GP15   the current setting goes down
#
# Same pins and names as the other clock kits in this repository.
BUTTON_MODE_PIN = 13
BUTTON_INCREMENT_PIN = 14
BUTTON_DECREMENT_PIN = 15

# RGB565: five bits of red, six of green, five of blue, packed into 16
# bits. color565(red, green, blue) builds any color from three ordinary
# 0-255 values, and it is re-exported above so labs can use config.color565().
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F
GRAY = color565(110, 110, 110)

# The red of the second hand: a traffic-sign red, a little darker than the
# pure RED above, which glows too harshly on a white dial.
RAIL_RED = color565(235, 0, 0)

# Fill flags for shapes.ellipse() / shapes.poly() -- outline vs. solid.
NO_FILL = 0
FILL = 1

# The geometry of a round screen. The driver addresses a 360x360 square,
# but only the circle inscribed in it is visible -- draw in the corners
# and you're spending SPI bytes on pixels under the bezel that no one
# will ever see.
CENTER_X = WIDTH // 2       # 180
CENTER_Y = HEIGHT // 2      # 180
RADIUS = WIDTH // 2         # 180 -- the physical edge of the glass

# The largest circle you can see all of: the glass is 360 px across, but
# the bezel covers the outermost pixels. Confirmed on real hardware with
# the sw-gc9b72 kit's red ring, which sits right at the visible edge at
# 168. If a different panel cuts the ring off, make this smaller.
SAFE_RADIUS = 168

# Local time zone, used when setting the clock from the internet (see
# wifi_time.py). NTP servers only ever hand out UTC.
#   Eastern -5, Central -6, Mountain -7, Pacific -8
TIMEZONE_HOURS = -6
# True to apply US daylight saving time (second Sunday in March to the
# first Sunday in November). Set False for Arizona, Hawaii, or anywhere
# that does not change its clocks.
USE_US_DST = True

# Fonts live in lib/ alongside the driver. The GC9B72 driver has no
# built-in font -- text() takes a font MODULE as its first argument.
import vga1_8x16 as SMALL_FONT       # 8 x 16 -- 45 characters across
import vga1_bold_16x32 as BIG_FONT   # 16 x 32 -- 22 characters across

_backlight = None


def init_display():
    """Start the SPI bus and the GC9B72. Returns the display object."""
    global _backlight

    spi = SPI(SPI_ID, baudrate=BAUDRATE,
              sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))

    _backlight = Pin(BL_PIN, Pin.OUT)

    return gc9b72.GC9B72(
        spi,
        dc=Pin(DC_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        reset=Pin(RST_PIN, Pin.OUT),
        backlight=_backlight,
        rotation=0)


def set_backlight(on):
    """Turn the backlight on or off."""
    _backlight.value(1 if on else 0)


def init_buttons():
    """Set up the three buttons. Returns (mode, increment, decrement).

    Each pin idles at 1 and reads 0 while its button is held down, so
    the labs test for `button.value() == 0`."""
    mode = Pin(BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
    increment = Pin(BUTTON_INCREMENT_PIN, Pin.IN, Pin.PULL_UP)
    decrement = Pin(BUTTON_DECREMENT_PIN, Pin.IN, Pin.PULL_UP)
    return mode, increment, decrement


def centered_text(display, font, text, y, color=WHITE, background=BLACK):
    """Draw text centered left-to-right on the screen at row y."""
    x = (WIDTH - len(text) * font.WIDTH) // 2
    display.text(font, text, x, y, color, background)
