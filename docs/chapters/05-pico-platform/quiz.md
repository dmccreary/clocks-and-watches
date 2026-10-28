# Quiz: The Pico Platform: Pins, Files, and Firmware

Test your understanding of GPIO pins, pull-up resistors, flash memory, boot files, and firmware with these review questions.

---

#### 1. A wire is connected to the pin labeled GP15, which is physical pin 20 on the board. Which number do you write inside `Pin()` in your code?

<div class="upper-alpha" markdown>
1. 15
2. 20
3. 40
4. 5
</div>

??? question "Show Answer"
    The correct answer is **A**. Your code always uses the GP number, so you write `Pin(15)`. The physical pin number only describes where the pin sits on the board, counted from a corner. Typing the physical number into `Pin()` is a very common mistake that lights the wrong pin or none at all. Always look up the GP label on a pinout diagram.

    **Concept Tested:** GPIO Pins

    **See:** [GPIO Pins](index.md#gpio-pins)

---

#### 2. In what order does MicroPython run the two special files when the Pico powers on?

<div class="upper-alpha" markdown>
1. `main.py` first, then `boot.py`
2. `config.py` first, then `main.py`
3. `boot.py` first, then `main.py`
4. `main.py` first, then the `/lib` folder
</div>

??? question "Show Answer"
    The correct answer is **C**. The file `boot.py` runs first and is for low-level setup, so it is usually left empty. The file `main.py` runs next and holds your clock program. To make a clock start by itself with no computer attached, save the program on the Pico as `main.py`. A program with any other name runs only when you press Run in Thonny.

    **Concept Tested:** Boot and Main Files

    **See:** [Boot and Main Files](index.md#boot-and-main-files)

---

#### 3. Why does a program saved on the Pico survive a power loss, while the variables it was using disappear?

<div class="upper-alpha" markdown>
1. Flash is faster than RAM, so it needs power to hold its data
2. Flash keeps its contents without power, while RAM is wiped when power is lost
3. RAM holds the firmware and your files, while flash holds the variables
4. Both are wiped at power-off, but flash restores itself from the USB cable
</div>

??? question "Show Answer"
    The correct answer is **B**. The Pico has 2 MB of flash that holds the MicroPython firmware and your files, and it keeps them with no power. The 264 KB of RAM is fast working memory for variables, and it is wiped whenever power is lost. Think of flash as a bookshelf and RAM as a desk. Flash also wears out after about 100,000 erase cycles per block.

    **Concept Tested:** Flash Memory

    **See:** [Flash Memory](index.md#flash-memory)

---

#### 4. What problem does a pull-up resistor solve for a button connected to an input pin?

<div class="upper-alpha" markdown>
1. It increases the current so the pin can drive an LED directly
2. It converts a 5 V button signal into a safe 3.3 V signal
3. It removes the contact bounce that happens when a button is pressed
4. It gives the pin a defined resting level so it does not float with noise
</div>

??? question "Show Answer"
    The correct answer is **D**. An input connected to nothing floats, so its voltage drifts with static electricity and `value()` flips unpredictably between 0 and 1. A pull-up connects the pin to 3.3 V through a large resistor, so it reads 1 by default. Pressing the button connects the pin to ground, which reads 0. Debouncing is a separate problem that Chapter 7 covers.

    **Concept Tested:** Pull-Up Resistors

    **See:** [Pull-Up Resistors](index.md#pull-up-resistors)

---

#### 5. Why do the buttons in this book need only two connections, one to a GPIO pin and one to ground?

<div class="upper-alpha" markdown>
1. The RP2040 has an internal pull-up that you switch on with `Pin.PULL_UP`
2. Every button has a resistor built into its plastic case
3. GPIO pins are always connected to ground inside the chip
4. The wireless chip on the Pico W supplies the resting voltage
</div>

??? question "Show Answer"
    The correct answer is **A**. Every GPIO pin has a built-in resistor of roughly 50 to 80 kΩ that you enable in code with `Pin.PULL_UP`. That saves parts and wiring because no external resistor is needed. The button then simply connects the pin to ground when pressed. This also works on the plain Pico, which has no wireless chip at all.

    **Concept Tested:** Internal Pull-Up

    **See:** [Internal Pull-Up](index.md#internal-pull-up)

---

#### 6. A button is wired between GP10 and ground, and the pin is configured with `Pin.PULL_UP`. What does `value()` return while the button is pressed?

<div class="upper-alpha" markdown>
1. 1
2. None
3. 0
4. 3.3
</div>

??? question "Show Answer"
    The correct answer is **C**. With the pull-up, an unpressed button leaves the pin at 3.3 V, so `value()` is 1. Pressing the button connects the pin to ground and overpowers the weak pull-up, so `value()` is 0. This backward-feeling behavior is called active low, and it is the standard way to wire buttons. The method returns only 0 or 1, never a voltage.

    **Concept Tested:** Pin Configuration

    **See:** [Pin Configuration](index.md#pin-configuration)

---

#### 7. You downloaded a new `.uf2` MicroPython firmware file. What must you do to make the `RPI-RP2` drive appear so you can drag the file onto it?

<div class="upper-alpha" markdown>
1. Press Ctrl+D in the Shell panel of Thonny
2. Hold the BOOTSEL button while plugging the Pico into USB
3. Save a program on the Pico with the name `main.py`
4. Run `os.uname()` in the REPL and copy the version text
</div>

??? question "Show Answer"
    The correct answer is **B**. Holding BOOTSEL while plugging in makes the Pico present itself as a USB drive named `RPI-RP2`. Drag the `.uf2` file onto that drive and the Pico reboots by itself with the new firmware. Thonny's Install MicroPython option can do this for you. Choose the firmware file for your exact board, since a plain Pico file will not give a Pico W any WiFi.

    **Concept Tested:** Firmware Flashing

    **See:** [Firmware Flashing](index.md#firmware-flashing)

---

#### 8. Your clock kit uses `config.py` with a line `BUTTON_PIN = 14`. You move the button wire to GP16. What is the best change to make?

<div class="upper-alpha" markdown>
1. Edit every program that creates a button and replace 14 with 16
2. Reflash the firmware so the Pico learns about the new pin
3. Rename `main.py` so that the Pico rereads its pin settings
4. Change `BUTTON_PIN` to 16 once in `config.py`
</div>

??? question "Show Answer"
    The correct answer is **D**. The config file pattern keeps every hardware setting in one file that other programs import. Changing a single line updates every program that uses `config.BUTTON_PIN`. Without this pattern, pin numbers are scattered through many files and rewiring means editing dozens of lines. Adding a comment naming the wire color next to each pin also turns the file into a wiring diagram.

    **Concept Tested:** Config File Pattern

    **See:** [Config File Pattern](index.md#config-file-pattern)

---

#### 9. A clock program works when you press Run in Thonny, but nothing happens after you unplug and replug the Pico. What is the most likely cause?

<div class="upper-alpha" markdown>
1. The file `boot.py` runs first and always erases the program
2. The flash memory has worn out after only a few runs
3. The program was not saved on the Pico as `main.py`
4. The Pico W firmware is missing from the board
</div>

??? question "Show Answer"
    The correct answer is **C**. Only a file named `main.py` on the Pico runs automatically at power-on. A program with another name, or one saved only on the computer, runs only when you press Run. Check with `os.listdir()` that the file arrived. Flash wear takes about 100,000 erase cycles per block, so a few runs cannot cause it, and `boot.py` is normally empty.

    **Concept Tested:** Code Upload Process

    **See:** [Code Upload Process](index.md#code-upload-process)

---

#### 10. A program fails on the line `from machine import Pin` with a `ModuleNotFoundError`, even though the same code worked yesterday. What should you check first?

<div class="upper-alpha" markdown>
1. Whether Thonny's interpreter was switched to Local Python 3
2. Whether the `machine` file was copied into the `/lib` folder
3. Whether the Pico has run out of its 264 KB of RAM
4. Whether the firmware is too old to support f-strings
</div>

??? question "Show Answer"
    The correct answer is **A**. The `machine` module exists only in MicroPython on the Pico. If Thonny's interpreter is set to Local Python 3, your code runs on the computer, where that module does not exist, and the import fails. Look at the bottom-right corner of the Thonny window and select MicroPython (Raspberry Pi Pico). The `machine` module is built in, so it never needs to be copied to `/lib`.

    **Concept Tested:** Interpreter Selection

    **See:** [Interpreter Selection](index.md#interpreter-selection)
