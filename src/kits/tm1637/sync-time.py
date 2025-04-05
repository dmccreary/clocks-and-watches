# DS3231 RTC Time Synchronization Program
# Gets time from localtime() and sets the DS3231 RTC

from machine import Pin, I2C
import time
import utime

# Import DS3231 driver
from ds3231 import DS3231, bcdtodec, dectobcd

# I2C setup
I2C_BUS = 0
I2C_CLK_PIN = 1
I2C_DST_PIN = 0

def print_datetime(dt):
    """Format datetime tuple for display"""
    year, month, day, weekday, hour, minute, second, _ = dt
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = days[weekday-1] if 1 <= weekday <= 7 else "Unknown"
    
    print(f"Date: {year}/{month:02d}/{day:02d} ({day_name})")
    print(f"Time: {hour:02d}:{minute:02d}:{second:02d}")
    print("-----------------------------")

def sync_time_to_ds3231():
    print("\n=== DS3231 Time Synchronization Program ===\n")
    
    # Initialize I2C
    print(f"Initializing I2C: Bus={I2C_BUS}, SCL={I2C_CLK_PIN}, SDA={I2C_DST_PIN}")
    i2c = I2C(I2C_BUS, scl=Pin(I2C_CLK_PIN), sda=Pin(I2C_DST_PIN), freq=100000)
    
    # Initialize RTC
    rtc = DS3231(i2c)
    
    # Read current time from DS3231 before sync
    print("\nCurrent DS3231 RTC Time (Before Sync):")
    current_time = rtc.datetime()
    print_datetime(current_time)
    
    # Get time from Pico's internal RTC (set by Thonny)
    pico_time = utime.localtime()
    year, month, day, hour, minute, second, weekday, _ = pico_time
    
    # Convert weekday: utime uses 0-6 (Mon-Sun), DS3231 uses 1-7 (Mon-Sun)
    weekday = weekday + 1
    
    print("\nPico's internal RTC Time:")
    print(f"Date: {year}/{month:02d}/{day:02d} (Weekday {weekday})")
    print(f"Time: {hour:02d}:{minute:02d}:{second:02d}")
    print("-----------------------------")
    
    # Prepare time tuple for DS3231
    ds3231_time = (year, month, day, weekday, hour, minute, second)
    print("\nSetting DS3231 with Pico's time...")
    
    # Fix for hour register issue - directly write to hour register
    # First, set the rest of the time using the normal method
    rtc.datetime(ds3231_time)
    
    # Now directly write to the hour register (0x02)
    # Convert hour to BCD format for the DS3231
    hour_bcd = dectobcd(hour)
    # Write directly to the hour register
    i2c.writeto_mem(rtc.addr, 0x02, bytes([hour_bcd]))
    
    # Wait a moment
    time.sleep(1)
    
    # Read back the time from DS3231 after sync
    print("\nDS3231 RTC Time (After Sync):")
    new_time = rtc.datetime()
    print_datetime(new_time)
    
    # Verify the hour was set correctly
    if new_time[4] == hour:
        print("✅ Time synchronization successful!")
    else:
        print(f"❌ Hour still incorrect: Set {hour}, Read {new_time[4]}")
        
        # One more attempt with raw register manipulation
        print("\nAttempting direct register manipulation...")
        
        # Read all time registers
        time_regs = bytearray(7)
        i2c.readfrom_mem_into(rtc.addr, 0, time_regs)
        
        print(f"Current registers: {[hex(x) for x in time_regs]}")
        
        # Set hour register (0x02) with proper value
        time_regs[2] = hour_bcd
        
        # Write all registers back
        i2c.writeto_mem(rtc.addr, 0, time_regs)
        
        # Wait a moment
        time.sleep(1)
        
        # Read back the time
        final_time = rtc.datetime()
        print("\nDS3231 RTC Time (Final Attempt):")
        print_datetime(final_time)
        
        if final_time[4] == hour:
            print("✅ Time synchronization successful on second attempt!")
        else:
            print(f"❌ Hour still incorrect after raw register manipulation")
    
    print("\n=== Time Synchronization Complete ===")

if __name__ == "__main__":
    sync_time_to_ds3231()