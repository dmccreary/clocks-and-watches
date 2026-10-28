# References: Drawing Shapes, Text, and Animation

1. [Bresenham's line algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm) - Wikipedia - Describes the integer-only incremental method for choosing which pixels best approximate a straight line. It explains what happens inside the line command students use to draw clock hands and tick marks.

2. [Midpoint circle algorithm](https://en.wikipedia.org/wiki/Midpoint_circle_algorithm) - Wikipedia - Shows how a circle is drawn on a pixel grid using integer decisions and eight-way symmetry. It clarifies how circles and arcs for a clock face are produced on a small display.

3. [Multiple buffering](https://en.wikipedia.org/wiki/Multiple_buffering) - Wikipedia - Explains double buffering and page flipping, where a complete image is prepared off screen before being shown. It directly supports this chapter's double buffering and smooth animation techniques that avoid flicker.

4. Computer Graphics from Scratch (1st Edition, 2021) - Gabriel Gambetta - No Starch Press - Gambetta's Lines chapter introduces a small Interpolate function that computes one variable from another, then reuses it to draw any line. This clear abstraction explains line drawing without heavy algebra.

5. Computer Graphics: Principles and Practice (3rd Edition) - John F. Hughes, Andries van Dam, and coauthors - Addison-Wesley - No single author originated pixel-level shape drawing, so this is chosen as the field's most widely cited textbook, a standard reference for rasterizing lines, circles, and polygons on a pixel grid.

6. [The Adafruit GFX Library: Graphics Primitives](https://learn.adafruit.com/adafruit-gfx-graphics-library/graphics-primitives) - Adafruit Learning System - Walks through drawing pixels, lines, rectangles, circles, and triangles, and contrasts outline and filled versions. It gives students a common vocabulary for the shape tools this chapter teaches.

7. [micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py) - Peter Hinch, GitHub - Documents the command-line tool that converts TrueType fonts into Python modules, plus the Writer class that draws them. It is the real tool behind this chapter's custom fonts and font loading sections.

8. [Double Buffer](https://gameprogrammingpatterns.com/double-buffer.html) - Game Programming Patterns, Robert Nystrom - Uses a clear analogy to explain why drawing straight into the visible framebuffer causes tearing and how swapping two buffers fixes it. Great reading for the double buffering section.

9. [MicroPython: SSD1306 OLED Display Scroll Functions and Draw Shapes](https://randomnerdtutorials.com/micropython-ssd1306-oled-scroll-shapes-esp32-esp8266) - Random Nerd Tutorials - Provides working code for scrolling the screen and drawing lines, rectangles, circles, and triangles on an SSD1306. It matches the shape and scroll marquee topics students practice here.

10. [Using a SSD1306 OLED display](https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html) - MicroPython Documentation - The official tutorial showing FrameBuffer calls such as line, rect, fill_rect, text, scroll, and show, plus a logo example. It reinforces how the chapter's drawing commands combine into a picture.
