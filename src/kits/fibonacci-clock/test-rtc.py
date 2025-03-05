from machine import I2C, Pin
import time

# I2C setup with a slightly lower frequency for better stability
I2C_SDA_PIN = 0  # data pin
I2C_SCL_PIN = 1  # clock
I2C_BUS = 0
I2C_FREQUENCY = 100000  # Reduced frequency for stability
DS3231_ADDR = 0x68

print("I2C Data SDA on pin: ", I2C_SDA_PIN)
print("I2C Clock SCL on pin: ", I2C_SCL_PIN)
print("Checking for devices on Bus", I2C_BUS, "at frequency", I2C_FREQUENCY)

# Initialize I2C
i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQUENCY)
scan_result = i2c.scan()
print(scan_result)
print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])

def bcd2dec(bcd):
    """Convert binary coded decimal to decimal."""
    return ((bcd >> 4) * 10) + (bcd & 0x0F)

def read_ds3231_time():
    """Read time directly from DS3231 registers with robust error handling."""
    try:
        # Make multiple attempts
        for attempt in range(3):
            try:
                # Read 7 bytes from register 0x00
                data = i2c.readfrom_mem(DS3231_ADDR, 0x00, 7)
                
                # If we got here, the read was successful
                second = bcd2dec(data[0] & 0x7F)  # Mask out CH bit
                minute = bcd2dec(data[1] & 0x7F)
                
                hour_reg = data[2]
                if hour_reg & 0x40:  # 12-hour mode
                    hour = bcd2dec(hour_reg & 0x1F)
                    if hour_reg & 0x20:  # PM
                        hour += 12
                else:  # 24-hour mode
                    hour = bcd2dec(hour_reg & 0x3F)
                
                weekday = bcd2dec(data[3] & 0x07)
                day = bcd2dec(data[4] & 0x3F)
                
                month_reg = data[5]
                month = bcd2dec(month_reg & 0x1F)
                
                year = bcd2dec(data[6]) + 2000
                
                return (year, month, day, weekday, hour, minute, second)
            
            except Exception as e:
                print(f"Attempt {attempt+1}: Error reading time: {e}")
                time.sleep(0.1)  # Short delay before retry
                
        # If all attempts failed
        print("All attempts to read time failed")
        return (0, 0, 0, 0, 0, 0, 0)
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return (0, 0, 0, 0, 0, 0, 0)

# Main loop
print("\nAttempting to read time from DS3231...")
try:
    while True:
        # Get date and time
        year, month, day, weekday, hour, minute, second = read_ds3231_time()
        
        # Get weekday name
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_name = days[weekday - 1] if 1 <= weekday <= 7 else "Unknown"
        
        # Print time even if zeros, so we can see if it ever succeeds
        print(f"Date: {year:04d}-{month:02d}-{day:02d} ({weekday_name})")
        print(f"Time: {hour:02d}:{minute:02d}:{second:02d}")
        print("-" * 40)
        
        # Longer delay to reduce I2C traffic
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\nProgram stopped by user")