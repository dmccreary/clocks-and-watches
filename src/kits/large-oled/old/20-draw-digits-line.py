# Lab 20: Draw Digits with just the line function
# this lab uses the line() function to draw the segments
import machine
import utime
import ssd1306
from utime import sleep, localtime
led = machine.Pin(25, machine.Pin.OUT)

SCL=machine.Pin(2) # SPI CLock
SDA=machine.Pin(3) # SPI Data
spi=machine.SPI(0, sck=SCL, mosi=SDA, baudrate=100000)

RES = machine.Pin(4)
DC = machine.Pin(5)
CS = machine.Pin(6)
WIDTH = 128
HEIGHT = 64

oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)

segmentMapping = [
  #a, b, c, d, e, f, g
  [1, 1, 1, 1, 1, 1, 0], # 0
  [0, 1, 1, 0, 0, 0, 0], # 1
  [1, 1, 0, 1, 1, 0, 1], # 2
  [1, 1, 1, 1, 0, 0, 1], # 3
  [0, 1, 1, 0, 0, 1, 1], # 4
  [1, 0, 1, 1, 0, 1, 1], # 5
  [1, 0, 1, 1, 1, 1, 1], # 6
  [1, 1, 1, 0, 0, 0, 0], # 7
  [1, 1, 1, 1, 1, 1, 1], # 8
  [1, 1, 1, 1, 0, 1, 1]  # 9
];

 
# x and y are the center of the digit, size is the center to edge
def drawDigit(digit, x, y, width, height, color):
  # get a list of the segments that are on for this digit
  segmentOn = segmentMapping[digit];
  
  # Draw the horizontal segments: top, bottem, middle
  for i in [0, 3, 6]:
    if (segmentOn[i]):
      if (i==0): # top
          yOffset = 0 
      if (i==3):
          yOffset = height # bottom element
      if (i==6):
          yOffset = height // 2 # middle line
      oled.line(x, y+yOffset, x + width, y+yOffset, 1)

  # Draw the vertical segments ur, lr, ll, ul
  for i in [1, 2, 4, 5]:
    if (segmentOn[i]) :
        # top two segments
        if (i==1 or i==5):
            startY = 0
            endY = height // 2
        if (i==2 or i==4):
            startY = height // 2
            endY = height
        # left segments
        if (i==4 or i==5): xOffset = 0
        # right segments
        if (i==1 or i==2): xOffset = width
        oled.line(x+xOffset, y+startY, x+xOffset, y+endY, 1)

x = 10 # upper left corner x
y = 15 # upper left corner y
w = 20 # digit width
h = 30 # digit height

while True:
    for i in range(0, 10):
        oled.fill(0)
        oled.text('Lab 20: line digit', 0, 0, 1)
        print(i)
        # create an outline one px away from the drawing region
        oled.rect(x-2, y-2, w+5, h+5, 1)
        # draw one digit
        drawDigit(i, x, y, w, h, 1)
        # draw a second digit
        #drawDigit(i, x + w + 4, w, h, t, 1)
        oled.text(str(i), 0, 54, 1)
        oled.show()
        sleep(2)
        oled.fill(0)





