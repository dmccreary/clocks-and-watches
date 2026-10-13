# Lab 04: Button Test
# Checks the wiring of K0, the square push button below the knob. Press
# it and let go, and watch the Thonny shell:
#
#   K0 pressed   (press number 1)
#   K0 released
#
# K0 is on GP11. The pin reads 1 while the button is up and 0 while it is
# held down -- a pull-up resistor holds the pin high until the button
# connects it to GND.
#
# If nothing prints when you press the button, K0 is not on GP11. An
# unconnected pull-up pin reads 1 forever, which looks exactly like "not
# pressed", so this lab never crashes on a wrong pin -- it just never
# reacts. Fix BUTTON_K0_PIN in config.py.
#
# The loop looks at the button 50 times a second. That is fast enough to
# catch the quickest press, and slow enough to skip over "bounce": the
# few thousandths of a second when a switch's metal contacts chatter as
# they close.

NAME = "04-button-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin
import config

k0 = Pin(config.BUTTON_K0_PIN, Pin.IN, Pin.PULL_UP)

print("Press the K0 button, below the knob. Ctrl-C to stop.")

presses = 0
was_down = False

while True:
    down = k0.value() == 0
    if down != was_down:
        was_down = down
        if down:
            presses += 1
            print("K0 pressed   (press number {})".format(presses))
        else:
            print("K0 released")
    time.sleep_ms(20)
