from machine import Pin, I2C
from utime import localtime
from ds3231 import DS3231
import config

sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
I2C_BUS = config.I2C_BUS
RTC_TYPE = config.RTC_TYPE
RTC_I2C_ADDR = config.RTC_I2C_ADDR

# I2C setup
i2c = I2C(I2C_BUS, scl=scl, sda=sda, freq=3000000)
print("I2C devices found:", [hex(addr) for addr in i2c.scan()])

# Initialize DS3231
rtc = DS3231(i2c=i2c, addr=RTC_I2C_ADDR)
print("DS3231 is on I2C address 0x{0:02x}".format(rtc.addr))
print("Before setting the time the RTC clock had:", rtc.datetime())

# Get local time
print("Localtime:", localtime())

# Set the RTC time from localtime
# localtime returns: (year, month, day, hour, minute, second, weekday, yearday)
# DS3231 expects: (year, month, day, hour, minutes, seconds, weekday)
rtc.datetime(localtime()[:7])  # Use first 7 elements of localtime tuple

print("After setting the time from local time the RTC had:", rtc.datetime())

# Print the date and time in ISO8601 format: 2023-04-18T21:14:22
dt = rtc.datetime()
print(f"{dt[0]:04d}-{dt[1]:02d}-{dt[2]:02d}T{dt[4]:02d}:{dt[5]:02d}:{dt[6]:02d}")