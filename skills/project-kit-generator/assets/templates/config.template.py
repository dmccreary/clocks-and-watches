# config.py -- every pin number and setting for the {{KIT_NAME}} kit.
#
# Every program in this kit reads its pins from THIS file. Move a wire, change the number
# here, and every program follows. Nobody has to hunt through the labs.
#
# Rules for this file (they came from real mistakes):
#   * Name every pin setting *_PIN (pin_check.py finds duplicates and bad bus pins by that name).
#   * Put NOTHING at the top that needs the display files (gc9a01, fonts) or hardware. Import
#     them inside init_display(), so labs 01-05 still run on a Pico that has no display files
#     yet. `import config` must never fail.
#   * Only put settings here that a student might change or that two files share. A number
#     that only one lab uses and nobody should touch can stay in that lab.
#   * Comment the WIRING next to the pins, with physical pin numbers. Students wire from this.
#   * Delete settings when you delete the lab that used them (dead settings mislead).
#
# Use it like this:
#
#     import config
#     from machine import Pin, I2C
#     i2c = I2C(config.I2C_BUS, sda=Pin(config.I2C_SDA_PIN), scl=Pin(config.I2C_SCL_PIN),
#               freq=config.I2C_BUS_FREQ)

# --- Sensor bus ------------------------------------------------------------
# Wiring: {{SENSOR_NAME}} VIN -> 3V3 OUT (pin 36)   NEVER pin 40 (VBUS, that is 5 V)
#         GND -> any GND pin, SDA -> GP{{SDA}} (pin {{SDA_PHYS}}), SCL -> GP{{SCL}} (pin {{SCL_PHYS}})
I2C_BUS = 0
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
I2C_BUS_FREQ = 400_000        # drop to 100_000 if you use long wires

SENSOR_ADDR = 0x00            # {{ADDRESS NOTES: other addresses some boards use}}

# --- Color display ({{DISPLAY_NAME}}, SPI) -------------------------------------
# Wiring (list every wire, with physical pin numbers):
#   Display pin    Pico pin
#   SCL / CLK      GP2  (pin 4)
#   SDA / MOSI     GP3  (pin 5)
#   DC             GP4  (pin 6)
#   CS             GP5  (pin 7)
#   RST            GP6  (pin 9)
#   VCC            3V3 OUT (pin 36)
#   GND            any GND pin
# If a sibling kit already runs this display, copy ITS pins exactly. They are known to work.
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 240
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
DC_PIN = 4
CS_PIN = 5
RES_PIN = 6
SPI_BAUDRATE = 60_000_000

# Colors are RGB565: 5 bits red, 6 bits green, 5 bits blue.
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
CYAN = 0x07FF
YELLOW = 0xFFE0
ORANGE = 0xFC00
GREY = 0x4208

# A round screen is still a square to the driver; only the inscribed circle is visible.
# Keep everything inside SAFE_RADIUS (the last few pixels sit under the bezel).
CENTER_X = DISPLAY_WIDTH // 2
CENTER_Y = DISPLAY_HEIGHT // 2
RADIUS = DISPLAY_WIDTH // 2
SAFE_RADIUS = 112


def init_display():
    """Start the SPI bus and the display driver and return the display object.

    The driver is imported HERE, inside the function, on purpose (see the rules at the top)."""
    from machine import Pin, SPI
    import gc9a01                                    # {{swap for your driver}}
    spi = SPI(SPI_ID, baudrate=SPI_BAUDRATE, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
    return gc9a01.GC9A01(spi, dc=Pin(DC_PIN, Pin.OUT), cs=Pin(CS_PIN, Pin.OUT),
                         reset=Pin(RES_PIN, Pin.OUT), rotation=0)


# --- Push button and heartbeat LED --------------------------------------------
# One push button between GP15 (pin 20) and any GND pin (pin 18 is closest). No outside
# resistor: the program turns on the Pico's own pull-up, so a press reads as 0.
# RULE: buttons are ALWAYS read with a pin interrupt and a 50 ms debounce (lib/button.py).
BUTTON_PIN = 15
BUTTON_DEBOUNCE_MS = 50
LONG_PRESS_MS = 800           # hold this long to switch units (F/C) or do the mode's special action
CLEAR_PRESS_MS = 3000         # hold this long in the records mode to clear the records
BUILT_IN_LED_PIN = 25         # GP25 on a plain Pico; heartbeat.py tries Pin("LED") first (Pico W too)
HEARTBEAT_MS = 60             # each LED blink lasts this long

# --- How often things happen --------------------------------------------------
LOG_SECONDS = 2               # the CSV logging lab
PLOT_SECONDS = 1              # the Thonny Plotter labs
DISPLAY_SECONDS = 1           # the display labs
# A sensor that heats itself when read too fast: say so here and pick a gentle rate.

# --- Display mode settings (the capstone lab) ---------------------------------
# Mood-ring colors: the reading is spread along a color line between these two ends.
MOOD_COLD = 50.0
MOOD_HOT = 95.0
# {{Add one block of settings per mode: thresholds, widths, targets, file names.}}
RECORDS_FILE = "records.txt"
RECORDS_SAVE_SECONDS = 60     # flash memory wears out: save a new record at most this often
