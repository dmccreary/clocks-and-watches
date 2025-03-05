## Pixel Test

```python
// Fibonacci Pixel Test
from machine import Pin
from neopixel import NeoPixel
from utime import sleep, ticks_ms

NEOPIXEL_PIN = 0
NUMBER_PIXELS = 45
RAINBOW_LENGTH = 7

strip = NeoPixel(Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

## our matrix is five rows by 9 columns
## rows 1 to five columns 4 to 9
five = [3,4,5,6,7,8,12,13,14,15,16,17,21,22,23,24,25,26,30,31,32,33,34,35,39,40,41,42,43,44]   
three = [18,19,20, 27,28,29,36,37,38]
two = [0,1,9,10] 
oneA = [2]
oneB = [11]

lists = [oneA, oneB, two, three, five]

for i in five:
   strip[i] = (25,0,0)

for i in three:
   strip[i] = (0,25,0)

for i in two:
   strip[i] = (0,0,25)

for i in oneA:
   strip[i] = (25,25,0)

for i in oneB:
   strip[i] = (25,0,25)
   
strip.write()
```