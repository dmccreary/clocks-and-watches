---
title: The Pico Platform: Pins, Files, and Firmware
description: GPIO pins, pull-up resistors, flash, files, firmware, boot files, and workflow on the Raspberry Pi Pico.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:32:03
version: 1.10
---

# The Pico Platform: Pins, Files, and Firmware

## Summary

Students configure GPIO pins, understand pull-up resistors, and learn how files and firmware live in flash memory. They practice transferring code and understanding boot and main files. After this chapter they can manage a Pico project reliably.

## Concepts Covered

This chapter covers the following 19 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Pin Configuration | 405 |
| Pico W | 22 |
| GPIO Pins | 404 |
| Flash Memory | 74 |
| Memory Management | 2 |
| Firmware Versions | 4 |
| Pull-Up Resistors | 8 |
| File System on Pico | 15 |
| Dual Core Usage | 1 |
| Garbage Collection | 1 |
| Firmware Flashing | 3 |
| Interpreter Selection | 1 |
| Internal Pull-Up | 1 |
| Boot and Main Files | 2 |
| File Transfer to Pico | 2 |
| Serial Monitor | 1 |
| Version Control Basics | 1 |
| Code Upload Process | 1 |
| Config File Pattern | 7 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)

---

!!! mascot-welcome "Meet Your Pico's Pins and Files"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This chapter turns the Pico from a mystery board into a tool you control: which pin is which, where your files live, and how a program starts by itself. Master it and your clock can run without a computer. Let's make time tick!

## Getting to Know the Platform

You can already write MicroPython. Now you will learn how the Pico itself works: its pins, its memory, its firmware, and its file system. These are the "how does the board behave?" questions that make projects reliable. The chapter has three parts: **pins** (GPIO, pull-up resistors), **memory and files** (flash, RAM, file system, boot files), and **workflow** (firmware, uploading, version control).

## GPIO Pins

A **GPIO pin** (general-purpose input/output pin) is a pin on the chip that your program can set as an input to read a signal or as an output to send one. GPIO pins are how the Pico touches the real world: they light LEDs, read buttons, and talk to displays.

The Pico has 40 physical pins, but only some are GPIO. The rest supply power and ground. There are two numbering systems, which confuses many beginners:

| Numbering | Example | Where you see it |
|-----------|---------|------------------|
| GP number | GP15 | Your code: `Pin(15)` |
| Physical pin | Pin 20 | The board's position, counted from a corner |

Your code always uses the **GP number**. GP15 is physical pin 20, but you write `Pin(15)`. Pinout diagrams show both.

!!! mascot-warning "GP Number vs Pin Number"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Counting physical pins and typing that number into `Pin()` is a very common mistake, and it lights the wrong pin or none at all. Always look up the **GP** label on the pinout diagram and use that number in code.

Useful facts about the Pico's GPIO:

- 26 GPIO pins are available: GP0 to GP22, and GP26 to GP28.
- GP26, GP27, and GP28 can also read analog voltages (ADC).
- Pins can serve special roles (I2C, SPI, UART, PWM), chosen by how you configure them.
- All signals are 3.3 V, as you learned in Chapter 2.

#### Diagram: Pico Pinout Explorer

<details markdown="1">
<summary>Pico Pinout Explorer</summary>
Type: interactive infographic
**sim-id:** pico-pinout-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *identify* GP numbers, physical pin numbers, and special functions on the Pico (Bloom: Remembering).

**Visual elements:** A top-down Pico drawing with all 40 pins labeled by physical number. Color coding: GPIO (blue), power (red), ground (black), ADC (green).

**Interactions:**

- Hover a pin to show its GP number, physical number, and possible functions (I2C0 SDA, SPI0 SCK, PWM slice, and so on).
- Click a pin to see the MicroPython line that configures it.
- A filter menu highlights all pins for I2C, SPI, UART, or ADC.
- A quiz mode names a GP number and asks the student to click the pin.

**Responsive design:** Board scales to canvas width; labels reflow on narrow screens.

Implementation: p5.js with a pin data array.
</details>

## Pin Configuration

**Pin configuration** means telling MicroPython how a pin should behave before you use it. You do this when you create a `Pin` object, and the two most important choices are direction and pull:

```python
from machine import Pin

led = Pin(15, Pin.OUT)                    # output: sends a signal
button = Pin(14, Pin.IN, Pin.PULL_UP)     # input with a pull-up resistor
```

Once configured, outputs are controlled with `led.value(1)`, `led.on()`, `led.off()`, or `led.toggle()`, and inputs are read with `button.value()`, which returns 0 or 1.

