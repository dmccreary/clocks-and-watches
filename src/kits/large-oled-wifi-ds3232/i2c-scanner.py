# I2C Bus Scanner for Raspberry Pi Pico W
# Scans the I2C bus and reports all detected devices
# Version 1.0

from machine import Pin, I2C
import config

print("I2C Bus Scanner v1.0")
print("=" * 40)

i2c_sda = Pin(config.I2C_SDA_PIN)
i2c_scl = Pin(config.I2C_SCL_PIN)
i2c = I2C(config.I2C_BUS, scl=i2c_scl, sda=i2c_sda, freq=200000)

print(f"Bus:  I2C{config.I2C_BUS}")
print(f"SDA:  GP{config.I2C_SDA_PIN}")
print(f"SCL:  GP{config.I2C_SCL_PIN}")
print(f"Freq: 200000 Hz")
print("=" * 40)

devices = i2c.scan()

if devices:
    print(f"Found {len(devices)} device(s):\n")
    print("  Addr (hex)  Addr (dec)  Known Device")
    print("  ---------   ---------   ------------")
    known = {
        0x27: "LCD (PCF8574)",
        0x3C: "SSD1306 OLED",
        0x3D: "SSD1306 OLED",
        0x50: "AT24C32 EEPROM",
        0x57: "AT24C32 EEPROM",
        0x68: "DS3231 RTC / DS1307 RTC",
        0x76: "BME280 / BMP280",
        0x77: "BME280 / BMP280",
    }
    for addr in devices:
        name = known.get(addr, "")
        print(f"  0x{addr:02X}        {addr:3d}         {name}")
else:
    print("No devices found!")
    print("\nTroubleshooting:")
    print("  - Check SDA and SCL wiring")
    print("  - Check VCC and GND connections")
    print("  - Verify pull-up resistors are present")
    print("  - Try different I2C bus or pins")

print()
