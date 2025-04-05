# Clock using DS3231 RTC module with TM1637 4-digit 7-segment display
from machine import Pin, I2C
from utime import sleep, ticks_ms, ticks_diff
import tm1637
import config
from ds3231 import DS3231

# Initialize I2C for the DS3231 RTC
i2c = I2C(config.I2C_BUS, scl=Pin(config.I2C0_SCL_PIN), sda=Pin(config.I2C0_SDA_PIN), freq=config.FREQ)
rtc = DS3231(i2c)

# Initialize TM1637 display
tm = tm1637.TM1637(clk=Pin(config.DISPLAY_CLK_PIN), dio=Pin(config.DISPLAY_DIO_PIN))

# Initialize pins
pm_pin = Pin(config.PM_LED_PIN, Pin.OUT)
mode_pin = Pin(config.MODE_PIN, Pin.IN, Pin.PULL_UP)
next_pin = Pin(config.NEXT_PIN, Pin.IN, Pin.PULL_UP)
previous_pin = Pin(config.PREV_PIN, Pin.IN, Pin.PULL_UP)

# Mode state
mode = 0  # 0: run, 1: set hour, 2: set minute, 3: set AM/PM
mode_names = ["run", "set hour", "set minute", "set AM/PM"]
mode_count = len(mode_names)

# Debounce state
last_mode_press = 0
last_next_press = 0
last_prev_press = 0
DEBOUNCE_MS = 500
last_flash = 0

# For flashing the colon and change LEDs
flash_state = 0
FLASH_INTERVAL_MS = 500  # 1/2 second flash interval

# Get initial time from RTC
dt = rtc.datetime()
year, month, day, weekday, hour, minute, second, _ = dt
is_pm = hour >= 12

def format_time():
    # 24-hour to 12-hour conversion for display
    display_hour = ((hour - 1) % 12) + 1
    return f"{display_hour:d}:{minute:02d}:{second:02d} {'PM' if is_pm else 'AM'}"

def set_pm():
    global is_pm
    is_pm = hour >= 12
    pm_pin.value(1 if is_pm else 0)

def handle_mode(pin):
    global mode, last_mode_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_mode_press) > DEBOUNCE_MS:
        mode = (mode + 1) % mode_count
        print(f"Mode: {mode_names[mode]}")
        last_mode_press = current_time

def handle_next(pin):
    global hour, minute, is_pm, last_next_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_next_press) > DEBOUNCE_MS:
        dt = rtc.datetime()  # Get current time
        year, month, day, weekday, current_hour, current_minute, current_second, _ = dt
        
        if mode == 1:  # Set hour
            # Set to the next hour, handling 12 to 1 transition
            new_hour = current_hour + 1
            if new_hour > 23:
                new_hour = 0
            # Update RTC
            rtc.datetime((year, month, day, weekday, new_hour, current_minute, current_second))
        elif mode == 2:  # Set minute
            # Increment minute, wrapping at 60
            new_minute = (current_minute + 1) % 60
            # Update RTC 
            rtc.datetime((year, month, day, weekday, current_hour, new_minute, current_second))
        elif mode == 3:  # Toggle AM/PM
            # Toggle between AM and PM
            if current_hour < 12:
                new_hour = current_hour + 12  # Switch to PM
            else:
                new_hour = current_hour - 12  # Switch to AM
            # Update RTC
            rtc.datetime((year, month, day, weekday, new_hour, current_minute, current_second))
        
        if mode != 0:
            # Refresh global variables
            dt = rtc.datetime()
            _, _, _, _, hour, minute, second, _ = dt
            is_pm = hour >= 12
            print(format_time())
            
        last_next_press = current_time

