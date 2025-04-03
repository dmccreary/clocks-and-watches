# Example 1: Basic Text Display
# This is the simplest way to show text
from machine import Pin, SPI
import ssd1306
from writer import Writer
import your_converted_font  # This is your converted font file

# Setup display
spi = SPI(0, sck=Pin(2), mosi=Pin(3))
oled = ssd1306.SSD1306_SPI(128, 64, spi, Pin(5), Pin(4), Pin(6))

# Create writer
writer = Writer(oled, your_converted_font)

# Clear screen
oled.fill(0)

# Write text at top left
writer.set_textpos(0, 0)
writer.printstring("Hello!")
oled.show()

# Example 2: Multiple Lines
def write_centered(text, y_position):
    # Get the width of the text (approximate)
    text_width = len(text) * your_converted_font.height()  # Assuming square-ish characters
    # Calculate starting x position to center text
    x_position = (oled.width - text_width) // 2
    writer.set_textpos(x_position, y_position)
    writer.printstring(text)

oled.fill(0)  # Clear screen
write_centered("Line 1", 0)
write_centered("Line 2", 20)
write_centered("Line 3", 40)
oled.show()

# Example 3: Scrolling Text
def scroll_text(text, delay=0.1):
    import time
    
    # Start below the screen
    y_pos = oled.height
    
    while y_pos > -20:  # Scroll until text is off screen
        oled.fill(0)  # Clear screen
        writer.set_textpos(0, y_pos)
        writer.printstring(text)
        oled.show()
        y_pos -= 1  # Move text up
        time.sleep(delay)

scroll_text("Scrolling Text!")

# Example 4: Alternating Fonts (if you have multiple fonts)
import small_font   # A smaller converted font
import large_font   # A larger converted font

small_writer = Writer(oled, small_font)
large_writer = Writer(oled, large_font)

def mixed_fonts():
    oled.fill(0)
    
    # Write title in large font
    large_writer.set_textpos(0, 0)
    large_writer.printstring("Title")
    
    # Write details in small font
    small_writer.set_textpos(0, 30)
    small_writer.printstring("Details here\nMore info\nLast line")
    
    oled.show()

mixed_fonts()

# Example 5: Simple Animation
def blink_text(text, times=3):
    import time
    
    for _ in range(times):
        # Show text
        oled.fill(0)
        writer.set_textpos(0, 20)
        writer.printstring(text)
        oled.show()
        time.sleep(0.5)
        
        # Hide text
        oled.fill(0)
        oled.show()
        time.sleep(0.5)

blink_text("Blink!")