# Full Running Clock Using the TM1637

In this section we create a detailed example of a running clock using the TM1637 display. This builds on some of the concepts shown in previous clock examples, but simplified for the TM1637.

```python
import tm1637
from machine import Pin, RTC
from utime import sleep, localtime

# Initialize the display
tm = tm1637.TM1637(clk=Pin(0), dio=Pin(1))

# Initialize the RTC (Real Time Clock)
rtc = RTC()

def set_initial_time():
    """
    Set an initial time if RTC isn't configured.
    In a real project, you'd sync this with a time server or user input.
    """
    # Format: (year, month, day, weekday, hours, minutes, seconds, subseconds)
    rtc.datetime((2024, 12, 28, 5, 12, 0, 0, 0))

def format_time(hours, minutes):
    """
    Convert 24-hour time to 12-hour format
    Returns hours and whether it's PM
    """
    is_pm = hours >= 12
    if hours > 12:
        hours -= 12
    elif hours == 0:
        hours = 12
    return hours, is_pm

def run_clock():
    # Set initial brightness (0-7)
    tm.brightness(2)
    
    # Track colon state for blinking
    colon_on = True
    
    while True:
        # Get current time from RTC
        year, month, day, weekday, hours, minutes, seconds, _ = rtc.datetime()
        
        # Convert to 12-hour format
        display_hours, is_pm = format_time(hours, minutes)
        
        # Toggle colon every second
        if seconds != prev_seconds:
            colon_on = not colon_on
            prev_seconds = seconds
        
        # Display the time
        tm.numbers(display_hours, minutes, colon=colon_on)
        
        # Brief pause to prevent display flicker
        sleep(0.1)

if __name__ == '__main__':
    set_initial_time()  # Only needed if RTC isn't set
    print("Starting clock...")
    run_clock()
```

## Core Concepts

Let's break down the key concepts students need to understand:

### 1. Real-Time Clock (RTC)

   - The RTC is a hardware component that keeps track of time
   - It continues running even when the microcontroller is reset
   - Time is stored as a tuple: (year, month, day, weekday, hours, minutes, seconds, subseconds)
   - Students should understand why RTCs are important for accurate timekeeping

### 2. Time Formats

   - 24-hour vs 12-hour time conversion
   - Why we need to handle special cases (midnight = 0 hours → 12, noon = 12 stays 12)
   - The concept of AM/PM

### 3. Display Multiplexing

   - How LED displays show multiple digits (though the TM1637 handles this internally)
   - Why we need a brief sleep to prevent display flicker
   - How brightness control works with PWM (Pulse Width Modulation)

### 4. State Management
   - Tracking the colon state for blinking
   - Maintaining previous second value to detect changes
   - Why we use global variables in this context

### 5. Program Structure
   - Main loop design
   - Function organization
   - Error handling (not shown but important in real applications)

## Common challenges 

Here are some challenges students might encounter:

### 1. Time Drift

   - The RTC might drift slightly over time
   - In real applications, you'd want to sync with an NTP server periodically

### 2. Power Management

   - Display brightness affects power consumption
   - Consider dimming display in low light conditions
   - Think about battery life in portable applications

### 3. User Interface

   - Adding buttons to set the time
   - Handling time zone changes
   - Adding features like alarms or timers

## Extensions

Here are some additional projects that students could try:

1. Add a temperature display that alternates with the time
2. Implement automatic brightness control using a light sensor
3. Add alarm functionality with a buzzer
4. Create a menu system for setting the time
5. Add a battery backup system

For reference, this code builds on the concepts shown in our
```clock-driver.py``` file, but simplifies the implementation thanks to the TM1637's built-in controller. 
