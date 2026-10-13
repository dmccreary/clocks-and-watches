# Lab 01: Blink the Onboard LED
# Confirms the Pico 2 W itself works before any display wiring matters.
# Nothing else is imported -- if this fails, the problem is the board,
# the USB cable, or the MicroPython firmware, not the display.
#
# The LED blinks once a second: half a second on, half a second off.
#
# On a Pico W or Pico 2 W the LED is wired to the wireless chip, not to
# GP25 like on a plain Pico. Pin("LED") works on every board; Pin(25)
# does not. If the LED stays dark, check that you flashed the WiFi
# firmware for your board (RPI_PICO_W or RPI_PICO2_W), not the plain
# RPI_PICO or RPI_PICO2 one.

NAME = "01-blink-onboard-led.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
