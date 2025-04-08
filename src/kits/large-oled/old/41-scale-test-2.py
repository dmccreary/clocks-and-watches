# Lab 42: Scale Test test v2

from machine import Pin
from time import sleep
import ssd1306
import config

SCL=Pin(config.SCL_PIN) # SPI CLock
SDA=Pin(config.SDA_PIN) # SPI Data

RES = Pin(config.RESET_PIN) # Reset
DC = Pin(config.DC_PIN) # Data/command
CS = Pin(config.CS_PIN) # Chip Select
WIDTH = config.WIDTH
HEIGHT = config.HEIGHT

spi=machine.SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=100000)
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
# digit is the numer to display
# x and y are upper-left-corner
# width and height are the dimensions of the digit
# thickness is the width of the line segments
# color is 1 for white and 0 for black
def drawDigit(digit, x, y, width, height, thickness, color):
  # get a list of the segments that are on for this digit
  if digit > 9 or digit < 0:
      print('Error: digit out of range:', digit)
      return -1
  segmentOn = segmentMapping[digit];
  
  # Draw the horizontal segments: top, bottom, middle
  for i in [0, 3, 6]:
    if (segmentOn[i]):
      if (i==0): # top
          yOffset = 0 
      if (i==3):
          yOffset = height - thickness # bottom element
      if (i==6):
          yOffset = height // 2 - thickness // 2# bottom
      # oled.line(x - size, y+yOffset-size, x + size, y+yOffset-size, 1);
      oled.fill_rect(x, y+yOffset, width, thickness, color)

  # Draw the vertical segments ur, lr, ll, ul
  for i in [1, 2, 4, 5]:
    if (segmentOn[i]) :
      # upper vertical lines
      if (i==1 or i==5):
          startY = y
          endY = y + height // 2
      # lower two vertical lines (2=lower right and 4=lower left)
      if (i==2 or i==4):
          startY = y + (height // 2)
          endY = y + height
      if (i==4 or i==5): xOffset = 0
      if (i==1 or i==2): xOffset = width-thickness

      oled.fill_rect(x+xOffset, startY, thickness, endY-startY, color)

def drawTime12h(hour, minute, x, y, width, height, color):
    
    # this does not scale
    am_pm_font_height = 8
    
    # horizontal spacing
    x1 = .73 # width of the hour tens digit (1 or off)
    x2 = .25 # space between hour tens and hour ones
    x3 = 3.0 # digit width
    x4 = 1.35 # space beteen hour ones and minute tens
    x5 = .5 # space between minute tens and minute ones
    x6 = .35 # space between minute ones and am/pm text
    x7 = 1.5 # an/pm text width
    
    # colon x positioning
    x8 = .35 # space between hour ones and colon
    x9 = .5 # colon width and height

    # vertical
    y1 = 5.31 # digit height
    y2 = (y1 // 2) - .1 # to top colon
    y3 = 1.5 # space between colons
    
    total_width = x1 + x2 + 3*x3 + x4 + x5 + x6 + x7
    # print("total width:", total_width)
    total_height = y1
    
    # calculate the scaling ratios
    x_scale = width / total_width
    y_scale = height / total_height 
    
    digit_width = x3 * x_scale
    digit_height = y1 * y_scale
    # print("x scale:", x_scale, "y scale:", y_scale)

    
    time_width = total_width * x_scale
    # print("time_width:", time_width)
    
    # thickness calculation based on a fraction of the width
    thickness = int(.25 * digit_width)
    
    if hour > 12:
        hour12 = hour - 12
    else: hour12 = hour
    
    hour_minute = hour % 10
    if hour_minute == 0:
        hour_minute = 2
        
    # hour tens display 
    if hour12 == 0 or hour12 > 9:
        oled.fill_rect(x,y,int(x1*x_scale),int(y1*y_scale), color)
        
    # hour ones for the d, x,y,w,h, t,c
    if hour12 == 0:
        hour12 = 12
    hour_ones_x = int((x + x1 + x2)*x_scale)
    drawDigit(hour12 % 10, hour_ones_x, y, int(x3*x_scale), int(y1*y_scale), thickness, color)
    
    # minute tens ones digit, x,y,w,h
    min_tens_x = int((x + x1 + x2 + x3 + x4)*x_scale)
    drawDigit(minute // 10, min_tens_x, y, int(x3*x_scale), int(y1*y_scale), thickness, color)
    
    # minute ones digit d, x,y,w,h, t, c
    min_ones_x = int((x + x1 + x2 + 2*x3 + x4 + x5)*x_scale)
    drawDigit(minute % 10, min_ones_x, y, int(x3*x_scale), int(y1*y_scale), thickness, color)

    # draw colon
    colon_size = int(x9*x_scale)
    # top colon
    oled.fill_rect(int((x+x1+x2+x3+x8)*x_scale), y+int(y2*y_scale), colon_size, colon_size, color)
    # bottom colon
    oled.fill_rect(int((x+x1+x2+x3+x8)*x_scale), y+int((y2+y3)*y_scale), colon_size, colon_size, color)
    
    # AM/PM
    if hour < 12:
        am_pm_text = 'am'
    else:
        am_pm_text = 'pm'
    # but here.  It displays outside the width
    am_pm_x = min_ones_x + int((x3+x6)*x_scale)
    # print('am/pm x:', am_pm_x)
    oled.text(am_pm_text, am_pm_x, y + int(y1*y_scale) - am_pm_font_height, color)
    
    oled.show()

# test times
tt = [[00,00], [12,59], [12,00], [8,33], [13,59], [23,59]]

while True:
    ## tti is the test time index
    for tti in range(0,len(tt)):
        for size in range(20, 110):
            oled.fill(0) # clear screen
            # bounding box for the entire screen
            # oled.rect(0,0, WIDTH-1, HEIGHT-1, 1)
            
            # bounding box for the time region
            height = int(size*.5)
            oled.rect(0, 0, size+20, height+5, 1)
            # print("h=", tt[tti][0], "min:", tt[tti][1])
            drawTime12h(tt[tti][0], tt[tti][1], 2, 2, size, height, 1)
            oled.text(str(tt[tti][0]) + ':' + str(tt[tti][1]), 0, 54, 1)
            oled.show()
            sleep(.1)
