# TM1637 MicroPython Clock Program - Code Walkthrough

I'll create a detailed step-by-step walkthrough of the `main.py` file (document 7) which implements a digital clock using a DS3231 real-time clock module and a TM1637 LED display. This walkthrough is designed for high school students who are just learning Python.

## Introduction

This program creates a digital clock with a 4-digit 7-segment LED display connected to a Raspberry Pi Pico microcontroller. The clock gets accurate time from a DS3231 real-time clock (RTC) module and also allows you to set the time using buttons.

## Program Structure Overview

1. Import necessary libraries and modules
2. Initialize hardware components
3. Set up global variables 
4. Define helper functions
5. Set up button interrupt handlers
6. Implement the main loop

Now, let's go through the code step by step:

## Step 1: Importing Libraries and Modules

```python
from machine import Pin, I2C
from utime import sleep, ticks_ms, ticks_diff
import tm1637
import config
from ds3231 import DS3231
```

- `machine` module: Provides access to hardware-specific functions like controlling pins and I2C communication
- `utime`: MicroPython's time module that provides timing functions
- `tm1637`: A library for controlling the 7-segment display
- `config`: A custom module that contains hardware configuration settings
- `ds3231`: A library for communicating with the DS3231 real-time clock module

## Step 2: Hardware Initialization

```python
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
```

This section:
- Sets up I2C communication with the RTC
- Initializes the TM1637 LED display
- Configures GPIO pins for:
  - PM LED indicator (output)
  - Three buttons with internal pull-up resistors (input)

## Step 3: Setting Up Global Variables

```python
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
```

This code:
- Defines the different modes for the clock (running, setting hours, etc.)
- Sets up variables for button debouncing (preventing multiple triggers from one press)
- Configures display flashing variables
- Gets the initial time from the RTC and unpacks the values
- Determines if it's AM or PM based on the hour

## Step 4: Helper Functions

### 4.1: Formatting Time for Display

```python
def format_time():
    # 24-hour to 12-hour conversion for display
    display_hour = ((hour - 1) % 12) + 1
    return f"{display_hour:d}:{minute:02d}:{second:02d} {'PM' if is_pm else 'AM'}"
```

This function:
- Converts 24-hour format to 12-hour format
- Creates a formatted time string (e.g., "3:45:30 PM")

### 4.2: Setting the PM Indicator

```python
def set_pm():
    global is_pm
    is_pm = hour >= 12
    pm_pin.value(1 if is_pm else 0)
```

This function:
- Updates the `is_pm` flag based on the current hour
- Sets the PM indicator LED on or off accordingly

### 4.3: Display Function

```python
def numbers_nlz(num1, num2, colon_state=True, flash_state=False, flash_mode=None):
    """Display two numeric values with flashing capability
    flash_mode can be 'hour', 'minute', or None
    colon_state controls the colon (True=on, False=off)"""
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
    
    if colon_state:
        segments[1] |= 0x80  # colon on
    tm.write(segments)
```

This function:
- Takes hour and minute values to display
- Limits numbers to valid range (-9 to 99)
- Adds a leading space for single-digit hours
- Handles different display modes:
  - Normal display
  - Flashing hours (when setting hours)
  - Flashing minutes (when setting minutes)
- Controls the colon between hours and minutes
- Writes the encoded segments to the display

## Step 5: Button Handler Functions

### 5.1: Mode Button Handler

```python
def handle_mode(pin):
    global mode, last_mode_press
    current_time = ticks_ms()
    if ticks_diff(current_time, last_mode_press) > DEBOUNCE_MS:
        mode = (mode + 1) % mode_count
        print(f"Mode: {mode_names[mode]}")
        last_mode_press = current_time
```

This function:
- Gets the current time in milliseconds
- Checks if enough time has passed since the last button press (debouncing)
- Cycles through the available modes
- Updates the mode and prints the new mode name
- Records the time of this button press

### 5.2: Next Button Handler

```python
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
```

This function:
- Implements debouncing like the mode button
- Gets the current date and time from the RTC
- Performs different actions based on the current mode:
  - In mode 1: Increments the hour
  - In mode 2: Increments the minute
  - In mode 3: Toggles between AM and PM
