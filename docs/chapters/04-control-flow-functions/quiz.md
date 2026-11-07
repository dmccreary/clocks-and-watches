# Quiz: Control Flow, Functions, and Modules

Test your understanding of conditionals, loops, functions, classes, and error handling with these review questions.

---

#### 1. Which statement exits a loop immediately?

<div class="upper-alpha" markdown>
1. `continue`
2. `break`
3. `pass`
4. `global`
</div>

??? question "Show Answer"
    The correct answer is **B**. The `break` statement leaves the loop at once, while `continue` skips only the rest of the current pass and moves to the next one. In the chapter's example, a loop over `range(10)` skips 3 with `continue` and stops at 6 with `break`, so it prints 0, 1, 2, 4, and 5. The `global` keyword has nothing to do with loop control.

    **Concept Tested:** Loop Control

    **See:** [Loop Control](index.md#loop-control)

---

#### 2. Which built-in MicroPython module provides the `Pin`, `I2C`, `SPI`, `PWM`, and `ADC` classes?

<div class="upper-alpha" markdown>
1. `time`
2. `framebuf`
3. `neopixel`
4. `machine`
</div>

??? question "Show Answer"
    The correct answer is **D**. The `machine` module is MicroPython's gateway to the Pico's hardware, and you will import from it in almost every lab. The `time` module handles delays and clock values, `framebuf` draws to a memory buffer, and `neopixel` controls NeoPixel LEDs. The `machine` module also offers utilities such as `machine.freq()` and `machine.reset()`.

    **Concept Tested:** Machine Module

    **See:** [Machine Module](index.md#machine-module)

---

#### 3. How does a module differ from a library in MicroPython?

<div class="upper-alpha" markdown>
1. A module is a single `.py` file, and a library is a collection of related modules
2. A module is built into the Pico, and a library is always copied from a computer
3. A module holds only classes, and a library holds only variables
4. A module runs on core 0, and a library runs on core 1
</div>

??? question "Show Answer"
    The correct answer is **A**. A module is one Python file whose name, without `.py`, becomes the name you import. A library groups modules that provide a set of related features. Some libraries are built in, such as `machine`, and others are added by copying files to the Pico, such as `ssd1306`. Modules can hold functions, variables, and classes, and neither is tied to a particular processor core.

    **Concept Tested:** Modules

    **See:** [Modules](index.md#modules)

---

#### 4. Starting with `seconds = 58`, what is its value after the line `seconds = (seconds + 1) % 60` runs four times?

<div class="upper-alpha" markdown>
1. 62
2. 0
3. 2
4. 1
</div>

??? question "Show Answer"
    The correct answer is **C**. The four passes produce 59, 0, 1, and 2. The `% 60` operator wraps the value back to 0 once it would reach 60, just like the numbers on a clock face. Without the modulo, the counter would reach 62. This wrap-around trick works for seconds, minutes, hours, and menu modes, and it handles going backward too.

    **Concept Tested:** Modular Arithmetic

    **See:** [Modular Arithmetic](index.md#modular-arithmetic)

---

#### 5. With `hour = 8`, what does `greeting` become in this chain: `if hour < 6` Night, `elif hour < 12` Morning, `elif hour < 18` Afternoon, `else` Evening?

<div class="upper-alpha" markdown>
1. Night
2. Morning
3. Afternoon
4. Evening
</div>

??? question "Show Answer"
    The correct answer is **B**. Python tests the conditions from the top and runs only the first block whose condition is true. Here `8 < 6` is false and `8 < 12` is true, so `greeting` is "Morning" and the remaining tests are skipped. Order matters: if the `hour < 18` test came first, every morning would also be called "Afternoon".

    **Concept Tested:** If Else Elif

    **See:** [If, Else, Elif](index.md#if-else-elif)

---

#### 6. Why does the line `if hour = 12:` cause a syntax error?

<div class="upper-alpha" markdown>
1. The number 12 is too large to use in a condition
2. The `if` statement must be written with parentheses around it
3. The `time` module must be imported before any `if` statement
4. A single `=` stores a value, so a comparison needs `==`
</div>

??? question "Show Answer"
    The correct answer is **D**. In Python, `=` is the assignment operator that stores a value, and `==` asks whether two values are equal. A condition needs a comparison that produces a boolean, so `if hour == 12:` is correct. If an `if` line still fails, check the colon at the end and the indentation of the block underneath. Those are the other two usual suspects.

    **Concept Tested:** Conditionals

    **See:** [Conditionals](index.md#conditionals)

---

#### 7. Which loop prints the five-minute-style marks 0, 15, 30, and 45 and nothing else?

<div class="upper-alpha" markdown>
1. `for m in range(0, 60, 15):`
2. `for m in range(0, 45, 15):`
3. `for m in range(15, 60, 15):`
4. `for m in range(0, 15, 60):`
</div>

??? question "Show Answer"
    The correct answer is **A**. The `range(start, stop, step)` function stops before the stop value, so `range(0, 60, 15)` yields 0, 15, 30, and 45. Option B stops at 30 because 45 is excluded, option C skips 0 and starts at 15, and option D yields only 0 because the step is larger than the gap. Counting how many values you need helps you check the stop value.

    **Concept Tested:** For Loops

    **See:** [For Loops](index.md#for-loops)

---

#### 8. Why would `count += 1` inside a function raise an error unless the function declares `global count`?

<div class="upper-alpha" markdown>
1. Functions are not allowed to change integer values
2. The word `count` is reserved by Python for loops
3. Assigning inside a function creates a new local variable that has no value yet
4. The `+=` operator works only on lists and strings
</div>

??? question "Show Answer"
    The correct answer is **C**. Assigning to a name inside a function normally creates a new local variable. Since `count += 1` needs a starting value, and the local `count` does not have one, Python raises an error. The `global` keyword tells Python to use the variable defined outside the function. Use it sparingly, though interrupt handlers and callbacks often need it because they cannot return a value to your main code.

    **Concept Tested:** Global Keyword

    **See:** [Global Keyword](index.md#global-keyword)

---

#### 9. You create `seconds = Counter(60)` and `minutes = Counter(60)`, then call `seconds.tick()` five times. What is `minutes.value`, and why?

<div class="upper-alpha" markdown>
1. 5, because both objects share one value stored in the class
2. 5, because `tick()` updates every object built from `Counter`
3. 60, because the limit is applied to every object at once
4. 0, because each object keeps its own copy of `value`
</div>

??? question "Show Answer"
    The correct answer is **D**. A class is a blueprint, and each object built from it stores its own data. The `__init__` method sets `self.value = 0` separately for `seconds` and for `minutes`, and `tick()` changes only the object it is called on. That is why one program can run several counters without interference. Calling `seconds.tick()` leaves `minutes` untouched.

    **Concept Tested:** Classes and Objects

    **See:** [Classes and Objects](index.md#classes-and-objects)

---

#### 10. Why is `except OSError:` usually better than a bare `except:` when reading a sensor that might be unplugged?

<div class="upper-alpha" markdown>
1. It handles only the failure you expect, so unrelated bugs are not hidden
2. It makes the program run faster than a bare `except:` block
3. It prevents the sensor from ever being unplugged during a run
4. It lets the program skip the `try` block entirely
</div>

??? question "Show Answer"
    The correct answer is **A**. Talking to an unplugged device raises `OSError`, and naming that exception lets your code print a helpful message or use a fallback. A bare `except:` catches every exception, including typos and logic errors, which hides real bugs and makes them hard to find. Naming the exception you expect keeps the handler focused and keeps unexpected problems visible.

    **Concept Tested:** Try Except Blocks

    **See:** [Try Except Blocks](index.md#try-except-blocks)
