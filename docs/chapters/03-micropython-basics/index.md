---
title: MicroPython Basics: Variables and Data Types
description: MicroPython basics in Thonny: variables, numbers, strings, lists, tuples, dictionaries, f-strings, and print debugging.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:29:37
version: 1.10
---

# MicroPython Basics: Variables and Data Types

## Summary

Students set up Thonny, connect over USB, and explore the REPL. They then work with MicroPython's core data types and operators. After this chapter they can write short programs that store, combine, and print values.

## Concepts Covered

This chapter covers the following 20 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Python Syntax | 1329 |
| MicroPython | 160 |
| Variables | 1041 |
| Data Types | 824 |
| Assignment Operators | 1 |
| USB Connection | 33 |
| Micropython Differences | 1 |
| Integers | 275 |
| Floats | 164 |
| Strings | 56 |
| Booleans | 120 |
| Lists | 125 |
| Thonny IDE | 27 |
| Tuples | 80 |
| Dictionaries | 1 |
| Arithmetic Operations | 162 |
| REPL | 21 |
| F-String Formatting | 11 |
| String Concatenation | 1 |
| Print Debugging | 10 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)

---

!!! mascot-welcome "Your First Real Code"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    In this chapter you'll type your first lines of MicroPython and watch the Pico answer back. By the end you'll be storing the time, doing clock math, and printing a neat `12:34:56`. Let's make time tick!

## From Thinking to Typing

In Chapter 1 you wrote an algorithm in plain English. Now you will teach the Pico to follow it. This chapter sets up your tools (a cable, an editor, and a live prompt), then covers the building blocks every clock program uses: variables, numbers, text, and collections of values. Chapter 4 adds decisions and loops.

## Python Syntax

**Syntax** is the set of grammar rules a programming language requires. A computer cannot guess what you meant, so if you break a rule it stops with an error message. **Python syntax** is famously readable, which is why it is a good first language.

Here are the rules you need on day one:

- **Case matters.** `Hour` and `hour` are different names.
- **Indentation matters.** Lines that belong together are indented by the same number of spaces (use four). Python uses indentation instead of curly braces.
- **A colon starts an indented block.** You will see this in Chapter 4 with `if`, `for`, and `def`.
- **Comments start with `#`.** Python ignores everything after it on that line.
- **One statement per line**, usually.

```python
# This is a comment: Python ignores it
print("Hello, clock!")   # print() shows text in the Shell
```

When you break a rule Python raises a **syntax error** and tells you the line number. For example, `print("Hello)` with a missing quote produces `SyntaxError: invalid syntax`. The line number in the message is where Python noticed the problem, and the real mistake is usually on that line or the one just before it.

!!! mascot-encourage "Errors Are Clues"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Everybody sees error messages, including experts who have coded for decades. Read the last line first, then look at the line number it names. A red message is a clue, not a failure.

## MicroPython

**MicroPython** is a version of Python 3 rewritten to fit on small microcontrollers. It was created by Damien George and first released in 2014. The full Python interpreter would not fit on a chip with 264 KB of RAM, so MicroPython includes the core language and a trimmed set of libraries, plus extra modules for controlling hardware.

MicroPython runs **directly on the Pico** with no operating system. When you plug the Pico in, the interpreter starts, waits for your commands, and runs your program the moment you press Run. This means you can experiment live: type a line, see the result, change it, and try again. That fast feedback is why we use MicroPython for teaching.

### MicroPython Differences

Most Python you learn here also works on a laptop, but MicroPython is a *subset* with a few differences that matter:

| Topic | Regular Python (laptop) | MicroPython (Pico) |
|-------|-------------------------|--------------------|
| Standard library | Very large | Small, trimmed |
| Hardware modules | None built in | `machine`, `neopixel`, `rp2` |
| Date and time | `datetime` module | `time` module and time tuples |
| Memory | Gigabytes | About 264 KB of RAM |
| Float precision | 64-bit | Roughly 7 significant digits |

If a program from the internet fails with `ImportError`, the first thing to check is whether that module exists in MicroPython. The differences are small, but they explain many surprises.

## USB Connection

The **USB connection** is the cable that powers the Pico and carries your code and text between it and your computer. The Pico appears to your computer as a **serial port**, a simple two-way text channel. Thonny talks to the Pico over that port.

Not every USB cable can do this. Many cheap cables are **charge-only** and contain no data wires.

!!! mascot-warning "The Charge-Only Cable Trap"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If Thonny cannot find your Pico, the most common cause is a USB cable that only carries power. Try a different cable, ideally the one that came with a phone or a data cable you know transfers files, and plug it in directly to the computer rather than through a hub.

