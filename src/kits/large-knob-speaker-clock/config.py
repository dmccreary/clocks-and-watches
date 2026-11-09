# Hardware configuration for the large-knob-speaker-clock kit: a Raspberry
# Pi Pico 2 W wired to a "2.4 TFT + EC11" board -- a 2.4" 320x240
# rectangular color TFT with a rotary encoder knob and a push button on
# the same PCB -- plus a MAX98357A I2S amplifier and a small speaker.
#
# Every lab in this folder imports this file instead of repeating pin
# numbers, so the whole kit only needs to be described in one place.
#
# The silkscreen on the back of the board reads:
#
#   2.4 TFT + EC11
#   2.4 TFT : 320*240 RGB
#   TFT Drive IC : ST7789
#   TFT Interface : 4 - SPI
#   EC11 interface : A, B, PUSH
#   START KEY : K0
#   VCC: 3.3V/5V
#
# It is the big brother of the "1.8 TFT + EC11" board in the
# rect-tft-display kit: the same 12-pin header in the same order, the
# same knob and the same K0 key, so the display and control wiring is
# identical. Only the screen is bigger (320x240 instead of 160x128) and
# its driver chip is an ST7789 instead of an ST7735S. lib/st7789.py has
# the same method names as that kit's lib/st7735s.py, so its labs port
# here by changing sizes and positions.

from machine import Pin, SPI
import st7789
from st7789 import color565

WIDTH = 320
HEIGHT = 240

# --- Display and controls -------------------------------------------------
#
# The 12-pin header reads (bottom to top, with the knob on the right):
# GND VCC SCL SDA RES DC CS BLK A B PUSH K0. All twelve are wired, in the
# same order, down one side of the Pico. The breadboard row is the Pico's
# physical pin number, so rows 8, 13 and 18 are the Pico's GND pins. The
# header's own GND goes to row 8; row 13 has no wire.
#
#   Board pin    Pico pin   Breadboard row   Wire color
#   ----------   --------   --------------   ----------
#   GND          GND        8                brown
#   VCC          3V3(OUT)   36               red
#   SCL / CLK    GP2        4                orange
#   SDA / MOSI   GP3        5                yellow
#   RES          GP4        6                green
#   DC           GP5        7                blue
#   CS           GP6        9                purple
#   BLK          GP7        10               gray
#   A            GP8        11               white
#   B            GP9        12               blue    (second ribbon)
#   PUSH         GP10       14               green   (second ribbon)
#   K0           GP11       15               purple  (second ribbon)
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

# The ST7789 datasheet allows a serial write clock of about 62 MHz, but
# the colorful 10 cm jumper wires between the board and the breadboard
# are not a circuit board. 24 MHz is a safe rate for them, and still
# fills all 320x240 pixels in about 55 ms.
#
# MicroPython rounds the rate you ask for DOWN to one it can make. On a
# Pico 2 W the steps near here are 8, 12 and 24 MHz, with nothing in
# between (measured for the sw-gc9b72 kit), so 24 MHz is what you get.
# Lab 02 prints the real rate. If the picture shows random specks, try
# 12_000_000.
BAUDRATE = 24_000_000

# The panel is 240 wide by 320 tall in its native portrait position. On
# this board it is mounted on its side, so with the knob on the right the
# screen is 320 wide by 240 tall.
#
# Three things vary between ST7789 boards. Lab 03 checks all three. The
# values below are confirmed on the real board. Note that the usual
# ST7789 settings (BGR False, INVERT True) are wrong for this one: they
# made the red, green and blue bars come out yellow, purple and cyan.
#
#   ROTATION   picture is upside down          -> try 3 instead of 1
#              picture is mirrored             -> try 3, then BGR/ROTATION
#   BGR        red and blue are swapped        -> flip True/False
#   INVERT     black is white, like a photo    -> flip True/False
#                negative
#   both       red, green and blue come out    -> flip both
#                yellow, purple and cyan
#
# The 2.4" ST7789 panel fills the controller's whole 240x320 memory, so
# it needs no offsets. They are here for boards that do.
ROTATION = 1
BGR = True
INVERT = False
X_OFFSET = 0
Y_OFFSET = 0

