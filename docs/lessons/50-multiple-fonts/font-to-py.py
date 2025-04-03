# Step 1: Install the font conversion tool
# pip install micropython-font-to-py

# Step 2: Convert TrueType Font
# Command line usage:
# font_to_py.py [font_file] [height] [output_file] [-x] [-f] [-s]
# 
# Options:
# -x          -- horizontally fixed-width font
# -f          -- format compressed output file
# -s          -- include ASCII codes >= 0x80 (extended ASCII)
# 
# Example commands:
# font_to_py.py Arial.ttf 20 arial_20.py
# font_to_py.py -x -s RobotoMono.ttf 16 roboto_mono_16.py

# Step 3: Create Writer Class (save as writer.py)
import framebuf

class Writer():
    def __init__(self, display, font, verbose=True):
        self.display = display
        self.font = font
        # Populate char_dict with font's characters
        self.char_dict = {}
        self.init_char_dict()
        self.x = 0
        self.y = 0
        self.verbose = verbose
        
    def init_char_dict(self):
        for char in range(self.font.get_start(), self.font.get_end() + 1):
            self.char_dict[chr(char)] = None

    def _newline(self):
        self.y += self.font.height()
        self.x = 0
        if self.y >= self.display.height - self.font.height():
            if self.verbose:
                print('Screen full! Returning to top.')
            self.y = 0
    
    def set_textpos(self, x, y):
        self.x = x
        self.y = y
    
    def printstring(self, string):
        for char in string:
            self._printchar(char)
            
    def _printchar(self, char):
        if char == '\n':
            self._newline()
            return
        
        if char not in self.char_dict:
            if self.verbose:
                print(f'Character {char} not in font!')
            return
            
        buf, w = self.font.get_ch(char)
        fb = framebuf.FrameBuffer(bytearray(buf), w, self.font.height(), framebuf.MONO_HLSB)
        
        # Check if we need to wrap to next line
        if self.x + w > self.display.width:
            self._newline()
            
        # Draw the character
        self.display.blit(fb, self.x, self.y)
        self.x += w

# Step 4: Example Implementation (save as main.py)
from machine import Pin, I2C, SPI
import ssd1306
import arial_20  # Your converted font
from writer import Writer

# Display setup (using your existing configuration)
SCL = Pin(2)
SDA = Pin(3)
RES = Pin(4)
DC = Pin(5)
CS = Pin(6)

spi = SPI(0, sck=SCL, mosi=SDA, baudrate=100000)
oled = ssd1306.SSD1306_SPI(128, 64, spi, DC, RES, CS)

# Initialize the Writer with the display and font
writer = Writer(oled, arial_20)

# Clear the display
oled.fill(0)

# Set text position (optional)
writer.set_textpos(0, 0)

# Write some text
writer.printstring("Hello!")
oled.show()

# Another example with multiple lines
oled.fill(0)
writer.set_textpos(0, 0)
writer.printstring("Line 1\nLine 2")
oled.show()

# Converting Bitmap Fonts:
# For bitmap fonts, create a Python module with the font definition:

# Example bitmap_font.py
class BitmapFont:
    def __init__(self):
        self._height = 8
        self._characters = {
            '0': bytearray([
                0b00111100,
                0b01000010,
                0b01000010,
                0b01000010,
                0b01000010,
                0b01000010,
                0b00111100,
                0b00000000
            ]),
            # Add more characters as needed
        }
    
    def height(self):
        return self._height
        
    def get_ch(self, ch):
        if ch in self._characters:
            return self._characters[ch], 8  # width is 8 pixels
        return None, 0
        
    def get_start(self):
        return ord('0')
        
    def get_end(self):
        return ord('9')

# Usage with bitmap font
from bitmap_font import BitmapFont
custom_font = BitmapFont()
writer = Writer(oled, custom_font)
writer.printstring("012")
oled.show()

# Tips for Font Creation:
# 1. Keep font size reasonable (12-20px) for OLED display
# 2. Test with your specific character set to save memory
# 3. Use fixed-width fonts for consistent spacing
# 4. Consider memory limitations when choosing font size
# 5. Test rendering performance with your chosen font

# Error Handling Example:
def safe_write(writer, text, x=None, y=None):
    try:
        if x is not None and y is not None:
            writer.set_textpos(x, y)
        writer.printstring(text)
        return True
    except Exception as e:
        print(f"Error writing text: {e}")
        return False