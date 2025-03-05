from machine import Pin
from neopixel import NeoPixel
from utime import sleep, localtime

# Pin and NeoPixel setup
NEOPIXEL_PIN = 2
NUMBER_PIXELS = 45
strip = NeoPixel(Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

# Define the pixel indices for each Fibonacci square
# Our matrix is five rows by 9 columns
# Organized in terms of Fibonacci numbers (1, 1, 2, 3, 5)
five = [3,4,5,6,7,8,12,13,14,15,16,17,21,22,23,24,25,26,30,31,32,33,34,35,39,40,41,42,43,44]   
three = [18,19,20,27,28,29,36,37,38]
two = [0,1,9,10] 
oneA = [2]
oneB = [11]
fibonacci_squares = [oneA, oneB, two, three, five]
fibonacci_values = [1, 1, 2, 3, 5]

# Color definitions - RGB format (red, green, blue)
OFF_COLOR = (0, 0, 0)          # Complete off (no light) for inactive squares
HOUR_COLOR = (25, 0, 0)        # Red for hours
MINUTE_COLOR = (0, 25, 0)      # Green for minutes
BOTH_COLOR = (0, 0, 25)        # Blue for both hours and minutes (not white)

def clear_display():
    """Turn all LEDs off (dark gray)"""
    for i in range(NUMBER_PIXELS):
        strip[i] = OFF_COLOR
    strip.write()

def calculate_square_usage(hours, minutes):
    """Determine which squares to use for hours and minutes"""
    hour_squares = []
    minute_squares = []
    
    # Calculate which squares to use for hours (1-12)
    remaining_hours = hours
    for i in range(len(fibonacci_values) - 1, -1, -1):
        if fibonacci_values[i] <= remaining_hours:
            hour_squares.append(i)
            remaining_hours -= fibonacci_values[i]
    
    # Calculate which squares to use for minutes (0-12 representing 0-60 minutes in 5-min increments)
    minutes_in_5min_blocks = minutes // 5
    remaining_minutes = minutes_in_5min_blocks
    for i in range(len(fibonacci_values) - 1, -1, -1):
        if fibonacci_values[i] <= remaining_minutes:
            minute_squares.append(i)
            remaining_minutes -= fibonacci_values[i]
            
    return hour_squares, minute_squares

def update_clock_display(hour_squares, minute_squares):
    """Update the NeoPixel display based on which squares are active"""
    # First, turn all pixels off
    clear_display()
    
    # Then, set the active squares with appropriate colors
    for i in range(len(fibonacci_squares)):
        pixels = fibonacci_squares[i]
        
        is_hour = i in hour_squares
        is_minute = i in minute_squares
        
        # Determine color based on function
        if is_hour and is_minute:
            color = BOTH_COLOR      # Blue: both hours and minutes
        elif is_hour:
            color = HOUR_COLOR      # Red: hours only  
        elif is_minute:
            color = MINUTE_COLOR    # Green: minutes only
        else:
            continue  # Skip inactive squares (they're already off)
        
        # Set all pixels in this Fibonacci square to the selected color
        for pixel in pixels:
            strip[pixel] = color
    
    # Write the changes to the strip
    strip.write()

def print_time_debug(hours, minutes, seconds, hour_squares, minute_squares):
    """Print detailed information about the time and active squares"""
    print(f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    # Print active hour squares and their values
    hour_values = [fibonacci_values[i] for i in hour_squares]
    hour_sum = sum(hour_values)
    print(f"Hours: {hour_sum} (using {hour_values})")
    
    # Print active minute squares and their values
    minute_values = [fibonacci_values[i] for i in minute_squares]
    minute_sum = sum(minute_values) * 5
    print(f"Minutes: {minute_sum} (using {minute_values} × 5)")
    
    # Show which Fibonacci squares are used for what
    for i, value in enumerate(fibonacci_values):
        usage = []
        if i in hour_squares:
            usage.append("hours")
        if i in minute_squares:
            usage.append("minutes")
            
        status = ", ".join(usage) if usage else "inactive"
        print(f"Square {value}: {status}")
    
    print("-" * 30)

# Main loop
while True:
    # Get current time
    current_time = localtime()
    hours = current_time[3] % 12
    if hours == 0:
        hours = 12  # Convert 0 to 12 for 12-hour format
    
    # Round minutes to nearest 5-minute mark
    minutes = current_time[4]
    minutes = round(minutes / 5) * 5
    if minutes == 60:
        minutes = 0
        hours = (hours % 12) + 1  # Increment hour when minutes roll over
    
    seconds = current_time[5]
    
    # Calculate which squares to use
    hour_squares, minute_squares = calculate_square_usage(hours, minutes)
    
    # Update the display
    update_clock_display(hour_squares, minute_squares)
    
    # Print time information to console
    print(f"Actual time: {current_time[3]:02d}:{current_time[4]:02d}:{seconds:02d}")
    print(f"Rounded time: {hours:02d}:{minutes:02d}")
    print_time_debug(hours, minutes, seconds, hour_squares, minute_squares)
    
    # Update every minute (or more frequently if needed)
    sleep(60 - seconds)  # Sleep until the next minute