import ntptime, network
from machine import RTC
from utime import sleep, sleep_ms, time, localtime, mktime
import ssd1306

# local parameters
import secrets
import config

wifi_ssid = secrets.wifi_ssid
wifi_pass = secrets.wifi_pass

led = machine.Pin('LED', machine.Pin.OUT)

SCL=machine.Pin(config.SCL_PIN) # SPI CLock
SDA=machine.Pin(config.SDA_PIN) # SPI Data

RES = machine.Pin(config.RESET_PIN) # Reset
DC = machine.Pin(config.DC_PIN) # Data/command
CS = machine.Pin(config.CS_PIN) # Chip Select

spi=machine.SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=100000)
oled = ssd1306.SSD1306_SPI(config.WIDTH, config.HEIGHT, spi, DC, RES, CS)

# US Central
timeZone = -6
# try one of these
ntptime.host = 'us.pool.ntp.org' #'time.nist.gov' #'pool.ntp.org'
ntptime.timeout = 10

# global array of integers for holding the current date and time
# Values are year=[0], month[1], day[2], hour[3], minute[4], second[5]
current_time = [] * 7
year = 0
month = 0
day = 0
hour = 0
minute = 0
second = 0

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

# x and y are upper-left-corner
# width and height are the dimensions of the digit
# thinkness is the width of the line segments
# color is 1 for white and 0 for black
def drawDigit(digit, x, y, width, height, thinkness, color):
  if digit < 0 or digit > 9:
      print('Error in drawDigit', digit)
      return -1
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

def draw_colon(x,y, color):
    oled.fill_rect(x, y, 2, 2, color)
    oled.fill_rect(x, y+8, 2, 2, color)
    
def update_display(year, month, day, hour, minute, second):
    global counter
    left_margin = 5
    digit_thinkness = 6
    second_digit_margin = left_margin + digit_thinkness + 5
    y_offset = 5
    digit_width = 25
    digit_height = 40
    digit_spacing = 35
    colon_left_margin = second_digit_margin + digit_width + 5

    oled.fill(0)
    
    if hour > 12:
        hour_ones = hour - 12

    # leftmost digit is black or a 1
    if hour_ones > 9:
        drawDigit(1, left_margin, y_offset, digit_width, digit_height, digit_thinkness, 1)
    
    # draw the hours ones digit
    drawDigit(hour_ones, second_digit_margin,  y_offset, digit_width, digit_height, digit_thinkness, 1)
    
    minute_tens = minute // 10
    drawDigit(minute_tens, second_digit_margin + digit_spacing,  y_offset, digit_width, digit_height, digit_thinkness, 1)
    
    minute_ones = minute % 10
    drawDigit(minute_ones, second_digit_margin + 2*digit_spacing, y_offset, digit_width, digit_height, digit_thinkness, 1)
    
    if (second % 2):
        draw_colon(colon_left_margin, 20, 0)
    else: draw_colon(colon_left_margin, 20, 1)
    
    if (hour < 11):
        # 112 is the max right for the am/pm text
        oled.text("am", 112, 38, 1) 
    else:
        oled.text("pm", 112, 38, 1)
    
    date_str = str(month) + '/' + str(day) + '/' + str(year)    
    oled.text(date_str, 0, 56, 1)
    
    oled.show()
    
# display a string on the 128x64 OLED screen using 9 pixel height and 16 characters per line
def display_msg(in_str, chunk_size=16):
    print(in_str)
    oled.fill(0)
    if len(in_str) < chunk_size:
        oled.text(in_str, 0, 0)
    else:
        # create an array of the strings for each line
        a = [in_str[i:i+chunk_size] for i in range(0, len(in_str), chunk_size)]
        for i in range(0,len(a)):
            oled.text(a[i], 0, i*9)
    oled.show()

# Connect the the local Wifi access point
# get the wifi network name and password from the config.py file
def wifiConnect():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.config(pm = 0xa11140) # disables wifi sleep mode
    if not wifi.isconnected():
        wifi.connect(wifi_ssid, wifi_pass)
        message = 'Connecting to ' + wifi_ssid
        display_msg(message)
        max_wait = 10
        while max_wait > 0:
            if wifi.status() < 0 or wifi.status() >= 3: break
            sleep_ms(1000)
            message = message + '.'
            display_msg(message + str(10-max_wait))
            max_wait -= 1
        print()
        if wifi.status() != 3:
            display_msg('Error: Could not connect to wifi!')
    display_msg('Connected IP: ' + wifi.ifconfig()[0])
    sleep_ms(100)
    return wifi

# daylight savings time
def dst():
    year, weekday = localtime()[0], localtime()[6]
    dst_start = mktime((year, 3, (8 - weekday) % 7 + 8, 2, 0, 0, 0, 0))
    dst_end = mktime((year, 11, (1 - weekday) % 7 + 1, 2, 0, 0, 0, 0))
    return dst_start <= time() < dst_end

