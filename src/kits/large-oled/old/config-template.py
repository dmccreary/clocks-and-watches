# these are the defualt connections

SPI_SCL_PIN = 2 # SPI CLock
SPI_SDA_PIN = 3 # SPI Data
SPI_RESET_PIN = 4 # Reset
SPI_DC_PIN = 5 # Data/command
SPI_CS_PIN = 6 # Chip Select

SPI_BUS = 0
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

I2C_SDA_PIN = 0 # RTC SDA
I2C_SCL_PIN = 1 # RTC SCL
I2C_BUS = 0
RTC_TYPE = "DS1307"
RTC_I2C_ADDR = 0x68

SPEAKER_PIN = 8

"""
Copy this code to your program:

import config
SPI_SCL_PIN = config.SPI_SCL_PIN
SPI_SDA_PIN = config.SPI_SDA_PIN

SPI_RESET_PIN = config.SPI_RES_PIN
# note these got reversed on the cable
SPI_DC_PIN = config.SPI_DC_PIN
SPI_CS_PIN = config.SPI_CS_PIN
SPI_BUS = config.SPI_BUS
DISPLAY_WIDTH = config.DISPLAY_WIDTH
DISPLAY_HEIGHT = config.DISPLAY_HEIGHT

I2C_SDA_PIN = config.I2C_SDA_PIN
I2C_SCL_PIN = config.I2C_SCL_PIN
I2C_BUS = config.I2C_BUS
RTC_TYPE = config.RTC_TYPE
RTC_I2C_ADDR = config.RTC_I2C_ADDR

SPEAKER_PIN = config.SPEAKER_PIN
"""