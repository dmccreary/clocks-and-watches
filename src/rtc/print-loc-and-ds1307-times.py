from machine import Pin, I2C
from utime import localtime, sleep
from ds1307 import DS1307

I2C_DATA_PIN = 16
I2C_CLOCK_PIN = 17

I2C_ADDR = 0x68     # DEC 104, HEX 0x68

i2c = I2C(0, scl=Pin(I2C_CLOCK_PIN), sda=Pin(I2C_DATA_PIN), freq=800000)
rtc = DS1307(addr=I2C_ADDR, i2c=i2c)

def printTimes():


    now = localtime()
    loc_year = now[0]
    loc_month = now[1]
    loc_day = now[2]
    loc_hour = now[3]
    loc_minute = now[4]
    loc_second = now[5]
    print(f"localtime(): {loc_month}/{loc_day}/{loc_year} {loc_hour:02d}:{loc_minute:02d}:{loc_second:02d}")

    rtc_time = rtc.datetime
    rtc_year = rtc_time[0]
    rtc_month = rtc_time[1]
    rtc_day = rtc_time[2]
    rtc_hour = rtc_time[3]
    rtc_minute = rtc_time[4]
    rtc_second = rtc_time[5]
    print(f"Time from DS1307 RTC: {rtc_month}/{rtc_day}/{rtc_year} {rtc_hour:02d}:{rtc_minute:02d}:{rtc_second:02d}")

print("   localtime()", localtime())
print("rtc.datetime()", rtc.datetime)
while True:
    
    printTimes()
    print("")
    sleep(1)
