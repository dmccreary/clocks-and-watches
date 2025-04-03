# Font to MicroPython

!!! prompt
    Please give me suggestions on how I can display other fonts on the SSD1306 OLED using MicroPython.

Based on the provided code and the SSD1306 OLED display usage, I can suggest several approaches for displaying different fonts:

1.  Using Framebuf-Based Custom Fonts

```python
import framebuf
# Define a custom font as a bytearrayCUSTOM_FONT ={'0':bytearray([0b01110000,0b10001000,0b10001000,0b10001000,0b01110000]),# Add more characters...}defdraw_custom_char(oled, char, x, y):if char in CUSTOM_FONT:        fb = framebuf.FrameBuffer(CUSTOM_FONT[char],8,8, framebuf.MONO_VLSB)        oled.blit(fb, x, y)`

```

2.  Using Third-Party Font Modules

```
python
Copy

`# writer.py module approachfrom writer import Writer
import font10  # Example font moduledefsetup_custom_font(oled):    font_writer = Writer(oled, font10)    font_writer.set_textpos(0,0)return font_writer`

```

3.  Converting TrueType Fonts You can convert TrueType fonts to a bitmap format using tools like `font2py` and then use them in your project:

```
python
Copy

`# After converting a font using font2pyimport my_converted_font
from writer import Writer
definit_custom_font(oled):    font_writer = Writer(oled, my_converted_font)return font_writer`

