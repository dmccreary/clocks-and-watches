# Lab 04: Test the Knob and the Button
# Tests all three controls at once, on the screen and in the Thonny shell:
#
#   1. TURN the knob     the click count goes up clockwise, down the
#                        other way, and the white marker slides along
#                        the track one notch per click
#   2. PRESS the knob    the PUSH box lights up yellow while it is down
#   3. PRESS the button  the K0 box (the square button below the knob)
#                        lights up green while it is down
#
# The A and B lights show the knob's two raw outputs, and "steps" counts
# every change of them. Turn slowly, one click at a time, and watch both.
#
# HOW THE KNOB WORKS. A and B are two switches inside the knob. As it
# turns they change one after the other, never both at once, so the pair
# (A, B) walks around a loop of four positions:
#
#   clockwise           0,0 -> 1,0 -> 1,1 -> 0,1 -> back to 0,0
#   counter-clockwise   the same loop, backwards
#
# Each move to the next position is one "step". Which neighbor the pair
# moved to tells you which way the knob went. One click you can feel is
# ENCODER_STEPS_PER_CLICK steps (config.py): 4 on this kit's knob.
#
# WHY INTERRUPTS. Drawing on the screen takes time, and a knob step that
# came and went while the program was busy drawing would be lost. So
# a.irq() and b.irq() ask MicroPython to call knob_moved() by itself the
# moment A or B changes, whatever the main loop is doing. knob_moved()
# only counts the step; the main loop does the slow drawing whenever it
# gets round to it. The two buttons do not need interrupts: a press lasts
# far longer than one trip round the loop.
#
# What to change in config.py if you see something else:
#
#   nothing happens when you turn     A and B are on the wrong pins --
#                                       ENCODER_A_PIN, ENCODER_B_PIN
#   only one of the A/B lights        the other one is on the wrong pin
#     ever changes
#   clockwise counts DOWN             swap ENCODER_A_PIN and
#                                       ENCODER_B_PIN
#   one click you feel counts 2,      set ENCODER_STEPS_PER_CLICK to
#     or two clicks count 1             the number of steps in one click
#   PUSH or K0 never lights up        ENCODER_PUSH_PIN or BUTTON_K0_PIN
#
# A wrong button pin never crashes anything. An unconnected pull-up pin
# reads 1 forever, which looks exactly like "not pressed" -- the box
# simply never lights.

NAME = "04-test-knob.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin
import config

display = config.init_display()
a, b, push, k0 = config.init_controls()

# ---------------------------------------------------------------------
# The knob: count steps in an interrupt handler.
# ---------------------------------------------------------------------
# The four positions of (A, B), in the order a clockwise turn visits them.
CLOCKWISE = ((0, 0), (1, 0), (1, 1), (0, 1))

steps = 0
missed = 0
last = CLOCKWISE.index((a.value(), b.value()))


def knob_moved(pin):
    global steps, last, missed
    now = CLOCKWISE.index((a.value(), b.value()))
    move = (now - last) % 4
    last = now
    if move == 1:
        steps += 1
    elif move == 3:
        steps -= 1
    elif move == 2:
        missed += 1          # jumped across the loop: no telling which way


a.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)
b.irq(knob_moved, Pin.IRQ_RISING | Pin.IRQ_FALLING)

# ---------------------------------------------------------------------
# The screen layout.
# ---------------------------------------------------------------------
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT
DIM = config.color565(50, 50, 50)

TITLE_Y = 6

BOX_Y = 34
BOX_WIDTH = 100
BOX_HEIGHT = 44

# (pin, name, x of its box, color while held)
BUTTONS = (
    (push, "PUSH", 40, config.YELLOW),
    (k0, "K0", 180, config.GREEN),
)

CLICKS_Y = 104          # "Clicks:" and the number, in the big font
NUMBER_X = 184          # where the number starts
DIRECTION_Y = 140

NOTCHES = 20
NOTCH_WIDTH = 14
TRACK_X = (config.WIDTH - NOTCHES * NOTCH_WIDTH) // 2
TRACK_Y = 166
MARKER_HEIGHT = 18

RAW_Y = 206             # the A and B lights, and the step count
LIGHT_SIZE = 14


def draw_box(name, x, color, down):
    """Fill the inside of a button's box -- its color if held, else black
    -- and write its name in the middle."""
    inside = color if down else config.BLACK
    display.fill_rect(x + 3, BOX_Y + 3, BOX_WIDTH - 6, BOX_HEIGHT - 6, inside)
    display.text(SMALL, name, x + (BOX_WIDTH - len(name) * SMALL.WIDTH) // 2,
                 BOX_Y + (BOX_HEIGHT - SMALL.HEIGHT) // 2,
                 config.BLACK if down else config.GRAY, inside)