On macOS the port looks like `/dev/tty.usbmodem...`, on Windows it is `COM3` or similar, and on Linux it is `/dev/ttyACM0`. The [Desktop Setup](../../setup/01-desktop.md) and [Pico Wireless](../../setup/06-pico-w-setup.md) pages walk through drivers and permissions for each system.

## Thonny IDE

An **IDE** (integrated development environment) is one program that combines a code editor, a way to run code, and tools for finding mistakes. **Thonny** is a free, beginner-friendly IDE for Python that has built-in support for MicroPython boards. Download it from thonny.org.

To connect Thonny to your Pico:

1. Plug in the Pico with a data cable.
2. In Thonny, choose the interpreter in the bottom-right corner (or **Tools > Options > Interpreter**) and pick *MicroPython (Raspberry Pi Pico)*.
3. If the Pico has no MicroPython yet, hold the **BOOTSEL** button while plugging in and use Thonny's *Install MicroPython* option.
4. When the bottom panel shows a `>>>` prompt, you are connected.

The window has three areas you will use constantly:

| Area | Purpose |
|------|---------|
| Editor (top) | Where you write and edit your program |
| Shell (bottom) | Where output appears and where you can type commands |
| Run and Stop buttons | Start or interrupt your program |

Thonny saves files in two places: your **computer** or the **MicroPython device** (the Pico). A program stored on the Pico's own storage is the one that will start when the Pico is powered without a computer. You will use this in a later chapter.

#### Diagram: Thonny Window Tour

<details markdown="1">
<summary>Thonny Window Tour</summary>
Type: interactive infographic
**sim-id:** thonny-window-tour<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *identify* the parts of the Thonny window and *explain* what each is for (Bloom: Remembering, Understanding).

**Visual elements:** A screenshot-style mockup of Thonny with numbered hotspots: interpreter selector, editor, Run button, Stop button, Shell, and file location tabs ("This computer" vs "MicroPython device").

**Interactions:** Hovering a hotspot shows its name; clicking shows a two-sentence description and a "Try this" step. A "Quiz me" mode asks "Where would you type a quick test line?" and the student clicks the right region.

**Responsive design:** Image scales to container; hotspot positions are stored as percentages.

Implementation: p5.js with normalized hotspot rectangles.
</details>

## REPL

The **REPL** (Read-Eval-Print Loop) is an interactive prompt where you type one line of code, MicroPython runs it immediately, and prints the result. The name describes the loop: it **reads** what you typed, **evaluates** it, **prints** the answer, and **loops** back for more. In Thonny, the REPL is the Shell panel and its prompt is `>>>`.

Try these lines one at a time:

```python
>>> 2 + 3
5
>>> hour = 15
>>> hour * 60
900
>>> print("time to build")
time to build
```

Notice that typing an expression like `2 + 3` shows its value automatically, while `print()` shows exactly what you give it. Keyboard shortcuts you will use:

| Keys | Effect |
|------|--------|
| Ctrl+C | Stop a running program |
| Ctrl+D | Soft reset (restart MicroPython) |
| Up arrow | Recall the previous line |

!!! mascot-tip "REPL as a Scratchpad"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Not sure how a command behaves? Test it in the REPL before putting it in your program. It takes five seconds and saves you from debugging a whole program later.

## Variables

A **variable** is a name that refers to a value stored in the computer's memory. Think of it as a label stuck on a box: the label is the name, and the box holds the value. You create a variable by giving it a value with the equals sign:

```python
hour = 15
minute = 42
label = "Clock"
```

After this, typing `hour` gives you 15. You can change the value at any time, and the label moves to a new box:

```python
hour = 16        # the label 'hour' now points at 16
```

Good variable names are short and describe the value. Follow these rules:

- Use letters, digits, and underscores, and do not start with a digit.
- Use **snake_case** (lowercase with underscores), like `seconds_left`.
- Do not use Python's reserved words such as `if`, `for`, or `while`.
- By convention, write values that never change in CAPITAL LETTERS, like `NAME` and `VERSION`.

!!! mascot-thinking "Labels, Not Boxes"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A variable is a *name* pointing at a value. That is why you can write `x = y` and later change `y` without disturbing `x` for simple values. Thinking of names as sticky labels will save you from confusing bugs in Chapter 4.

**Worked example.** Store a time and reuse it:

```python
NAME = "03-variables.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

hour = 9
minute = 5
print(hour)
print(minute)
```

The first three lines are the program banner every lab in this book prints. It shows the file name and version, so you always know which copy of the program is running on your Pico.

