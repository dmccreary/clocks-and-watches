# Lab 02: Hello World
# Confirms the GC9B72 display is wired correctly and MicroPython can draw
# on it.
#
# There is no built-in font on this driver -- text() takes a font MODULE
# as its first argument. config.py imports two of them for you.
#
#     display.text(config.SMALL_FONT, "Hello!", x, y, WHITE, BLACK)
#                  ^^^^^^^^^^^^^^^^^^ not optional
#
# There is also no show(). Every drawing call streams straight over SPI,
# so each line below is already on the glass before the next one runs.

NAME = "02-hello.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config
import shapes

display = config.init_display()

display.fill(config.BLACK)

# The small font: 8 pixels wide, 16 tall.
config.centered_text(display, config.SMALL_FONT, "Hello World!", 150)

# The big font: 16 x 32, readable from across the room.
config.centered_text(display, config.BIG_FONT, "GC9B72", 175, config.GREEN)

# A red ring at config.SAFE_RADIUS, the largest circle you can see all
# of -- it should sit right at the edge of the glass. If yours is cut
# off, make SAFE_RADIUS smaller; if there is a wide black gap outside it,
# make it bigger. The watch face in lab 05 places its ticks from it.
shapes.ring(display, config.CENTER_X, config.CENTER_Y,
            config.SAFE_RADIUS, config.RED, 2)
