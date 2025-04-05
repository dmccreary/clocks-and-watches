from machine import I2C, Pin
import config

# get the data from the config.py file
I2C_BUS = config.I2C_BUS
DST0_PIN = config.I2C0_DST_PIN
CLK0_PIN = config.I2C0_CLK_PIN

DST1_PIN = config.I2C1_DST_PIN
CLK1_PIN = config.I2C1_CLK_PIN

print("I2C Bus pin: ", I2C_BUS)
print("Data DST on pin: ", DST0_PIN)
print("Clock CLK on pin: ", CLK0_PIN)

i2c0 = I2C(0, scl=Pin(CLK0_PIN), sda=Pin(DST0_PIN), freq=1_000_000)
i2c1 = I2C(1, scl=Pin(CLK1_PIN), sda=Pin(DST1_PIN), freq=1_000_000)

id_list0 = i2c0.scan()
id_list1 = i2c1.scan()

print("Found ", len(id_list0), "I2C IDs on I2C Bus 0")

for id in id_list0:
   print("dec=", id, " hex =", hex(id) )
print("")

print("Found ", len(id_list1), "I2C IDs on I2C Bus 1")

for id in id_list1:
   print("dec=", id, " hex =", hex(id) )
"""
Results of I2C Scanner

I2C Bus pin:  0
Data DST on pin:  0
Clock CLK on pin:  1
Found  12 I2C IDs
dec= 18  hex = 0x12
dec= 27  hex = 0x1b
dec= 37  hex = 0x25
dec= 46  hex = 0x2e
dec= 55  hex = 0x37
dec= 64  hex = 0x40
dec= 73  hex = 0x49
dec= 82  hex = 0x52
dec= 91  hex = 0x5b
dec= 100  hex = 0x64
dec= 109  hex = 0x6d
dec= 118  hex = 0x76
"""