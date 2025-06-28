from machine import I2C, Pin
import config

DST_PIN = 0
CLK_PIN = 1

print("Data DST on pin: ", DST_PIN)
print("Clock CLK on pin: ", CLK_PIN)

i2c = I2C(0, scl=Pin(CLK_PIN), sda=Pin(DST_PIN), freq=1_000_000)

scan_result = i2c.scan()

print(scan_result)

print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])