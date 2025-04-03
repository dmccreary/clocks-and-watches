# Step 1: Convert Helvetica font WITHOUT fixed width
# python3 font_to_py.py Helvetica.ttf 40 helvetica_40.py
# Note: Removed the -x flag to allow variable width characters

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

"""
Key Changes from Fixed-Width Version:
1. Removed -x flag from font conversion
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
"""