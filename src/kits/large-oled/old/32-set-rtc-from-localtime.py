from machine import Pin, I2C
from utime import localtime
from ds1307 import DS1307
import config

sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
I2C_BUS = config.I2C_BUS
RTC_TYPE = config.RTC_TYPE
RTC_I2C_ADDR = config.RTC_I2C_ADDR

# I2C setup
i2c = I2C(I2C_BUS, scl=scl, sda=sda, freq=3000000)
print(i2c.scan())
rtc = DS1307(addr=RTC_I2C_ADDR, i2c=i2c)
print("DS1307 is on I2C address 0x{0:02x}".format(rtc.addr))
print("Before setting the time the RTC clock had: ", rtc.datetime)
print("Localtime: ", localtime())

# Set the local time
rtc.datetime = localtime()

print("After setting the time from local time the RTC had: ", rtc.datetime)

# Print the date and time in ISO8601 format: 2023-04-18T21:14:22
print("Today is {:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d} weekday:{}".format(
    rtc.year, rtc.month, rtc.day,
    rtc.hour, rtc.minute, rtc.second, rtc.weekday))

