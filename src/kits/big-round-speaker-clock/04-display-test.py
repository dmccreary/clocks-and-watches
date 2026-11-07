# 04-display-test.py: Display Test
# Prints "Hello World" in the middle of the round display, with a thin ring
# just inside the edge of the glass.
#
# If the screen stays black:
#   - is the backlight on? Some modules need BL wired to GP7 (or to 3V3).
#   - are SCL and SDA swapped? SCL (clock) goes to GP2, SDA (data) to GP3.
#   - are VCC and GND on 3V3 and GND?
# If the screen lights up but shows snow or stripes, check RST (GP4),
# DC (GP5) and CS (GP6), or lower BAUDRATE in config.py to 12_000_000.
#
# The ring is drawn at config.SAFE_RADIUS. If any part of it is hidden
# under the bezel, make SAFE_RADIUS a little smaller -- the clock face
# places its ticks from it.

NAME = "04-display-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import shapes

started = time.ticks_ms()
display = config.init_display()
print("display started in {} ms".format(time.ticks_diff(time.ticks_ms(),
                                                         started)))

display.fill(config.BLACK)
shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS,
            config.CYAN, 2)

big = config.BIG_FONT
config.centered_text(display, big, "Hello", config.CENTER_Y - big.HEIGHT,
                     config.WHITE)
config.centered_text(display, big, "World", config.CENTER_Y, config.YELLOW)
config.centered_text(display, config.SMALL_FONT, "GC9B72  360 x 360",
                     config.CENTER_Y + 60, config.GRAY)

print("You should see 'Hello World' inside a cyan ring.")

# Try This
#   1. Change config.YELLOW to config.color565(255, 128, 0) for orange.
#   2. Move the words up by changing config.CENTER_Y - big.HEIGHT to
#      config.CENTER_Y - 100. How close to the top can text go before the
#      round edge cuts it off?