| Setting | Meaning |
|---------|---------|
| `Pin.OUT` | The Pico drives the pin high or low |
| `Pin.IN` | The Pico reads the voltage on the pin |
| `Pin.PULL_UP` | Adds a weak connection to 3.3 V |
| `Pin.PULL_DOWN` | Adds a weak connection to ground |

Configure each pin once, near the top of the program, so the choices are easy to find later.

## Pull-Up Resistors

An input pin that is connected to nothing is said to be **floating**. Its voltage drifts randomly with static electricity and noise, so `value()` flips between 0 and 1 unpredictably. A **pull-up resistor** solves this by connecting the pin to 3.3 V through a large resistor, so the pin reads 1 by default.

A push button wired between the pin and ground then works cleanly:

- Button not pressed: the pull-up holds the pin at 3.3 V, so `value()` is **1**.
- Button pressed: the button connects the pin to ground, overpowering the weak pull-up, so `value()` is **0**.

Notice the result feels backward: pressed reads 0. This is called **active low**, and it is the standard way to wire buttons.

!!! mascot-thinking "Floating Is Not Zero"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A disconnected input does not read 0; it reads whatever noise is nearby. Every digital input needs a defined resting level, and the pull-up is what supplies it.

### Internal Pull-Up

You do not need an external resistor, because the RP2040 has a pull-up built into every GPIO pin. The **internal pull-up** is a resistor of roughly 50 to 80 kΩ that you switch on in code with `Pin.PULL_UP`. That saves parts and wiring, and it is why buttons in this book need only two connections: one to the GPIO pin and one to ground.

```python
NAME = "05-button-read.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

button = Pin(14, Pin.IN, Pin.PULL_UP)   # button between GP14 and GND

while True:
    if button.value() == 0:      # 0 means pressed (active low)
        print("pressed")
    sleep(0.1)
```

The program reads the button ten times a second and prints a message while it is held. Chapter 7 shows how to handle bouncing and use interrupts.

#### Diagram: Pull-Up Button Lab

<details markdown="1">
<summary>Pull-Up Button Lab</summary>
Type: MicroSim
**sim-id:** pull-up-button-lab<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* how a pull-up resistor sets an input's resting voltage (Bloom: Analyzing).

**Visual elements:** A schematic of GP14, a resistor to 3.3 V, and a button to ground. A voltage bar shows the pin voltage; a readout shows `value()`.

**Controls:** A "Press button" toggle; a "Pull-up: on/off" toggle. With the pull-up off and the button open, the voltage bar jitters randomly and the readout flickers to show a floating input.

**Responsive design:** Schematic scales to canvas width.

Implementation: p5.js with randomized noise when floating.
</details>

## Pico W

The **Pico W** is the version of the Pico with a wireless chip added. It has the same RP2040 and the same 40-pin layout, and it supports 2.4 GHz WiFi and Bluetooth through a separate wireless chip. WiFi is what allows a clock to set itself from the internet in Chapter 14.

Two differences to remember:

- Its on-board LED is controlled through the wireless chip, so you address it as `Pin("LED")`. On the regular Pico it is `Pin(25)`.
- It needs its own MicroPython firmware. A regular Pico firmware file will not give you WiFi.

## Flash Memory

**Flash memory** is storage that keeps its contents when the power is off. The Pico has 2 MB of flash on the board. It holds two things: the MicroPython **firmware** (the interpreter itself, roughly the first 1 MB) and the **file system** where your programs live (the remainder).

Flash is different from **RAM**, the Pico's fast working memory. RAM is 264 KB and is wiped whenever power is lost.

| Property | Flash | RAM |
|----------|-------|-----|
| Size on Pico | 2 MB | 264 KB |
| Keeps data without power | Yes | No |
| Speed | Slower | Fast |
| Holds | Firmware, your files | Variables while running |
| Wear | About 100,000 erase cycles per block | None |

The wear limit means you should not write to files thousands of times per second. Saving a setting once a minute is fine, but writing every loop pass is not.

!!! mascot-thinking "Storage vs Working Space"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Flash is like a bookshelf: it holds things when the lights are off. RAM is like your desk: fast, but cleared at the end of the day. Your variables live on the desk, and your program files live on the shelf.

## File System on Pico

The **file system** is the organized set of files and folders stored in the Pico's flash. It works like a small hard drive: you can create, read, and delete files. Your programs, drivers, and configuration files live here.

Use the `os` module to look around from the REPL:

