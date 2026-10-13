# Lab 07: Controls on the Screen
# Shows the K0 button, the knob's push switch, and the knob's rotation on
# the screen, all at the same time:
#
#   - the K0 and PUSH boxes light up while each one is held down
#   - the number counts clicks of the knob: up when you turn it
#     clockwise, down when you turn it the other way
#   - the white marker slides along the track one notch per click, and
#     wraps around at the ends -- 20 clicks take it all the way across
#
# Labs 04, 05 and 06 found the controls by looking at their pins over and
# over in a loop. That is not good enough here. Drawing on the screen
# takes time, and a knob step that came and went while the program was
# busy drawing would be lost.
#
# So the knob uses interrupts instead. a.irq() and b.irq() ask MicroPython
# to call knob_moved() by itself the moment A or B changes, whatever the
# main loop is doing. knob_moved() only counts the step; the main loop
# does the slow drawing whenever it gets round to it.
#
# The two buttons do not need interrupts. A press lasts far longer than
# one trip round the loop, so looking at them each time round is enough.

NAME = "07-controls-display-test.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin
import config

display = config.init_display()
a, b, push, k0 = config.init_controls()

# ---------------------------------------------------------------------
# The knob: count steps in an interrupt handler.
# ---------------------------------------------------------------------
# The four positions of (A, B), in the order a clockwise turn visits
# them. Lab 06 explains.
CLOCKWISE = ((0, 0), (1, 0), (1, 1), (0, 1))

steps = 0
last = CLOCKWISE.index((a.value(), b.value()))


def knob_moved(pin):
    global steps, last
    now = CLOCKWISE.index((a.value(), b.value()))
    move = (now - last) % 4
    last = now
    if move == 1:
        steps += 1
    elif move == 3:
        steps -= 1


a.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)
b.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)

# ---------------------------------------------------------------------
# The screen layout.
# ---------------------------------------------------------------------
SMALL = config.SMALL_FONT

BOX_Y = 20
BOX_WIDTH = 60
BOX_HEIGHT = 30

# (pin, name, x of its box, color while held)
BUTTONS = (
    (k0, "K0", 14, config.GREEN),
    (push, "PUSH", 86, config.YELLOW),
)

KNOB_Y = 70
NUMBER_X = 84           # where the click count starts, after "Knob: "

NOTCHES = 20
NOTCH_WIDTH = 7
TRACK_X = (config.WIDTH - NOTCHES * NOTCH_WIDTH) // 2
TRACK_Y = 110
MARKER_HEIGHT = 12


def draw_box(x, color, down):
    """Fill the inside of a button's box: its color if held, else black."""
    display.fill_rect(x + 2, BOX_Y + 2, BOX_WIDTH - 4, BOX_HEIGHT - 4,
                      color if down else config.BLACK)


def draw_marker(clicks, visible):
    """Draw the marker at its notch, or put back the track it covered."""
    x = TRACK_X + (clicks % NOTCHES) * NOTCH_WIDTH
    display.fill_rect(x, TRACK_Y, NOTCH_WIDTH, MARKER_HEIGHT,
                      config.WHITE if visible else config.BLACK)
    if not visible:
        display.fill_rect(x, TRACK_Y + MARKER_HEIGHT // 2 - 1,
                          NOTCH_WIDTH, 2, config.GRAY)


display.fill(config.BLACK)
config.centered_text(display, SMALL, "Controls", 2)

for pin, name, x, color in BUTTONS:
    display.fill_rect(x, BOX_Y, BOX_WIDTH, BOX_HEIGHT, config.GRAY)
    draw_box(x, color, False)
    display.text(SMALL, name, x + (BOX_WIDTH - len(name) * SMALL.WIDTH) // 2,
                 BOX_Y + BOX_HEIGHT + 2, config.WHITE, config.BLACK)

# text() paints each character's background as well as its shape, so
# drawing a new number on top of the old one erases it -- as long as the
# new text is just as wide. "{:<5}" pads the number to 5 characters.
display.text(SMALL, "Knob:", NUMBER_X - 6 * SMALL.WIDTH, KNOB_Y,
             config.WHITE, config.BLACK)
display.text(SMALL, "{:<5}".format(0), NUMBER_X, KNOB_Y,
             config.WHITE, config.BLACK)
config.centered_text(display, SMALL, "turn the knob", KNOB_Y + 18, config.GRAY)

display.fill_rect(TRACK_X, TRACK_Y + MARKER_HEIGHT // 2 - 1,
                  NOTCHES * NOTCH_WIDTH, 2, config.GRAY)
draw_marker(0, True)

# ---------------------------------------------------------------------
# The main loop: redraw only what changed since last time round.
# ---------------------------------------------------------------------
print("Press K0, press the knob, and turn the knob. Ctrl-C to stop.")

held = [False, False]
shown_clicks = 0
shown_direction = None

while True:
    for i, (pin, name, x, color) in enumerate(BUTTONS):
        down = pin.value() == 0
        if down != held[i]:
            held[i] = down
            draw_box(x, color, down)
            print(name, "pressed" if down else "released")

    # Round the step count to the nearest whole click.
    per_click = config.ENCODER_STEPS_PER_CLICK
    clicks = (steps + per_click // 2) // per_click
    if clicks != shown_clicks:
        if clicks > shown_clicks:
            direction = "clockwise"
        else:
            direction = "counter-clockwise"
        draw_marker(shown_clicks, False)
        draw_marker(clicks, True)
        display.text(SMALL, "{:<5}".format(clicks), NUMBER_X, KNOB_Y,
                     config.WHITE, config.BLACK)
        if direction != shown_direction:
            # Padded to 17 characters so it always covers the old words.
            config.centered_text(display, SMALL, "{:^17}".format(direction),
                                 KNOB_Y + 18, config.CYAN)
            shown_direction = direction
        shown_clicks = clicks
        print("knob", direction, "-- clicks", clicks)

    time.sleep_ms(20)
