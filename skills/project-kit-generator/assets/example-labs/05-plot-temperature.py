# Plot Temperature in Thonny's Plotter
#
# Run 01-i2c-scanner.py and 02-get-single-temp-reading.py first.
#
# This is the same idea as 04-plot-temp-and-humidity.py, but it draws only
# ONE line: the temperature.  It prints one number on every line and
# nothing else:
#
#     80.49
#     80.53
#
# The number is the temperature in degrees Fahrenheit.  The sensor measures
# in Celsius, so the program changes each reading to Fahrenheit before it
# prints it.  Thonny's Plotter draws a moving line graph of any numbers
# your program prints, so you get a live picture of how the temperature is
# changing.
#
# To see the graph:
#   1. Start Thonny and open this file.
#   2. Choose View > Plotter from the menu.  A graph panel appears
#      next to the Shell.
#   3. Click the green Run button.
#   4. Press a fingertip on the sensor and watch the line climb.
#
# Press Ctrl-C or the red Stop button to stop.
#
# Want Celsius instead?  In the loop at the bottom, print temperature_c
# instead of temperature_f.
#
# IMPORTANT: this program prints ONLY numbers.  The Plotter tries to
# graph every number it sees, so a stray "Hello" or "TEST PASS" would
# either clutter the graph or be drawn as a bogus data point.  That is
# why there is no heading row and no summary here.  Use
# 03-continuous-logging.py when you want labels, CSV and a summary.
#
# Wiring (standard Pico breadboard):
#   SHT40 VIN -> 3V3 OUT (pin 36)  <- NOT pin 40 (VBUS), that is 5V
#   SHT40 GND -> GND
#   SHT40 SDA -> GP0 (pin 1)
#   SHT40 SCL -> GP1 (pin 2)

from machine import Pin, I2C
import time
import config

# All of these come from config.py so you only ever edit them in one place.
SHT40_ADDR = config.SHT40_ADDR
CMD_MEASURE_HIGH = config.SHT40_CMD_MEASURE_HIGH
CMD_SOFT_RESET = config.SHT40_CMD_SOFT_RESET

SAMPLE_SECONDS = config.PLOT_SECONDS  # wait between points on the graph

sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
i2c = I2C(config.I2C_BUS, sda=sda, scl=scl, freq=config.I2C_BUS_FREQ)


def crc8(data):
    """Check that the bytes we read were not scrambled on the way."""
    crc = 0xFF
    for byte in data:
        crc = crc ^ byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


def read_temperature_c():
    """Return one temperature reading in Celsius."""
    i2c.writeto(SHT40_ADDR, bytes([CMD_MEASURE_HIGH]))
    time.sleep_ms(config.SHT40_MEASURE_MS)

    # The sensor always answers with 6 bytes: 2 of temperature, 1 checksum,
    # 2 of humidity, and 1 more checksum.  We read all 6, but this program
    # only uses the temperature half.
    data = i2c.readfrom(SHT40_ADDR, 6)

    if crc8(data[0:2]) != data[2]:
        raise ValueError("Temperature checksum failed")

    temp_ticks = (data[0] << 8) | data[1]
    return -45.0 + 175.0 * temp_ticks / 65535.0


# Give the sensor a clean start.
#
# If the last program was stopped in the middle of taking a reading, the
# sensor can be left half way through a conversation and it will refuse to
# answer. Unplugging the Pico and plugging it back in always clears this.
try:
    i2c.writeto(SHT40_ADDR, bytes([CMD_SOFT_RESET]))
    time.sleep_ms(10)
except OSError:
    print("The sensor is not answering.")
    print()
    print("This almost always means the last program was stopped in the")
    print("middle of a reading. Unplug the Pico from USB, plug it back in,")
    print("and run this program again.")
    raise SystemExit

while True:
    try:
        temperature_c = read_temperature_c()

        # Celsius to Fahrenheit: times 9, divide by 5, then add 32.
        temperature_f = temperature_c * 9.0 / 5.0 + 32.0

        # One number and nothing else.
        # Thonny draws one line on the graph for it.
        print("{:.2f}".format(temperature_f))

    except (OSError, ValueError):
        # A reading failed.  We print nothing at all and try again next
        # time around, because printing an error message here would draw
        # junk on the graph.  If you see the graph freeze, stop the
        # program and run 01-i2c-scanner.py to check the wiring.
        pass

    time.sleep(SAMPLE_SECONDS)
