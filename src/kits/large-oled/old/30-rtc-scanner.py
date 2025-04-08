from machine import I2C, Pin
import config

sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
I2C_BUS = config.I2C_BUS

print("I2C Data on pin:", config.I2C_SDA_PIN)
print("I2C Clock on pin:", config.I2C_SCL_PIN)
print("I2C Bus:", I2C_BUS)

i2c = I2C(I2C_BUS, scl=scl, sda=sda, freq=1000000)
scan_result = i2c.scan()
print("I2C addresses found:", [hex(device_address) for device_address in scan_result])

if 104 in scan_result:
    print("PASS: DS1307 FOUND")
else:
    print("FAIL: DS1307 NOT FOUND")