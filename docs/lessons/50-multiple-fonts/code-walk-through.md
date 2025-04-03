# Understanding Font Display on OLED - A Student's Guide

## Introduction
Hey there! Let's learn how to display different fonts on an OLED screen using MicroPython. Think of this like creating your own digital sign board, where you can choose different writing styles (fonts) to display your messages.

## Part 1: The Writer Class - Your Digital Pen
First, let's understand the `Writer` class. This is like a special pen that knows how to write characters on your OLED screen.

```python
class Writer:
    def __init__(self, display, font, verbose=True):
        self.display = display    # Your OLED screen
        self.font = font         # The font you want to use
        self.char_dict = {}      # Dictionary to store characters
        self.init_char_dict()    # Set up the characters
        self.x = 0              # Starting position (left)
        self.y = 0              # Starting position (top)
        self.verbose = verbose  # Whether to show helpful messages
```

Think of this like:
- `display` is your paper (OLED screen)
- `font` is your pen style
- `x` and `y` are where your pen is on the paper
- `char_dict` is like your alphabet reference

## Part 2: Character Management
```python
def init_char_dict(self):
    # Get all characters from start to end of font
    for char in range(self.font.get_start(), self.font.get_end() + 1):
        self.char_dict[chr(char)] = None
```

This is like making a list of all the letters and symbols your font can write. If you only need numbers 0-9, your list would be shorter than if you need the whole alphabet.

## Part 3: Moving to a New Line
```python
def _newline(self):
    # Move down by the font height
    self.y += self.font.height()
    # Go back to the left side
    self.x = 0
    # If we reach the bottom, go back to top
    if self.y >= self.display.height - self.font.height():
        if self.verbose:
            print('Screen full! Returning to top.')
        self.y = 0
```

This is like when you reach the end of a line in your notebook:
1. Move down to the next line
2. Start from the left again
3. If you reach the bottom of the page, go back to the top

## Part 4: Writing Characters
```python
def _printchar(self, char):
    # Handle new line character
    if char == '\n':
        self._newline()
        return
    
    # Check if we can write this character
    if char not in self.char_dict:
        if self.verbose:
            print(f'Character {char} not in font!')
        return
    
    # Get the character's image data
    buf, w = self.font.get_ch(char)
    fb = framebuf.FrameBuffer(bytearray(buf), w, self.font.height(), 
                             framebuf.MONO_HLSB)
    
    # If we'll go past the right edge, start a new line
    if self.x + w > self.display.width:
        self._newline()
    
    # Draw the character and move right
    self.display.blit(fb, self.x, self.y)
    self.x += w
```

This is the most important part! For each character:
1. Check if it's a new line (\n)
2. Make sure we can write this character
3. Get the character's picture (like a stamp)
4. If we're too close to the right edge, move to next line
5. "Stamp" the character on the screen
6. Move right for the next character

## Part 5: Putting It All Together
Here's how you use it:

```python
# Set up your OLED display
spi = SPI(0, sck=SCL, mosi=SDA, baudrate=100000)
oled = ssd1306.SSD1306_SPI(128, 64, spi, DC, RES, CS)

# Create your writer with a font
writer = Writer(oled, your_font)

# Clear the screen
oled.fill(0)

# Move to position (0,0) - top left
writer.set_textpos(0, 0)

# Write some text
writer.printstring("Hello!")

# Show it on the screen
oled.show()
```

## Common Questions

### Q: Why do we need a special writer class?
A: The OLED screen only understands pixels (tiny dots). The Writer class converts letters into the right pattern of dots.

### Q: What's a framebuffer?
A: Think of it like a rough draft - we draw the character there first, then copy it to the screen. It's like using tracing paper before drawing on your final paper.

### Q: Why check the screen edges?
A: Just like you don't want to write off the edge of your paper, we need to make sure text stays within the screen boundaries.

## Tips for Success
1. Start with small fonts - big fonts take more memory
2. Test your text before running it on the device
3. Remember to call `oled.show()` to display your changes
4. Clear the screen (`oled.fill(0)`) before writing new text
5. Keep track of your position with `set_textpos()`

## Practice Exercises
1. Try writing your name in different positions on the screen
2. Make text that automatically wraps around when it hits the edge
3. Create a scrolling message that moves up the screen
4. Mix different fonts in the same display

Remember: The OLED screen is 128 pixels wide and 64 pixels tall. Think of it like a very small piece of graph paper where you can light up individual squares to form letters!
```