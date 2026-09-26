# Introduction to Clock and Watch Project and Kits

We have grouped information on specific projects together in
structures that allow you to find what you are looking for
and customize both the hardware and software.  We focus on
using generative AI tools to customize the code to accelerate
your development an enhance your understanding of how each
project works.

## Project Structure

Each kit has the following structure:

### 1. Introduction

A brief overview of the project including a image of the clock, key features, approximate costs and possible variations.

### 2. Purchasing and Assembly
This section shows how to purchase and assemble the clock.  Most of
the clocks require at a minimum a Raspberry Pi Pico ($4), a breadboard ($2) and a display.  In addition you might add one or more of the following items:

1. A real-time clock with a coin-cell battery backup to remember the time between power resets.
2. Buttons to manually set the date and time.
3. A wireless Pico W to allow your clock to connect to the internet.
4. A speaker for alarms.
5. A photodetector for detecting the lighting conditions.
6. Additional controls such as a knob for adjusting the time.

Since these features can be used in combination, we also provide
you with generative AI prompts to customize the code to run these
clocks and watches

### 3. Code

This kit section provides you with a  walkthrough of the core pa
project has a brief overview of the project, a separate page for the physical assembly of the clock and a detailed guide to program the clock.  The documentation may also
have sample generative AI prompts you can use to generate your own code using a tool such as OpenAI's ChatGPT or Anthropic Claude.  In general, the more precise your prompt is, the higher the odds that the code generated will be correct.

Each project also has separate folder in the GitHub "src/kits" folder.  The running clock programs (called the "mains") come in several variations.  One uses manual buttons (main-buttons.py) to set the time after a power outage.  The other version called the "main-rtc.py" file name uses a real-time-clock to remember the time between power outages.  They require an additional RTC clock that uses a coin-cell battery to hold the current time.  If you find a "main-w.py" file that uses the secrets.py file to lookup
your local wifi login to get the time from the internet.  These versions don't need buttons or a RTC to get the correct time. They only need internet access.

### 4. Generative AI Prompts

## LED Clocks

### Standard TM1637 LED Clock

This is a great starter clock.  The display is low-cost ($1-2), and
it only requires four wires to connect it up. It is easy to program LED clock with 4 7-segment displays.

[TM1637 LED Clock Kit](./tm1637/index.md)

### TinySSD1306 OLED with an I2C Interface

This small low-cost OLED display is easy to hook up with just 4 wires.
The combination of low-cost and easy hookup makes it an ideal
starter project.

We hav purchased these OLEDs on eBay for under $4 each.  Some of
they have the first 20 rows yellow and the remaining 44 rows blue.

[Tiny SSD1306 OLED with I2C Interface](./ssd1306-i2c/index.md)

### Larger 2.42" OLED SSD1306 with SPI Interface

[Larger OLED](./oled-large/index.md)

## NeoPixel Clocks

### Binary Clock

[Binary Clock](./neopixel/binary-clock/index.md)

### Seven Segment Clock

[](./neopixel/seven-segment-clock/index.md)

### Fibonacci Clock

[Fibonacci Clock](./neopixel/fibonacci-clock/index.md)


## LilyGo RP2040

[LilyGo RP2040 Kit](./lilygo/index.md)

## SmartWatch Displays

[GC9a01 Smartwatch Display](./gc9a01/index.md)

[GC9B72 2.1" Smartwatch Display with Pico 2 W](./sw-gc9b72/index.md)

[Waveshare LCD Smartwatch Display](./waveshare-lcd/index.md)

## E-Paper Clocks

[Waveshare e-Paper](./e-paper/index.md)

