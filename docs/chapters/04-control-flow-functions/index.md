---
title: Control Flow, Functions, and Modules
description: Decisions, loops, functions, modules, and classes for structuring MicroPython clock programs.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:30:47
version: 1.10
---

# Control Flow, Functions, and Modules

## Summary

Students learn to make decisions with if/elif/else, repeat work with loops, and package code into functions, modules, and small classes. They also learn error handling. After this chapter they can organize a program into clear, reusable parts.

## Concepts Covered

This chapter covers the following 19 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Import Statements | 126 |
| Libraries | 80 |
| Modules | 45 |
| Conditionals | 119 |
| Machine Module | 1 |
| If Else Elif | 13 |
| For Loops | 2 |
| While Loops | 26 |
| Functions | 72 |
| Modular Arithmetic | 10 |
| Loop Control | 1 |
| Arguments and Returns | 17 |
| Error Handling | 3 |
| Code Modularity | 16 |
| Global Keyword | 1 |
| Classes and Objects | 2 |
| Lambda Functions | 1 |
| Try Except Blocks | 1 |
| Object Methods | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)

---

!!! mascot-welcome "Now Your Code Can Decide"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Until now your programs ran top to bottom and stopped. In this chapter they learn to make choices, repeat forever, and pack work into tidy pieces, which is exactly what a clock does. Let's make time tick!

## Structuring a Program

A clock never finishes: it checks the time, decides what to show, draws it, and repeats. That needs three things you have not used yet: **decisions** (conditionals), **repetition** (loops), and **reusable pieces** (functions and modules). This chapter covers all three, plus a first look at classes and error handling.

## Import Statements

An **import statement** loads code from a module so you can use it in your program. Most useful features, such as timing and hardware control, live in modules rather than in the core language.

There are three common forms:

```python
import time                  # use as time.sleep(1)
from time import sleep       # use as sleep(1)
from machine import Pin, I2C # import several names at once
import time as t             # give the module a short nickname
```

The first form keeps names organized (`time.sleep`), while the second saves typing. Put imports near the top of the file, but after the name and version banner, so the banner still prints if an import fails. If MicroPython cannot find the module you asked for, it raises `ImportError`, which usually means a misspelled name or a file that has not been copied to the Pico.

## Modules

A **module** is a single Python file (`.py`) containing functions, variables, or classes that other programs can import. The file name, without `.py`, becomes the module name. If you save the following on your Pico as `clockmath.py`:

```python
def to_12_hour(hour24):
    return (hour24 + 11) % 12 + 1
```

then any program can use it:

```python
import clockmath
print(clockmath.to_12_hour(15))    # 3
```

Modules let you split a large program across files and reuse the same code in many clocks. MicroPython looks for modules in the Pico's main folder and in a `/lib` folder. Avoid naming your file after a built-in module such as `time` or `machine`, because yours would be found first and break everything else.

## Libraries

A **library** is a collection of modules that provides a set of related features. Some are built into MicroPython and others you add yourself.

| Library or module | What it provides | Included? |
|-------------------|------------------|-----------|
| `time` | Time, delays, sleeping | Built in |
| `machine` | Pins, I2C, SPI, PWM, ADC | Built in |
| `framebuf` | Drawing to a memory buffer | Built in |
| `neopixel` | NeoPixel LED control | Built in |
| `ssd1306` | OLED display driver | Copy the file to the Pico |
| `tm1637` | Four-digit LED driver | Copy the file to the Pico |

