# Helvetica Example

This example shows how to use the font-to-python.py program to generate aHelvetica font in a fixed width and variable width version.  Note that the fixed width version is easier to place digits on the display, but the variable width version is more aesthetically pleasing for times such as 11:11.

## Fixed Width Version

Here are the key points about this version

The font is converted at 40 pixels high.  This is about the maximum size that will fit on a 128x64 OLED display with four digits and a colon.

This allows approximately:

- Each digit: ~25-30 pixels wide
- Total for 4 digits: ~100-120 pixels
- Colon and spacing: ~8-10 pixels
- Total width: ~120 pixels (fits within 128 pixel display)
- Height of 40 pixels (fits within 64 pixel display)

To maximize size while ensuring fit:

1. Start with 40px height
2. If too large, decrease by 2px until perfect fit
3. If too small, increase by 2px until just before overflow

```python
# Step 1: Convert Helvetica font
# First, download Helvetica.ttf (or use Arial as a free alternative)
# Then run the conversion tool (assuming 40px height which allows ~128px width for 4 digits + colon):
#
# python3 font_to_py.py -x Helvetica.ttf 40 helvetica_40.py
#
# The -x flag creates a fixed-width font which is better for digit alignment

from machine import Pin, SPI
import ssd1306
from writer import Writer
import helvetica_40  # Your converted font

class LargeTimeDisplay:
    def __init__(self):
        # Initialize SPI and display
        self.spi = SPI(0, 
                      sck=Pin(2),   # Clock
                      mosi=Pin(3),  # Data
                      baudrate=100000)
        
        # Display pins
        self.dc = Pin(6)    # Data/Command
        self.rst = Pin(4)   # Reset
        self.cs = Pin(5)    # Chip Select
        
        # Initialize display
        self.display = ssd1306.SSD1306_SPI(
            128,    # Width
            64,     # Height
            self.spi,
            self.dc,
            self.rst,
            self.cs
        )
        
        # Initialize writer with large font
        self.writer = Writer(self.display, helvetica_40)
        
        # Calculate center position (implemented below)
        self.calculate_positions()
    
    def calculate_positions(self):
        """Calculate positions for centered time display"""
        # Get character width (should be fixed due to -x flag in conversion)
        dummy_char, char_width = helvetica_40.get_ch('0')
        
        # Calculate total width (4 digits + colon)
        total_width = (char_width * 4) + 20  # 20 pixels for colon and spacing
        
        # Calculate starting x position to center time
        self.start_x = (128 - total_width) // 2
        
        # Calculate y position to center vertically
        self.start_y = (64 - helvetica_40.height()) // 2
        
        # Store character width for later use
        self.char_width = char_width
    
    def draw_colon(self, x, y):
        """Draw a large colon for separating hours and minutes"""
        # Draw two rectangles for the colon
        colon_width = 6
        colon_height = 6
        spacing = 10
        
        # Top dot
        self.display.fill_rect(x, y + 10, colon_width, colon_height, 1)
        # Bottom dot
        self.display.fill_rect(x, y + 10 + spacing + colon_height, 
                             colon_width, colon_height, 1)
    
    def show_time(self, hours, minutes):
        """Display time in large font"""
        # Clear display
        self.display.fill(0)
        
        # Format hours and minutes
        hour_str = f"{hours:02d}"
        min_str = f"{minutes:02d}"
        
        # Current x position for drawing
        x = self.start_x
        
        # Draw hours
        self.writer.set_textpos(x, self.start_y)
        self.writer.printstring(hour_str)
        
        # Draw colon
        x += self.char_width * 2 + 5  # Move past hours
        self.draw_colon(x, self.start_y)
        
        # Draw minutes
        x += 15  # Move past colon
        self.writer.set_textpos(x, self.start_y)
        self.writer.printstring(min_str)
        
        # Update display
        self.display.show()

# Example usage
if __name__ == '__main__':
    # Create display instance
    time_display = LargeTimeDisplay()
    
    # Test display with different times
    from time import sleep
    
    test_times = [
        (12, 30),
        (1, 15),
        (5, 45),
        (10, 20),
    ]
    
    # Show each test time for 2 seconds
    for hours, minutes in test_times:
        time_display.show_time(hours, minutes)
        sleep(2)
```

