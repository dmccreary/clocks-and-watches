# Lab 06: Button Test
# Checks the wiring of all three buttons. Each one lights up its circle
# while you hold it down, and prints to the Thonny shell when it changes.
#
#   MODE  GP13     UP  GP14     DOWN  GP15
#
# Every button reads 1 when it is up and 0 while it is held -- the pull-up
# resistor holds the pin high until the button connects it to GND.
#
# A button that never lights up is wired wrong or not wired at all. An
# unconnected pull-up pin reads 1 forever, which looks exactly like "not
# pressed" -- so this lab never crashes on a missing button, it just
# never reacts to it.

NAME = "06-button-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import shapes

display = config.init_display()
mode, increment, decrement = config.init_buttons()

RADIUS = 32
Y = 170

# (pin, label, pin name, x position of the circle, color when held)
BUTTONS = (
    (mode, "MODE", "GP13", 100, config.YELLOW),
    (increment, "UP", "GP14", 180, config.GREEN),
    (decrement, "DOWN", "GP15", 260, config.RED),
)

display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Buttons", 90)
for pin, label, pin_name, x, color in BUTTONS:
    shapes.circle(display, x, Y, RADIUS, config.GRAY)
    display.text(config.SMALL_FONT, label,
                 x - len(label) * 4, Y + RADIUS + 10, config.WHITE)
    display.text(config.SMALL_FONT, pin_name,
                 x - len(pin_name) * 4, Y + RADIUS + 28, config.GRAY)

# Remember what each button looked like last time, and only redraw the
# ones that changed -- redrawing all three circles 50 times a second
# would keep the SPI bus busy for nothing. They all start out "not held",
# which is what the empty circles drawn above already show.
last = [False, False, False]

while True:
    for i, (pin, label, pin_name, x, color) in enumerate(BUTTONS):
        held = pin.value() == 0
        if held != last[i]:
            last[i] = held
            # Fill 2 px inside the outline so the gray ring stays put.
            shapes.circle(display, x, Y, RADIUS - 2,
                          color if held else config.BLACK, config.FILL)
            print(label, "pressed" if held else "released")
    time.sleep_ms(20)