def draw_marker(clicks, visible):
    """Draw the marker at its notch, or put back the track it covered."""
    x = TRACK_X + (clicks % NOTCHES) * NOTCH_WIDTH
    display.fill_rect(x + 1, TRACK_Y, NOTCH_WIDTH - 2, MARKER_HEIGHT,
                      config.WHITE if visible else config.BLACK)
    if not visible:
        display.fill_rect(x, TRACK_Y + MARKER_HEIGHT // 2 - 1,
                          NOTCH_WIDTH, 3, config.GRAY)


def draw_light(x, level):
    """One of the A/B lights: bright for 1, dim for 0."""
    display.fill_rect(x, RAW_Y + 1, LIGHT_SIZE, LIGHT_SIZE,
                      config.CYAN if level else DIM)
    display.text(SMALL, str(level), x + LIGHT_SIZE + 4, RAW_Y,
                 config.WHITE, config.BLACK)


display.fill(config.BLACK)
config.centered_text(display, SMALL, "Knob and Button Test", TITLE_Y,
                     config.CYAN)

for pin, name, x, color in BUTTONS:
    display.fill_rect(x, BOX_Y, BOX_WIDTH, BOX_HEIGHT, config.GRAY)
    draw_box(name, x, color, False)

# text() paints each character's background as well as its shape, so
# drawing a new number on top of the old one erases it -- as long as the
# new text is just as wide. "{:<5}" pads the number to 5 characters.
display.text(BIG, "Clicks:", NUMBER_X - 8 * BIG.WIDTH, CLICKS_Y,
             config.WHITE, config.BLACK)
display.text(BIG, "{:<5}".format(0), NUMBER_X, CLICKS_Y,
             config.WHITE, config.BLACK)
config.centered_text(display, SMALL, "turn the knob", DIRECTION_Y, config.GRAY)

display.fill_rect(TRACK_X, TRACK_Y + MARKER_HEIGHT // 2 - 1,
                  NOTCHES * NOTCH_WIDTH, 3, config.GRAY)
draw_marker(0, True)

display.text(SMALL, "A", 40, RAW_Y, config.WHITE, config.BLACK)
display.text(SMALL, "B", 104, RAW_Y, config.WHITE, config.BLACK)
display.text(SMALL, "steps", 176, RAW_Y, config.WHITE, config.BLACK)
A_LIGHT_X = 54
B_LIGHT_X = 118
STEPS_X = 224

# ---------------------------------------------------------------------
# The main loop: redraw only what changed since last time round.
# ---------------------------------------------------------------------
print("Turn the knob, press the knob, and press K0. Ctrl-C to stop.")
print("A={} B={}   at rest".format(a.value(), b.value()))

held = [False, False]
shown_clicks = 0
shown_direction = None
shown_raw = None
shown_steps = None
shown_missed = 0

while True:
    for i, (pin, name, x, color) in enumerate(BUTTONS):
        down = pin.value() == 0
        if down != held[i]:
            held[i] = down
            draw_box(name, x, color, down)
            print(name, "pressed" if down else "released")

    # Take one snapshot of the knob for this whole pass. The interrupt
    # handler keeps changing `steps` while the screen is being drawn, so
    # reading it again later would print a step count that does not match
    # the click count worked out from it.
    now_steps = steps
    raw = (a.value(), b.value())
    if raw != shown_raw:
        draw_light(A_LIGHT_X, raw[0])
        draw_light(B_LIGHT_X, raw[1])
        shown_raw = raw
    if now_steps != shown_steps:
        display.text(SMALL, "{:<6}".format(now_steps), STEPS_X, RAW_Y,
                     config.WHITE, config.BLACK)
        shown_steps = now_steps

    # Round the step count to the nearest whole click. Turn the knob fast
    # and several clicks go by in one pass of the loop, so the shell skips
    # numbers (2, 3, 6, 7 ...). Nothing is lost: the interrupt counted
    # every step, and the total is still right.
    per_click = config.ENCODER_STEPS_PER_CLICK
    clicks = (now_steps + per_click // 2) // per_click
    if clicks != shown_clicks:
        if clicks > shown_clicks:
            direction = "clockwise"
        else:
            direction = "counter-clockwise"
        draw_marker(shown_clicks, False)
        draw_marker(clicks, True)
        display.text(BIG, "{:<5}".format(clicks), NUMBER_X, CLICKS_Y,
                     config.WHITE, config.BLACK)
        if direction != shown_direction:
            # Padded to 17 characters so it always covers the old words.
            config.centered_text(display, SMALL, "{:^17}".format(direction),
                                 DIRECTION_Y, config.CYAN)
            shown_direction = direction
        shown_clicks = clicks
        print("A={} B={}   {:<19} steps={:<4} clicks={}".format(
            raw[0], raw[1], direction, now_steps, clicks))

    if missed != shown_missed:
        print("missed a step ({} so far) -- turn a little slower".format(
            missed))
        shown_missed = missed

    time.sleep_ms(20)
