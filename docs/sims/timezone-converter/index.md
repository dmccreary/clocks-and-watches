---
title: Timezone Converter
description: Convert UTC to local time for seven time zones using integer second arithmetic, with a world map of time-zone bands, a DST toggle, highlighted date rollovers, and a Predict mode.
image: /sims/timezone-converter/timezone-converter.png
og:image: /sims/timezone-converter/timezone-converter.png
twitter:image: /sims/timezone-converter/timezone-converter.png
social:
   cards: false
quality_score: 100
---

# Timezone Converter

<iframe src="main.html" height="527px" width="100%" scrolling="no"></iframe>

[Run the Timezone Converter MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/timezone-converter/main.html"
        height="527px"
        width="100%"
        scrolling="no"></iframe>
```

## About This MicroSim

After `ntptime.settime()`, the Pico's clock holds **UTC**. To show local time, your program adds the zone's offset, in seconds, to the UTC count:

```python
local_secs = utc_secs + OFFSET_HOURS * 3600
```

Because the time is a single count of seconds, crossing midnight takes care of itself: the date simply rolls forward or backward. This MicroSim does the same integer arithmetic.

The world map is divided into 24 time-zone bands, one for each hour of offset, labeled −12 to +12 across the top. The orange band is the zone you chose and the red dot marks a city in it. Under the map, each band shows its local hour right now. Bands tinted **purple** are still on the previous calendar day, and bands tinted **green** are already on the next day, so you can see where the date line between "today" and "yesterday" falls.

The two clocks show UTC and the local time. When the local date is different from the UTC date, the local clock gets an orange border and its date is highlighted. The line at the bottom writes the conversion out as arithmetic. The zones match the table in Chapter 14, including India's half-hour offset of +5:30.

## How to Use

1. Drag **UTC time** to change the time of day in 15-minute steps, and pick a **date** with the date box.
2. Choose a zone from the menu. The orange band moves on the map.
3. Check **DST on** to use the daylight offset (one hour larger). UTC and India do not observe DST, so nothing changes for them.
4. Press **Predict**. The MicroSim picks a random UTC time and hides the local clock. Type your answer as `HH:MM` and press **Check**. Press **Exit Predict** to leave the mode.

## Lesson Plan

### Learning Objective

Students will apply offsets to convert UTC to local time, including date rollovers (Bloom: Applying).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- UTC and time zones (Chapter 14)
- Seconds since an epoch (Chapter 6)

### Activities

1. **Worked example** (3 min): Set 01:30 UTC on the 15th with US Central. Confirm the chapter's result: 19:30 on the 14th.
2. **Find the rollovers** (4 min): For US Pacific, find the range of UTC times that give a local date one day earlier. Repeat for India and Central Europe. Which zones roll forward instead of back?
3. **Daylight saving** (3 min): Turn on DST for US Central and explain why the offset becomes −5, not −7.
4. **Predict** (5 min): Students use Predict mode until they get five right in a row, saying out loud whether the date changes before they press Check.

### Assessment

- It is 23:00 UTC on March 3. What is the local time and date in Central Europe in winter? (00:00 on March 4.)
- How many seconds is India's offset? (19,800.)
- Explain why storing time in UTC and converting only for display makes daylight saving easier to handle.

## References

1. [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) - Wikipedia article on UTC.
2. [Time zone](https://en.wikipedia.org/wiki/Time_zone) - Wikipedia; how zones and offsets are defined, including half-hour zones.
3. [Daylight saving time in the United States](https://en.wikipedia.org/wiki/Daylight_saving_time_in_the_United_States) - Wikipedia; the second-Sunday-in-March rule.
4. [MicroPython time module](https://docs.micropython.org/en/latest/library/time.html) - `time.time()` and `time.localtime()` on the Pico.
