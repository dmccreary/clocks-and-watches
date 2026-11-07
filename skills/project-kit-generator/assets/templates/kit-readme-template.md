<!--
KIT README TEMPLATE (src/kits/<kit>/README.md). This is the kit's own documentation for the
person who builds and maintains it. The student lesson lives in docs/kits/<kit>/index.md; this
file is shorter and more technical, but it keeps the same friendly, plain-words voice.
Keep both in step: file counts, lab numbers, pin tables and expected outputs must match.
-->
# {{Sensor}} Kit with a {{Low-cost Color Display}}

{{Two sentences: what it measures, what it shows.}}

{{One paragraph for each part: what it is, how it talks to the Pico (define I2C / SPI in one line).}}

{{One paragraph on how this kit relates to its parent kit: which labs are unchanged, which are
new, and why any number is skipped or reused.}}

## What You Need

| Part | Notes |
|------|-------|
| Raspberry Pi Pico | Any Pico or Pico W with MicroPython already installed |
| {{Sensor}} | {{price, where, alternatives that cost more but ship faster}} |
| {{Display}} | {{size, controller, interface; "about $5"}} |
| Solderless breadboard | Half-size is plenty |
| {{N}} jumper wires | {{how many per part; which kind}} |
| USB cable | Must be a data cable, not a charge-only cable |

## Wiring

<!-- One numbered list AND one pin table for each part. Say which pins are NOT the same as another
     part's pins that have the same name. Note the optional pins (backlight). -->

## Upload the Programs

```bash
./upload-code.sh
```

{{What gets copied (lib first, then config, labs, main.py = the capstone), how main.py starts by
itself, how to stop it, how to pick a port, what to do if the port is busy.}}

## The Programs

<!-- One section per lab: what it does, when to run it, the exact expected output in a code block,
     and what "TEST PASS" means. Paste real output. -->

### 01-{{bus-scanner}}.py

## Things to Try

## When Things Go Wrong

| What you see | What to try |
|--------------|-------------|
| {{symptom}} | {{fix}} |

## How the Math Works

## {{Sensor}} Facts

| Item | Value |
|------|-------|
| {{range}} | {{from the datasheet}} |
