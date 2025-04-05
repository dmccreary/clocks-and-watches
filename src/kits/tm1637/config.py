# Hardware configuration file for a clock using a TM1637 LED display and a DS3231 RTC

# I2C Configuration
# The DS3231 is on I2C bus 0
I2C_BUS = 0
I2C0_SDA_PIN = 0 # data
I2C0_SCL_PIN = 1 # clock
FREQ = 1_000_000
# Example
# i2c = I2C(config.I2C_BUS, scl=Pin(config.I2C0_SCL_PIN), sda=Pin(config.I2C0_SDA_PIN), freq=config.FREQ)
# rtc = DS3231(i2c)

# The TM1637 is on I2C bus 1 pins but it is not a true I2C device
DISPLAY_DIO_PIN = 18
DISPLAY_CLK_PIN = 19
# Example
# tm = tm1637.TM1637(dio=Pin(config.DISPLAY_DIO_PIN), clk=Pin(config.DISPLAY_CLK_PIN), )


PM_LED_PIN = 25

# Button Pins for Setting Time
# Note these pins go though the buttons to GND - Use PULL_UP
MODE_PIN = 13
NEXT_PIN = 14
PREV_PIN = 15
# Example Code:
# mode_pin = Pin(13, Pin.IN, Pin.PULL_UP)
# next_pin = Pin(14, Pin.IN, Pin.PULL_UP)
# previous_pin = Pin(15, Pin.IN, Pin.PULL_UP)