## Variable Width Version

Here are the key changes from the Fixed-Width Version:

1. Removed -x flag from font conversion which allows variable width characters
2. Added methods to calculate individual character widths
3. Dynamically calculate positions based on actual character widths
4. Adjusted spacing to look better with variable width characters
5. Removed leading zero from hours for better appearance
6. Added flexible spacing calculations

Notes on Spacing:
- Hours: No leading zero, natural width
- Minutes: Always show leading zero
- Colon: Centered between hours and minutes
- Overall: Centered on display

This allows approximately:

```python
from machine import Pin, SPI
import ssd1306
from writer import Writer
import helvetica_40  # Your converted font

class LargeTimeDisplay:
    def __init__(self):
        # Initialize SPI and display
        self.spi = SPI(0, 
                      sck=Pin(2),   # Clock
                      mosi=Pin(3),  # Data
                      baudrate=100000)
        
        # Display pins
        self.dc = Pin(6)    # Data/Command
        self.rst = Pin(4)   # Reset
        self.cs = Pin(5)    # Chip Select
        
        # Initialize display
        self.display = ssd1306.SSD1306_SPI(
            128,    # Width
            64,     # Height
            self.spi,
            self.dc,
            self.rst,
            self.cs
        )
        
        # Initialize writer with large font
        self.writer = Writer(self.display, helvetica_40)
        
    def get_char_width(self, char):
        """Get width of a specific character"""
        _, width = helvetica_40.get_ch(char)
        return width
    
    def get_string_width(self, text):
        """Calculate total width of a string"""
        return sum(self.get_char_width(char) for char in text)
    
    def draw_colon(self, x, y):
        """Draw a large colon for separating hours and minutes"""
        colon_width = 6
        colon_height = 6
        spacing = 10
        
        # Top dot
        self.display.fill_rect(x, y + 10, colon_width, colon_height, 1)
        # Bottom dot
        self.display.fill_rect(x, y + 10 + spacing + colon_height, 
                             colon_width, colon_height, 1)
        
        return colon_width  # Return width for position calculations
    
    def show_time(self, hours, minutes):
        """Display time with variable width font"""
        # Clear display
        self.display.fill(0)
        
        # Format numbers with leading zeros for minutes only
        hour_str = str(hours)  # No leading zero for hours
        min_str = f"{minutes:02d}"  # Leading zero for minutes
        
        # Calculate widths
        hour_width = self.get_string_width(hour_str)
        min_width = self.get_string_width(min_str)
        colon_total_width = 16  # Colon width plus spacing
        
        # Calculate total width
        total_width = hour_width + colon_total_width + min_width
        
        # Calculate starting position to center everything
        start_x = (128 - total_width) // 2
        start_y = (64 - helvetica_40.height()) // 2
        
        # Current x position
        x = start_x
        
        # Draw hours
        self.writer.set_textpos(x, start_y)
        self.writer.printstring(hour_str)
        x += hour_width + 5  # Move past hours plus small gap
        
        # Draw colon
        self.draw_colon(x, start_y)
        x += colon_total_width - 5  # Move past colon (adjusted for spacing)
        
        # Draw minutes
        self.writer.set_textpos(x, start_y)
        self.writer.printstring(min_str)
        
        # Update display
        self.display.show()

# Example usage
if __name__ == '__main__':
    # Create display instance
    time_display = LargeTimeDisplay()
    
    # Test display with different times
    from time import sleep
    
    test_times = [
        (1, 11),   # Testing narrow digits
        (11, 11),  # Testing wide number combination
        (10, 01),  # Testing leading zero
        (2, 22),   # Testing repeated digits
    ]
    
    # Show each test time for 2 seconds
    for hours, minutes in test_times:
        time_display.show_time(hours, minutes)
        sleep(2)
```