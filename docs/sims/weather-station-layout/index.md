---
title: Weather Station Layout
description: Design a 152 by 152 pixel e-paper weather display by dragging and resizing panels, choose each panel's update schedule, and simulate a day to count refreshes, WiFi connections and battery life.
image: /sims/weather-station-layout/weather-station-layout.png
og:image: /sims/weather-station-layout/weather-station-layout.png
twitter:image: /sims/weather-station-layout/weather-station-layout.png
social:
   cards: false
quality_score: 0
---

# Weather Station Layout

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Weather Station Layout MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A weather station display shows three kinds of data, and each one changes at a different
speed:

| Panel | Data source | Typical update |
|-------|-------------|----------------|
| **Time** | DS3231 real-time clock | Every minute |
| **Indoor** temperature and humidity | DHT22 sensor | Every 5 to 10 minutes |
| **Forecast** icon, high and low | Open-Meteo over WiFi | Every 1 to 3 hours |

The gray square is a mock 152 by 152 pixel e-paper screen. You can **drag** each panel to
move it and drag its **corner** to resize it. Hover over a panel to see its data source and
update interval. The info box also checks whether the time digits are tall enough to read
from across a room, and warns you if two panels overlap (then updating one panel forces the
other to be redrawn too).

Press **Simulate day** to run a 24-hour timeline. The MicroSim counts the updates, the
partial and full refreshes, and the WiFi connections, then estimates the battery life on a
500 mAh cell.

**The energy model is deliberately simple:** the Pico sleeps at 0.3 mA between updates, wakes
for 0.2 s at 25 mA for each update, a partial refresh costs 10 mA for 0.25 s plus up to 0.5 s
more for a larger area, a full refresh (after every 30 partial refreshes) costs 10 mA for 2 s,
and each forecast fetch keeps WiFi on for 4 s at 70 mA. Real parts differ, but the
comparisons between layouts and schedules are what matter.

## How to Use

1. Drag the panels into a layout you like, and resize them by dragging a corner.
2. Hover over each panel to read its data source and update interval.
3. Choose how often each panel updates with the **Time every**, **Indoor every** and
   **Forecast every** menus.
4. Press **Simulate day** and read the counts and the estimated battery life. Press it again
   to pause, and once more to continue.
5. Press **Reset layout** to go back to the starting design.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/weather-station-layout/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
20 minutes

### Prerequisites

- E-paper partial and full refresh (Chapter 19)
- The non-blocking `due()` timer pattern (Chapter 6)
- WiFi power cost (Chapters 14 and 18)

### Learning Objectives

Students will be able to:

- Design a readable layout for a small e-paper weather display
- Evaluate how each panel's update interval changes refreshes, WiFi connections and battery life
- Justify an update schedule by matching it to how fast each kind of data changes

### Activities

1. **Baseline** (4 min): Without changing anything, press **Simulate day**. Record the refresh
   counts, WiFi connections and battery life.
2. **Which schedule matters?** (8 min): Change one menu at a time and simulate again: forecast
   every 30 minutes, then every 6 hours; indoor every 1 minute, then every 30 minutes; time every
   5 minutes. Which single change moved the battery life the most? Why does the forecast
   schedule matter so much more than the indoor schedule?
3. **Design and defend** (8 min): Design your own layout for a bedside clock that must be read from
   the bed. Make the time digits pass the readability check, avoid overlapping panels, and choose a
   schedule. Simulate a day and write two sentences explaining your trade-offs.

### Assessment

- The student explains why the forecast panel should update far less often than the time panel.
- The student identifies WiFi connections as the most expensive single event in the day.
- The student justifies a layout that balances readable digits against refresh cost.

## References

1. [Electronic paper](https://en.wikipedia.org/wiki/Electronic_paper) - Wikipedia article on bistable e-paper displays and how they refresh.
2. [Open-Meteo API documentation](https://open-meteo.com/en/docs) - The free weather forecast service used by the Chrono Smart Clock Kit.
3. [DHT22 / AM2302 sensor](https://learn.adafruit.com/dht) - Adafruit guide to the temperature and humidity sensor.
4. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - The frame buffer used to draw each panel before it is sent to the e-paper display.
