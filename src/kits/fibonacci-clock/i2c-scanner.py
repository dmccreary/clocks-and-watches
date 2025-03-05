from machine import I2C, Pin
import config

I2C_SDA_PIN = 0 # data pin
I2C_SCL_PIN = 1 # clock
I2C_BUS = 0
I2C_FREQUENCY = 200000

print("I2C Data SDA on pin: ", I2C_SDA_PIN)
print("I2C Clock SCL on pin: ", I2C_SCL_PIN)
print("Checking for devices on Bus", I2C_BUS, "at frequency", I2C_FREQUENCY)

i2c = I2C(I2C_BUS, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQUENCY)

scan_result = i2c.scan()

print(scan_result)

print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])