```

4.  Creating Bitmap Fonts

```python
# Define a simple bitmap font
DIGIT_FONT ={'0':[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
# # Add more characters...
}
def draw_bitmap_char(oled, char, x, y, scale=1):
    if char in DIGIT_FONT:
        bitmap = DIGIT_FONT[char]
        for y_pos, row in enumerate(bitmap):
            for x_pos, pixel in enumerate(row):
                if pixel:
                    if scale ==1:
                        oled.pixel(x + x_pos, y + y_pos,1)
                    else:
                        oled.fill_rect(x + x_pos*scale, y + y_pos*scale, scale, scale,1)
```

5. Using the `micropython-font-to-py` Tool First, install the tool on your computer:

You will need to go to the Peter Hinch GitHub site and clone the repo

```sh
git clone https://github.com/peterhinch/micropython-font-to-py.git
```

```bash
pip install micropython-font-to-py
```

Then convert a font:

```bash
font_to_py.py YourFont.ttf 20 font20.py
```

And use it in your code:

```python
import font20
from writer import Writer
defsetup_font(oled):    font_writer = Writer(oled, font20)    font_writer.set_textpos(0,0)return font_writer
# Usage
# writer = setup_font(oled)
# writer.writeln('Hello World!')
# oled.show()`
```

Important considerations:

1. **Memory constraints** - The OLED display and MicroPython device have limited memory, so be mindful of font size
2. **Performance** - Larger fonts or complex rendering can impact refresh rates
3. **Display resolution** - The SSD1306 is 128x64 pixels, so ensure fonts are appropriately sized
4. **Character set** - Consider limiting to necessary characters to save memory

!!! prompt
    Please proved detailed steps to use the micropython-font-to-py program to convert both truetype and bitmap fonts to be used with MicroPython on the OLED display

Here are steps for converting and using fonts with micropython-font-to-py.

## Font Conversion and Implementation Guide

### 1.  **Installation**:

```bash
pip install micropython-font-to-py
```

### 2.  **Font Preparation**:

-   For TrueType fonts: Get your .ttf file ready
-   For bitmap fonts: Create a Python module with your bitmap definitions
-   Ensure you have necessary font licenses for usage

### 3.  **Converting TrueType Fonts**

```bash
# Basic conversionfont_to_py.py YourFont.ttf 20 font20.py
# Fixed-width conversion
font_to_py.py -x YourFont.ttf 20 font20.py
# Include extended ASCII
font_to_py.py -x -s YourFont.ttf 20 font20.py
# Compressed output
font_to_py.py -f YourFont.ttf 20 font20.py`
```

### 4. File Transfer To Pico

-   Transfer both the generated font file (e.g., `font20.py`) and the `writer.py` class to your MicroPython device
-   You can use tools like Thonny IDE or `ampy` for file transfer

### 5. Implementation

-   Use the code from the artifact above to implement the font rendering
-   Start with small fonts (12-20px) to ensure good performance
-   Test with your specific character set

## Common Issues and Solutions

### Memory Issues

The Raspberry Pi Pico is limited to using 264K of RAM.  Fonts
can easily use up this memory.

-   If you get memory errors, try:
    -   Using smaller font sizes
    -   Converting fewer characters
    -   Using compressed output (-f option)
    -   Using fixed-width fonts (-x option)

2.  **Performance Issues**:

-   If rendering is slow:
    -   Use smaller fonts
    -   Reduce update frequency
    -   Consider buffering text changes
    -   Use fixed-width fonts for faster rendering

3.  **Display Issues**:

-   If text appears garbled:
    -   Check font orientation
    -   Verify display initialization
    -   Ensure proper I2C/SPI configuration
    -   Verify font file transfer was successful


## Download GitHub Code

### 1. First, clone the repository:

```bash
git clone https://github.com/peterhinch/micropython-font-to-py.git`

```

### 2. Navigate to the directory:

```bash
cd micropython-font-to-py`
```

### 3. Pillow Library

You'll also need the Python Imaging Library (PIL) installed:

```bash
pip install pillow`
```
### 4. Move Conversion Tool

The `font_to_py.py` script is in this directory. You can either:

-   Use it directly from this location
-   Copy it to a convenient location in your PATH
-   Make it executable with `chmod +x font_to_py.py`

### 5. Run Converter

Now you can use the tool. For example:

```bash
python3 font_to_py.py YourFont.ttf 20 font20.py`
```

If you want to make the tool generally available on your system:

```bash
# Make executablechmod +x font_to_py.py
# Optional: Move to a directory in your PATH (e.g., /usr/local/bin)sudocp font_to_py.py /usr/local/bin/font_to_py`
```

These examples and explanations should help you understand how fonts work on the OLED display. The first artifact provides a thorough explanation of the concepts, while the second gives you practical code examples to try.

Some key points to remember:

1.  Always convert your font files before using them
2.  Keep track of your screen position
3.  Clear the screen before writing new text
4.  Don't forget to call `oled.show()` to display changes
5.  Be mindful of memory usage with large fonts

## Limiting Font Sets

For most clocks, you will only need the digits 0-9, the colon and the "A", "M" and "P" letters

!!! prompt
    The Raspberry Pi Pico has 264K or RAM. Will this be a problem if I just use the digits 0-9, a colon and the "P" and "M" letters?

No, using just digits 0-9, a colon, and the letters "A" "M" and "P" (14 characters total) won't cause memory problems on the Raspberry Pi Pico's 264KB of RAM, even with relatively large font sizes. Let me explain why:

### 1. Memory Requirements per Character

-   Each character in a bitmap font is essentially a grid of pixels
-   For example, if you use a 32x32 pixel font size:
    -   Each character = 32x32 = 1024 bits = 128 bytes
    -   14 characters × 128 bytes = 1,892 bytes total
-   Even at 64x64 pixels (very large):
    - Each character = 64x64 = 4096 bits = 512 bytes
    - 14 characters × 512 bytes = 7,168 bytes

### 2. OLED Frame Buffer Size
The SSD1306 OLED (128x64) buffer takes:
- 128 × 64 = 8,192 bits = 1,024 bytes (1K RAM)

### 3. Total Memory Impact
- Font data: ~1.7KB - 6.7KB (depending on size)
- OLED buffer: 1KB
- Writer class and supporting code: ~1KB
- Total: ~4KB - 9KB

This means:

- You're using less than 4% of the Pico's RAM even with very large fonts
- Plenty of memory remains for your program logic
- You could even store multiple font sizes if desired

## Helvetica Variable Width

!!! prompt
    When I display the time "1:11" the screen looks odd. Please change the code to use a variable width helvetica font.

Yes, with a fixed-width font, the "1" digits can look awkwardly spaced. Let's modify the code to use variable-width Helvetica for better visual appearance.

The key improvements in this version:

1. **Variable Width Handling**:
   - Each digit takes only the space it needs
   - "1" is narrower than other digits
   - Spacing looks more natural

2. **Hour Format Changes**:
   - Hours don't show leading zeros (e.g., "1:11" not "01:11")
   - Minutes still show leading zeros
   - Looks more like a traditional clock display

3. **Dynamic Positioning**:
   - Calculates exact width of each character
   - Centers the entire time display properly
   - Adjusts spacing between elements automatically

4. **Improved Spacing**:
   - Colon spacing adjusted for better visual balance
   - Small gaps added between elements
   - Everything remains centered regardless of digit widths

Would you like me to:
1. Adjust any of the spacing parameters?
2. Add AM/PM display?
3. Test with specific time combinations?

```python
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
```