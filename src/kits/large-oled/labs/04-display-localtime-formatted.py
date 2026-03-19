import machine
import ssd1306
import config
from time import localtime

SCL=machine.Pin(config.SPI_SCL_PIN) # SPI CLock
SDA=machine.Pin(config.SPI_SDA_PIN) # SPI Data

RES = machine.Pin(config.SPI_RESET_PIN) # Reset
DC = machine.Pin(config.SPI_DC_PIN) # Data/command
CS = machine.Pin(config.SPI_CS_PIN) # Chip Select

spi=machine.SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=10_000_000)
oled = ssd1306.SSD1306_SPI(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, spi, DC, RES, CS)

while True:
    # clear the entire screen
    
    oled.fill(0)
    year = localtime()[0]
    month = localtime()[1]
    day = localtime()[2]
    hour = localtime()[3]
    minute = localtime()[4]
    second = localtime()[5]
    
    if hour > 11:
        am_pm = 'pm'
    else: am_pm = 'am'
    # display the time in hour and minute on the first line
    oled.text(str(hour % 12) + ":" + str(minute) + ":" + str(second) + ' ' + am_pm, 0, 0, 1)

    # display the date on the second line
    oled.text(str(month) + "/" + str(day) + "/" + str(year), 0, 10, 1)
    # send the entire screen to the display via SPI
    oled.show()
