import machine
import ssd1306
import config
from time import sleep, localtime
import math

SCL=machine.Pin(config.SPI_SCL_PIN) # SPI CLock
SDA=machine.Pin(config.SPI_SDA_PIN) # SPI Data

RES = machine.Pin(config.SPI_RESET_PIN) # Reset
DC = machine.Pin(config.SPI_DC_PIN) # Data/command
CS = machine.Pin(config.SPI_CS_PIN) # Chip Select

WIDTH = config.DISPLAY_WIDTH
HEIGHT = config.DISPLAY_HEIGHT
spi=machine.SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=100000)
oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)
TWO_PI = 3.14159 * 2


CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
print("Center: (", CENTER_X, ",", CENTER_Y, ")")
oled.fill(0)

# draw the digits
for i in range(0,4):
    radians = (i/4)*TWO_PI
    x = int(math.sin(radians)*WIDTH) // 7
    y = -int(math.cos(radians)*HEIGHT) // 2
    print(i, i*3, "rad:", radians, "(", x, ",", y, ")")
    
    # Adjustments for the placments of the digits
    if i == 0:
        digit_str = "12"
        x -= 7
        y += 4
    elif i == 1:
        x += 4
        y -= 2
    elif i == 2:
        y -= 9
        x -=  4
    elif i == 3:
        x -= 11
        y -= 2
    if i > 0:
        digit_str = str(i*3)
    
    oled.text(digit_str, CENTER_X + x, CENTER_Y + y, 1)
    
# draw center dot and outer circle
oled.ellipse(CENTER_X, CENTER_Y, 1, 1, 1)

oled.ellipse(CENTER_X, CENTER_Y, 32, 31, 1)
oled.show()
    
