# Hardware configuration for the rect-tft-display kit: a Raspberry Pi Pico
# 2 W wired to a "1.8 TFT + EC11" board -- a 1.8" 128x160 rectangular
# color TFT with a rotary encoder knob and a push button on the same PCB.
#
# Every lab in this folder imports this file instead of repeating pin
# numbers, so the whole kit only needs to be described in one place.
#
# The silkscreen on the back of the board reads:
#
#   1.8 TFT + EC11
#   1.8 TFT : 128*160 RGB
#   TFT Drive IC : ST7735S
#   TFT Interface : 4 - SPI
#   EC11 interface : A, B, PUSH
#   START KEY : K0
#   VCC: 3.3V/5V
#
# The driver (lib/st7735s.py) has the same method names as the GC9B72
# driver in the sw-gc9b72 smartwatch kit, and the fonts, shapes.py and
# watchparts.py in lib/ come from that kit too. Most of the labs here
# are that kit's labs, laid out again for a small rectangular screen and
# worked by a knob instead of three buttons.

from machine import Pin, SPI
import st7735s
from st7735s import color565

WIDTH = 160
HEIGHT = 128

# The 12-pin header reads (bottom to top, with the knob on the right):
# GND VCC SCL SDA RES DC CS BLK A B PUSH K0. All twelve are wired, in the
# same order, to one side of the Pico -- GP2 through GP11.
#
#   Board pin    Pico pin   Wire color
#   ----------   --------   ----------
#   GND          GND        brown
#   VCC          3V3        red
#   SCL / CLK    GP2        orange
#   SDA / MOSI   GP3        yellow
#   RES          GP4        green
#   DC           GP5        blue
#   CS           GP6        purple
#   BLK          GP7        gray
#   A            GP8        white
#   B            GP9        green   (second ribbon)
#   PUSH         GP10       blue    (second ribbon)
#   K0           GP11       purple  (second ribbon)
#
# This wiring is confirmed on the real board. With SCL, SDA, RES and DC,
# lab 02 draws a correct picture. Lab 08 switches the backlight with BLK.
# Lab 06 counts the knob's steps cleanly, and lab 07 shows each button
# lighting its own box on the screen and a clockwise turn counting up,
# which covers A, B, PUSH and K0. CS is the only pin not tested on its
# own: it sits between two confirmed pins, and the display would still
# draw if CS were held low.
#
# Power VCC from the Pico's 3V3(OUT) pin, not VBUS. The board accepts 5 V,
# but its pull-up resistors on A, B, PUSH and K0 would then idle those
# lines at 5 V, and Pico GPIO pins are not 5 V tolerant.
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
RST_PIN = 4
DC_PIN = 5
CS_PIN = 6
BL_PIN = 7

# On a Pico 2 W the onboard LED is NOT wired to GP25 the way it is on a
# plain Pico -- it hangs off the CYW43439 wireless chip. MicroPython hides
# that behind the pin name "LED", so always use Pin("LED"), never Pin(25).
#
# GP23, GP24, GP25 and GP29 belong to the wireless chip on this board.
# Don't wire anything to them.
LED_PIN = "LED"

# The ST7735S datasheet rates its serial write clock at about 15 MHz, so
# 12 MHz stays inside the limit and still sends all 160x128 pixels in
# under 30 ms.
#
# MicroPython rounds the rate you ask for DOWN to one it can make. On a
# Pico 2 W the steps near here are 8, 12 and 24 MHz, with nothing in
# between (measured for the sw-gc9b72 kit -- see its config.py), so 12 MHz
# is what you get. Print the SPI object to check.
BAUDRATE = 12_000_000

# The panel is 128 wide by 160 tall in its native portrait position. On
# this board it is mounted on its side, so with the knob on the right the
# screen is 160 wide by 128 tall.
#
# Three things vary between ST7735 boards. All three are confirmed on
# this one: lab 02's picture is the right way up with the knob on the
# right, its bars come out red, green, blue, and lab 03's white border
# is complete on all four sides. If a different board disagrees:
#
#   ROTATION   picture is upside down          -> try 3 instead of 1
#   X_OFFSET   a strip of garbage down one     -> try 1, then 2
#   Y_OFFSET     side, or along the top or bottom
#   BGR        red and blue are swapped        -> flip True/False
ROTATION = 1
X_OFFSET = 0
Y_OFFSET = 0
BGR = False

