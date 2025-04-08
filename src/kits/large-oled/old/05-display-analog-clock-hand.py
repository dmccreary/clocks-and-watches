# Lab 05: Display analog clock hand
import machine
import ssd1306
import config
from time import sleep, localtime
import math

SCL=machine.Pin(config.SCL_PIN) # SPI CLock
SDA=machine.Pin(config.SDA_PIN) # SPI Data

RES = machine.Pin(config.RESET_PIN) # Reset
DC = machine.Pin(config.DC_PIN) # Data/command
CS = machine.Pin(config.CS_PIN) # Chip Select

spi=machine.SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=100000)
oled = ssd1306.SSD1306_SPI(config.WIDTH, config.HEIGHT, spi, DC, RES, CS)

# constants
TWO_PI = 3.14159 * 2

LENGTH = config.HEIGHT // 2
CENTER_X = config.WIDTH // 2
CENTER_Y = config.HEIGHT // 2

oled.fill(0)

while True:
    for i in range(0,61):
        radians = (i/60)*TWO_PI
        x = int(math.sin(radians)*LENGTH)
        y = -int(math.cos(radians)*LENGTH)
        # print(i, radians, x, y, x, y)
        # draw a single line from the center to the edge of the circle
        oled.line(CENTER_X, CENTER_Y, CENTER_X + x, CENTER_Y + y, 1)
        oled.show()
        sleep(.1)
        # erase the old line
        oled.line(CENTER_X, CENTER_Y, CENTER_X + x, CENTER_Y + y, 0)
    
