# Clock Lab 20: Draw Seven Segments
# this lab uses the fill_rect function to draw the segments
from machine import Pin, I2C, SPI
import utime
import ssd1306
# the real-time clock module
from ds1307 import DS1307
from utime import sleep, localtime

led = Pin(25, Pin.OUT)

SCL=Pin(2) # SPI CLock
SDA=Pin(3) # SPI Data
spi=SPI(0, sck=SCL, mosi=SDA, baudrate=100000)

RES = Pin(4)
DC = Pin(5)
CS = Pin(6)
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
I2C_ADDR = 0x68     # DEC 104, HEX 0x68

oled = ssd1306.SSD1306_SPI(128, 64, spi, DC, RES, CS)

i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=800000)
ds1307 = DS1307(addr=I2C_ADDR, i2c=i2c)

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

# digit is the numer to display
# x and y are upper-left-corner
# width and height are the dimensions of the digit
# thickness is the width of the line segments
# color is 1 for white and 0 for black
def drawDigit(digit, x, y, width, height, thinkness, color):
  if digit < 0:
      return
  # get a list of the segments that are on for this digit
  segmentOn = segmentMapping[digit];
  
  # Draw the horizontal segments: top, bottem, middle
  for i in [0, 3, 6]:
    if (segmentOn[i]):
      if (i==0): # top
          yOffset = 0 
      if (i==3):
          yOffset = height - thinkness # bottem element
      if (i==6):
          yOffset = height // 2 - thinkness // 2# bottum
      # oled.line(x - size, y+yOffset-size, x + size, y+yOffset-size, 1);
      oled.fill_rect(x, y+yOffset, width, thinkness, color)

  # Draw the vertical segments ur, lr, ll, ul
  for i in [1, 2, 4, 5]:
    if (segmentOn[i]) :
      # upper vertical lines
      if (i==1 or i==5):
          startY = y
          endY = y + height // 2
      # lower two vertical lines (2=lower right and 4=lower left)
      if (i==2 or i==4):
          startY = y + height // 2
          endY = y + height
      if (i==4 or i==5): xOffset = 0
      if (i==1 or i==2): xOffset = width-thinkness

      oled.fill_rect(x+xOffset, startY, thinkness, endY-startY, color)


oled.fill(0)
oled.text('Lab 12: rect', 0, 0, 1)
x = 5 # upper left corner x
y = 5 # upper left corner y
w = 10 # digit width
h = 15 # digit height
t = 3

def update_screen(year, month, day, hour, minute, am_pm, colon_on):   
    
    ## Adjust these to fit the display
    left_margin = -15
    y_offset = 16
    digit_width = 30
    digit_height = 37
    digit_spacing = 36
    digit_thickness = 5
    oled.fill(0)
    date_str = f"{month}/{day}/{year}"
    oled.text(date_str, 0, 0, 1)
    if hour > 12:
        hour = hour - 12
    if hour > 10:
        hour_ten = 1
    else:
        hour_ten = -1
    hour_right = hour % 10
    
    minute_ten = minute // 10
    minute_right = minute % 10
    
    # left digit will be 1 or blank
    drawDigit(hour_ten, left_margin,  y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(hour_right, left_margin + 1*digit_spacing,  y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_ten, left_margin + 2*digit_spacing,  y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_right, left_margin + 3*digit_spacing, y_offset, digit_width, digit_height, digit_thickness, 1)
    
    if colon_on:
        draw_colon(53,30)
    
    pm_xoffset = 106
    pm_yoffset = 55

    oled.text(am_pm, pm_xoffset, pm_yoffset, 1)
    
    oled.show()

def draw_colon(x,y):
    oled.fill_rect(x, y, 2, 2,1)
    oled.fill_rect(x, y+8, 2, 2,1)

counter = 0
counter = 0
while True:
    now = localtime()
    print("now from localtime():", now)
    # now - ds1307.datetime
    year = ds1307.year
    month = ds1307.month
    day = ds1307.day
    hour = ds1307.hour
    if hour > 12:
        am_pm = "PM"
    else:
        am_pm = "AM"
    minute = ds1307.minute
    
    update_screen(year, month, day, hour, minute, am_pm, True)
    sleep(1)
    update_screen(year, month, day, hour, minute, am_pm, False)
    sleep(1)
    counter += 1
    if counter > 9:
        counter = 0
