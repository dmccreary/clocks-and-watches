# Raspberry Pi Pico W Clock Hardware Configuration file.

# SPI Display Bus and Pins
SPI_BUS = 0
SPI_SCL_PIN = 2 # Clock
SPI_SDA_PIN = 3 # labeled SDI(MOSI) on the back of the display
SPI_RESET_PIN = 4 # Reset
SPI_DC_PIN = 5 # Data/command
SPI_CS_PIN = 6 # Chip Select

# OLED Screen Dimensions
DISPLAY_WIDTH=128
DISPLAY_HEIGHT=64

# I2C Bus and Pins
I2C_BUS = 0
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1

# Real Time CLock
RTC_TYPE = "DS3123"
RTC_I2C_ADDR = 0x68

# Buttons to change the time
BUTTON_MODE_PIN = 13
BUTTON_INCREMENT_PIN = 14
BUTTON_DECREMENT_PIN = 15

# Speaker Pin
SPEAKER_PIN = 10