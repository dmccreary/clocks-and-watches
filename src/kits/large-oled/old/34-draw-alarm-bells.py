from machine import Pin, I2C, SPI
from utime import sleep, localtime
from ds1307 import DS1307
from array import array

import ssd1306
import config

SCL=Pin(config.SPI_SCL_PIN)
SDA=Pin(config.SPI_SDA_PIN)
DC = Pin(config.SPI_DC_PIN)
RES = Pin(config.SPI_RESET_PIN)
CS = Pin(config.SPI_CS_PIN)
SPI_BUS = config.SPI_BUS
WIDTH = config.DISPLAY_WIDTH
HEIGHT = config.DISPLAY_HEIGHT

spi=SPI(SPI_BUS, sck=SCL, mosi=SDA, baudrate=1000000)
oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)

i2c_sda = Pin(config.I2C_SDA_PIN)
i2c_scl = Pin(config.I2C_SCL_PIN)
I2C_BUS = config.I2C_BUS
RTC_TYPE = config.RTC_TYPE
RTC_I2C_ADDR = config.RTC_I2C_ADDR

# I2C setup
i2c = I2C(I2C_BUS, scl=i2c_scl, sda=i2c_sda, freq=3000000)
rtc = DS1307(addr=RTC_I2C_ADDR, i2c=i2c)

def draw_alarm_icon(display, x, y, size=24):
    """
    Draw an alarm bell icon with time display using polygons.
    
    Args:
        display: SSD1306 display instance
        x, y: Top-left position for the icon
        size: Base size of the icon (default 24 pixels)
    """
    # Scale factors
    scale = size / 24  # Base size is 24 pixels
    
    # Bell body coordinates (scaled from base design 22 wide and 20 high)
    bell_body = array('B', [
        # start at the top right and go 0,4,10,17 and 20 down
        int(14 * scale), int(0 * scale),    # Top right of dome top row right
        int(17 * scale), int(4 * scale),    # Top right of dome 2nd row
        int(19 * scale), int(10 * scale),   # Bottom right curve
        int(18 * scale), int(16 * scale),   # Right side indent
        # bottom row
        int(22 * scale), int(20 * scale),   # Right bottom corner
        int(0 * scale),  int(20 * scale),   # Bottom left corner
        # left side
        int(4 * scale),  int(16 * scale),   # Left up indent
        int(3 * scale),  int(10 * scale),   # Left up
        int(5 * scale),  int(4 * scale),    # Top left of dome 2nd row
        int(8 * scale),  int(0 * scale),    # Top left of dome top row left
    ])
    
    # Clapper coordinates
    clapper = array('B', [
        int(10 * scale), int(20 * scale),   # Top left
        int(12 * scale), int(20 * scale),   # Top right
        int(14 * scale), int(24 * scale),   # Bottom right
        int(8 * scale), int(24 * scale),   # Bottom left
    ])
    
    # Draw the components
    display.poly(x, y, bell_body, 1, 1)  # Filled bell body
    display.poly(x, y, clapper, 1, 1)    # Filled clapper

def demo_alarm_icons(display):
    """
    Demonstrate the alarm icon at different sizes and positions
    """
    # Clear the display
    display.fill(0)
    
    # Draw three different sized bells
    draw_alarm_icon(display, 0,  0, size=10)    # Very small bell 10
    draw_alarm_icon(display, 20, 0, size=14)    # Very small bell 14 
    draw_alarm_icon(display, 40, 0, size=16)    # Very small bell 16
    draw_alarm_icon(display, 60, 0, size=20)    # Small bell 20
    draw_alarm_icon(display, 80, 0, size=24)    # Standard bell 24
    
    draw_alarm_icon(display, 0,  24, size=28)   # Medium bell 28
    draw_alarm_icon(display, 30, 24, size=32)   # Medium bell 28
    draw_alarm_icon(display, 60, 24, size=36)   # Large bell 36

    
    # Update the display
    display.show()


demo_alarm_icons(oled)