from machine import I2C, Pin
import config

SCL_PIN = config.I2C_SCL_PIN
SDA_PIN = config.I2C_SDA_PIN

print("Clock on pin:", SCL_PIN)
print("Data on pin:", SDA_PIN)

i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)
scan_result = i2c.scan()
print("I2C addresses found:", [hex(device_address) for device_address in scan_result])

if 104 in scan_result:
    print("PASS: DS1307 FOUND")
else:
    print("FAIL: DS1307 NOT FOUND")