### Assignment Operators

An **assignment operator** stores a value in a variable. The basic one is `=`. Python also has shortcuts that update a variable using its current value:

| Operator | Meaning | Same as |
|----------|---------|---------|
| `x = 5` | Store 5 in x | |
| `x += 1` | Add 1 to x | `x = x + 1` |
| `x -= 1` | Subtract 1 | `x = x - 1` |
| `x *= 2` | Multiply | `x = x * 2` |
| `x //= 2` | Whole-number divide | `x = x // 2` |
| `x %= 60` | Keep the remainder | `x = x % 60` |

Note that `=` means "store," not "is equal to." The `+=` shortcut is how a clock program adds one to a seconds counter, as in `seconds += 1`.

#### Diagram: Variable Box Visualizer

<details markdown="1">
<summary>Variable Box Visualizer</summary>
Type: MicroSim
**sim-id:** variable-box-visualizer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *predict* the value of variables after a sequence of assignments (Bloom: Understanding, Applying).

**Visual elements:** A code panel of 3 to 6 lines on the left and labeled boxes on the right. As the student steps through, the labels move to new values and a changed box flashes.

**Controls:** "Step" and "Reset" buttons; a preset menu (basic assignments, `+=` counter, swap two values). "Predict first" mode asks the student to type the value of `x` before each step is revealed.

**Responsive design:** The two panels stack vertically below 600 px.

Implementation: p5.js with a small interpreter for assignment lines.
</details>

## Data Types

A **data type** describes what kind of value something is and what you can do with it. You can add two numbers, but adding a number to a word makes no sense. Python tracks each value's type so it knows which operations are allowed. Ask for it with `type()`:

```python
>>> type(15)
<class 'int'>
>>> type(3.14)
<class 'float'>
>>> type("hi")
<class 'str'>
>>> type(True)
<class 'bool'>
```

The types in this chapter fall into two groups:

| Group | Types | Holds |
|-------|-------|-------|
| Single values | `int`, `float`, `str`, `bool` | One number, text, or yes/no |
| Collections | `list`, `tuple`, `dict` | Several values together |

Python decides the type automatically from the value you write. This is called **dynamic typing**. It makes code short, but it also means a mismatched type produces an error at run time, such as `TypeError`.

#### Diagram: Data Type Sorter

<details markdown="1">
<summary>Data Type Sorter</summary>
Type: MicroSim
**sim-id:** data-type-sorter<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *classify* values by data type (Bloom: Understanding).

**Visual elements:** Six bins labeled int, float, str, bool, list, tuple. A stack of value cards such as `42`, `3.0`, `"12:00"`, `True`, `[1, 2, 3]`, `(2026, 9, 28)`.

**Interactions:** Drag each card to a bin. Correct drops turn green; wrong drops bounce back with a hint ("Look for a decimal point"). Score and streak are shown, and tricky cards (`"42"` in quotes, `3.0`) are included on purpose.

**Responsive design:** Bins wrap into two rows on narrow screens.

Implementation: p5.js drag-and-drop with a card array.
</details>

## Integers

An **integer** (`int`) is a whole number with no decimal point, like 0, 42, or -7. Integers are the workhorse of clock programs because time is counted in whole units: hours, minutes, seconds, pixels, and pin numbers.

Integer arithmetic has two operators that beginners often skip but clocks depend on:

- `//` is **floor division**: divide and throw away the remainder.
- `%` is the **modulo** operator: give only the remainder.

Here is the seconds-to-clock algorithm from Chapter 1 as real code. The comments explain each line before you run it:

```python
NAME = "03-seconds-to-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

total = 45296              # seconds since midnight
hours = total // 3600      # whole hours
left = total % 3600        # seconds left after removing hours
minutes = left // 60       # whole minutes
seconds = left % 60        # seconds left over
print(hours, minutes, seconds)
```

The output is `12 34 56`, matching the hand calculation in Chapter 1. MicroPython integers can also be written in other bases: `0b1010` is binary (10) and `0xFF` is hexadecimal (255). These show up when you talk to hardware.

## Floats

A **float** (floating-point number) is a number with a decimal point, like 3.14 or 0.5. Use floats for measurements that are not whole, such as temperature (21.5 °C) or an angle.

Floats store approximate values. On the Pico, a float carries roughly 7 significant digits, so very small rounding errors are normal. The practical rule is: **never test two floats for exact equality**. Instead check whether they are close.

The `/` operator always returns a float, even when the answer is whole:

```python
>>> 6 / 2
3.0
>>> 7 / 2
3.5
>>> int(3.9)      # convert to int by dropping the decimal part
3
>>> round(3.9)    # round to the nearest whole number
4
```

!!! mascot-warning "Float or Int?"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A hidden float can break code that needs a whole number, such as a pixel position or a list index, because `/` returns `3.0`, not `3`. Use `//` for whole-number division, or convert with `int()` or `round()`.

## Arithmetic Operations

An **arithmetic operation** is a calculation on numbers. MicroPython has seven operators to know:

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `+` | Add | `7 + 2` | 9 |
| `-` | Subtract | `7 - 2` | 5 |
| `*` | Multiply | `7 * 2` | 14 |
| `/` | Divide (float) | `7 / 2` | 3.5 |
| `//` | Floor divide | `7 // 2` | 3 |
| `%` | Remainder (modulo) | `7 % 2` | 1 |
| `**` | Power | `7 ** 2` | 49 |

Python follows the usual order of operations: parentheses first, then `**`, then `* / // %`, then `+ -`. Use parentheses whenever you want to be sure.

**Worked example: converting to a 12-hour clock.** A 24-hour value from 0 to 23 must become 1 to 12. The plain remainder `hour % 12` gives 0 for both midnight and noon, but a clock should show 12. A neat fix is:

\[ h_{12} = ((h_{24} + 11) \bmod 12) + 1 \]

```python
hour24 = 15
hour12 = (hour24 + 11) % 12 + 1
print(hour12)     # 3
```

Check the edge cases: hour 0 gives \( (0+11) \bmod 12 + 1 = 12 \), hour 12 gives \( (23 \bmod 12) + 1 = 12 \), and hour 13 gives \( (24 \bmod 12) + 1 = 1 \). Testing the edges is a habit worth keeping.

## Booleans

A **boolean** (`bool`) is a value that is either `True` or `False`. Booleans answer yes/no questions, and they are the result of every comparison:

| Operator | Meaning | Example (`x = 5`) |
|----------|---------|-------------------|
| `==` | Equal to | `x == 5` is `True` |
| `!=` | Not equal | `x != 5` is `False` |
| `<`, `>` | Less, greater | `x > 3` is `True` |
| `<=`, `>=` | Less or equal, greater or equal | `x <= 4` is `False` |

Booleans combine with `and`, `or`, and `not`. For example, `hour >= 9 and hour < 17` is `True` during work hours. Hardware also speaks in booleans: a pin's `value()` is 1 when the pin is high and 0 when low, which acts like `True` and `False`. Next chapter you will use booleans to make decisions.

Watch out for one classic slip: `=` stores a value, while `==` asks a question. Writing `x = 5` when you meant `x == 5` changes your variable instead of testing it.

## Strings

A **string** (`str`) is a sequence of characters, used for any text. Write strings inside single or double quotes: `"12:34"` and `'12:34'` are the same. Strings are **immutable**, meaning you cannot change one in place; every operation makes a new string.

Useful string tools:

```python
>>> msg = "clock"
>>> len(msg)            # number of characters
5
>>> msg[0]              # first character (indexing starts at 0)
'c'
>>> msg[-1]             # last character
'k'
>>> msg[1:3]            # slice: characters 1 up to (not including) 3
'lo'
>>> msg.upper()
'CLOCK'
```

Displays need strings. A clock reading like `9:05` has to be text before it can be drawn, so you will convert numbers to strings constantly.

### String Concatenation

**String concatenation** means joining strings end to end with `+`:

```python
>>> "12" + ":" + "34"
'12:34'
```

You can only join strings with strings. `"Hour: " + 9` raises a `TypeError` because 9 is an integer. Convert it first with `str()`:

```python
>>> "Hour: " + str(9)
'Hour: 9'
```

Concatenation works, but it becomes clumsy with many pieces. That is where f-strings help.

### F-String Formatting

An **f-string** is a string that begins with `f` and lets you put variables and expressions inside curly braces. It also lets you control how a value is displayed with a **format specifier** after a colon. The specifier `02d` means "an integer, at least 2 characters wide, padded with zeros."

```python
hour = 9
minute = 5
print(f"{hour}:{minute}")           # 9:5      (looks wrong)
print(f"{hour:02d}:{minute:02d}")   # 09:05    (correct)
```

Zero-padding is essential for clocks, since `9:5` looks broken but `09:05` looks right. The older `.format()` method does the same job: `"{:02d}:{:02d}".format(hour, minute)`. It works on every MicroPython version, while f-strings need a reasonably recent firmware.

