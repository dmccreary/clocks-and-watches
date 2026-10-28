# References: OLED Displays and Framebuffers

1. [OLED](https://en.wikipedia.org/wiki/OLED) - Wikipedia - Explains how organic light-emitting diodes make each pixel its own light source, giving true blacks and high contrast without a backlight. Useful background for the small SSD1306 panel students wire up in this chapter.

2. [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) - Wikipedia - Describes the framebuffer as a block of memory holding every pixel's value, plus display modes and page flipping. It supports this chapter's central idea of drawing in memory first and then pushing it to the screen.

3. [Display resolution](https://en.wikipedia.org/wiki/Display_resolution) - Wikipedia - Defines resolution as the number of pixels across and down a screen, such as 128 by 64. It helps students connect pixel counts to coordinate mapping and to the memory a framebuffer needs.

4. Computer Graphics with OpenGL (4th Edition) - Donald Hearn, M. Pauline Baker, and W. Randolph Carithers - Pearson - No single author originated the frame buffer idea, so this is chosen as a widely used text whose graphics-systems overview presents raster-scan displays, refresh buffers, and pixel memory clearly, which matches this chapter's model.

5. Making Embedded Systems (2nd Edition) - Elecia White - O'Reilly Media - No single author originated this topic, so this is chosen as a well-regarded practical book that treats displays and other peripherals as hardware plus software working together, reinforcing how a microcontroller talks to an OLED.

6. [framebuf: Frame buffer manipulation](https://docs.micropython.org/en/latest/library/framebuf.html) - MicroPython Documentation - The official reference for the FrameBuffer class, including fill and pixel methods and pixel formats like MONO_VLSB and RGB565. It is the exact module behind this chapter's fill and pixel drawing commands.

7. [Monochrome OLED Breakouts](https://learn.adafruit.com/monochrome-oled-breakouts) - Adafruit Learning System - Introduces 128x64 and 128x32 SSD1306 OLED boards and explains their I2C and SPI interface options. It helps students choose between the two wiring styles covered in the SSD1306 setup sections.

8. [Raspberry Pi Pico: SSD1306 OLED Display (MicroPython)](https://randomnerdtutorials.com/raspberry-pi-pico-ssd1306-oled-micropython/) - Random Nerd Tutorials - A step-by-step guide wiring a 0.96 inch SSD1306 to a Pico over I2C, scanning for the 0x3C address, and writing text, filling, and drawing pixels. It mirrors this chapter's first working display program.

9. [SSD1306 Datasheet: 128 x 64 Dot Matrix OLED/PLED Driver with Controller](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf) - Solomon Systech (hosted by Adafruit) - The manufacturer's datasheet describing the controller's display memory, addressing modes, and I2C and SPI interfaces. Advanced readers can see how framebuffer bytes map onto physical pixels.

10. [Raspberry Pi Pico and RP2 Quick Reference](https://docs.micropython.org/en/latest/rp2/quickref.html) - MicroPython Documentation - Shows how to create hardware I2C and SPI buses on the Pico with pin choices and freq or baudrate settings. It supports this chapter's baudrate tuning and refresh rate discussion.
