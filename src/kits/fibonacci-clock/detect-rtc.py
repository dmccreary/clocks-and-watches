from machine import Pin, I2C
from utime import sleep

I2C_DATA_PIN = 0
I2C_CLOCK_PIN = 1

def force_temp_conversion(i2c, addr):
    """Force a new temperature conversion in the DS3231."""
    try:
        # Read control register (0x0E)
        i2c.writeto(addr, b'\x0E')
        control = i2c.readfrom(addr, 1)[0]
        
        # Set CONV bit (bit 5)
        control |= (1 << 5)
        
        # Write back to control register
        i2c.writeto_mem(addr, 0x0E, bytes([control]))
        
        # Wait for conversion to complete (max 10ms)
        sleep(0.01)
        return True
    except:
        return False

def read_temperature(i2c, addr):
    """Read temperature from DS3231 RTC with 0.25°C (0.45°F) resolution."""
    # Temperature registers are 0x11 (MSB) and 0x12 (LSB)
    temp_msb = i2c.readfrom_mem(addr, 0x11, 1)[0]
    temp_lsb = i2c.readfrom_mem(addr, 0x12, 1)[0] >> 6  # Top 2 bits only
    
    # Handle signed temperature value (2's complement)
    if temp_msb & 0x80:  # If negative (bit 7 is 1)
        temp_msb = -(~temp_msb & 0x7F) - 1
    
    # Convert to temperature value
    # MSB is temperature in degrees Celsius
    # LSB bits 7 and 6 are decimal points (0.25°C resolution)
    temp_c = temp_msb + ((temp_lsb & 0x03) * 0.25)
    
    # Convert to Fahrenheit
    temp_f = (temp_c * 9/5) + 32
    
    return temp_c, temp_f

def identify_rtc():
    """
    Identify whether the RTC is a DS1307 or DS3231
    """
    # Initialize I2C
    i2c = I2C(0, sda=Pin(I2C_DATA_PIN), scl=Pin(I2C_CLOCK_PIN), freq=1000000)
    
    RTC_ADDR = 0x68
    
    devices = i2c.scan()
    if RTC_ADDR not in devices:
        return "No RTC found at address 0x68"
        
    try:
        # Force a new temperature conversion first
        if force_temp_conversion(i2c, RTC_ADDR):
            sleep(0.1)  # Give it a moment
            
        # Read temperature using the new function
        temp_c, temp_f = read_temperature(i2c, RTC_ADDR)
        
        return f"DS3231 found! Current temperature: {temp_c:.2f}°C ({temp_f:.2f}°F)"
        
    except OSError:
        try:
            i2c.writeto(RTC_ADDR, b'\x07')
            control = i2c.readfrom(RTC_ADDR, 1)[0]
            return "DS1307 found!"
        except:
            return "Unknown RTC device type"

def main():
    print("\nRTC Identifier")
    print("-" * 40)
    
    result = identify_rtc()
    print(result)
    
    # If you want to monitor temperature continuously, uncomment these lines:
    # while True:
    #     i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
    #     temp_c, temp_f = read_temperature(i2c, 0x68)
    #     print(f"Temperature: {temp_c:.2f}°C ({temp_f:.2f}°F)")
    #     sleep(2)

if __name__ == "__main__":
    main()