def handle_previous(pin):
    global hour, minute, is_pm, last_prev_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_prev_press) > DEBOUNCE_MS:
        dt = rtc.datetime()  # Get current time
        year, month, day, weekday, current_hour, current_minute, current_second, _ = dt
        
        if mode == 1:  # Set hour
            # Set to the previous hour, handling 1 to 12 transition
            new_hour = current_hour - 1
            if new_hour < 0:
                new_hour = 23
            # Update RTC
            rtc.datetime((year, month, day, weekday, new_hour, current_minute, current_second))
        elif mode == 2:  # Set minute
            # Decrement minute, wrapping at 0
            new_minute = (current_minute - 1) % 60
            # Update RTC
            rtc.datetime((year, month, day, weekday, current_hour, new_minute, current_second))
        elif mode == 3:  # Toggle AM/PM
            # Toggle between AM and PM
            if current_hour < 12:
                new_hour = current_hour + 12  # Switch to PM
            else:
                new_hour = current_hour - 12  # Switch to AM
            # Update RTC
            rtc.datetime((year, month, day, weekday, new_hour, current_minute, current_second))
        
        if mode != 0:
            # Refresh global variables
            dt = rtc.datetime()
            _, _, _, _, hour, minute, second, _ = dt
            is_pm = hour >= 12
            print(format_time())
            
        last_prev_press = current_time

def numbers_nlz(num1, num2, colon=True, flash_state=False, flash_mode=None):
    """Display two numeric values with flashing capability
    flash_mode can be 'hour', 'minute', or None"""
    num1 = max(-9, min(num1, 99))
    num2 = max(-9, min(num2, 99))
    prefix = ' ' if num1 < 10 else ''
    
    if flash_state and flash_mode == 'hour':
        # Flash only hour by using spaces for hour digits
        segments = tm.encode_string(f'  {num2:0>2d}')
    elif flash_state and flash_mode == 'minute':
        # Flash only minutes by using spaces for minute digits
        segments = tm.encode_string(f'{prefix}{num1:d}  ')
    else:
        # Normal running display
        segments = tm.encode_string(f'{prefix}{num1:d}{num2:0>2d}')
    
    if colon and (not flash_state or flash_mode != 'colon'):
        segments[1] |= 0x80  # colon on
    tm.write(segments)

# Set up interrupts
mode_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode)
next_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_next)
previous_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_previous)

# Main loop
print("Clock started with DS3231 RTC. Press mode button to change settings.")
print("Current mode:", mode_names[mode])

last_second = -1  # Use -1 to force initial display update

while True:
    current_time = ticks_ms()
    
    # Update flash state every FLASH_INTERVAL_MS
    flash_state = (ticks_diff(current_time, last_flash) // FLASH_INTERVAL_MS) % 2
    if ticks_diff(current_time, last_flash) >= FLASH_INTERVAL_MS:
        last_flash = current_time
    
    # Get current time from DS3231 RTC
    dt = rtc.datetime()
    year, month, day, weekday, hour, minute, second, _ = dt
    
    # Only print time when second changes (saves serial output spam)
    if second != last_second:
        if mode == 0:  # Only print in run mode
            print(f"{year}/{month:02d}/{day:02d} - {hour:02d}:{minute:02d}:{second:02d}")
        last_second = second
    
    # Convert 24-hour to 12-hour format for display
    display_hour = ((hour - 1) % 12) + 1
    set_pm()  # Update AM/PM status based on hour
    
    if mode == 0:  # Run mode
        # Normal clock display with flashing colon
        numbers_nlz(display_hour, minute, True, flash_state)
        pm_pin.value(1 if is_pm else 0)
    elif mode == 1:  # Set hour mode
        numbers_nlz(display_hour, minute, True, flash_state, 'hour')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 2:  # Set minute mode
        numbers_nlz(display_hour, minute, True, flash_state, 'minute')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 3:  # Set AM/PM mode
        numbers_nlz(display_hour, minute, True)
        # Flash the PM LED
        pm_pin.value(0 if flash_state else (1 if is_pm else 0))
    
    sleep(0.1)  # Short sleep for responsive UI