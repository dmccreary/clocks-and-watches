# Quiz: MicroPython Basics: Variables and Data Types

Test your understanding of Thonny, the REPL, variables, data types, and string formatting with these review questions.

---

#### 1. What does the REPL do with each line you type at the `>>>` prompt?

<div class="upper-alpha" markdown>
1. It saves the line to a file and runs the file when you press Stop
2. It compiles your whole program on the laptop and sends the result to the Pico
3. It reads the line, evaluates it, prints the result, and loops back for more
4. It waits for a complete program to be uploaded before running anything
</div>

??? question "Show Answer"
    The correct answer is **C**. REPL stands for Read-Eval-Print Loop. It reads what you typed, evaluates it, prints the answer, and loops back for the next line. This gives you instant feedback, so you can test a command in five seconds before adding it to a program. Typing an expression like `2 + 3` shows its value automatically, while `print()` shows exactly what you give it.

    **Concept Tested:** REPL

    **See:** [REPL](index.md#repl)

---

#### 2. What does the `//` operator do in MicroPython?

<div class="upper-alpha" markdown>
1. It divides and discards the remainder, giving a whole number
2. It divides and returns only the remainder
3. It divides and always returns a number with a decimal point
4. It raises the first number to the power of the second
</div>

??? question "Show Answer"
    The correct answer is **A**. The `//` operator is floor division, so `7 // 2` is 3. The `%` operator returns only the remainder, so `7 % 2` is 1. The `/` operator always returns a float, so `7 / 2` is 3.5, and `**` raises to a power. Clock programs use `//` and `%` together to split a number of seconds into hours, minutes, and seconds.

    **Concept Tested:** Arithmetic Operations

    **See:** [Arithmetic Operations](index.md#arithmetic-operations)

---

#### 3. Which collection type cannot be changed after it is created, and is what `localtime()` returns?

<div class="upper-alpha" markdown>
1. List
2. Dictionary
3. Float
4. Tuple
</div>

??? question "Show Answer"
    The correct answer is **D**. A tuple is an ordered collection like a list, but it is immutable. The `localtime()` function returns the current time as an 8-item tuple of year, month, day, hour, minute, second, weekday, and year day. Colors are also tuples, such as `(255, 0, 0)` for red. Lists and dictionaries can change, and a float is a single number, not a collection.

    **Concept Tested:** Tuples

    **See:** [Tuples](index.md#tuples)

---

#### 4. Why can using `/` to compute a pixel position cause an error?

<div class="upper-alpha" markdown>
1. The `/` operator can only be used with negative numbers
2. The `/` operator always returns a float such as `3.0`, not a whole number
3. The `/` operator discards the remainder and returns zero
4. The `/` operator works only on strings, not on numbers
</div>

??? question "Show Answer"
    The correct answer is **B**. Division with `/` always returns a float, even when the answer is whole, so `6 / 2` gives `3.0`. Code that needs a whole number, such as a pixel position or a list index, can break on that hidden float. Use `//` for whole-number division, or convert the result with `int()` or `round()`. Remember that `int(3.9)` drops the decimal part, while `round(3.9)` gives 4.

    **Concept Tested:** Floats

    **See:** [Floats](index.md#floats)

---

#### 5. Thonny cannot find your Pico even though it is plugged in. What is the most common cause?

<div class="upper-alpha" markdown>
1. The Pico has run out of its 264 KB of RAM
2. The editor is saving files to the computer instead of the device
3. The program uses an f-string on an older firmware version
4. The USB cable only carries power and has no data wires
</div>

??? question "Show Answer"
    The correct answer is **D**. Many cheap USB cables are charge-only and contain no data wires, so the Pico powers up but never appears as a serial port. Try a different cable, ideally one you know can transfer files, and plug it directly into the computer instead of a hub. The other options affect how a program behaves after the connection already works, not whether Thonny can find the board.

    **Concept Tested:** USB Connection

    **See:** [USB Connection](index.md#usb-connection)

---

#### 6. Why is MicroPython described as a subset of Python 3?

<div class="upper-alpha" markdown>
1. It includes the core language and a trimmed library, plus extra hardware modules like `machine`
2. It is an older version of Python that was written before Python 3
3. It must be compiled on a laptop before the code can run on the Pico
4. It supports only whole numbers and has no floating-point type
</div>

??? question "Show Answer"
    The correct answer is **A**. The full Python interpreter would not fit on a chip with 264 KB of RAM, so MicroPython keeps the core language and a smaller standard library, then adds modules such as `machine`, `neopixel`, and `rp2` for hardware. If a program from the internet fails with `ImportError`, check whether that module exists in MicroPython. It does support floats, with about 7 significant digits.

    **Concept Tested:** Micropython Differences

    **See:** [MicroPython Differences](index.md#micropython-differences)

---

#### 7. What does the expression `(hour24 + 11) % 12 + 1` produce when `hour24` is 0?

<div class="upper-alpha" markdown>
1. 0
2. 11
3. 12
4. 1
</div>

??? question "Show Answer"
    The correct answer is **C**. Add 11 to get 11, take the remainder when divided by 12 to get 11, then add 1 to get 12. The plain remainder `hour % 12` would give 0 for midnight, but a 12-hour clock should show 12. The same formula gives 12 for hour 12 and 1 for hour 13, so testing the edge cases confirms that it works for the whole day.

    **Concept Tested:** Arithmetic Operations

    **See:** [Arithmetic Operations](index.md#arithmetic-operations)

---

#### 8. With `hour = 9` and `minute = 5`, what does `print(f"{hour:02d}:{minute:02d}")` display?

<div class="upper-alpha" markdown>
1. 9:5
2. 09:05
3. 9:05
4. 09:5
</div>

??? question "Show Answer"
    The correct answer is **B**. The format specifier `02d` means an integer at least two characters wide, padded with zeros. Applying it to both values turns 9 into `09` and 5 into `05`. Without the specifier, the clock would show `9:5`, which looks broken. The older `.format()` method does the same job and works on every MicroPython version, while f-strings need reasonably recent firmware.

    **Concept Tested:** F-String Formatting

    **See:** [F-String Formatting](index.md#f-string-formatting)

---

#### 9. Given `total = 3725`, what value does `minutes` hold after `left = total % 3600` and `minutes = left // 60`?

<div class="upper-alpha" markdown>
1. 62
2. 5
3. 1
4. 2
</div>

??? question "Show Answer"
    The correct answer is **D**. The expression `3725 % 3600` leaves 125 seconds after removing one whole hour. Then `125 // 60` gives 2 whole minutes, with 5 seconds remaining. So the time is 1 hour, 2 minutes, and 5 seconds. The value 62 would be the total number of minutes, which ignores the step of separating hours from the leftover seconds.

    **Concept Tested:** Integers

    **See:** [Integers](index.md#integers)

---

#### 10. A program stops with a `TypeError` on the line `print("Hour: " + hour)`. Adding `print(type(hour))` shows `<class 'int'>`. What does this reveal and how should you fix it?

<div class="upper-alpha" markdown>
1. The variable name is a reserved word, so it must be renamed
2. Concatenation needs strings, so convert with `str(hour)` or use an f-string
3. The variable is a float, so it should be rounded with `round()`
4. The variable is a tuple, so it must be unpacked before printing
</div>

??? question "Show Answer"
    The correct answer is **B**. The `+` operator joins strings only with strings, and `hour` is an integer. Print debugging with `type()` revealed the mismatch. You can fix it with `"Hour: " + str(hour)`, or more cleanly with an f-string such as `f"Hour: {hour}"`. Printing a value and its type is often the quickest way to uncover a hidden string, float, or integer.

    **Concept Tested:** String Concatenation

    **See:** [String Concatenation](index.md#string-concatenation)