```python
import os
print(os.listdir())        # files in the current folder
st = os.statvfs("/")       # file-system statistics
free_kb = st[0] * st[3] // 1024
print(free_kb, "KB free")
```

A typical layout looks like this:

| Path | Contents |
|------|----------|
| `/main.py` | Program that runs at startup |
| `/config.py` | Pin numbers and settings |
| `/lib/` | Driver libraries such as `ssd1306.py` |

Thonny's **Files** view (View > Files) shows this tree next to the one on your computer.

## Boot and Main Files

When the Pico powers on, MicroPython runs two special files automatically, in this order:

1. `boot.py` runs first. It is for low-level setup and is usually left empty.
2. `main.py` runs next. This is your clock program.

To make a clock start by itself without a computer, save your program on the Pico as `main.py`. A program with any other name runs only when you press Run in Thonny.

!!! mascot-warning "Locked Out by main.py"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A `main.py` with an endless loop that never sleeps can make the Pico hard to reach from Thonny, because the program is always running. Press the Stop button or Ctrl+C repeatedly to interrupt it, then fix or delete the file. If that fails, hold BOOTSEL while plugging in and reinstall the firmware to reset the file system.

#### Diagram: Pico Startup Sequence

<details markdown="1">
<summary>Pico Startup Sequence</summary>
Type: workflow diagram
**sim-id:** pico-startup-sequence<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *understand* what happens from power-on to a running clock (Bloom: Understanding).

**Nodes:** Power on, MicroPython firmware starts, run `boot.py`, run `main.py`, main loop runs, USB connected? (Thonny can interrupt), REPL prompt.

**Interactions:** Every node has a Mermaid `click` directive that opens an infobox explaining that step. A toggle switches between "Has main.py" and "No main.py," and the path that changes is highlighted.

**Responsive design:** The diagram scales to container width.

Implementation: Mermaid flowchart with click callbacks.
</details>

## Config File Pattern

The **config file pattern** puts every hardware setting, such as pin numbers and screen size, in one file named `config.py` that other programs import. Without it, pin numbers are scattered through every program, and rewiring means editing dozens of lines.

```python
# config.py: hardware settings for this kit
BUTTON_PIN = 14
LED_PIN = 15
WIDTH = 240
HEIGHT = 240
```

```python
# main.py
import config
from machine import Pin

button = Pin(config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)
```

The benefit is one change in one place: if you move the button to GP16, you update `config.py` and every program follows. This is the modularity idea from Chapter 4 applied to hardware, and the [Hardware Config Files lesson](../../lessons/00-hardware-config.md) shows a full example with an SPI display.

!!! mascot-tip "Comment Your Wiring"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Add a comment next to every pin number in `config.py` naming the wire color and the part it goes to. When something stops working next month, that file is a wiring diagram.

## Firmware Versions

**Firmware** is the low-level software stored in flash that runs the chip. For the Pico, the MicroPython interpreter is the firmware. Firmware has **versions**, and newer versions add features and fix bugs. Some features in this book, such as f-strings, need a reasonably recent one.

Check your version in the REPL:

```python
import os
print(os.uname())
```

The output includes a line like `version='v1.2x...'` and the board name, which tells you whether it is a Pico or a Pico W. Download the right firmware from micropython.org, choosing the file for your exact board.

### Firmware Flashing

**Firmware flashing** is copying new firmware into the Pico's flash. The Pico makes it easy because it presents itself as a USB drive:

1. Hold the **BOOTSEL** button while plugging the Pico into USB.
2. A drive named `RPI-RP2` appears on your computer.
3. Drag the downloaded `.uf2` file onto that drive.
4. The Pico reboots by itself and runs the new firmware.

Thonny can also do this for you through its *Install MicroPython* option. Flashing does not erase your Pico's hardware; it can always be repeated.

## Interpreter Selection

Thonny can run your code in more than one place. The **interpreter** setting chooses which one. For this course it must be *MicroPython (Raspberry Pi Pico)*. If it is set to *Local Python 3*, your code runs on the computer, and a line like `from machine import Pin` fails with a `ModuleNotFoundError` because the `machine` module does not exist there.

Look at the bottom-right corner of the Thonny window to see the current interpreter, and check it first whenever a Pico program mysteriously fails.

## File Transfer to Pico

Files you write must be copied to the Pico's flash before the Pico can use them without the computer. There are two easy ways in Thonny:

