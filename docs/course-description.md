---
title: Course Description
description: A detailed course description for Building Clocks and Watches with MicroPython
quality_score: 96
---
# Course Description

**Course Title:** Building Clocks and Watches with MicroPython<br/>
**Duration:** 14 Weeks<br/>
**Target Audience:** High School Students Learning Computational Thinking<br/>
**Prerequisites:** No prior programming or electronics experience required

**Course Description:**
In this 14-week, hands-on course, high school students learn to design and program functional timekeeping devices---from simple LED clocks to round smartwatch displays, NeoPixel art clocks, stopwatches, and web-connected weather displays---using MicroPython on the Raspberry Pi Pico W. Students progress through increasingly sophisticated projects, building both programming skills and electronics knowledge. Our goal is to create fun projects that teach [computational thinking](glossary.md#computational-thinking).

## Weekly Schedule

### Weeks 1--2: Introduction to MicroPython and Basic Electronics

Students set up their development environment using the Thonny IDE and the Raspberry Pi Pico. They learn Python fundamentals---variables, data types, arithmetic operations, and basic syntax---while writing their first programs that draw rectangles, lines, and text to a display. Students build their first working clock using the TM1637 4-digit LED display ($1--2), learning to use just four wires to show hours and minutes with a flashing colon.

**Key concepts:** Variables, data types, the `localtime()` function, basic I/O, lists of colors

### Weeks 3--4: Control Structures, Functions, and Button Input

Students learn conditionals (`if`/`else`/`elif`), loops (`for`/`while`), and functions while adding interactivity to their clocks. They wire up momentary push buttons to GPIO pins and learn about interrupt handlers, debouncing (both hardware and software), and state machines for cycling through clock modes (run, set hour, set minute, set AM/PM). Students practice modular arithmetic for cycling through time values.

**Key concepts:** Conditionals, loops, functions, GPIO input, interrupts, debouncing, state machines

### Weeks 5--6: Communication Buses and the I2C OLED Clock

Students explore how microcontrollers communicate with peripheral devices through the I2C bus (SDA, SCL, 4 wires) and the faster SPI bus (7 wires). They build a small SSD1306 OLED clock ($3--4) using I2C, learning to initialize displays, draw text, and update the screen. They run I2C scanner programs to detect connected devices and understand device addressing.

**Key concepts:** I2C protocol, SPI protocol, device addressing, display initialization, framebuffers, `config.py` hardware abstraction

### Weeks 7--8: The Large OLED Clock and Real-Time Clocks

Students build the Large OLED kit---a 128x64 SSD1306 on the SPI bus mounted on acrylic with a half-size breadboard. They integrate the DS3231 real-time clock module, learning about battery backup (CR2032), temperature-compensated crystal oscillators, and BCD-encoded time registers. Students write programs that read time from the RTC and survive power outages.

**Key concepts:** SPI bus wiring, real-time clock (DS3231), I2C device integration, BCD format, backup power, `main-rtc.py` vs. `main-buttons.py` program variants

### Weeks 9--10: WiFi, NTP Time Sync, and Weather Displays

Using the Raspberry Pi Pico W, students connect to WiFi and synchronize time from internet NTP servers. They learn about the NTP client-server model, time server hierarchy (stratum levels), and UTC-to-local-time conversion. Students build the OLED Wireless Weather Kit, fetching real-time temperature data and displaying it alongside the time. They learn to manage `secrets.py` files for WiFi credentials.

**Key concepts:** WiFi connectivity, NTP protocol, UTC and timezone conversion, web services, `secrets.py` configuration, `main-w.py` program variant

### Week 11: Color Displays---ILI9341, ST7735, and GC9A01

Students move to color TFT and round smartwatch displays. They work with the ILI9341 (240x320, ~$9), the ST7735 (160x128, ~$3.50), and the round GC9A01 (240x240) used in smartwatch projects. Students learn about RGB565 color encoding, drawing primitives, custom fonts, and designing both digital and analog clock faces with tick marks and rotating hands. They explore the `color565()` function and manage color palettes in a `colors.py` file.

**Key concepts:** Color displays, RGB565 encoding, drawing primitives (lines, rectangles, circles, polygons), analog clock face design, custom fonts, display driver differences

### Week 12: NeoPixel Art Clocks and Shift Registers

Students build creative NeoPixel LED strip clocks---including a binary clock, a seven-segment clock, and an elegant Fibonacci clock. They learn about addressable WS2812B LEDs (just 3 wires for up to 400 RGB LEDs), soldering, and the 74HC595 shift register for controlling more outputs than available GPIO pins. Students explore how shift registers expand a few Pico pins into many output pins using serial data, clock, and latch signals.

**Key concepts:** Addressable LEDs (WS2812B/NeoPixel), shift registers (74HC595), serial-to-parallel conversion, binary number systems, soldering skills

### Week 13: Sound, DACs, Power, and Advanced Features

Students add sound to their clocks using piezoelectric buzzers with PWM and explore the PCM5102 DAC board with the I2S protocol for higher-quality audio. They learn about alarm clock features (snooze, alarm tones, hourly chimes), stopwatch and timer implementations, and photosensors for automatic brightness adjustment. Power topics include USB vs. battery power, LiPo batteries, and coin cells for RTC backup.

**Key concepts:** PWM sound generation, I2S protocol, digital-to-analog conversion, photosensors and ADC, power management, alarm and timer logic

### Week 14: Custom Clock Design and Final Presentations

Students design and build their own custom timekeeping project, choosing from any combination of displays, sensors, and features covered in the course. They use generative AI tools (ChatGPT, Claude) to help customize and extend their code. Teams present their finished clocks, explaining their design trade-offs---cost, display readability, power consumption, accuracy, and user experience.

**Key concepts:** Project planning, design trade-offs, AI-assisted code generation, integration of multiple subsystems, presentation skills

## Learning Outcomes (Bloom's Taxonomy)

1.  **Remember:** Identify essential electronic components---breadboards, microcontrollers, buttons, rotary encoders, real-time clocks, and displays (LED, OLED, TFT, e-paper, NeoPixel)---and recall fundamental MicroPython programming concepts.
2.  **Understand:** Explain how communication buses (I2C, SPI), timing functions (`localtime()`, NTP), and hardware connections work together to create a functioning clock. Describe computational thinking concepts including abstraction, decomposition, pattern recognition, and algorithmic thinking.
3.  **Apply:** Wire and program multiple display types, integrate real-time clocks and WiFi time synchronization, implement stopwatches and alarm clocks, and use buttons and interrupts to handle user input with proper debouncing.
4.  **Analyze:** Diagnose wiring and code issues using I2C scanners and debugging techniques. Compare I2C vs. SPI bus trade-offs, evaluate timing accuracy across different clock sources (internal RTC, DS3231, NTP), and analyze how baudrate and display refresh rates affect performance.
5.  **Evaluate:** Assess multiple clock designs for accuracy, cost, power consumption, display readability, and user experience. Use generative AI to explore design alternatives and critically evaluate AI-generated code.
6.  **Create:** Design and build a custom timekeeping project that integrates hardware (display, RTC, buttons, sensors, speaker) and software (time management, display rendering, user input handling) into a polished, functioning prototype.

## Kit Projects

Students build from a library of over 20 clock and watch kits at various price points:

- **LED Clocks ($5--8):** TM1637 4-digit display, MAX7219 serial LED driver, character LCD (LCD1602)
- **OLED Clocks ($7--12):** Small SSD1306 I2C, large SSD1306 SPI, SH1106
- **Color Display Clocks ($12--20):** ILI9341 TFT, ST7735 LCD, GC9A01 round smartwatch
- **NeoPixel Art Clocks ($11--15):** Binary clock, seven-segment clock, Fibonacci clock
- **Specialty Clocks:** E-paper/e-ink displays, Waveshare RP2040 smartwatch, LilyGo RP2040, shift register clock
- **Feature Projects:** Stopwatch, alarm clock, wireless weather clock

By the end of the course, students will have built a diverse collection of digital clocks, stopwatches, and timers while gaining a rich understanding of electronics, computational thinking, and MicroPython. They will leave empowered to continue exploring the world of embedded systems and creative hardware projects, with skills in using generative AI tools to accelerate their development.

## Computational Thinking

A structured problem-solving approach that uses computer science principles to formulate solutions by breaking down complex tasks into logical, repeatable steps that can be understood by both humans and machines **Example:** Breaking down the task of making a peanut butter sandwich into discrete steps: "open jar", "grasp knife", "scoop peanut butter".

The main concepts of computational thinking are:

### Decomposition

The process of breaking a complex problem into smaller, more manageable parts.

**Example:** Dividing a clock program into separate functions for displaying time, handling buttons, and managing alarms.

### Pattern Recognition

The ability to identify similarities, trends, and regularities in data or problems.

**Example:** Noticing that both analog and digital clocks need similar time calculation functions despite different display methods.

### Abstraction

Focusing on essential details while filtering out irrelevant information to create a generalized solution 

**Example:** Creating a `display_time()` function that works with any type of display by hiding the specific implementation details.

### Algorithmic Thinking

Creating a set of ordered steps that will solve a problem or achieve a goal.

**Example:** Developing a sequence of steps to synchronize a clock with an internet time server.

These concepts work together:

1.  First, decompose the problem
2.  Look for patterns in the smaller pieces
3.  Abstract away unnecessary details
4.  Create step-by-step solutions with algorithms

## Detailed Learning Objectives Using Bloom's Taxonomy

### Level 1: Remember

Retrieve relevant knowledge from long-term memory.

1. **List** the five core components of a clock architecture: sensors, microcontroller, communication bus, display, and power supply.
2. **Identify** the pins and wiring for I2C (SDA, SCL, VCC, GND) and SPI (SCK, MOSI, DC, CS, RES, VCC, GND) communication buses.
3. **Name** the eight values returned by the MicroPython `localtime()` function: year, month, day, hour, minute, second, weekday, and yearday.
4. **Recall** common I2C device addresses used in clock projects (e.g., `0x3C` for SSD1306 OLED, `0x68` for DS3231 RTC).
5. **Define** key terms: GPIO, interrupt, debouncing, framebuffer, baudrate, pull-up resistor, PWM, NTP, UTC, BCD, RGB565.
6. **Recognize** the physical components in a clock kit: Raspberry Pi Pico, breadboard, OLED display, DS3231 RTC module, push buttons, and coin-cell battery.

### Level 2: Understand

Construct meaning from instructional messages and component interactions.

1. **Explain** how the I2C and SPI buses transfer data between a microcontroller and a display, including the role of each wire.
2. **Describe** how the DS3231 real-time clock maintains accurate time through temperature-compensated crystal oscillation and battery backup.
3. **Summarize** the NTP client-server model, including the stratum hierarchy and how a Pico W requests and applies a time update.
4. **Distinguish** between the internal Pico RTC (resets on power loss), an external DS3231 RTC (battery-backed), and NTP synchronization (internet-dependent) as time sources.
5. **Interpret** the relationship between baudrate settings on the SPI bus and display update performance.
6. **Classify** display types by their technology and trade-offs: LED segment (low cost, high visibility), OLED (high contrast, graphic capable), TFT LCD (color, larger), e-paper (low power, slow refresh), and NeoPixel (colorful, creative layouts).
7. **Paraphrase** computational thinking concepts---decomposition, pattern recognition, abstraction, and algorithmic thinking---using clock project examples.

### Level 3: Apply

Carry out or use a procedure in a given situation.

1. **Wire** a TM1637 LED display, an SSD1306 OLED (I2C and SPI), and an ILI9341 color TFT display to a Raspberry Pi Pico following pin configuration diagrams.
2. **Write** a MicroPython program that reads the current time using `localtime()` and formats it for display in 12-hour format with AM/PM labels.
3. **Implement** button interrupt handlers with software debouncing to cycle through clock modes (run, set hour, set minute, set AM/PM).
4. **Use** the I2C scanner program to detect connected devices and verify wiring before writing display code.
5. **Program** the DS3231 RTC to set and read time values over the I2C bus, and use battery backup to maintain time through power cycles.
6. **Configure** WiFi connectivity on the Pico W using a `secrets.py` file and synchronize time from an NTP server using `ntptime.settime()`.
7. **Draw** clock faces on graphic displays using drawing primitives: lines for tick marks, filled shapes for hands, and text rendering for digit labels.
8. **Construct** a `config.py` file to abstract hardware pin assignments so the same clock program runs on different wiring configurations.
9. **Build** a stopwatch application using two buttons (start/stop and reset) with accurate elapsed-time tracking.

### Level 4: Analyze

Break material into constituent parts and determine how parts relate to each other and to an overall structure.

1. **Compare** I2C and SPI communication buses in terms of wire count, speed, complexity, and suitability for different display types.
2. **Diagnose** common clock malfunctions: blank displays (wiring errors), incorrect time (RTC not set), display flicker (baudrate too low), and double button presses (inadequate debouncing).
3. **Differentiate** between the three program variants (`main-buttons.py`, `main-rtc.py`, `main-w.py`) and determine which is appropriate for a given hardware configuration.
4. **Examine** how the modular arithmetic expression `hour = ((hour - 2) % 12) + 1` correctly decrements hours within the 1--12 range, and why simpler approaches fail.
5. **Deconstruct** a complete clock program into its subsystems: time acquisition, time formatting, display rendering, user input handling, and alarm management.
6. **Investigate** how photosensor readings from the ADC can be mapped to display brightness levels, including the role of hysteresis in preventing rapid brightness oscillation.

### Level 5: Evaluate

Make judgments based on criteria and standards.

1. **Assess** clock kit options for a given budget and use case, weighing cost, display quality, assembly complexity, and feature set.
2. **Justify** the choice of time source (manual buttons, DS3231 RTC, or NTP) based on project requirements for accuracy, cost, and internet availability.
3. **Critique** AI-generated MicroPython code for a clock project, identifying errors, inefficiencies, and missing edge cases before deploying it to hardware.
4. **Judge** the trade-offs between display technologies: OLED contrast vs. TFT color, e-paper battery life vs. refresh rate, NeoPixel creativity vs. readability.
5. **Rank** power strategies (USB wall power, AA batteries, LiPo, USB battery pack) for different deployment scenarios: desk clock, portable watch, and battery-backup alarm clock.
6. **Appraise** a peer's clock project against criteria including code modularity, wiring neatness, time accuracy, user interface quality, and documentation.

### Level 6: Create

Put elements together to form a coherent or functional whole; reorganize elements into a new pattern or structure.

1. **Design** a custom clock that integrates at least three subsystems (e.g., color display, RTC, WiFi sync, buttons, speaker, photosensors) into a unified project.
2. **Compose** a MicroPython program that combines time display, alarm functionality, automatic brightness adjustment, and NTP synchronization in a single application.
3. **Construct** an original NeoPixel clock layout (beyond binary, seven-segment, or Fibonacci) that represents time in a novel visual format.
4. **Develop** a multi-screen clock interface that cycles between time, date, temperature (from the DS3231), and weather data (from a web service).
5. **Produce** a generative AI prompt that accurately specifies hardware connections, display type, desired features, and edge cases to generate working clock code.
6. **Assemble** and present a finished clock prototype with documentation that explains design decisions, wiring diagrams, code architecture, and lessons learned.