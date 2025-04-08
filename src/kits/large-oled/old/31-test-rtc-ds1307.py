from machine import Pin, I2C
from ds1307 import DS1307
from utime import sleep, localtime

# Use the same pins as your working examples
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

# Debug: Print found devices
devices = i2c.scan()
print("Found I2C devices:", [hex(device) for device in devices])

# Only proceed if we find our device
if 0x68 in devices:
    rtc = DS1307(i2c=i2c)  # No need to specify addr - it's default in DS1307 class
    try:
        print("Current RTC time:", rtc.datetime)
    except OSError as e:
        print("Error reading RTC:", e)
else:
    print("DS1307 not found! Check connections.")