- **Save as:** choose *File > Save as*, then pick *MicroPython device* and name the file.
- **Files view:** right-click a file in the computer pane and choose *Upload to /*.

The command-line tool `mpremote` does the same from a terminal, for example `mpremote cp main.py :`. Whichever method you use, confirm with `os.listdir()` that the file arrived.

## Code Upload Process

The **code upload process** is the full routine for getting a working program onto the Pico for good. It has five steps:

1. Write and test the program with the **Run** button.
2. Save it to the Pico as `main.py` (or as the library name).
3. Copy any needed libraries and `config.py` to the Pico.
4. Press Ctrl+D or unplug and replug the Pico to restart it.
5. Confirm the program starts by itself.

The program name and version banner you print at the top of every lab is your safety net. If an old copy is on the Pico, the banner shows the old version number immediately.

## Serial Monitor

A **serial monitor** is a window that shows text your program prints and lets you type text back. In Thonny, the **Shell** is the serial monitor: everything from `print()` appears there. Other tools, such as `mpremote` and terminal programs, show the same stream.

Thonny also has a **Plotter** (View > Plotter) that draws a live graph of numbers you print, which is a quick way to watch a sensor value change over time. Print one number per line, or several separated by commas.

## Version Control Basics

**Version control** is a system that records each saved version of your project so you can go back, compare, or see who changed what. The most popular tool is **Git**. It lets you experiment without fear because you can always return to a working copy.

The core Git commands are short:

```bash
git init                       # start tracking a folder
git add main.py                # choose files to save
git commit -m "Add wrap-around minutes"   # save a snapshot with a message
git log                        # see the history
```

Never commit passwords. The WiFi `secrets.py` file from Chapter 14 belongs in a `.gitignore` list so it stays off the internet. Even without Git, keep a `VERSION` variable in each program and bump it when you change the code.

## Memory Management

**Memory management** is the job of using the Pico's small RAM wisely. With 264 KB, a program that builds giant lists or many long strings can run out, and MicroPython raises `MemoryError`. Ways to save RAM:

- Use short strings and reuse objects rather than creating new ones inside loops.
- Avoid building large lists when a simple counter will do.
- Import only the modules you need.

Check free memory at any time:

```python
import gc
print(gc.mem_free(), "bytes free")
```

### Garbage Collection

**Garbage collection** is the automatic process that finds objects your program no longer uses and frees their memory. MicroPython does it for you when memory runs low. You can also trigger it yourself with `gc.collect()`, which is a good idea before allocating something large, such as a display buffer.

## Dual Core Usage

The RP2040's second core can run a function in parallel with your main program, using the `_thread` module:

```python
import _thread
from time import sleep

def blink_worker():
    while True:
        print("core 1 tick")
        sleep(1)

_thread.start_new_thread(blink_worker, ())   # starts on the second core
```

The main program continues on core 0 at the same time. Use this feature carefully, since both cores share the same memory and the same hardware. Two cores writing to the same display at once will garble it. Almost every clock in this book needs only one core, so treat this as an advanced option.

## Putting It Together

| Task | Tool |
|------|------|
| Read a button | `Pin(n, Pin.IN, Pin.PULL_UP)` |
| Run automatically at power-on | Save as `main.py` |
| Keep pin numbers in one place | `config.py` |
| Check firmware | `os.uname()` |
| See free RAM | `gc.mem_free()` |
| Go back to a working version | Git commit history |

## Key Takeaways

- Use the **GP number** in code, not the physical pin number.
- A pull-up resistor gives inputs a defined resting level; buttons are active low.
- Flash holds firmware and files without power; RAM holds variables and is wiped at power-off.
- `boot.py` then `main.py` run at startup, and `main.py` makes a program start on its own.
- `config.py` keeps hardware settings in one place.
- Flash firmware by dragging a `.uf2` file onto the `RPI-RP2` drive while holding BOOTSEL.
- Git and a printed name and version banner keep track of your code.

!!! mascot-celebration "Platform Mastered"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now pick the right pin, wire a button with a pull-up, save a `main.py` that runs on its own, and keep your settings in `config.py`. Your Pico is ready to run real clock projects. Every second counts!

## Practice Questions

1. GP18 is physical pin 24. Which number goes inside `Pin()`, and why?
2. A button between GP10 and ground is configured with `Pin.PULL_UP`. What does `value()` return when it is pressed?
3. Explain in your own words why flash and RAM are both needed.
4. Your program works from Thonny's Run button but does nothing after you unplug and replug the Pico. What is the most likely cause?
5. Write a `config.py` with three constants for a clock kit and show how to use one of them in another file.
