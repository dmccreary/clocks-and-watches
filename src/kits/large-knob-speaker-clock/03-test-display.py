# Lab 03: Test the Display
# Confirms the display is wired correctly and MicroPython can draw on it.
# It also checks the four display settings in config.py that nobody can
# know until a real picture is on the glass.
#
# What you should see, with the knob on the right:
#
#   - a BLACK screen with a thin white line around all four edges
#   - "Hello World!" in big white letters, and "ST7789 320 x 240" in green
#   - three bars labeled RED, GREEN and BLUE, in that order
#   - a small yellow arrow in the top-left corner, pointing at the corner
#
# What to change in config.py if you see something else:
#
#   the screen is white and the            flip INVERT
#     letters are black, like a photo
#     negative
#   the picture is upside down             ROTATION = 3
#   the words read backwards (mirrored)    ROTATION = 3, and if that is
#                                            still mirrored, go back to 1
#                                            and flip BGR
#   one side of the white line is          X_OFFSET or Y_OFFSET = 1,
#     missing, or an edge has a strip        then 2
#     of colored specks along it
#   the RED bar is blue and the            flip BGR
#     BLUE bar is red
#   RED, GREEN and BLUE come out           flip BGR AND flip INVERT --
#     yellow, purple and cyan                every color is its opposite,
#                                            and red and blue are swapped
#   random colored specks everywhere       BAUDRATE = 12_000_000
#
# There is no built-in font on this driver -- text() takes a font MODULE
# as its first argument. config.py imports three of them for you.
#
#     display.text(config.SMALL_FONT, "Hello!", x, y, WHITE, BLACK)
#                  ^^^^^^^^^^^^^^^^^^ not optional
#
# There is also no show(). Every drawing call streams straight over SPI,
# so each line below is already on the glass before the next one runs.

NAME = "03-test-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import shapes

start = time.ticks_ms()
display = config.init_display()

display.fill(config.BLACK)

# A white line one pixel thick around the very edge of the screen.
display.rect(0, 0, config.WIDTH, config.HEIGHT, config.WHITE)

# The top-left corner, so you can tell a mirrored picture from a
# correct one: the arrow must point INTO the corner.
shapes.triangle(display, 4, 4, 24, 4, 4, 24, config.YELLOW, config.FILL)

# The big font: 16 x 32, readable from across the room.
config.centered_text(display, config.BIG_FONT, "Hello World!", 24)

# The small font: 8 pixels wide, 16 tall.
config.centered_text(display, config.SMALL_FONT, "ST7789 320 x 240", 64,
                     config.GREEN)
config.centered_text(display, config.SMALL_FONT, "knob on the right", 84,
                     config.GRAY)

# Three bars, each with its name underneath. If the names and the colors
# do not match, the color order in config.py is wrong for this panel.
BAR_WIDTH = 80
BAR_HEIGHT = 64
GAP = 16
BAR_Y = 116
BARS = (
    ("RED", config.RED),
    ("GREEN", config.GREEN),
    ("BLUE", config.BLUE),
)

font = config.SMALL_FONT
x = (config.WIDTH - 3 * BAR_WIDTH - 2 * GAP) // 2
for label, color in BARS:
    display.fill_rect(x, BAR_Y, BAR_WIDTH, BAR_HEIGHT, color)
    label_x = x + (BAR_WIDTH - len(label) * font.WIDTH) // 2
    display.text(font, label, label_x, BAR_Y + BAR_HEIGHT + 8,
                 config.WHITE, config.BLACK)
    x += BAR_WIDTH + GAP

took = time.ticks_diff(time.ticks_ms(), start)
config.centered_text(display, config.TINY_FONT,
                     "drawn in {} ms".format(took), 220, config.GRAY)

print("Drawn in {} ms.".format(took))
print("Check the screen: black background, a white border, Hello World!,")
print("a yellow arrow in the top-left corner, and red, green and blue bars")
print("from left to right.")