# The EC11 rotary encoder. A and B are its two quadrature outputs: they
# take turns going low as the knob turns, and which one goes first tells
# you the direction. If clockwise counts backwards, swap these two numbers.
# PUSH is the switch you close by pressing the knob straight down.
ENCODER_A_PIN = 8
ENCODER_B_PIN = 9
ENCODER_PUSH_PIN = 10

# One click of the knob moves A and B through this many steps (lab 06
# shows them). Many EC11 knobs take 4. This one takes 2, confirmed with
# lab 06 on the real board: it clicks into place with A and B both 1,
# and again one click later with both 0.
ENCODER_STEPS_PER_CLICK = 2

# The square push button below the knob, labeled "START KEY: K0".
BUTTON_K0_PIN = 11

# An optional piezo buzzer for the countdown timer's alarm (lab 16). Wire
# its + leg to a free GPIO pin and its - leg to GND, then put that pin
# number here. None means no buzzer: the alarm flashes the screen and the
# onboard LED instead.
BUZZER_PIN = None

# Local time zone: US Central. The clock in lab 09 does not need these --
# Thonny sets the Pico's clock from your computer, which already keeps
# local time. They are for setting the clock from the internet instead
# (see wifi_time.py), because internet time servers only ever hand out
# UTC.
#   Eastern -5, Central -6, Mountain -7, Pacific -8
TIMEZONE_HOURS = -6
# True to apply US daylight saving time (second Sunday in March to the
# first Sunday in November), when Central time is 5 hours behind UTC
# instead of 6. Set False for Arizona, Hawaii, or anywhere that does not
# change its clocks.
USE_US_DST = True

# Where to get the weather forecast for (see forecast.py). Latitude and
# longitude in degrees -- look up your town on a map site, or search for
# "<your town> latitude longitude". North and east are positive; the
# United States has a NEGATIVE longitude. This is Minneapolis, the same
# city as the weather labs in the Learning MicroPython course.
LATITUDE = 44.98
LONGITUDE = -93.27
TEMPERATURE_UNIT = "fahrenheit"      # or "celsius"

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

# Fill flags for shapes.ellipse() / shapes.poly() -- outline vs. solid.
NO_FILL = 0
FILL = 1

CENTER_X = WIDTH // 2       # 80
CENTER_Y = HEIGHT // 2      # 64

# Fonts live in lib/ alongside the driver. The ST7735S driver has no
# built-in font -- text() takes a font MODULE as its first argument.
import vga1_8x8 as TINY_FONT         # 8 x 8   -- 20 characters across
import vga1_8x16 as SMALL_FONT       # 8 x 16  -- 20 characters across
import vga1_bold_16x32 as BIG_FONT   # 16 x 32 -- 10 characters across

_backlight = None


def init_spi():
    """Start the SPI bus the display hangs off. Returns the SPI object.

    The display never talks back, so there is no MISO pin."""
    return SPI(SPI_ID, baudrate=BAUDRATE,
               sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))


def init_display():
    """Start the SPI bus and the ST7735S. Returns the display object."""
    global _backlight

    _backlight = Pin(BL_PIN, Pin.OUT)

    return st7735s.ST7735S(
        init_spi(),
        dc=Pin(DC_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        reset=Pin(RST_PIN, Pin.OUT),
        backlight=_backlight,
        rotation=ROTATION,
        bgr=BGR,
        x_offset=X_OFFSET,
        y_offset=Y_OFFSET)


def set_backlight(on):
    """Turn the backlight on or off."""
    global _backlight
    if _backlight is None:
        _backlight = Pin(BL_PIN, Pin.OUT)
    _backlight.value(1 if on else 0)


def init_controls():
    """Set up the knob and the button. Returns (a, b, push, k0).

    push and k0 idle at 1 and read 0 while pressed, so the labs test for
    `pin.value() == 0`. a and b change as the knob turns -- wrap them in
    watchparts.Knob to count clicks."""
    a = Pin(ENCODER_A_PIN, Pin.IN, Pin.PULL_UP)
    b = Pin(ENCODER_B_PIN, Pin.IN, Pin.PULL_UP)
    push = Pin(ENCODER_PUSH_PIN, Pin.IN, Pin.PULL_UP)
    k0 = Pin(BUTTON_K0_PIN, Pin.IN, Pin.PULL_UP)
    return a, b, push, k0


def centered_text(display, font, text, y, color=WHITE, background=BLACK):
    """Draw text centered left-to-right on the screen at row y."""
    x = (WIDTH - len(text) * font.WIDTH) // 2
    display.text(font, text, x, y, color, background)
