# Lab 00: Blink the Onboard LED
# Confirms the Pico 2 W itself works before any display wiring matters.
# Nothing else is imported -- if this fails, the problem is the board,
# the USB cable, or the MicroPython firmware, not the display.
#
# On a Pico 2 W the LED is wired to the wireless chip, not to GP25 like
# on a plain Pico. Pin("LED") works on both boards; Pin(25) does not.
# If the LED stays dark, check that you flashed the RPI_PICO2_W firmware
# and not the plain RPI_PICO2 one.

NAME = "00-blink-onboard-led.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    sleep(0.5)