To add a library that is not built in, copy its `.py` file to the Pico (Thonny's *Save as > MicroPython device*), often into a `lib` folder. A Pico W that is on WiFi can also fetch libraries with the `mip` installer. Later chapters use these driver libraries so you do not have to write display code from scratch.

### Machine Module

The **machine module** is MicroPython's gateway to the Pico's hardware. It contains the classes for pins, buses, and analog inputs, so you will import from it in almost every lab:

| Name | Controls |
|------|----------|
| `Pin` | Digital input and output pins |
| `I2C`, `SPI` | Communication buses |
| `PWM` | Pulse-width modulation for sound and dimming |
| `ADC` | Analog-to-digital converter |

It also has utility functions such as `machine.freq()`, which returns the processor speed (125,000,000 Hz by default), and `machine.reset()`, which restarts the Pico.

## Conditionals

A **conditional** is code that runs only when a condition is true. The condition is any expression that gives a boolean, such as `hour < 12`. The basic form is the `if` statement:

```python
hour = 15
if hour >= 12:
    print("Afternoon or evening")
```

The colon ends the `if` line, and the indented line under it is the block that runs when the condition is `True`. If the condition is `False`, Python skips the block entirely. Indentation is not decoration: it is how Python knows which lines belong to the `if`.

### If, Else, Elif

`else` supplies a block for when the condition is false, and `elif` (short for "else if") checks additional conditions in order. Python tests them from the top and runs only the first one that is true.

```python
hour = 15
if hour < 12:
    suffix = "AM"
else:
    suffix = "PM"
print(suffix)     # PM
```

Here is a chain with `elif`:

```python
if hour < 6:
    greeting = "Night"
elif hour < 12:
    greeting = "Morning"
elif hour < 18:
    greeting = "Afternoon"
else:
    greeting = "Evening"
```

**Worked example.** For `hour = 15`, the first test (`15 < 6`) fails, the second (`15 < 12`) fails, the third (`15 < 18`) is true, so `greeting` becomes `"Afternoon"` and the last `else` is skipped. Order matters: if you tested `hour < 18` first, every morning would also be called "Afternoon".

!!! mascot-warning "One Equals or Two?"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Writing `if hour = 12:` is a syntax error because a single `=` stores a value. Use `==` to compare. Also check the colon at the end of the `if` line and the indentation underneath; those are the other two usual suspects.

#### Diagram: Greeting Decision Path

<details markdown="1">
<summary>Greeting Decision Path</summary>
Type: MicroSim
**sim-id:** greeting-decision-path<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *trace* an if/elif/else chain to predict its result (Bloom: Applying).

**Visual elements:** A vertical flowchart with four diamond tests (`hour < 6`, `< 12`, `< 18`, else) and four result boxes. A marker travels down the chain.

**Controls:** A slider for `hour` (0 to 23) and a "Step" button. The path taken lights up green; skipped tests gray out. A toggle "Reorder tests" swaps the tests to show how order changes the answer.

**Responsive design:** The flowchart scales to canvas width.

Implementation: p5.js with a small array of test objects.
</details>

## For Loops

A **for loop** repeats a block once for each item in a sequence. It is the tool to use when you know how many times to repeat, or when you have a collection to walk through.

```python
for i in range(3):
    print("tick", i)         # tick 0, tick 1, tick 2

for day in ["Mon", "Tue", "Wed"]:
    print(day)
```

`range(3)` produces 0, 1, 2 (it stops *before* the number). You can give a start, stop, and step: `range(0, 60, 5)` gives 0, 5, 10, ... 55, which is the position of every five-minute mark on a clock face.

## While Loops

A **while loop** repeats a block for as long as a condition stays true. Use it when you do not know in advance how many repetitions you need, such as "keep going until a button is pressed."

```python
seconds = 0
while seconds < 5:
    print(seconds)
    seconds += 1
```

Every clock program has a **main loop**: `while True:` runs forever because `True` is never false. Inside it you read the time, update the display, and pause.

```python
NAME = "04-main-loop.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from time import sleep

count = 0
while True:
    print(count)
    count += 1
    sleep(1)       # wait one second between passes
```

!!! mascot-tip "Stopping a Runaway Loop"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    A `while True:` loop never ends by itself. Click Stop in Thonny (or press Ctrl+C in the Shell) to interrupt it, and always add a `sleep()` so the loop does not spin as fast as possible.

### Loop Control

Two statements change how a loop runs from inside:

- `break` exits the loop immediately.
- `continue` skips the rest of this pass and goes to the next one.

```python
for n in range(10):
    if n == 3:
        continue      # skip 3
    if n == 6:
        break         # stop at 6
    print(n)          # prints 0 1 2 4 5
```

## Modular Arithmetic

**Modular arithmetic** is math where numbers wrap around after reaching a limit, like the numbers on a clock face. In Python it uses the `%` operator: `x % n` is the remainder after dividing by `n`, and it is always between 0 and `n - 1`.

This is the pattern behind every counter in a clock. To add one second and wrap at 60:

\[ s_{next} = (s + 1) \bmod 60 \]

```python
seconds = 58
for _ in range(4):
    seconds = (seconds + 1) % 60
    print(seconds)        # 59, 0, 1, 2
```

Going backward works too: `(0 - 1) % 60` gives 59 in Python, which is what you want when a "down" button is pressed on minute 0. The same trick cycles through modes: `mode = (mode + 1) % 4` walks through mode 0, 1, 2, 3, then back to 0.

!!! mascot-tip "The Wrap-Around Trick"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Any time a value must go around like a dial (seconds, hours, menu choices), reach for `% limit` instead of writing an `if` to reset it. It is shorter and it also handles going backward.

#### Diagram: Wrap-Around Dial

<details markdown="1">
<summary>Wrap-Around Dial</summary>
Type: MicroSim
**sim-id:** wrap-around-dial<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* the modulo operator to predict where a counter lands after adding or subtracting (Bloom: Applying).

**Visual elements:** A circular dial with a modulus set by a selector (12, 24, or 60). A pointer sits on the current value, and the equation `(x + step) % n` is shown live.

**Controls:** "+1", "-1", and "+10" buttons, a modulus selector, and a "Predict" mode where the student types the resulting number before the pointer moves.

**Responsive design:** The dial scales to canvas width.

Implementation: p5.js with polar coordinates for tick placement.
</details>

## Functions

A **function** is a named, reusable block of code that performs one job. You define it once with `def` and then **call** it by name whenever you need it. Functions are the most powerful tool for keeping programs organized, and they are the abstraction skill from Chapter 1 made real.

```python
def show_time(hour, minute):
    print(f"{hour:02d}:{minute:02d}")

show_time(9, 5)     # 09:05
show_time(14, 30)   # 14:30
```

The line with `def` names the function and lists its **parameters** (`hour` and `minute`), the values it expects. The indented block is its **body**. Python must see the `def` before the first call, so put definitions near the top.

Functions have three benefits:

- **Reuse:** write once, use many times.
- **Clarity:** `show_time(h, m)` says what happens without showing how.
- **Testing:** you can check a small function alone.

Variables created inside a function are **local**: they exist only while it runs and cannot clash with names elsewhere.

!!! mascot-thinking "A Function Is an Abstraction"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Remember hiding details behind a simple name? That is exactly what `def` does. Once `show_time()` works, you can stop thinking about *how* and only think about *when* to call it.

### Arguments and Returns

An **argument** is the actual value you pass into a function when you call it, and the **return value** is what the function sends back. The keyword `return` ends the function and hands back a result.

```python
def to_12_hour(hour24):
    return (hour24 + 11) % 12 + 1

h = to_12_hour(15)      # h is now 3
```

A function with no `return` gives back `None`. You can also give parameters **default values**, and a function can return several values as a tuple:

```python
def split_seconds(total, per_hour=3600):
    hours = total // per_hour
    left = total % per_hour
    return hours, left // 60, left % 60

h, m, s = split_seconds(45296)     # 12, 34, 56
```

### Global Keyword

Assigning to a variable inside a function normally makes a *new* local variable. The **global keyword** tells Python to use the variable defined outside the function instead:

```python
count = 0

def add_tick():
    global count
    count += 1
```

Without `global count`, the line `count += 1` would raise an error. Use `global` sparingly. Returning a value is usually cleaner, but interrupt handlers and callbacks in Chapter 7 often need it because they cannot return anything to your main code.

### Lambda Functions

A **lambda function** is a tiny unnamed function written on one line. It is handy when you need a short function just once:

```python
double = lambda x: x * 2
print(double(21))          # 42
to_12 = lambda h: (h + 11) % 12 + 1
```

A lambda can contain only one expression and no statements. If it gets complicated, write a normal `def` instead.

## Code Modularity

**Code modularity** means organizing a program into small, independent pieces that each do one thing, so you can understand, test, and reuse each piece separately. It applies the decomposition skill from Chapter 1 to real files.

A well-modularized clock might look like this:

| File | Job |
|------|-----|
| `config.py` | Pin numbers and hardware settings |
| `timeutil.py` | Time math such as `to_12_hour()` |
| `display.py` | Drawing functions |
| `main.py` | The main loop that ties them together |

Two habits make modular code work. First, give each function one job and a name that says it. Second, never copy and paste code: if you need the same lines twice, make them a function. Keeping pin numbers in `config.py` also means switching to a different board changes one file, not fifty lines.

#### Diagram: Function Machine

<details markdown="1">
<summary>Function Machine</summary>
Type: MicroSim
**sim-id:** function-machine<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *understand* functions as input-output machines and *create* their own simple function (Bloom: Understanding, Creating).

**Visual elements:** A machine box with input chutes on the left labeled by parameter names and an output chute on the right. Number tokens drop into the chutes and a result token comes out.

**Controls:** A dropdown of functions (`to_12_hour`, `split_seconds`, `add`, and a "Write your own" text field with a one-line lambda). Input boxes for arguments and a "Run" button that animates the token flow and shows the return value.

**Responsive design:** Machine scales to container width; controls stack below 600 px.

Implementation: p5.js with `eval` restricted to a whitelisted set of expressions.
</details>

## Classes and Objects

A **class** is a blueprint that bundles data and the functions that work with that data. An **object** (or instance) is one thing built from that blueprint. You have already used classes: `Pin` is a class, and `led = Pin(15, Pin.OUT)` builds one `Pin` object with its own pin number.

Here is a small class for a wrap-around counter. The special method `__init__` runs when the object is created, and `self` refers to the object itself.

```python
class Counter:
    def __init__(self, limit):
        self.limit = limit
        self.value = 0

    def tick(self):
        self.value = (self.value + 1) % self.limit
        return self.value

seconds = Counter(60)
minutes = Counter(60)
seconds.tick()      # 1
```

Each object keeps its own `value`, so `seconds` and `minutes` do not interfere.

!!! mascot-encourage "Classes Look Scarier Than They Are"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    The words `self` and `__init__` puzzle nearly everyone at first. You already use objects every time you write `led.toggle()`, so you understand the idea; you'll write only a few classes yourself, and each one follows this same pattern.

### Object Methods

A **method** is a function that belongs to an object. You call it with a dot after the object's name. `led.toggle()` is a method on the `Pin` object, and `"clock".upper()` is a method on a string. In the `Counter` class above, `tick()` is a method. Methods can read and change the object's own data, which is why `seconds.tick()` remembers where it left off.

## Error Handling

**Error handling** means writing code that survives problems instead of crashing. When something goes wrong at run time, Python raises an **exception** and, if nothing deals with it, the program stops and prints a **traceback** showing where it happened.

Common exceptions you will meet:

| Exception | Typical cause |
|-----------|---------------|
| `ValueError` | `int("abc")`, a value of the right type but wrong content |
| `TypeError` | Adding a string to a number |
| `ZeroDivisionError` | Dividing by zero |
| `OSError` | Hardware or network trouble (device not found, WiFi failed) |

### Try Except Blocks

A **try/except block** runs code that might fail and provides a fallback if it does:

```python
try:
    value = int("12x")
except ValueError:
    value = 0
    print("Not a number, using 0")
```

This matters for hardware. If a sensor is unplugged, talking to it raises `OSError`, and a `try/except` can print a helpful message instead of crashing. Name the exception you expect; a bare `except:` hides real bugs.

## Putting It Together

This short program combines a function, a conditional, a loop, and modular arithmetic to run a simulated clock in the Shell:

```python
NAME = "04-sim-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from time import sleep

def to_12_hour(hour24):
    return (hour24 + 11) % 12 + 1

hour, minute = 23, 58
while True:
    suffix = "AM" if hour < 12 else "PM"
    print(f"{to_12_hour(hour)}:{minute:02d} {suffix}")
    minute = (minute + 1) % 60
    if minute == 0:
        hour = (hour + 1) % 24
    sleep(1)
```

Watch what happens after 11:59 PM: the minute wraps to 0, the hour wraps to 0, and the display flips to `12:00 AM`.

## Key Takeaways

- `import` loads modules; libraries are collections of modules, and `machine` controls the hardware.
- `if`/`elif`/`else` make decisions; `for` and `while` repeat; `break` and `continue` adjust loops.
- The `%` operator makes counters wrap around like a clock.
- Functions package work behind a name; `return` sends back a value; `global` reaches an outside variable.
- Classes bundle data and methods; `try`/`except` keeps programs alive when something fails.
- Modular code splits a project into files that each do one job.

!!! mascot-celebration "Program Structure Unlocked"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now write decisions, loops, and functions, and you built a simulated clock that correctly wraps from `11:59 PM` to `12:00 AM`. That is the shape of every clock program in this book. Every second counts!

## Practice Questions

1. Write an `if/elif/else` chain that prints "Weekday" for weekday numbers 0 to 4 and "Weekend" for 5 and 6.
2. Use a `for` loop and `range` to print every 15th minute mark: 0, 15, 30, 45.
3. Explain why `(0 - 1) % 60` is useful for a "minute down" button.
4. Write a function `pad(n)` that returns a two-digit string, so `pad(7)` returns `"07"`.
5. What is the difference between a function and a method? Give one example of each from code you have seen.
