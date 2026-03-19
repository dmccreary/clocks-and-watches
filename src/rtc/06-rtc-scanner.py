from machine import I2C, Pin

# Both modules use same I2C interface setup
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400_000)
print(i2c.scan())

# RTC module addresses
DS1307_ADDR = 0x68  # Address for DS1307 and DS3231
PCF8523_ADDR = 0x68 # PCF8523 uses same address
MCP7940_ADDR = 0x6F # MCP7940N has a different address

def check_rtc_present():
    """Scan I2C bus for common RTC modules and return True if found"""
    devices = i2c.scan()  # Scan the I2C bus for all devices
    
    # Check if any known RTC addresses are present
    rtc_addresses = [DS1307_ADDR, MCP7940_ADDR]
    
    for addr in rtc_addresses:
        if addr in devices:
            print(f"Found RTC device at address: 0x{addr:02x}")
            return True
    
    print("No RTC device found")
    return False

# Main program
try:
    result = check_rtc_present()
    print(f"\nRTC Present: {result}")
    
    # Print all detected I2C devices for debugging
    print("\nAll I2C devices found:")
    for device in i2c.scan():
        print(f"Device at address: 0x{device:02x}")
        
except Exception as e:
    print(f"Error: {e}")