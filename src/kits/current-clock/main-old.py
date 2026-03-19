from machine import Pin, I2C, SPI
from utime import sleep, localtime
from ds3231 import DS3231
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
i2c = I2C(I2C_BUS, scl=i2c_scl, sda=i2c_sda, freq=200000)
rtc = DS3231(addr=RTC_I2C_ADDR, i2c=i2c)

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
]

def day_to_str(day_num):
    """
    Convert a day number (0-6) to a three-letter day abbreviation.
    
    Args:
        day_num (int): Day number, where 0=Monday through 6=Sunday
        
    Returns:
        str: Three-letter day abbreviation ('Mon', 'Tue', etc.)
        
    Raises:
        ValueError: If day_num is not between 0 and 6
    """
    # The dan_num returns by the RTC is from 1 to 7
    day_num = day_num - 1
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if not 0 <= day_num <= 6:
        raise ValueError("Day number must be between 0 and 6")
    return days[day_num]

def month_to_str(month_num):
    """
    Convert a month number (0-11) to a three-letter month abbreviation.
    
    Args:
        month_num (int): Month number, where 0=January through 11=December
        
    Returns:
        str: Three-letter month abbreviation ('Jan', 'Feb', etc.)
        
    Raises:
        ValueError: If month_num is not between 0 and 11
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if not 0 <= month_num <= 11:
        raise ValueError("Month number must be between 0 and 11")
    return months[month_num]

def drawDigit(digit, x, y, width, height, thickness, color):
    if digit < 0 or digit > 9:
        return
    segmentOn = segmentMapping[digit]

    # Draw horizontal segments
    for i in [0, 3, 6]:
        if segmentOn[i]:
            if i == 0:  # top
                yOffset = 0
            elif i == 3:  # bottom
                yOffset = height - thickness
            else:  # middle
                yOffset = height // 2 - thickness // 2
            oled.fill_rect(x, y+yOffset, width, thickness, color)

    # Draw vertical segments
    for i in [1, 2, 4, 5]:
        if segmentOn[i]:
            if i == 1 or i == 5:  # upper segments
                startY = y
                endY = y + height // 2
            else:  # lower segments
                startY = y + height // 2
                endY = y + height
            xOffset = 0 if (i == 4 or i == 5) else width-thickness
            oled.fill_rect(x+xOffset, startY, thickness, endY-startY, color)

def draw_colon(x, y):
    oled.fill_rect(x, y, 3, 3, 1)
    oled.fill_rect(x, y+14, 3, 3, 1)

def read_temperature():
    try:
        # Temperature registers are 0x11 (MSB) and 0x12 (LSB)
        temp_msb = i2c.readfrom_mem(0x68, 0x11, 1)[0]
        temp_lsb = i2c.readfrom_mem(0x68, 0x12, 1)[0] >> 6  # Top 2 bits only
        
        # Handle signed temperature value (2's complement)
        if temp_msb & 0x80:  # If negative (bit 7 is 1)
            temp_msb = -(~temp_msb & 0x7F) - 1
        
        # Convert to temperature value with 0.25°C resolution
        temp_c = temp_msb + ((temp_lsb & 0x03) * 0.25)
        temp_f = (temp_c * 9/5) + 32
        
        return temp_f
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return 0

def update_screen(year, month, day, hour, minute, second, weekday):
    left_margin = -28
    y_offset = 11
    digit_width = 33
    digit_height = 40
    digit_spacing = 41
    digit_thickness = 5

    oled.fill(0)
    
    # put the date in the upper left corner
    date_str = f"{day_to_str(weekday)} {month_to_str(month-1)} {day} {year}"
    oled.text(date_str, 0, 0, 1)

    # Convert 24-hour to 12-hour format
    if hour > 12:
        display_hour = hour - 12
    else:
        display_hour = hour
        
    if display_hour == 0:
        display_hour = 12

    # don't display the hour_ten for hours < 10
    if display_hour < 10:
        hour_ten = -1
    else:
        hour_ten = display_hour // 10
    
    hour_right = display_hour % 10
    minute_ten = minute // 10
    minute_right = minute % 10

    drawDigit(hour_ten, left_margin, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(hour_right, left_margin + digit_spacing-2, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_ten, left_margin + 2*digit_spacing, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_right, left_margin + 3*digit_spacing, y_offset, digit_width, digit_height, digit_thickness, 1)

    if second % 2:
        draw_colon(47, 20)
        
    am_pm_x_offset = 112
    
    if hour > 12:
        oled.text("PM", am_pm_x_offset, 55, 1)
    else:
        oled.text("AM", am_pm_x_offset, 55, 1)
    
    # draw the seconds in the lower right corner
    oled.text(str(second), 0, 54, 1)
    temperature = read_temperature()
    if temperature > 0:
        oled.text(str(temperature)+"F", 30, 54, 1)
    oled.show()

while True:
    now = rtc.datetime()
    # year, month, day, weekday, hour, minute, second, _ = dt
    
    year = now[0]
    month = now[1]
    day = now[2]
    weekday = now[3]
    hour = now[4]
    minute = now[5]
    second = now[6]
    if hour >= 12:
        is_pm = True
    update_screen(year, month, day, hour, minute, second, weekday)
    print("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d} weekday:{}".format(
      year, month, day,
      hour, minute, second, weekday))
    sleep(1)