# The EC11 rotary encoder. A and B are its two quadrature outputs: they
# take turns going low as the knob turns, and which one goes first tells
# you the direction. If clockwise counts backwards, swap these two numbers.
# PUSH is the switch you close by pressing the knob straight down.
ENCODER_A_PIN = 8
ENCODER_B_PIN = 9
ENCODER_PUSH_PIN = 10

# One click of the knob moves A and B through this many steps (lab 04
# shows them). This board's knob takes 4 -- a whole trip around the
# A/B loop per click -- unlike the 1.8" board's, which takes 2. With 2
# here, every click counted as two (setting the alarm in lab 08 jumped
# two minutes a click). If one click you feel ever counts as two, or two
# clicks count as one, change this to match.
ENCODER_STEPS_PER_CLICK = 4

# The square push button below the knob, labeled "START KEY: K0".
BUTTON_K0_PIN = 11

# --- Speaker: MAX98357A I2S amplifier -------------------------------------
#
#   Amp pin   Pico pin   Breadboard row   Wire color   What it does
#   -------   --------   --------------   ----------   ------------
#   BCLK      GP12       16               yellow       "bit clock": one
#                                                        tick per bit
#   LRC       GP13       17               green        "left/right clock":
#                                                        which channel
#   GND       GND        18               black
#   DIN       GP14       19               orange       "data in": the
#                                                        audio itself
#   GAIN      GP15       20               brown        how loud the amp
#                                                        makes it
#   SD        --         --               --           not connected (the
#                                                        amp stays on)
#   VIN       VBUS (5 V) or 3V3
#
# THE ONE RULE: MicroPython's I2S on the Pico needs LRC on the pin right
# AFTER BCLK. Here BCLK is GP12 and LRC is GP13, so it works. Swap those
# two wires and I2S() raises an error. 02-probe.py checks the rule.
#
# (The MAX98357A is only an amplifier -- it has no microphone.)
I2S_BCLK_PIN = 12
I2S_LRC_PIN = 13
I2S_DIN_PIN = 14
I2S_GAIN_PIN = 15

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

# --- Location and time ----------------------------------------------------
# Thonny sets the Pico's clock from your computer, which already keeps
# local time. These are for setting the clock from the internet instead
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
# United States has a NEGATIVE longitude. This is Minneapolis.
LATITUDE = 44.98
LONGITUDE = -93.27
TEMPERATURE_UNIT = "fahrenheit"      # or "celsius"

# The clock faces in labs 13 and 15 (lib/timerow.py): True for 1:00 PM,
# False for 13:00.
TWELVE_HOUR = True

# --- Colors ---------------------------------------------------------------
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
RAIL_RED = color565(235, 0, 0)      # the railway clock's second hand (lib/mondaine.py)

# Fill flags for shapes.ellipse() / shapes.poly() -- outline vs. solid.
NO_FILL = 0
FILL = 1

CENTER_X = WIDTH // 2       # 160
CENTER_Y = HEIGHT // 2      # 120

# Fonts live in lib/ alongside the driver. The ST7789 driver has no
# built-in font -- text() takes a font MODULE as its first argument.
import vga1_8x8 as TINY_FONT         # 8 x 8   -- 40 characters across
import vga1_8x16 as SMALL_FONT       # 8 x 16  -- 40 characters across
import vga1_bold_16x32 as BIG_FONT   # 16 x 32 -- 20 characters across

_backlight = None


def init_spi():
    """Start the SPI bus the display hangs off. Returns the SPI object.

    The display never talks back, so there is no MISO pin."""
    return SPI(SPI_ID, baudrate=BAUDRATE,
               sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))


def init_display():
    """Start the SPI bus and the ST7789. Returns the display object."""
    global _backlight

    _backlight = Pin(BL_PIN, Pin.OUT)

    return st7789.ST7789(
        init_spi(),
        dc=Pin(DC_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        reset=Pin(RST_PIN, Pin.OUT),
        backlight=_backlight,
        rotation=ROTATION,
        bgr=BGR,
        invert=INVERT,
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
