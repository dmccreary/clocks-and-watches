# Big Round Speaker Clock

## Parts

1. Raspberry Pio Pico W (not the Pico 2W)
1. GC9B72 Display
2. MAX98357A Microphone and Amplifier
3. Two momentary press buttons

## Pins

GC9B72

CLK - GPIO 2
DSA - GPIO 3
RST GPIO 4
DC 5
VS 6
BL 7

MAX98357A

BCLK GPIO 9
LRC GPIO 10
DIN GPIO 11
GAIN GPIO 12
SD - Not Connected

Buttons

MODE - GPIO 13
UP - GPIO 14
DOWN 15

## Test Programs

### Blink Onboard LED
01-blink-onboard-led.py

Blinks the on board LED every .5 second on and off.

### Probe
02-probe.py

Runs a probe of the hardware capabilities of the Pico including RAM and file system.

### Button Test
03-button-tests.py

Test if the mode, up and down buttons are connected correctly

### Display Test
04-display-test.py

Prints "Hello World" on the display

### Speaker Test
05-speaker-test.py

Sends a simple sound to the speaker for 2 seconds to verify the MAX AMP is connected correctly

### WiFi Test
06-test-wifi.py

Test the wifi and checks that the secrets.py file exists and has valid values.
Also checks that the config.py file exists and has the location (city), timezone and DST settings.

### Get Time
07-get-time.py

Gets the time from an NTP server displays it on the console and the screen in a simple digital format

## Clock Functions

### Big Clock

Use all the surface of the display to display the largest clock using geometric drawing functions.

## Big Clock + Current Temp

Add the current outside temperature based on the city in the config.py

## Medium Clock + Current Temp + Forecast

Make the clock digits smaller so that the current temp plus the hi/low forecast is shown for today and tomorrow

## Alarm Clock

Allow the user to set and alarm and a wake-up tone

## Stopwatch

## Timer

## Quote of the Day