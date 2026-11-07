# 03-button-tests.py: Button Test
# Checks that the MODE, UP and DOWN buttons are wired to the right pins.
# Nothing else is used -- no display, no speaker -- so if a button does not
# show up here, the problem is that button's two wires.
#
# Press each button in turn. The Thonny shell prints its name when it goes
# down and again when it comes back up, and the Pico's onboard LED stays lit
# for as long as any button is held.
#
# Each button goes from its GPIO pin to GND. The pin's internal pull-up
# holds it at 1, and a press pulls it to 0:
#
#   MODE  GP13      UP  GP14      DOWN  GP15
#
# What can go wrong:
#   a button prints nothing    one of its wires is loose, or it goes to the
#                              wrong pin (does a DIFFERENT name print?)
#   a button reads PRESSED     its pin is touching GND, or the button is
#   before you touch it        turned 90 degrees in the breadboard so its
#                              legs are always connected
#   one press prints twice     contact bounce. This test shows it on
#                              purpose; the clock filters it out.

NAME = "03-button-tests.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config

led = Pin(config.LED_PIN, Pin.OUT)
mode, up, down = config.init_buttons()
buttons = (
    ("MODE", config.BUTTON_MODE_PIN, mode),
    ("UP", config.BUTTON_INCREMENT_PIN, up),
    ("DOWN", config.BUTTON_DECREMENT_PIN, down),
)

print()
print("Starting state (all three should say 'up'):")
last = []
for name, number, pin in buttons:
    value = pin.value()
    last.append(value)
    print("  {:<5} GP{:<3} {}".format(
        name, number, "up" if value else "PRESSED -- check the wiring"))
print()
print("Press each button. Ctrl-C to stop.")

seen = set()
all_seen = False
try:
    while True:
        any_down = False
        for i, (name, number, pin) in enumerate(buttons):
            value = pin.value()
            if value == 0:
                any_down = True
            if value != last[i]:
                last[i] = value
                if value == 0:
                    seen.add(name)
                    print("{:<5} down   ({} of 3 buttons seen)".format(
                        name, len(seen)))
                    if len(seen) == 3 and not all_seen:
                        print("      All three buttons work!")
                        all_seen = True
                else:
                    print("{:<5} up".format(name))
        led.value(1 if any_down else 0)
        time.sleep_ms(10)
finally:
    led.off()

# Try This
#   1. Hold UP and press DOWN. Does the LED stay lit? Both pins are read
#      separately, so the Pico can tell any mix of buttons apart.
#   2. Change time.sleep_ms(10) to time.sleep_ms(500). Now tap a button
#      quickly. Why are some taps missed? (lib/watchparts.py's Button uses an
#      interrupt so the clock never misses one.)