!!! mascot-tip "Pad With Zeros"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Whenever you show minutes or seconds, format them with `:02d`. It is a one-line fix that makes `9:5` show as `09:05` every time.

## Lists

A **list** is an ordered collection of values, written in square brackets. Lists can hold any types and can grow or shrink, which is called being **mutable**.

```python
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
print(days[0])        # Mon   (positions start at 0)
print(days[-1])       # Sun   (negative counts from the end)
days.append("Extra")  # add to the end
print(len(days))      # 8
days[0] = "Monday"    # change one item
```

Each item has an **index**, its position, starting at 0. That matters because the time tuple you will meet next stores the weekday as a number where Monday is 0, so `days[weekday]` gives you its label.

Lists are great for repeated values such as a palette of clock colors, or the number of days in each month:

```python
month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
print(month_days[1])   # 28, the value for February
```

## Tuples

A **tuple** is an ordered collection like a list, but **immutable**: once created, it cannot change. It is written with parentheses.

```python
date = (2026, 9, 28)
print(date[0])        # 2026
year, month, day = date   # unpacking: three variables at once
```

**Unpacking** splits a tuple into separate variables in one line. Tuples are important for clocks because MicroPython's `localtime()` function returns the current time as an 8-item tuple: `(year, month, mday, hour, minute, second, weekday, yearday)`. Colors are also tuples, such as `(255, 0, 0)` for red. You will use both in Chapter 6.

!!! mascot-thinking "Change or Protect?"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Lists are for collections that change, and tuples are for values that should stay put, like a fixed color or a timestamp. Choosing the right one tells anyone reading your code what you intended.

| Feature | List | Tuple |
|---------|------|-------|
| Brackets | `[ ]` | `( )` |
| Can change items | Yes | No |
| Good for | Collections that grow | Fixed groups, such as time and color |

## Dictionaries

A **dictionary** (`dict`) stores values under names called **keys** instead of positions. It is written with curly braces and colons.

```python
colors = {"red": (255, 0, 0), "green": (0, 255, 0)}
print(colors["red"])        # (255, 0, 0)
colors["blue"] = (0, 0, 255)  # add a new entry
print(colors.get("pink", "not found"))   # safe lookup with default
```

Use a dictionary when a name is more meaningful than a number. A missing key with square brackets raises a `KeyError`, while `.get()` returns a default instead.

## Print Debugging

**Print debugging** means adding `print()` statements to your program to see what values it holds while it runs. It is the simplest and most widely used way to find a bug. When something is wrong, ask "what does the program think this variable is?" and print it.

Label every value so you can tell the output lines apart:

```python
hour = 15
minute = 7
print("DEBUG hour =", hour, type(hour))
print("DEBUG minute =", minute)
```

Printing the `type()` too can reveal a hidden string or float. The output appears in Thonny's Shell. Use it in three steps: print the input, print the intermediate result, print the final result, and find the line where the value first goes wrong.

Print debugging has limits: too many prints slow the program and clutter the Shell, so delete them when the bug is fixed. Still, it is the tool you will reach for first.

## Putting It Together

Here is a complete first program that combines what you learned: it stores a time, converts it, and prints it neatly.

```python
NAME = "03-time-format.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

hour24 = 15
minute = 7
weekday = 2                         # Wednesday, since Monday is 0

hour12 = (hour24 + 11) % 12 + 1
print(f"{days[weekday]} {hour12}:{minute:02d}")   # Wed 3:07
```

## Key Takeaways

- Thonny plus a USB data cable connects your computer to the Pico; the REPL is a live prompt for quick tests.
- Variables are names for values, and `+=` style operators update them.
- Integers count, floats measure, strings hold text, and booleans answer yes/no questions.
- `//` and `%` split a number of seconds into hours, minutes, and seconds.
- Lists change, tuples do not, and dictionaries look up values by name.
- F-strings with `:02d` make time display correctly, and print debugging shows what your program is thinking.

!!! mascot-celebration "First Code, Done"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now connect Thonny to the Pico, store values in variables, do clock math with `//` and `%`, and format time as `09:05`. That's a working toolkit for your first clock. Every second counts!

## Practice Questions

1. What type does each value have: `7`, `7.0`, `"7"`, `True`, `(7, 7)`?
2. Write the code to turn 3,725 seconds into hours, minutes, and seconds, and predict the output.
3. What does `(0 + 11) % 12 + 1` produce, and why is the formula useful?
4. Explain the difference between a list and a tuple, and give one example of when you would prefer each.
5. A program prints `9:5` for 9:05. Change the print statement so it displays `09:05`.
