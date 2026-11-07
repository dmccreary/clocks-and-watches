# Test the Button and the Blinking LED
#
# Before we use the button in the six-mode display (program 09), let's prove it
# works. This program does not need the sensor or the screen.
#
# Wiring (see config.py):
#   button leg 1 -> GP15 (physical pin 20, the bottom left corner of the Pico)
#   button leg 2 -> GND  (physical pin 18 is the closest GND pin)
#
# You do NOT need a resistor. button.py turns on the Pico's own pull-up
# resistor, which holds GP15 at 3.3 V until you press the button.
#
# What to do:
#   1. Run this program. The green LED on the Pico blinks once a second.
#      That blink is the "heartbeat". In program 09 it blinks every time the
#      sensor is read. If it ever stops, the program has stopped.
#   2. Press the button three times. Try a quick tap, and try holding it for
#      a second. The Shell tells you what kind of press it saw.
#
# A press is a "tap" if it is shorter than LONG_PRESS_MS (in config.py).
# That is the press that changes to the next mode in program 09. A longer
# press is a "hold". Holding switches between F and C.

import time
import config
from button import Button
from heartbeat import Heartbeat, onboard_led

PRESSES_NEEDED = 3

led = Heartbeat(onboard_led(config.BUILT_IN_LED_PIN), config.HEARTBEAT_MS)
button = Button(config.BUTTON_PIN, config.BUTTON_DEBOUNCE_MS)

print("Button on GP{}. Press it {} times.".format(config.BUTTON_PIN, PRESSES_NEEDED))
print("Taps shorter than {} ms are ignored as button bounce.".format(config.BUTTON_DEBOUNCE_MS))
print("The green LED blinks once a second. Press Ctrl-C to give up.")
print()

# If the button already reads "pressed" before we touch it, the wiring is wrong.
if button.is_down():
    print("The button reads PRESSED, but nobody is touching it.")
    print("Check that one leg goes to GP15 and the other goes to GND.")
    print()

presses = 0
next_beat = time.ticks_ms()

try:
    while presses < PRESSES_NEEDED:
        now = time.ticks_ms()

        if time.ticks_diff(now, next_beat) >= 0:
            led.beat(now)
            next_beat = time.ticks_add(now, 1000)
        led.tick(now)

        length = button.next_press()
        if length > 0:
            presses = presses + 1
            if length < config.LONG_PRESS_MS:
                kind = "tap (next mode)"
            elif length < config.CLEAR_PRESS_MS:
                kind = "hold (switch F and C)"
            else:
                kind = "long hold (clear the records in Hi/Lo)"
            print("Press {}: {} ms, a {}".format(presses, length, kind))

        time.sleep_ms(10)

    print()
    print("The button works!")
    print("TEST PASS")

except KeyboardInterrupt:
    print()
    print("No presses were seen.")
    print("Check the two button wires, and that GP15 is the pin you used.")
    print("TEST FAIL")

finally:
    led.off()
