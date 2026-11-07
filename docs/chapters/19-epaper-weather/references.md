# References: E-Paper and Weather Displays

1. [Electronic paper](https://en.wikipedia.org/wiki/Electronic_paper) - Wikipedia - Surveys reflective displays that mimic printed ink, including electrophoretic types with charged pigment particles, and notes that they hold an image without power. It directly supports the chapter's e-paper, refresh, and ghosting discussion.

2. [Bistability](https://en.wikipedia.org/wiki/Bistability) - Wikipedia - Explains systems with two stable resting states, using examples such as light switches and flip-flop memory. It clarifies the chapter's bistable display idea: pixels stay black or white until energy flips them.

3. [Weather station](https://en.wikipedia.org/wiki/Weather_station) - Wikipedia - Describes the instruments that measure temperature, humidity, pressure, wind, and precipitation, and how stations are sheltered and networked. It gives context for the chapter's weather station display and its temperature and humidity readouts.

4. The Visual Display of Quantitative Information (2nd Edition) - Edward R. Tufte - Graphics Press - Tufte introduced the data-ink ratio: erase ink that carries no information. Applied to a small black-and-white e-paper screen, it guides which borders and labels to drop from a weather layout.

5. Code: The Hidden Language of Computer Hardware and Software (2nd Edition) - Charles Petzold - Microsoft Press - Petzold builds memory step by step from relays and gates in its Feedback and Flip-Flops chapter, making bistability concrete. That story helps students see why e-paper can remember a picture.

6. [Pico-ePaper-2.9 Wiki](https://www.waveshare.com/wiki/Pico-ePaper-2.9) - Waveshare - Manufacturer page for a Pico e-paper module, listing SPI wiring, full versus partial refresh timing, and advice to refresh fully now and then to clear ghosting. It matches the chapter's Waveshare display and refresh sections.

7. [Adafruit E-Ink Display Breakouts](https://learn.adafruit.com/adafruit-eink-display-breakouts) - Adafruit Learning System - Overview of e-ink breakouts that keep their image without power, using on-board SRAM as a frame buffer and the Adafruit_EPD library. It supports the chapter's bistable display and low-power points.

8. [Temperature and Humidity (DHT11 and DHT22)](https://docs.micropython.org/en/latest/esp8266/tutorial/dht.html) - MicroPython Documentation - Shows the built-in dht module: create the sensor, call measure(), then read temperature() in Celsius and humidity() as a percentage, with polling limits. It supports the chapter's temperature and humidity displays.

9. [Raspberry Pi Pico with DHT11/DHT22 using MicroPython](https://randomnerdtutorials.com/raspberry-pi-pico-dht11-dht22-micropython/) - Random Nerd Tutorials - A step-by-step Pico tutorial covering wiring, pull-up resistors, a script using try/except to survive failed reads, and saving it as main.py. It helps students build the weather station's sensor input.

10. [Open-Meteo Weather Forecast API](https://open-meteo.com/en/docs) - Open-Meteo - Documents a free forecast service returning JSON for any latitude and longitude, with hourly and daily temperature, precipitation, and wind. It lets a Wi-Fi Pico W add forecast data to the weather display.
