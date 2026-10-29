---
title: Time Tuple Explorer
description: "The eight fields of time.localtime() as labeled boxes filled from your clock: click for an index, drag for a slice like now[3:6], or quiz yourself on the field order."
image: /sims/time-tuple-explorer/time-tuple-explorer.png
og:image: /sims/time-tuple-explorer/time-tuple-explorer.png
twitter:image: /sims/time-tuple-explorer/time-tuple-explorer.png
social:
   cards: false
quality_score: 100
---

# Time Tuple Explorer

<iframe src="main.html" height="502px" width="100%" scrolling="no"></iframe>

[Run the Time Tuple Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

`time.localtime()` returns a **time tuple** of eight integers in a fixed order: year, month, day of the month, hour, minute, second, weekday and day of the year. Almost every clock program starts by pulling a few of those numbers out, usually with the one-line slice `hour, minute, second = time.localtime()[3:6]`.

The boxes show each field with its index above and its name below, filled from your computer's clock when the page loads (the same way Thonny sets the Pico's clock). A small analog and digital clock show the same moment. Click one box to see the expression that extracts it, or drag across several boxes to build a slice; the panel shows the resulting tuple and the matching unpacking line. You can also set the slice with the start and stop menus. **Quiz me** hides the names and asks you to find a field by name. Check **Live clock** to make the values tick.

This MicroSim supports the chapter [Getting the Time in MicroPython](../../chapters/06-getting-time/index.md).

## How to Use

1. Click a box to see `now[i]` and that field's range.
2. Press on one box and drag to another to select a slice. The bracket and the panel show `now[start:stop]` and its result.
3. Use the **Slice** menus to set the start and stop indexes exactly. Try a stop that is not bigger than the start.
4. Check **Quiz me**, read the question and click the right box. Press **New question** for another. Check **Live clock** to update the values every second.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/time-tuple-explorer/main.html"
        height="502px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Identify the name, index and range of each of the eight time tuple fields
- Apply indexing such as now[3] to extract one field
- Apply slicing such as now[3:6] to extract several fields and unpack them

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Tuples and indexing from Chapter 3
- The localtime() function

### Activities

1. **Exploration** (4 min): Click each box in turn and read its range. Note which fields start at 0 and which start at 1.
2. **Guided Practice** (6 min): Make the slices for the date [0:3], the time [3:6] and a one-field slice [3:4]. Explain the trailing comma in (14,).
3. **Assessment** (5 min): Turn on Quiz me and answer eight questions in a row correctly.

### Assessment

- Students give the index of any field from memory.
- Students write the slice that returns (month, day).
- Students explain that the stop index is not included in a slice.

## References

1. [MicroPython time.localtime()](https://docs.micropython.org/en/latest/library/time.html#time.localtime) - official description of the eight-field tuple
2. [Python Tutorial: Lists and slicing](https://docs.python.org/3/tutorial/introduction.html#lists) - how indexing and slicing work, with examples
3. [ISO week date](https://en.wikipedia.org/wiki/ISO_week_date) - why weekday numbering starts on Monday in ISO 8601
