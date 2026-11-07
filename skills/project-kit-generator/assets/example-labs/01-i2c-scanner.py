# I2C Scanner for the SHT40 Temperature and Humidity Sensor
#
# The SHT40 is an I2C device.  Before we can read a temperature from it
# we have to prove the Pico can actually "see" the sensor on the I2C bus.
# This program asks the I2C bus "who is out there?" and prints every
# address that answers back.
#
# Wiring (standard Pico breadboard):
#   SHT40 VIN -> 3V3 OUT (pin 36)  <- NOT pin 40 (VBUS), that is 5V
#   SHT40 GND -> GND
#   SHT40 SDA -> GP0 (pin 1)       <- row one on our standard breadboard
#   SHT40 SCL -> GP1 (pin 2)       <- row two on our standard breadboard
#
# The pin numbers come from config.py. If you move a wire, change the
# number there and every lab in this kit follows.

from machine import Pin, I2C
import config

# The SHT40 always answers at one of these three addresses.
# Most breakout boards (Adafruit, SparkFun) use 0x44.
SHT40_ADDRESSES = {
    0x44: "SHT40-AD1B (most common)",
    0x45: "SHT40-BD1B",
    0x46: "SHT40-CD1B",
}

sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
i2c = I2C(config.I2C_BUS, sda=sda, scl=scl, freq=config.I2C_BUS_FREQ)

# i2c.scan() returns a list of the addresses of every device it found
devices = i2c.scan()

print("Scanning I2C bus {} on SDA=GP{} and SCL=GP{}...".format(
    config.I2C_BUS, config.I2C_SDA_PIN, config.I2C_SCL_PIN))
print()

if len(devices) == 0:
    print("No I2C devices found.")
    print()
    print("Things to check:")
    print("  1. Is VIN on pin 36 (3V3 OUT), not pin 40 (VBUS)?")
    print("  2. Is GND connected?")
    print("  3. Are SDA and SCL swapped? Try swapping them.")
    print("  4. Are the jumper wires pushed all the way into the breadboard?")
    print("TEST FAIL")
else:
    print("Found", len(devices), "device(s):")
    for device in devices:
        print("  decimal:", device, " hex:", hex(device))

    # Now check if any of those devices is our SHT40
    found_sht40 = False
    for device in devices:
        if device in SHT40_ADDRESSES:
            print()
            print("SHT40 found at", hex(device), "-", SHT40_ADDRESSES[device])
            found_sht40 = True

    print()
    if found_sht40:
        print("TEST PASS")
    else:
        print("Devices were found, but none of them is an SHT40.")
        print("The SHT40 should appear at 0x44, 0x45 or 0x46.")
        print("TEST FAIL")
