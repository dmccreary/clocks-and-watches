---
title: Font Pipeline
description: Follow the steps from a TrueType font on your computer to large text on the OLED, and estimate how much memory a font module needs.
image: /sims/font-pipeline/font-pipeline.png
og:image: /sims/font-pipeline/font-pipeline.png
twitter:image: /sims/font-pipeline/font-pipeline.png
social:
   cards: false
quality_score: 0
---

# Font Pipeline

<iframe src="main.html" height="442px" width="100%" scrolling="no"></iframe>

[Run the Font Pipeline MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

The OLED's built-in font is fixed at 8 by 8 pixels. To get large, clean clock digits you convert a
normal font into a Python module. This diagram shows the whole pipeline:

1. A **TrueType font file** on your computer (for example `FreeSans.ttf`).
2. **`font_to_py.py`** draws each character at a chosen pixel height and saves the bitmaps.
   The `-c` option keeps only the characters you list.
3. A **generated module**, such as `freesans32.py`.
4. **Copy to the Pico** with `mpremote` or Thonny.
5. **`import`** the module on the Pico.
6. A **Writer** copies each character's bitmap into the framebuffer.
7. The **text on screen** appears after `show()`.

The first three steps run on your computer and the last three on the Pico. Click (or hover over)
any box to see the command it uses.

The **Memory estimate** view answers the chapter's warning that big fonts can use tens of
kilobytes. Set a font height and a list of characters, and it estimates the module's size step by
step and compares it with the Pico's 264 KB of RAM.

## How to Use

1. Click each box in order and read the command in the side panel.
2. Notice which steps run on your computer and which run on the Pico.
3. Press **Memory estimate**. With height 32 and the digits plus colon, read the estimated size.
4. Press **Full ASCII (95)**. How many times bigger is the font now?
5. Drag **Font height** to 64. Which change costs more memory: more characters or a taller font?

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/font-pipeline/main.html"
        height="442px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
13 minutes

### Prerequisites

- Text rendering with the built-in 8 by 8 font (Chapter 12)
- Copying files to the Pico (Chapter 4)

### Learning Objectives

Students will be able to:

- Describe the steps from a font file to text on the OLED
- Identify which steps run on the computer and which run on the Pico
- Estimate how font height and character count affect memory use

### Activities

1. **Order the steps** (4 min): Without looking, write the seven steps in order. Then check against the diagram.
2. **Size it** (5 min): Use the Memory estimate to compare digits-only and full-ASCII fonts at heights 24, 32 and 48.
3. **Pick fonts** (4 min): Plan a clock with big time digits and a small date line. Choose two fonts and estimate their total memory.

### Assessment

- The student explains that font_to_py.py runs on the computer, not the Pico.
- The student explains why -c 0123456789: keeps the module small.
- The student estimates that doubling the height roughly triples or quadruples the bitmap size.

## References

1. [micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py) - Peter Hinch's converter and writer.py, used in this chapter.
2. [TrueType](https://en.wikipedia.org/wiki/TrueType) - Wikipedia article on outline font files.
3. [Computer font](https://en.wikipedia.org/wiki/Computer_font) - Wikipedia article comparing bitmap and outline fonts.
4. [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) - Official documentation for copying files to the Pico from the command line.
5. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) - Documentation for the diagram library used here.
