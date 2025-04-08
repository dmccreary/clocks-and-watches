from machine import Pin, SPI
import ssd1306
from time import localtime
import config

SCL=Pin(config.SPI_SCL_PIN)
SDA=Pin(config.SPI_SDA_PIN)
DC = Pin(config.SPI_DC_PIN)
RES = Pin(config.SPI_RES_PIN)
CS = Pin(config.SPI_CS_PIN)
SPI_BUS = config.SPI_BUS
WIDTH = config.DISPLAY_WIDTH
HEIGHT = config.DISPLAY_HEIGHT

spi=SPI(SPI_BUS, sck=SCL, mosi=SDA, baudrate=1000000)
oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)

while True:
    year = localtime()[0]
    month = localtime()[1]
    day = localtime()[2]
    hour = localtime()[3]
    minute = localtime()[4]
    second = localtime()[5]

    if hour > 11:
        am_pm = 'pm'
    else: am_pm = 'am'
    # display the time in hours, minute and seconds on the first line
    oled.fill(0)
    oled.text(str(hour % 12) + ":" + str(minute) + ":" + str(second) + ' ' + am_pm, 0, 0, 1)

    # display the date on the second line
    oled.text(str(month) + "/" + str(day) + "/" + str(year), 0, 10, 1)

    oled.show()
