# Lab 01: Hello, Display
# Confirms the GC9B72 display is wired correctly and MicroPython can draw
# on it -- on a WHITE screen, because a railway clock has a white dial.
#
# NEW IDEAS: importing a module, calling functions, and the screen's
# coordinate system (x grows to the right, y grows DOWN).
#
# There is no built-in font on this driver -- text() takes a font MODULE
# as its first argument. config.py imports two of them for you, and
# config.centered_text() does the arithmetic of centering a line.
#
# There is also no show(). Every drawing call streams straight over SPI,
# so each line below is already on the glass before the next one runs.

NAME = "01-hello-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config
import shapes

display = config.init_display()

# Paint the whole screen white. Colors are 16-bit numbers; config.py
# names the ones this kit uses.
display.fill(config.WHITE)

# The big font is 16 x 32 pixels. Black letters on a white background.
config.centered_text(display, config.BIG_FONT, "HELLO", 110,
                     config.BLACK, config.WHITE)

# The small font is 8 x 16 pixels.
config.centered_text(display, config.SMALL_FONT, "I am going to be a",
                     160, config.GRAY, config.WHITE)
config.centered_text(display, config.SMALL_FONT, "Swiss railway clock",
                     180, config.GRAY, config.WHITE)

# A red dot at the exact center of the screen: x = 180, y = 180.
shapes.circle(display, config.CENTER_X, config.CENTER_Y, 8,
              config.RAIL_RED, config.FILL)

# A red ring at config.SAFE_RADIUS, the largest circle you can see all
# of. It should sit right at the edge of the glass. If yours is cut off,
# make SAFE_RADIUS in config.py smaller. The clock face you build in the
# next labs places its outer bars just inside this ring.
shapes.ring(display, config.CENTER_X, config.CENTER_Y,
            config.SAFE_RADIUS, config.RAIL_RED, 2)
