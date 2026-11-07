# heartbeat.py -- blink the onboard LED so you can see the program is alive.
#
#   beat()   one short blink. We do this every time the sensor is read, so the
#            speed of the blinking IS the speed of the sensor readings.
#   alarm()  two quick blinks. We do this when a reading fails.
#
# If the LED goes solid (always on or always off), the program has stopped.
#
# The blinks are timed with ticks_ms() instead of sleep(), so blinking never
# makes the rest of the program wait.
import time


def onboard_led(fallback_pin_number):
    """Find the Pico's built-in LED.

    Newer MicroPython calls it Pin("LED") on every Pico, including the Pico W
    (where the LED hangs off the wireless chip). If that name is not known,
    we fall back to plain GP25, which is the LED on an older Pico."""
    from machine import Pin
    try:
        return Pin("LED", Pin.OUT)
    except (ValueError, TypeError):
        return Pin(fallback_pin_number, Pin.OUT)


class Heartbeat:
    def __init__(self, led, pulse_ms):
        self.led = led
        self.pulse_ms = pulse_ms
        self.steps = []          # a list of (time to act, LED value)
        self.led.value(0)

    def _start(self, now, pattern):
        # pattern is a list of (milliseconds from now, LED value)
        self.steps = [(time.ticks_add(now, when), value) for when, value in pattern]

    def beat(self, now):
        self._start(now, ((0, 1), (self.pulse_ms, 0)))

    def alarm(self, now):
        p = self.pulse_ms
        self._start(now, ((0, 1), (p, 0), (p * 2, 1), (p * 3, 0)))

    def tick(self, now):
        """Call this often. It turns the LED on and off at the right moments."""
        while self.steps and time.ticks_diff(now, self.steps[0][0]) >= 0:
            self.led.value(self.steps[0][1])
            self.steps.pop(0)

    def off(self):
        self.steps = []
        self.led.value(0)
