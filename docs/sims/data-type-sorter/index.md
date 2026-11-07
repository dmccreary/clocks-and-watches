---
title: Data Type Sorter
description: "Drag Python value cards such as 3.0, \"42\" and (2026, 9, 28) into bins for int, float, str, bool, list and tuple, with hints for wrong answers."
image: /sims/data-type-sorter/data-type-sorter.png
og:image: /sims/data-type-sorter/data-type-sorter.png
twitter:image: /sims/data-type-sorter/data-type-sorter.png
social:
   cards: false
quality_score: 100
---

# Data Type Sorter

<iframe src="main.html" height="467px" width="100%" scrolling="no"></iframe>

[Run the Data Type Sorter MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Every value in a MicroPython program has a **data type**, and the type decides what you can do with it. You can add two `int` values, but adding an `int` to a `str` raises a `TypeError`. This MicroSim turns the clues for each type into a quick sorting game.

A card shows one value written exactly as it would appear in Python code. You decide which of six bins it belongs in. The deck includes tricky cards on purpose: `"42"` has quote marks, so it is a string; `3.0` and `1e3` are floats; `"True"` in quotes is a string, not a boolean. A wrong drop sends the card back with a hint about the clue to look for, and a right drop shows what `type()` would print.

This MicroSim supports the chapter [MicroPython Basics: Variables and Data Types](../../chapters/03-micropython-basics/index.md).

## How to Use

1. Drag the card on top of the stack into the bin you think matches its type, or simply click a bin.
2. A correct answer turns the bin green, shows the `type()` result and deals the next card.
3. A wrong answer turns the bin pink, sends the card back and shows a hint. Try again.
4. The score line counts cards sorted right on the first try, your current streak and your best streak.
5. Press **Shuffle and Restart** to deal all 16 cards again in a new order.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/data-type-sorter/main.html"
        height="467px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Classify a written Python value as int, float, str, bool, list or tuple
- Name the clue that marks each type: a decimal point, quote marks, True/False, square brackets or parentheses
- Explain why "42" is a string and 3.0 is a float even though both look like whole numbers

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Typing values in the Thonny REPL
- The type() function from this chapter

### Activities

1. **Exploration** (5 min): Sort the whole deck once without help. Write down every card that you got wrong on the first try.
2. **Guided Practice** (5 min): For each card you missed, say the clue out loud ("quote marks mean str"), then test it in the Thonny REPL with `type()`.
3. **Assessment** (5 min): Shuffle and sort the deck again. Aim for 14 or more correct on the first try.

### Assessment

- Students sort at least 14 of 16 cards correctly on the first try.
- Students can explain why `"42"` is a `str` and `3.0` is a `float`.
- Students can write one new example value for each of the six types.

## References

1. [Python Built-in Types](https://docs.python.org/3/library/stdtypes.html) - official reference for numbers, strings, lists and tuples
2. [MicroPython Language and Implementation](https://docs.micropython.org/en/latest/reference/index.html) - how MicroPython follows standard Python
3. [Data type](https://en.wikipedia.org/wiki/Data_type) - Wikipedia overview of data types in programming
