from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from utime import sleep, localtime

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

while True:
    # Clear the display before writing new content
    lcd.clear()
    
    now = localtime()
    year = now[0]
    month = now[1]
    day = now[2]
    hour = now[3]
    minute = now[4]
    second = now[5]
    
    if hour == 0:
        # Midnight edge case
        hour = 12
        am_pm = 'AM'
    elif hour == 12:
        # Noon edge case
        am_pm = 'PM'
    elif hour > 12:
        # Afternoon hours
        hour -= 12
        am_pm = 'PM'
    else:
        # Morning hours
        am_pm = 'AM'
    
    # Format date on first row - centered
    date_str = f"{month:02d}/{day:02d}/{year}"
    lcd.move_to((16 - len(date_str)) // 2, 0)  # Center the date
    lcd.putstr(date_str)
    
    # Format time on second row - use zero padding for minutes
    time_str = f"{hour}:{minute:02d}:{second:02d} {am_pm}"
    lcd.move_to((16 - len(time_str)) // 2, 1)  # Center the time
    lcd.putstr(time_str)
    
    sleep(1)