maxtries = 5
timetries = 0
timeset = False

def setRTC():
    global maxtries, current_time, timetries, timeset, year, month, day, hour, minute, second
    while not timeset and timetries < maxtries:
        timetries += 1
        try:
            ntptime.settime() # update time from ntp server
            timeset = True
        except:
            error_msg = 'NTP update attempt' + str(timetries) + ' of ' + str(maxtries) + ' Check config.'
            display_msg(error_msg)
            if timetries < maxtries: sleep_ms(15000)
        if timeset:
            sleep_ms(200)
            rtc = RTC()
            tz_offset = (timeZone + 1) * 3600 if dst() else timeZone * 3600
            #tz_offset = timeZone * 3600 # without daylight savings
            myt = localtime(time() + tz_offset)
            print('myt: ', myt)
            current_time = myt
            year = myt[0]
            month = myt[1]
            day = myt[2]
            hour = myt[3]
            minute = myt[4]
            second = myt[5]
            rtc.datetime((myt[0], myt[1], myt[2], myt[6], myt[3], myt[4], myt[5], 0))
            print('Seconds in myt[5]', myt[5])
            sleep_ms(200)
            dtime = rtc.datetime()
            timestr = '%2d:%02d%s' %(12 if dtime[4] == 0 else dtime[4] if dtime[4] < 13 else dtime[4] - 12, dtime[5], 'am' if dtime[4] < 12 else 'pm')
            datestr = f'{dtime[1]}/{dtime[2]}/{dtime[0] % 100}'
            print('Time set to:', timestr, datestr)
            print(timestr, datestr)
            return True
    display_msg('ERROR! Unable to update time from server:' + ntptime.host)
    return False

# get an update of the time from the Network Time Protocol Server
def update():
    success = False
    wifi = wifiConnect()
    sleep_ms(100)
    if wifi.isconnected():
        success = setRTC()
        sleep_ms(100)
    return wifi, success

# convert the current time to 12 hour am/pm format
def timeStrFmt():
    hour = current_time[3]
    if hour > 12:
        hour = hour - 12
        am_pm = ' pm'
    else: am_pm = ' am'
    # format minutes and seconds with leading zeros
    minutes = "{:02d}".format(current_time[4])
    seconds = "{:02d}".format(current_time[5])
    return str(hour) + ':' + minutes + ':' + seconds + am_pm

def dateStrFmt():
    return   str(month) + '/' + str(day) + str(year)

"""
def update_display(year, month, day, hour, minute, second):
    oled.fill(0)
    # no 12/24, leadering zero formatting or am/pm formatting
    # time_strs = str(hour) + ':' + str(minute) + ':' + str(second)
    # with formatting
    timestrf = '%2d:%02d:%02d %s' %(12 if hour == 0 else hour if hour < 13 else hour - 12, minute, second, 'am' if hour < 12 else 'pm')
    oled.text(timestrf, 10, 20, 1)
    
    date_str = str(month) + '/' + str(day) + '/' + str(year)    
    oled.text(date_str, 10, 40, 1)
    oled.show()
"""

def update_wifi_status():
    oled.fill(0)
    oled.text('n: ' + wifi_ssid , 0, 0, 1)
    oled.text('tries: ' + str(timetries), 0, 10, 1)
    if timeset:
        oled.text('Connection OK', 0, 20, 1)
    else:
        oled.text('CONNECTION ERROR', 0, 20, 1)
    oled.text('host: ' + ntptime.host, 0, 30, 1)
    oled.show()

def break_string_into_chunks(s, chunk_size=12):
    """Breaks a string into chunks of a specified size."""
    return [s[i:i+chunk_size] for i in range(0, len(s), chunk_size)]

led.on()
display_msg('Booting.')
sleep(.2)

display_msg('Updating from NTP.')
sleep(.2)
update()

display_msg('Updating from NTP.')
update_wifi_status()
sleep(.2)

update_display(year, month, day, hour, minute, second)

# run this loop every second
while True:

    print('current manual time local based on sleep:', year, month, day, hour, minute, second)
    print('sycurrent_time[4])
    update_display(year, month, day, hour, minute, second)
    led.toggle()
    sleep(1)
    second += 1
    
    # check the time server every day at 2:24 am
    if second > 59:
        second = 0
        if minute > 59:
            minute = 0
            # get a new time from the network time server at 2:47 am each night
            if (hour == 2) and (minute == 24):
                display_message('Syncing time server')
                sleep(2)
                update()
            if hour > 23:
                hour = 0
            else:
                hour += 1
        else:
            minute += 1
