# References: Color Displays and Smartwatch Faces

1. [High color](https://en.wikipedia.org/wiki/High_color) - Wikipedia - Explains storing each pixel in two bytes, including the 5-6-5 layout where green gets the extra bit. It introduces the RGB565 encoding used by the chapter's color565 function and palette.

2. [RGB color model](https://en.wikipedia.org/wiki/RGB_color_model) - Wikipedia - Covers how mixing red, green, and blue light reproduces a wide range of colors and how values are numerically encoded. It underpins the chapter's RGB565 color mixer and color palette sections.

3. [Thin-film-transistor liquid-crystal display](https://en.wikipedia.org/wiki/Thin-film-transistor_liquid-crystal_display) - Wikipedia - Describes how a transistor at each pixel improves addressing and contrast in LCDs, along with panel types and interfaces. It explains the TFT LCD hardware behind the ILI9341 and ST7735 screens.

4. Envisioning Information (1990) - Edward R. Tufte - Graphics Press - Tufte's "Color and Information" chapter sets the guiding rule "above all, do no harm" and sorts color into labeling, measuring, representing, and decorating. A clear guide for picking watch face palettes.

5. Digital Video and HD: Algorithms and Interfaces (2nd Edition) - Charles Poynton - Morgan Kaufmann - No single author originated color encoding, so this is chosen as the book most praised for clearly explaining how digital color values, gamma, and perception relate to what appears on a screen.

6. [ILI9341 Datasheet: 240RGBx320 Resolution and 262K Color](https://cdn-shop.adafruit.com/datasheets/ILI9341.pdf) - ILI Technology (hosted by Adafruit) - The manufacturer's specification for the single-chip TFT driver, listing resolution, color depth, and SPI interface. Advanced readers can see what the ILI9341 driver in this chapter controls.

7. [1.8" TFT Display Breakout and Shield](https://learn.adafruit.com/1-8-tft-display) - Adafruit Learning System - Introduces a 128x160 color display using the ST7735R driver with 4-wire SPI. A practical overview of the small TFT type and wiring this chapter compares with others.

8. [1.28inch LCD Module](https://www.waveshare.com/wiki/1.28inch_LCD_Module) - Waveshare Wiki - Documents a round 240x240 IPS module driven by the GC9A01 over SPI, noting the circular visible area and RGB565 support. Practical specs for the round smartwatch display.

9. [micropython-nano-gui](https://github.com/peterhinch/micropython-nano-gui) - Peter Hinch, GitHub - A MicroPython graphics library supporting color TFTs and circular GC9A01 displays, with a shared colors module. It shows how real projects organize palettes and drivers like this chapter's colors file.

10. [WebAIM: Contrast and Color Accessibility](https://webaim.org/articles/contrast/) - WebAIM - Defines contrast ratio and explains the 4.5:1 and 3:1 readability thresholds for text. It helps students choose watch face colors that stay legible, supporting the contrast ratio section.
