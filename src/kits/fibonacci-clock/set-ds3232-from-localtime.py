from machine import Pin, I2C
from utime import localtime

# Constants
DS3231_ADDR = 0x68
STATUS_REG = 0x0F  # Status register address

# I2C setup
sda = Pin(0)
scl = Pin(1)
i2c = I2C(0, scl=scl, sda=sda, freq=200000)

def dec2bcd(dec):
    """Convert decimal to binary coded decimal."""
    return (dec // 10) << 4 | (dec % 10)

def check_osf():
    """Check the oscillator stop flag."""
    status = i2c.readfrom_mem(DS3231_ADDR, STATUS_REG, 1)[0]
    return bool(status >> 7)

def reset_osf():
    """Clear the oscillator stop flag."""
    status = bytearray(1)
    i2c.readfrom_mem_into(DS3231_ADDR, STATUS_REG, status)
    i2c.writeto_mem(DS3231_ADDR, STATUS_REG, bytearray([status[0] & 0x7f]))

def set_ds3231():
    """Set the DS3231 RTC time and ensure oscillator is running."""
    now = localtime()
    year = now[0] % 100  # Convert to 2-digit year
    month = now[1]
    day = now[2]
    hour = now[3]
    minute = now[4]
    second = now[5]
    
    # First check if oscillator is stopped
    if check_osf():
        print("Oscillator was stopped. Resetting OSF flag...")
        reset_osf()
    
    data = bytearray([
        dec2bcd(second),
        dec2bcd(minute),
        dec2bcd(hour),
        dec2bcd(now[6] + 1),  # Convert weekday from 0-6 to 1-7
        dec2bcd(day),
        dec2bcd(month),
        dec2bcd(year)
    ])
    
    i2c.writeto_mem(DS3231_ADDR, 0x00, data)
    print(f"RTC set to: {month}/{day}/{now[0]} {hour:02d}:{minute:02d}:{second:02d}")
    
    # Verify oscillator is running
    if check_osf():
        print("Warning: Oscillator still shows stopped state!")
    else:
        print("Oscillator running normally")

if __name__ == "__main__":
    set_ds3231()