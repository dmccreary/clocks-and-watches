# Lab 03: Hello World
# Confirms the display is wired correctly and MicroPython can draw on it.
# It also checks the three display settings in config.py that nobody can
# know until a real picture is on the glass.
#
# What you should see, with the knob on the right:
#
#   - a black screen with a thin white line around all four edges
#   - "Hello World!" in white, and "ST7735S" in big green letters
#   - three bars labeled RED, GREEN and BLUE, in that order
#
# What to change in config.py if you see something else:
#
#   the picture is upside down             ROTATION = 3
#   one side of the white line is          X_OFFSET or Y_OFFSET = 1,
#     missing, or an edge has a strip        then 2
#     of colored specks along it
#   the RED bar is blue and the            BGR = True
#     BLUE bar is red
#
# There is no built-in font on this driver -- text() takes a font MODULE
# as its first argument. config.py imports three of them for you.
#
#     display.text(config.SMALL_FONT, "Hello!", x, y, WHITE, BLACK)
#                  ^^^^^^^^^^^^^^^^^^ not optional
#
# There is also no show(). Every drawing call streams straight over SPI,
# so each line below is already on the glass before the next one runs.

NAME = "03-hello-world.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import config

display = config.init_display()

display.fill(config.BLACK)

# A white line one pixel thick around the very edge of the screen.
display.rect(0, 0, config.WIDTH, config.HEIGHT, config.WHITE)

# The small font: 8 pixels wide, 16 tall.
config.centered_text(display, config.SMALL_FONT, "Hello World!", 8)

# The big font: 16 x 32, readable from across the room.
config.centered_text(display, config.BIG_FONT, "ST7735S", 28, config.GREEN)

# Three bars, each with its name underneath in the tiny 8 x 8 font. If
# the names and the colors do not match, the color order in config.py is
# wrong for this panel.
BAR_WIDTH = 40
BAR_HEIGHT = 32
GAP = 10
BARS = (
    ("RED", config.RED),
    ("GREEN", config.GREEN),
    ("BLUE", config.BLUE),
)

font = config.TINY_FONT
x = (config.WIDTH - 3 * BAR_WIDTH - 2 * GAP) // 2
for label, color in BARS:
    display.fill_rect(x, 68, BAR_WIDTH, BAR_HEIGHT, color)
    label_x = x + (BAR_WIDTH - len(label) * font.WIDTH) // 2
    display.text(font, label, label_x, 106, config.WHITE, config.BLACK)
    x += BAR_WIDTH + GAP

print("Check the screen: a white border, Hello World!, and red, green")
print("and blue bars from left to right.")
