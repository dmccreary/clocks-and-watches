# Lab 06: Encoder Rotation Test
# Checks the wiring of A and B, the two outputs that tell which way the
# knob is turning. Turn the knob slowly, one click at a time, and watch
# the Thonny shell:
#
#   A=1 B=1   at rest
#   A=0 B=1   clockwise           steps=1    clicks=1
#   A=0 B=0   clockwise           steps=2    clicks=1
#   A=1 B=0   clockwise           steps=3    clicks=2
#   A=1 B=1   clockwise           steps=4    clicks=2
#
# How it works: A and B are two switches inside the knob. As the knob
# turns they change one after the other, never both at once, so the pair
# (A, B) walks around a loop of four positions:
#
#   clockwise           0,0 -> 1,0 -> 1,1 -> 0,1 -> back to 0,0
#   counter-clockwise   the same loop, backwards
#
# Each move to the next position is one "step". Which neighbor the pair
# moved to tells you which way the knob went.
#
# This knob clicks into place twice in each trip round the loop: once
# with A and B both 1, and once with both 0. So one click is two steps,
# and ENCODER_STEPS_PER_CLICK in config.py is 2. Halfway through a click
# the count is rounded to the nearest whole click.
#
# What to change in config.py if you see something else:
#
#   nothing prints at all             A and B are on the wrong pins
#   only A changes, or only B         the other one is on the wrong pin
#   it says clockwise when you        swap ENCODER_A_PIN and
#     turn the other way                ENCODER_B_PIN
#   clicks does not go up by one      set ENCODER_STEPS_PER_CLICK to
#     for each click you feel           the number of steps in one click
#
# This loop looks at the knob 1000 times a second, which is plenty for a
# slow turn. Spin it fast and you will see "missed a step": the pair
# jumped two positions between looks, and there is no telling which way
# round it went. Lab 07 fixes that with interrupts.

NAME = "06-encoder-rotation-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin
import config

a = Pin(config.ENCODER_A_PIN, Pin.IN, Pin.PULL_UP)
b = Pin(config.ENCODER_B_PIN, Pin.IN, Pin.PULL_UP)

# The four positions of (A, B), in the order a clockwise turn visits them.
CLOCKWISE = ((0, 0), (1, 0), (1, 1), (0, 1))

pair = (a.value(), b.value())
last = CLOCKWISE.index(pair)
steps = 0

print("Turn the knob slowly. Ctrl-C to stop.")
print("A={} B={}   at rest".format(pair[0], pair[1]))

while True:
    pair = (a.value(), b.value())
    now = CLOCKWISE.index(pair)
    if now != last:
        # How far round the loop did the pair move? 1 is one step
        # clockwise, 3 is one step back, and 2 is a jump across the loop.
        move = (now - last) % 4
        last = now
        if move == 1:
            steps += 1
            direction = "clockwise"
        elif move == 3:
            steps -= 1
            direction = "counter-clockwise"
        else:
            direction = "missed a step"

        # Round to the nearest whole click.
        per_click = config.ENCODER_STEPS_PER_CLICK
        clicks = (steps + per_click // 2) // per_click
        print("A={} B={}   {:<19} steps={:<4} clicks={}".format(
            pair[0], pair[1], direction, steps, clicks))
    time.sleep_ms(1)
