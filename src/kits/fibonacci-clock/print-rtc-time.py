from machine import I2C, Pin
import time
import ds3231
# I2C setup
I2C_SDA_PIN = 0  # data pin
I2C_SCL_PIN = 1  # clock
I2C_BUS = 0
I2C_FREQUENCY = 200000
print("I2C Data SDA on pin: ", I2C_SDA_PIN)
print("I2C Clock SCL on pin: ", I2C_SCL_PIN)
print("Checking for devices on Bus", I2C_BUS, "at frequency", I2C_FREQUENCY)
# Initialize I2C
i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQUENCY)
scan_result = i2c.scan()
print(scan_result)
print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])
# Initialize DS3231 RTC
rtc = ds3231.DS3231(i2c)
# Function to read time directly from registers to avoid library issues
def read_time_directly():
    try:
        # Read 7 bytes from register 0x00 (time registers)
        data = i2c.readfrom_mem(0x68, 0, 7)
        
        # Convert BCD values to decimal
        def bcd2dec(bcd):
            return ((bcd >> 4) * 10) + (bcd & 0x0F)
        
        second = bcd2dec(data[0])
        minute = bcd2dec(data[1])
        
        # Handle hour based on 12/24 hour mode
        hour_reg = data[2]
        if hour_reg & 0x40:  # 12-hour mode
            hour = bcd2dec(hour_reg & 0x1F)
            is_pm = bool(hour_reg & 0x20)  # PM bit
        else:  # 24-hour mode
            hour = bcd2dec(hour_reg & 0x3F)
            is_pm = hour >= 12
            
        weekday = bcd2dec(data[3])
        day = bcd2dec(data[4])
        month = bcd2dec(data[5] & 0x7F)
        year = bcd2dec(data[6]) + 2000
        
        return (year, month, day, weekday, hour, minute, second, is_pm)
    except Exception as e:
        print(f"Error reading time: {e}")
        return (0, 0, 0, 0, 0, 0, 0, False)
# Function to read temperature directly from registers
def read_temperature():
    try:
        # Temperature registers are 0x11 (MSB) and 0x12 (LSB)
        temp_msb = i2c.readfrom_mem(0x68, 0x11, 1)[0]
        temp_lsb = i2c.readfrom_mem(0x68, 0x12, 1)[0] >> 6  # Top 2 bits only
        
        # Handle signed temperature value (2's complement)
        if temp_msb & 0x80:  # If negative (bit 7 is 1)
            temp_msb = -(~temp_msb & 0x7F) - 1
        
        # Convert to temperature value with 0.25°C resolution
        temp_c = temp_msb + ((temp_lsb & 0x03) * 0.25)
        temp_f = (temp_c * 9/5) + 32
        
        return temp_c, temp_f
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return (0, 0)

# Convert 24-hour time to 12-hour format
def to_12hour_format(hour, is_pm=None):
    # Determine AM/PM if not provided
    if is_pm is None:
        is_pm = hour >= 12
    
    # Convert hour to 12-hour format
    if hour == 0:
        hour_12 = 12  # 12 AM
    elif hour > 12:
        hour_12 = hour - 12
    else:
        hour_12 = hour
        
    # Return hour and AM/PM indicator
    return hour_12, "PM" if is_pm else "AM"

# Main loop to read and display time
print("\nReading time from DS3231 RTC...")
try:
    while True:
        # Get date and time
        try:
            # First try using the library
            dt = rtc.datetime()
            year, month, day, weekday, hour, minute, second, _ = dt
            is_pm = hour >= 12
        except Exception as e:
            print(f"Library error: {e}")
            # Fall back to direct register access
            year, month, day, weekday, hour, minute, second, is_pm = read_time_directly()
        
        # Convert to 12-hour format
        hour_12, am_pm = to_12hour_format(hour, is_pm)
        
        # Get weekday name
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_name = days[weekday - 1] if 1 <= weekday <= 7 else "Unknown"
        
        # Format time as HH:MM:SS AM/PM
        time_str = f"{hour_12:d}:{minute:02d}:{second:02d} {am_pm}"
        
        # Format date as YYYY-MM-DD
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Get temperature
        temp_c, temp_f = read_temperature()
        
        # Print formatted time, date, and temperature
        print(f"Date: {date_str} ({weekday_name})")
        print(f"Time: {time_str}")
        print(f"Temperature: {temp_c:.2f}°C ({temp_f:.2f}°F)")
        print("-" * 40)
        
        # Wait 1 second before reading again
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nProgram stopped by user")