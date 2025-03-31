# TM1650 Simple Clock Demo
# Displays time in HH:MM format with blinking colon

from machine import Pin, I2C
import config
from utime import sleep, localtime

# Configure I2C
sda = Pin(config.I2C_SDA_PIN)
scl = Pin(config.I2C_SCL_PIN)
i2c = I2C(config.I2C_BUS, sda=sda, scl=scl, freq=50000)  # 50 kHz

# Display addresses - one for each digit
DIGIT_ADDR = [0x34, 0x35, 0x36, 0x37]  # Left to right

# Segment patterns for digits
SEGMENT_PATTERNS = {
    0: 0x3F,   # 0
    1: 0x06,   # 1
    2: 0x5B,   # 2
    3: 0x4F,   # 3
    4: 0x66,   # 4
    5: 0x6D,   # 5
    6: 0x7D,   # 6
    7: 0x07,   # 7
    8: 0x7F,   # 8
    9: 0x6F,   # 9
    ' ': 0x00,  # space (blank)
}

# Decimal point bit
DP_BIT = 0x80  # Bit 7 controls the decimal point

def reset_display():
    """Reset the display by clearing all digits"""
    for addr in DIGIT_ADDR:
        i2c.writeto(addr, b'\x00')
    sleep(0.05)

def set_digit(position, value, decimal_point=False):
    """Set a specific digit (position 0-3) with optional decimal point"""
    if 0 <= position <= 3:
        # Get pattern for the value
        if isinstance(value, int) and 0 <= value <= 9:
            pattern = SEGMENT_PATTERNS[value]
        elif value in SEGMENT_PATTERNS:
            pattern = SEGMENT_PATTERNS[value]
        else:
            pattern = SEGMENT_PATTERNS[' ']  # Default to blank for unsupported characters
        
        # Add decimal point if requested
        if decimal_point:
            pattern |= DP_BIT
        
        # Write pattern to the appropriate digit address
        i2c.writeto(DIGIT_ADDR[position], bytes([pattern]))

def display_time(hours, minutes, blink_colon=True):
    """Display time in HH:MM format with blinking colon
    
    Args:
        hours: Hours (0-23)
        minutes: Minutes (0-59)
        blink_colon: Whether to show the colon (decimal point)
    """
    # Convert 24-hour to 12-hour format
    hours_12 = hours % 12
    if hours_12 == 0:
        hours_12 = 12  # 12 AM/PM instead of 0
    
    # Display hours (left two digits)
    if hours_12 < 10:
        set_digit(0, ' ')  # Blank for single-digit hours
        set_digit(1, hours_12, blink_colon)  # Hour with colon
    else:
        set_digit(0, 1)  # First digit of hour (always 1 for 10-12)
        set_digit(1, hours_12 % 10, blink_colon)  # Second digit with colon
    
    # Display minutes (right two digits)
    set_digit(2, minutes // 10)  # Tens place of minutes
    set_digit(3, minutes % 10)  # Ones place of minutes

def run_clock(duration=60, update_interval=0.5):
    """Run the clock for the specified duration
    
    Args:
        duration: How many seconds to run the clock
        update_interval: How often to update the display (seconds)
    """
    print(f"Running clock for {duration} seconds...")
    
    # Calculate number of iterations
    iterations = int(duration / update_interval)
    
    for i in range(iterations):
        # Get current time
        current_time = localtime()
        hours = current_time[3]    # hours (0-23)
        minutes = current_time[4]  # minutes (0-59)
        seconds = current_time[5]  # seconds (0-59)
        
        # Blink the colon every second
        blink_colon = (seconds % 2 == 0)
        
        # Display the time
        display_time(hours, minutes, blink_colon)
        
        # Print time to console for debugging
        hours_12 = hours % 12
        if hours_12 == 0:
            hours_12 = 12
        print(f"Time: {hours_12:02d}:{minutes:02d}:{seconds:02d}")
        
        # Wait for the next update
        sleep(update_interval)

# Main program
def main():
    print("TM1650 Simple Clock Demo")
    print("Press Ctrl+C to exit")
    
    # Clear the display
    reset_display()
    
    try:
        # Run the clock continuously
        while True:
            run_clock(duration=60, update_interval=0.5)
    except KeyboardInterrupt:
        print("\nClock stopped by user")
    finally:
        # Clear the display before exit
        reset_display()
        print("Clock demo completed")

if __name__ == "__main__":
    main()