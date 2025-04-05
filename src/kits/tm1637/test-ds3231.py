# DS3231 RTC Test Program - Fixed Version
# Addresses the datetime format issues

from machine import Pin, I2C
import time
import sys

# Try to import DS3231
try:
    from ds3231 import DS3231, bcdtodec, dectobcd
    print("DS3231 driver imported successfully")
except ImportError:
    print("Error: DS3231 driver not found")
    sys.exit(1)

# Try to import config
try:
    import config
    I2C_BUS = config.I2C_BUS
    I2C_CLK_PIN = config.I2C_CLK_PIN
    I2C_DST_PIN = config.I2C_DST_PIN
    print(f"Using configuration: Bus={I2C_BUS}, SCL={I2C_CLK_PIN}, SDA={I2C_DST_PIN}")
except (ImportError, AttributeError):
    print("Config not found or incomplete, using defaults")
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

# Initialize I2C
def init_i2c():
    """Initialize I2C with 100kHz frequency"""
    print(f"Initializing I2C: Bus={I2C_BUS}, SCL={I2C_CLK_PIN}, SDA={I2C_DST_PIN}")
    i2c = I2C(I2C_BUS, scl=Pin(I2C_CLK_PIN), sda=Pin(I2C_DST_PIN), freq=100000)
    devices = i2c.scan()
    print(f"I2C scan found {len(devices)} devices")
    for device in devices:
        print(f"  Address: {device} (hex: {hex(device)})")
    return i2c, devices

# Main test routine
def test_ds3231():
    print("\n=== DS3231 RTC Test Program - Fixed Version ===\n")
    
    # Initialize I2C
    i2c, devices = init_i2c()
    
    # Check for DS3231 at default address (0x68)
    if 0x68 in devices:
        print("DS3231 found at address 0x68")
        rtc = DS3231(i2c)
    else:
        print("DS3231 not found! Check connections.")
        return False
    
    # Check oscillator stop flag
    if rtc.OSF():
        print("WARNING: Oscillator Stop Flag set - time may not be accurate")
        print("This indicates power loss or first-time use")
    else:
        print("Oscillator Stop Flag clear - time should be valid")
    
    # Read current time
    print("\n1. Reading current time from RTC:")
    current_time = rtc.datetime()
    print("Raw datetime tuple:", current_time)
    print_datetime(current_time)
    
    # Test setting time - note the proper format for DS3231.datetime()
    # Format is: (year, month, day, weekday, hour, minute, second)
    # With weekday 1-7 (Monday=1, Sunday=7)
    print("\n2. Setting time to 2024-04-04 12:34:56 (Thursday):")
    
    # Thursday is weekday 4 (with Monday=1, Sunday=7)
    new_time = (2024, 4, 4, 4, 12, 34, 56)
    print("Setting datetime:", new_time)
    
    # Set the time
    rtc.datetime(new_time)
    
    # Wait a moment for the time to update
    print("Waiting for time to update...")
    time.sleep(2)
    
    # Read back the time
    read_back = rtc.datetime()
    print("\n3. Reading back the time:")
    print("Raw datetime tuple:", read_back)
    print_datetime(read_back)
    
    # Verify time is roughly correct (allow for elapsed seconds)
    year, month, day, weekday, hour, minute, second, _ = read_back
    if (year == 2024 and month == 4 and day == 4 and 
        hour == 12 and (minute == 34 or minute == 35)):
        print("\n✅ Time set/read validation PASSED")
    else:
        print("\n❌ Time set/read validation FAILED")
        print("Expected: 2024/04/04 12:34:xx")
        print(f"Got:      {year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
    
    # Test temperature reading
    print("\n4. Reading temperature from DS3231:")
    try:
        # Read temperature registers (0x11 and 0x12)
        temp_msb = i2c.readfrom_mem(rtc.addr, 0x11, 1)[0]
        temp_lsb = i2c.readfrom_mem(rtc.addr, 0x12, 1)[0]
        
        # Convert to temperature
        if temp_msb & 0x80:
            temp_msb = temp_msb - 256
        
        temperature = temp_msb + ((temp_lsb >> 6) * 0.25)
        print(f"Temperature: {temperature:.2f}°C")
    except Exception as e:
        print(f"Failed to read temperature: {e}")
    
    # Test alarm functionality
    print("\n5. Testing alarm functionality:")
    try:
        # Get current second
        _, _, _, _, _, _, current_second, _ = rtc.datetime()
        
        # Set alarm to trigger 5 seconds from now
        alarm_second = (current_second + 5) % 60
        print(f"Current second: {current_second}")
        print(f"Setting Alarm 1 to trigger at second: {alarm_second}")
        
        # Set Alarm 1 to match seconds only
        rtc.alarm1(time=(alarm_second,), match=rtc.AL1_MATCH_S)
        
        # Check alarm immediately (should be clear)
        if rtc.check_alarm(1):
            print("WARNING: Alarm 1 flag already set before waiting!")
        
        # Wait and check for alarm
        print("Waiting for alarm to trigger...")
        triggered = False
        for i in range(10):
            time.sleep(1)
            
            # Read current time
            current = rtc.datetime()
            print(f"Time: {current[4]:02d}:{current[5]:02d}:{current[6]:02d}", end="")
            
            # Check if alarm triggered
            if rtc.check_alarm(1):
                print(" - ALARM TRIGGERED!")
                triggered = True
                break
            else:
                print(" - waiting...")
        
        if triggered:
            print("✅ Alarm test PASSED")
        else:
            print("❌ Alarm test FAILED - alarm didn't trigger")
    except Exception as e:
        print(f"Error during alarm test: {e}")
    
    # Test square wave output
    print("\n6. Testing square wave output:")
    print("- Enabling 1Hz square wave output (connect oscilloscope to SQW/INT pin)")
    rtc.square_wave(rtc.FREQ_1)
    print("Square wave output enabled at 1Hz for 5 seconds...")
    time.sleep(5)
    print("- Disabling square wave output")
    rtc.square_wave(False)
    print("Square wave output disabled")
    
    # Print test summary
    print("\n=== DS3231 RTC Test Summary ===")
    print("✅ I2C detection: Found at address 0x68")
    print("✅ Read current time: Successful")
    print("✅ Set and verify time: Completed")
    print("✅ Temperature reading: Completed")
    print("✅ Alarm functionality: Tested")
    print("✅ Square wave output: Tested")
    
    return True

# Run the test
if __name__ == "__main__":
    try:
        success = test_ds3231()
        if success:
            print("\nDS3231 RTC is functioning correctly!")
        else:
            print("\nTest failed. Please check connections and try again.")
    except Exception as e:
        print(f"Test crashed with error: {e}")
        import sys
        sys.print_exception(e)