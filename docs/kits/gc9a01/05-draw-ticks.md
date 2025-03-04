# Draw Clock Face Ticks

This program draws 12 short white radial lines around a watch face.

![](../../img/watch-face-ticks.png)

We use the same math we used to draw a single hand.  However, in
this example we just need to iterate through a range of 0 to 12.

```py
for i in range(0,12):
    radians = (i/12)*TWO_PI
    x1 = int(math.sin(radians)*TICK_START)
    y1 = -int(math.cos(radians)*TICK_START)
    x2 = int(math.sin(radians)*TICK_END)
    y2 = -int(math.cos(radians)*TICK_END)
    tft.line(CENTER+x1, CENTER+y1, CENTER+x2, CENTER+y2, WHITE)
```

Instead of just drawing from the center to a point at (x,y), we
need to calculate four numbers.  These are the start and
ending points of each tick.

## Full Program

```py
from machine import Pin, SPI
from utime import sleep, localtime
import math
import gc9a01

# this uses the standard Dupont ribbon cable spanning rows 4-9 on our breadboard
SCK_PIN = 2 # row 4
SDA_PIN = 3
DC_PIN = 4
CS_PIN = 5
# GND is row 8
RST_PIN = 6

# define the SPI intrface
spi = SPI(0, baudrate=60000000, sck=Pin(SCK_PIN), mosi=Pin(SDA_PIN))
tft = gc9a01.GC9A01(spi, 240, 240, reset=Pin(RST_PIN, Pin.OUT),
    cs=Pin(CS_PIN, Pin.OUT), dc=Pin(DC_PIN, Pin.OUT), rotation=0
)
tft.init()

CENTER = 120
TICK_START = 80
TICK_END = 100

# our counter will range from 0 to 59
# A full circle is 2*Pi radians
TWO_PI = 3.145175*2
counter = 0
WHITE = gc9a01.color565(255, 255, 255)
BLACK = gc9a01.color565(0, 0, 0)
tft.fill(BLACK)
for i in range(0,12):
    radians = (i/12)*TWO_PI
    x1 = int(math.sin(radians)*TICK_START)
    y1 = -int(math.cos(radians)*TICK_START)
    x2 = int(math.sin(radians)*TICK_END)
    y2 = -int(math.cos(radians)*TICK_END)
    print(i, radians, x1, y1, x2, y2)  
    tft.line(CENTER+x1, CENTER+y1, CENTER+x2, CENTER+y2, WHITE)
```