- Updates the RTC with the new time
- Refreshes global variables with the updated time
- Prints the new formatted time
- Records the time of this button press

### 5.3: Previous Button Handler

```python
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
```

This function is similar to the "next" button handler but:
- Decrements the hour in mode 1
- Decrements the minute in mode 2
- Toggles AM/PM (same as the next handler) in mode 3

## Step 6: Setting Up Button Interrupts

```python
# Set up interrupts
mode_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_mode)
next_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_next)
previous_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_previous)
```

This code:
- Configures each button to trigger an interrupt when pressed (falling edge)
- Associates each button with its respective handler function
- These are "interrupt service routines" that run whenever a button is pressed

## Step 7: Main Loop

```python
# Main loop
print("Clock started with DS3231 RTC. Press mode button to change settings.")
print("Current mode:", mode_names[mode])

last_second = -1  # Use -1 to force initial display update

while True:
    current_time = ticks_ms()
    
    # Update flash state every FLASH_INTERVAL_MS for UI flashing
    flash_state = (ticks_diff(current_time, last_flash) // FLASH_INTERVAL_MS) % 2
    if ticks_diff(current_time, last_flash) >= FLASH_INTERVAL_MS:
        last_flash = current_time
        
    # Colon state matches the second (on for even seconds, off for odd seconds)
    colon_state = second % 2 == 0
    
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
        # Normal clock display with colon controlled by seconds
        numbers_nlz(display_hour, minute, colon_state, flash_state)
        pm_pin.value(1 if is_pm else 0)
    elif mode == 1:  # Set hour mode
        numbers_nlz(display_hour, minute, colon_state, flash_state, 'hour')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 2:  # Set minute mode
        numbers_nlz(display_hour, minute, colon_state, flash_state, 'minute')
        pm_pin.value(1 if is_pm else 0)
    elif mode == 3:  # Set AM/PM mode
        numbers_nlz(display_hour, minute, colon_state)
        # Flash the PM LED
        pm_pin.value(0 if flash_state else (1 if is_pm else 0))
    
    sleep(0.1)  # Short sleep for responsive UI
```

This is the main program loop that:
1. Updates the flash state for UI elements that blink
2. Determines if the colon should be on or off based on even/odd seconds
3. Gets the current time from the RTC
4. Prints the time only when the second changes (to avoid flooding the console)
5. Converts 24-hour format to 12-hour format for display
6. Updates the display based on the current mode:
   - Run mode: Normal clock display
   - Set hour mode: Display with flashing hours
   - Set minute mode: Display with flashing minutes
   - Set AM/PM mode: Display with flashing PM indicator
7. Sleeps briefly to save power and maintain responsiveness

## Key Programming Concepts Demonstrated

1. **Object-Oriented Programming**: Uses objects for hardware components (I2C, RTC, display)
2. **Functions**: Organizes code into reusable functions
3. **Global Variables**: Uses globals to maintain state across functions
4. **Conditional Statements**: Uses if/elif/else for different modes and states
5. **String Formatting**: Uses f-strings to format time displays
6. **Hardware Interfaces**: Works with GPIO pins and I2C communication
7. **Interrupts**: Uses interrupt handlers for button presses
8. **Modular Arithmetic**: Uses modulo (%) for time calculations and cycling through modes
9. **Infinite Loop**: Uses a while True loop for continuous operation
10. **Error Prevention**: Implements debouncing to prevent multiple triggers from one button press

## How the Clock Operates

1. When powered on, the clock initializes in "run" mode, displaying current time from the RTC
2. Press the mode button to cycle through modes:
   - Run mode: Normal clock operation
   - Set hour mode: Press next/previous to adjust hours
   - Set minute mode: Press next/previous to adjust minutes
   - Set AM/PM mode: Press next/previous to toggle between AM and PM
3. The colon flashes every second (on for even seconds, off for odd seconds)
4. In setting modes, the relevant parts of the display flash to indicate what's being set
5. The PM indicator LED lights up when the time is PM

This clock is a great example of a practical MicroPython application that combines hardware control with time-keeping functionality.