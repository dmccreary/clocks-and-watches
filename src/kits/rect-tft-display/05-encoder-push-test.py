# Lab 05: Encoder Push Test
# Checks the wiring of PUSH, the switch inside the knob. Press the knob
# straight down, like a button, and let go. Watch the Thonny shell:
#
#   PUSH pressed   (press number 1)
#   PUSH released
#
# PUSH is on GP10. It works just like K0 in lab 04: the pin reads 1 while
# the knob is up and 0 while it is pressed down.
#
# If nothing prints when you press the knob, PUSH is not on GP10. Fix
# ENCODER_PUSH_PIN in config.py.
#
# Pressing the knob without turning it takes a steady hand. Turning is
# tested on its own in lab 06.

NAME = "05-encoder-push-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin
import config

push = Pin(config.ENCODER_PUSH_PIN, Pin.IN, Pin.PULL_UP)

print("Press the knob straight down. Ctrl-C to stop.")

presses = 0
was_down = False

while True:
    down = push.value() == 0
    if down != was_down:
        was_down = down
        if down:
            presses += 1
            print("PUSH pressed   (press number {})".format(presses))
        else:
            print("PUSH released")
    time.sleep_ms(20)
