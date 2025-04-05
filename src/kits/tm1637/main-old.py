# Clock with no RTC module using tm1637 4-digit 7-segment display
from machine import Pin, RTC
from utime import localtime, sleep, ticks_ms, ticks_diff
import tm1637

# Pin setup
CLK_PIN = 19
DST_PIN = 18
PM_PIN = 25

# the three buttons to set the pins
mode_pin = Pin(13, Pin.IN, Pin.PULL_UP)
next_pin = Pin(14, Pin.IN, Pin.PULL_UP)
previous_pin = Pin(15, Pin.IN, Pin.PULL_UP)
pm_pin = Pin(PM_PIN, Pin.OUT)
power_reset = True # if we are here, then we just got powered up

# Time state on power on
hour = 0
minute = 0
second = 0
is_pm = 0

rtc = RTC()
# set the datetime
rtc.datetime((2024, 12, 30, 0, hour, minute, second, 0))  # Year, month, day, weekday, hour, minute, second, subsecond

tm = tm1637.TM1637(clk=Pin(CLK_PIN), dio=Pin(DST_PIN))

mode = 4
mode_names = ["run", "set hour", "set minute", "set AM/PM", "power reset"]
mode_count = len(mode_names)

# Debounce state
last_mode_press = 0
last_next_press = 0
last_prev_press = 0
DEBOUNCE_MS = 500
last_flash = 0

# for flashing the colon and change LEDs
flash_state = 0
FLASH_INTERVAL_MS = 500  # 1/2 second flash interval

def format_time():
    return f"{hour:d}:{minute:02d}:{second:02d} {'PM' if is_pm else 'AM'}"

def set_pm():
    global is_pm
    if hour < 12:
        is_pm = False
        pm_pin.value(0)
    else:
        is_pm = True
        pm_pin.value(1)

def handle_mode(pin):
    global mode, mode_count, last_mode_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_mode_press) > DEBOUNCE_MS:
        if mode == 4:
            mode = 0;
            mode_count -= 1; # no need to go to mode 4 agin
            return
        mode = (mode + 1) % mode_count
        print(f"Mode: {mode_names[mode]}")
        last_mode_press = current_time

def handle_next(pin):
    global hour, minute, is_pm, last_next_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_next_press) > DEBOUNCE_MS:
        if mode == 1:  # Set hour
            hour = (hour % 12) + 1
        elif mode == 2:  # Set minute
            minute = (minute + 1) % 60
        elif mode == 3:  # Toggle AM/PM
            is_pm = not is_pm
            pm_pin.value(1 if is_pm else 0)
        
        if mode != 0:
            print(format_time())
        last_next_press = current_time
        # set the new datetime
        rtc.datetime((2024, 12, 30, 0, hour, minute, second, 0))  # Year, month, day, weekday, hour, minute, second, subsecond


def handle_previous(pin):
    global hour, minute, is_pm, last_prev_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_prev_press) > DEBOUNCE_MS:
        if mode == 1:  # Set hour
            hour = ((hour - 2) % 12) + 1
        elif mode == 2:  # Set minute
            minute = (minute - 1) % 60
        elif mode == 3:  # Toggle AM/PM
            is_pm = not is_pm
            pm_pin.value(1 if is_pm else 0)       
        if mode != 0:
            print(format_time())
        last_prev_press = current_time
        # set the new datetime
        rtc.datetime((2024, 12, 30, 0, hour, minute, second, 0))  # Year, month, day, weekday, hour, minute, second, subsecond


def numbers_nlz(num1, num2, colon=True, flash_state=False, flash_mode=None):
    """Display two numeric values with flashing capability
    flash_mode can be 'hour', 'minute', 'reset' or None"""
    num1 = max(-9, min(num1, 99))
    num2 = max(-9, min(num2, 99))
    prefix = ' ' if num1 < 10 else ''
    
    if flash_state and flash_mode == 'hour':
        # Flash only hour by using spaces for hour digits
        segments = tm.encode_string(f'  {num2:0>2d}')
    elif flash_state and flash_mode == 'minute':
        # Flash only minutes by using spaces for minute digits
        segments = tm.encode_string(f'{prefix}{num1:d}  ')
    elif flash_state and flash_mode == 'reset':
        segments = tm.encode_string('    ')
    else:
        # Normal running display
        segments = tm.encode_string(f'{prefix}{num1:d}{num2:0>2d}')
    
    if colon and flash_state:
        segments[1] |= 0x80  # colon on
    tm.write(segments)

# Set up interrupts
mode_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode)
next_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_next)
previous_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_previous)

# Main loop
print("Clock started. Press mode button to change settings.")
print("mode:", mode, mode_names[mode])
last_minute = localtime()[4]
while True:
    current_time = ticks_ms()
    # set to be True every 1/2 second
    flash_state = (ticks_diff(current_time, last_flash) // FLASH_INTERVAL_MS) % 2
    # print(flash_state)

    if ticks_diff(current_time, last_flash) >= FLASH_INTERVAL_MS:
        last_flash = current_time
        
    if mode == 0:  # Only update time in run mode the power has not been reset
        current_time = localtime()
        hour = current_time[3]
        # Convert 24-hour to 12-hour format
        display_hour = ((hour - 1) % 12) + 1
        minute = current_time[4]
        second = current_time[5]
        set_pm()  # Update AM/PM status based on hour
        # Add code here to onl display the hour from 1 to 12
        numbers_nlz(display_hour, minute, True, flash_state, 'run')  
        pm_pin.value(1 if is_pm else 0)
    elif mode == 1:  # Set hour mode
        power_reset = False
        numbers_nlz(hour, minute, True, flash_state, 'hour')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 2:  # Set minute mode
        power_reset = False
        numbers_nlz(hour, minute, True, flash_state, 'minute')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 3:  # Set AM/PM mode
        numbers_nlz(hour, minute, True)
        # Flash the PM LED
        pm_pin.value(0 if flash_state else (1 if is_pm else 0))
    else: # must be mode == 4 Power on or reset - need to set time
        # flash all LEDs
        numbers_nlz(88, 88, True, flash_state, 'reset')
    sleep(0.25)  # Shorter sleep for more responsive flashing
    # print the time only if we have a new minute
    if last_minute != localtime()[4]:
        last_minute = localtime()[4]
        print(localtime())
