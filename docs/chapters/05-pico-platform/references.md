# References: The Pico Platform: Pins, Files, and Firmware

1. [General-purpose input/output](https://en.wikipedia.org/wiki/General-purpose_input/output) - Wikipedia - Explains GPIO pins as software-controlled digital connections that can act as inputs or outputs, with typical uses and electrical limits. It supports this chapter's GPIO pins and pin configuration sections.

2. [Pull-up resistor](https://en.wikipedia.org/wiki/Pull-up_resistor) - Wikipedia - Describes how pull-up and pull-down resistors keep a digital input at a defined level when nothing drives it, such as an unpressed button. It supports the chapter's pull-up resistor and internal pull-up sections.

3. [Flash memory](https://en.wikipedia.org/wiki/Flash_memory) - Wikipedia - Covers flash memory, the non-volatile storage that keeps data without power, including its types and erase limits. It explains where the Pico stores firmware and your files, matching the chapter's flash memory section.

4. Get Started with MicroPython on Raspberry Pi Pico (2nd Edition) - Gareth Halfacree and Ben Everard - Raspberry Pi Press - No single author originated one idea here; this official Pico guide is praised for beginners. It walks through drag-and-drop firmware installation, Thonny, and wiring LEDs and buttons to numbered pins.

5. Programming with MicroPython - Nicholas H. Tollervey - O'Reilly Media - No single author originated one idea here; Tollervey is a MicroPython community developer, and the book is chosen for plain explanations of hardware-facing MicroPython. It supports the chapter's pins, device file system, and startup files.

6. [Raspberry Pi Pico W Datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf) - Raspberry Pi Datasheets - The official board reference with the pinout diagram, GPIO functions, power pins, and wireless chip details. Students use it to find which physical pin matches a GPIO number in this chapter.

7. [Reset and Boot Sequence](https://docs.micropython.org/en/latest/reference/reset_boot.html) - MicroPython Documentation - Explains how MicroPython runs boot.py for one-time setup and then main.py for the program, and how reset behaves. It directly supports the chapter's boot and main files section.

8. [Pull-up Resistors](https://learn.sparkfun.com/tutorials/pull-up-resistors) - SparkFun Learn - Shows how a floating input pin behaves, how a pull-up resistor fixes it, and how to wire a button with one. The idea carries over to the Pico's internal pull-ups in this chapter's lab.

9. [MicroPython on Raspberry Pi Pico](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) - Raspberry Pi Documentation - Official instructions for installing MicroPython by holding BOOTSEL and dragging a UF2 file onto the Pico, plus how to check which board your firmware targets. It supports the firmware flashing section.

10. [MicroPython firmware for Raspberry Pi Pico W](https://micropython.org/download/RPI_PICO_W/) - MicroPython.org - The download page for Pico W firmware images, listing stable releases, older versions, and preview builds, with flashing steps. It supports the chapter's firmware versions and interpreter selection sections.
