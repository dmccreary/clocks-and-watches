#### 12-Hour vs 24-Hour Formats
Methods for displaying time in either 12-hour (AM/PM) or 24-hour (military) format, including conversion between the two.

**Example:** Converting 13:00 to 1:00 PM and handling the AM/PM indicator.

#### 3D Printing Clock and Watch Enclosures

A process of creating custom protective cases for watch components using additive manufacturing technology.

We will not cover these topics in this course.  Our focus in this website is using clock and watch projects to teach computational thinking.

#### Abstraction

A technique for managing complexity by hiding unnecessary details while keeping essential features visible. 

**Example:** Using a `display_time()` function that accepts hours and minutes without needing to know how individual LED segments are controlled.

Abstraction is one of the four key computational thinking topics we teach in this course.

#### Accelerometer
A sensor that measures physical acceleration and orientation, useful for tilt-based display activation.

**Example:** Detecting when a user lifts their wrist to view the watch face.

#### Alarm
A scheduled alert that triggers audio, visual, or vibration notifications at specific times.

**Example:** Setting multiple daily alarms using the RTC module.

#### Analog Clock Face
A traditional clock display using rotating hands to show time on a circular dial.

**Example:** Drawing hour and minute hands using `math.sin()` and `math.cos()` for position calculations.

#### Animation
The process of creating movement by rapidly updating display contents.

**Example:** Smoothly rotating second hands or creating blinking colons between hours and minutes.

#### Asynchronous Programming
A coding technique that allows multiple tasks to run concurrently without blocking each other.

**Example:** Using `uasyncio` to handle display updates while monitoring button presses.

#### Battery Backup
A power system that maintains time and settings when main power is disconnected.

#### Battery Drain Calculation
The process of measuring and estimating power consumption to determine battery life.

**Example:** Measuring current draw during different display update modes.

#### Battery Power
Portable electrical energy storage used to operate mobile timepieces.

**Example:** Calculating power consumption to estimate battery life.

#### Battery Tools
Instruments and methods for measuring power consumption and battery health.

**Example:** Using multimeters to measure current draw in different modes.

#### Blitting
A technique for rapidly copying rectangular portions of memory to update displays efficiently.

**Example:** Using framebuffer operations to reduce screen flicker.

#### Breadboard
A reusable plastic board with holes and internal connections for prototyping electronic circuits without soldering.

**Example:** Connecting LED displays and buttons to the Pico W using jumper wires on a breadboard.

#### Button Debouncing
A technique to prevent false button readings caused by mechanical switch contacts bouncing when pressed or released.

**Example:** `debounce_time = 100` in button configuration prevents multiple accidental triggers.

#### Button Input Handling
Software techniques for detecting and responding to button presses.

**Example:** Using interrupts and debouncing for reliable input detection.

#### Callback Function
A function passed as an argument to another function, which will be executed when a specific event occurs.

**Example:** `button_mode_irq` function that runs whenever the mode button is pressed.

#### Changing Fonts
The process of modifying text appearance by loading and applying different typefaces.

**Example:** Using the micropython-ufont library to load compact digital number styles.

#### Chimes
Musical or tone sequences played at specific intervals or times.

**Example:** Playing Westminster quarter-hour chimes using PWM audio output.

#### Chronograph
A timepiece with both timekeeping and stopwatch capabilities.

#### Color Animations
Dynamic changes in display colors to create visual effects or indicate status.

**Example:** Gradually shifting background colors throughout the day.

#### Color Conversion
The process of transforming between different color representation systems.

**Example:** Converting RGB colors to 16-bit format for TFT displays.

#### Color Conversion & Palettes
Methods for transforming between different color representations and managing limited color sets.

**Example:** Converting RGB colors to display-specific formats and creating custom color themes.

#### Color Depth
The number of bits used to represent colors in a display.

**Example:** Using 16 bits per pixel to show 65,536 different colors.

#### Computational Thinking

A structured problem-solving approach that uses computer science principles to formulate solutions by breaking down complex tasks into logical, repeatable steps that can be understood by both humans and machines **Example:** Breaking down the task of making a peanut butter sandwich into discrete steps: "open jar", "grasp knife", "scoop peanut butter".

The main concepts of computational thinking are:

##### Decomposition

The process of breaking a complex problem into smaller, more manageable parts **Example:** Dividing a clock program into separate functions for displaying time, handling buttons, and managing alarms.

##### Pattern Recognition

The ability to identify similarities, trends, and regularities in data or problems **Example:** Noticing that both analog and digital clocks need similar time calculation functions despite different display methods.

##### Abstraction

Focusing on essential details while filtering out irrelevant information to create a generalized solution **Example:** Creating a `display_time()` function that works with any type of display by hiding the specific implementation details.

##### Algorithmic Thinking

Creating a set of ordered steps that will solve a problem or achieve a goal **Example:** Developing a sequence of steps to synchronize a clock with an internet time server.

These concepts work together:

1.  First, decompose the problem
2.  Look for patterns in the smaller pieces
3.  Abstract away unnecessary details
4.  Create step-by-step solutions with algorithms

#### Concurrency

The ability to handle multiple tasks or events simultaneously in a program.

**Example:** Updating the display while checking for button presses.

#### Conditionals
Programming statements that perform different actions based on whether a condition is true or false.

**Example:** Switching between 12-hour and 24-hour time formats.

#### Connecting Speakers
Methods for attaching and controlling audio output devices to create sound effects and alarms.

**Example:** Wiring a speaker to a PWM-capable GPIO pin for generating tones for an alarm clock.

#### Console Output
Text-based information displayed in the development environment for debugging.

**Example:** `print("Current time:", hours, ":", minutes)`

#### Cuckoo Clock
A timepiece that marks specific hours with sound and optional mechanical movement.

**Example:** Playing bird sounds and activating a servo at the top of each hour.

#### Custom Font
A specialized set of character designs loaded into memory for display purposes.

**Example:** Loading compact number fonts using the micropython-ufont library.

#### Custom Segment Display
A specialized arrangement of LED segments for showing numbers or characters.

**Example:** Creating unique digit patterns using individual LED segments.

#### Digital to Analog Converter (DAC)

An integrated circuit that transforms digital data into a continuous analog voltage.
For example we can generate sound using a microcontroller to play an alarm sounds.

In our labs we use the MicroPython [I2S](#i2s) (Inter-IC Sound) protocol for generating
high-fidelity audio output. 

For example we have a lab that generates a sine wave to create audible tones through a speaker.

Specifically our class uses the [PCM5102A DAC](#pcm5102a-dac) Module to generate [Sound](./lessons/60-sound/index.md).

#### Date and Calendar Display

Showing current date information including day of week, month, and year.

**Example:** Formatting and displaying full date alongside time information.

#### datetime Objects
Programming structures that store date and time information together.

**Example:** Converting between timestamp integers and datetime format.

#### Daylight Saving Time
A seasonal time adjustment typically involving a one-hour shift.

**Example:** Automatically adjusting clock time based on DST rules.

#### Deep Sleep
A low-power mode that disables most system functions to conserve energy.

**Example:** Entering sleep mode when the watch face isn't being viewed.

#### Digital Display
An electronic output device that shows numbers, letters, or symbols using discrete segments or pixels.

**Example:** Four-digit seven-segment LED display showing hours and minutes.

#### Display Driver
Software that controls how information is shown on a specific type of display.

**Example:** Using the ST7735 driver for TFT LCD screens.

#### Display Technology Comparison
Analysis of different screen types' advantages and limitations.

**Example:** Evaluating power consumption versus update speed for various displays.

#### Double Buffering
A technique using two memory areas to prepare the next frame while displaying the current one.

**Example:** Creating smooth animations without visible drawing operations.

#### Drawing Arcs
Creating curved lines as portions of circles on displays.

**Example:** Drawing round clock face elements and decorative features.

#### Drawing Circles
Creating perfect circular shapes on displays.

**Example:** Drawing clock face outlines and hour markers.

#### Drawing Ellipses
Creating oval shapes on displays.

**Example:** Designing stylized clock faces and decorative elements.

#### Drawing Hands
Creating moving indicators for hours, minutes, and seconds.

**Example:** Using line drawing functions to show analog time.

#### Drawing Libraries
Software collections that provide functions for creating visual elements.

**Example:** Using built-in graphics functions to draw clock hands and numbers.

#### Drawing Lines
Creating straight line segments on displays.

**Example:** Drawing clock hand indicators and markings.

#### Drawing Numbers
Displaying numerical values on screen.

**Example:** Showing digital time values and markers.

#### Drawing Pixels
Setting individual display points for custom graphics.

**Example:** Creating fine details in watch face designs.

#### Drawing Polygons
Creating shapes with multiple straight sides.

**Example:** Making custom hour markers and decorative elements.

#### Drawing Primitives
Basic shapes and elements used to create more complex visual displays.

**Example:** Using lines and arcs to create clock hands.

#### Drawing Rectangles
Creating four-sided shapes with right angles.

**Example:** Drawing display borders and menu backgrounds.

#### Drawing Text
Displaying characters and strings on screen.

**Example:** Showing time, date, and menu options.

#### Drawing Tick Marks
Creating small indicators around a clock face.

**Example:** Marking hours and minutes on an analog display.

#### DS1307

#### DS3231
A high-precision real-time clock (RTC) integrated circuit with temperature compensation for accurate timekeeping.

**Example:** Using the DS3231 to maintain time accuracy within seconds per month.

#### E-Paper Display
A low-power screen technology that maintains its image without constant power.

**Example:** Using partial updates to change only modified portions of the display.

### Epoch

A fixed point in time chosen as a reference for measuring or calculating elapsed time in a computer system or data structure.

**Example:** The Unix epoch begins at midnight UTC on January 1, 1970, while the NTP epoch begins at midnight UTC on January 1, 1900.  The MicroPython epoch is often set to be January 1 2000.  On the Raspberry Pi Pico the epoch is January 1st, 2021.

#### Error Handling and Recovery

Techniques for detecting and recovering from timing errors, power issues, or communication failures.

**Example:** Implementing watchdog timers and automatic resynchronization after power loss.#### Event Handler
A function that responds to specific occurrences like button presses or timer updates.

**Example:** The `button_mode_irq` function handles mode button press events.

#### External RTC
A separate timekeeping chip that maintains accurate time independent of the main processor.

**Example:** Using a DS3231 module for precise timekeeping.

#### External Sensors
Additional hardware components that measure environmental conditions.

**Example:** Reading temperature and humidity for weather display.

#### Fast Redraw
Techniques for updating displays quickly to maintain smooth animation.

**Example:** Using hardware acceleration for screen updates.

#### Filesystem
A system for storing and organizing files on the microcontroller.

**Example:** Saving configuration settings and logs to internal storage.

#### Flicker Reduction
Methods to minimize visible display instability during updates.

**Example:** Using double buffering to prevent partial frame displays.

#### Framebuffer
A region of memory that holds the complete contents of a display.

**Example:** Modifying pixel data before updating the screen.

#### Functions
Reusable blocks of code that perform specific tasks.

**Example:** Creating a function to convert between 12-hour and 24-hour formats.

#### Generating Waveforms for Audio
Creating electrical signals for producing sounds and tones using digital-to-analog conversion or PWM.

**Example:** Synthesizing different frequencies for alarm sounds and hourly chimes.

#### Ghosting
A visual artifact where previous images remain partially visible on certain display types.

**Example:** Using display clearing techniques on e-paper screens.

#### GPIO Pin
General Purpose Input/Output connection on a microcontroller that can be programmed to send or receive electrical signals.

**Example:** Using GPIO pin 16 for the mode button: `mode_pin = Pin(16, Pin.IN, Pin.PULL_UP)`

#### Hardware Documentation
Technical specifications and usage instructions for electronic components.

**Example:** Consulting pinout diagrams for display connections.

#### I2C

A medium speed 4-wire communication protocol that allows multiple digital components to exchange data using just two wires plus power and ground.

I2C also has many different connectors that allow you to connect I2C components without the need for soldering.

#### I2C Sensors
Digital components that communicate using the I2C protocol to provide measurements.

**Example:** Reading temperature and humidity data for weather display.

#### I2S

The Inter-sound protocol we use to transmit sound data to components such as a [Digital to Analog Converter](#digital-to-analog-converter-dac).

Inter-IC Sound bus protocol is a synchronous serial protocol used to connect digital audio devices. 

I2S is a communication protocol that allows multiple digital 
components to exchange data using just two wires plus power and ground.

MicroPython 1.21 has builtin support for the I2S bus.

* [MicroPython I2S Documentation](https://docs.micropython.org/en/latest/library/machine.I2S.html)
* See also: [DAC](#digital-to-analog-converter-dac)
* See also: [PCM5102A DAC](#pcm5102a-dac)

#### Implementing Clock Themes
Creating customizable visual styles for clock displays, including colors, fonts, and layouts.

**Example:** Allowing users to switch between day/night themes or seasonal variations.

#### Incremental Drawing
Updating only the necessary portions of a display to improve efficiency.

**Example:** Refreshing only the seconds indicator rather than the full screen.

#### Interrupt
A signal that temporarily pauses normal program execution to handle important events.

**Example:** Responding immediately to button presses.

#### JSON
A text-based data format commonly used for exchanging information with web services.

**Example:** Parsing weather data from online APIs.

#### LED Clock Displays
A digital timepiece display using light-emitting diodes arranged in segments or matrices to show time information.

**Example:** Using a four-digit seven-segment LED display to show hours and minutes.

#### LED Matrix
An array of light-emitting diodes arranged in rows and columns that can display patterns, numbers, or text.

#### Libraries
Collections of pre-written code that provide useful functions and features.

**Example:** Using the `math` module for trigonometric calculations.

#### LiPo Charging
The process of safely recharging Lithium Polymer batteries.

**Example:** Implementing USB charging circuits with protection features.

#### LiPo Charging Circuit
Electronic system for safely charging Lithium Polymer batteries while protecting against overcharge and overdischarge.

**Example:** Implementing USB charging with voltage regulation and protection features.

#### Loading Drivers
Installing and initializing software that controls specific hardware components.

**Example:** Importing and configuring TFT display drivers.

#### localtime() Function
A MicroPython function that returns the current time as a tuple of values.

**Example:** `year, month, day, hour, minute, second = localtime()`

#### Logging
The practice of recording program events and data for debugging or analysis.

**Example:** Saving timing discrepancies to investigate accuracy issues.

#### Logging Time Data to an SD Card
Recording timestamped information to external storage for debugging or data collection.

**Example:** Saving temperature readings with timestamps every hour.

#### Loops
Programming structures that repeat code blocks multiple times.

**Example:** Continuously updating the display every second.

#### Math Module
A collection of mathematical functions for complex calculations.

**Example:** Using trigonometry to position clock hands.

#### math.sin() and math.cos()
Trigonometric functions used for calculating positions on circular displays.

**Example:** Computing analog clock hand coordinates.

#### Menu System
An interface allowing users to navigate options and settings.

**Example:** Creating hierarchical settings menus for watch configuration.

#### Menu Systems for Watch Settings
Hierarchical interface structures for configuring watch parameters and features.

**Example:** Creating nested menus for time, alarm, and display settings.

#### MicroPython
A streamlined version of Python programming language designed to run on microcontrollers and embedded systems.

#### MicroPython Drawing
Built-in functions for creating visual elements on displays.

**Example:** Using framebuf methods to draw shapes and text.

#### MicroPython network
A module providing Wi-Fi and network connectivity functions.

**Example:** Connecting to wireless networks for time synchronization.

#### MicroPython Syntax
The specific programming language rules and structure for MicroPython code.

**Example:** Using Python-style indentation for code blocks.

#### micropython-ufont Library
A specialized library for handling compact font rendering in MicroPython applications.

**Example:** Loading custom digit fonts optimized for small displays.

### NeoPixel

A programmable light-emitting diode that combines red, green, and blue elements in a single package with built-in control circuitry.

NeoPixel's strips only require three wires: GND, 5V and data.  It makes creating clock display patterns very easy.

**Example:** Creating a ring of 12 individually addressable RGB LEDs to mark hour positions on a clock face.

#### Network Time Protocol (NTP)
A method for synchronizing time over the internet.

**Example:** Updating the RTC from online time servers.

#### OLED Display
A thin, bright display that uses organic light-emitting diodes to show text and graphics without a backlight.

#### Partial Refresh
Updating only changed portions of a display to improve efficiency.

**Example:** Refreshing only the seconds digits each update.

#### Partial Screen Updates
Techniques for refreshing only the changed portions of a display to improve efficiency and reduce flicker.

**Example:** Updating only the seconds digits while leaving hours and minutes static.

#### Pedometer
A feature that counts steps using motion sensor data.

**Example:** Calculating daily step counts from accelerometer readings.

#### PCM5102A DAC

An audio [Digital to Analog](#digital-to-analog-converter-dac) chip we use in
our clock projects.

* See Also: [PCM5102A Data Sheet](https://www.ti.com/product/PCM5102A)

#### Pin
A metal connector on electronic components that carries electrical signals or power.

#### Power Management
Techniques for minimizing and controlling energy consumption.

**Example:** Using sleep modes and efficient display updates.

#### Power Monitoring
Methods for measuring and tracking power consumption in battery-operated devices.

**Example:** Logging battery voltage and current draw to optimize device lifetime.

#### Project-Based Learning

A teaching methodology in which students actively engage in exploring real-world problems and challenges through extended inquiry, collaboration, and the creation of tangible products or presentations. 

Project-Based Learning (PBL) emphasizes student-centered learning, critical thinking, and application of knowledge in authentic contexts.  We focus on what topics are most interesting to students and what they are curious about.  By doing PBL students also learn soft-skills needed to work in teams.

**Example:** A high school coding class implements project-based learning by having students design and build a wall clock that adjusts the time using WiFi.  They do this by applying principles of microcontrollers, displays and wireless. Students research, prototype, test, and refine their designs before presenting their findings to the class.

#### Pull-up Resistor
An electronic component that ensures a consistent voltage level on input pins when buttons or switches are not pressed.

**Example:** Using internal pull-up resistors with `Pin.PULL_UP` for button inputs.

#### PWM
Pulse Width Modulation - a technique for creating varying levels of brightness or speed by rapidly switching a signal on and off.

#### PWM Audio
Using Pulse Width Modulation to generate sounds and tones.

**Example:** Creating alarm beeps and hourly chimes.

#### Raspberry Pi Pico W
A small, low-cost microcontroller board with built-in wireless capabilities, designed for learning and DIY projects.

#### Real-Time Clock (RTC)
A specialized chip or circuit that keeps accurate time even when main power is removed.

**Example:** Using the RTC module to maintain accurate time: `rtc = RTC()`

#### Real-time Clock (RTC) Overview
A comprehensive explanation of how real-time clock modules maintain accurate time, including initialization, synchronization, and backup power considerations.

**Example:** Understanding how the RTC maintains time even when main power is disconnected.

#### Rotary Encoder
A input device that converts rotational movement into digital signals.

**Example:** Using encoder rotation to adjust time settings.

#### Screen Tearing Prevention
Techniques to avoid visual artifacts caused by updating display content while it's being refreshed.

**Example:** Using vsync or double buffering to ensure clean display updates.

#### Screen Update
The process of refreshing display contents to show new information.

**Example:** Efficiently updating only changed portions of the time display.

#### Screen Via SPI
High-speed serial communication method for updating displays.

**Example:** Sending framebuffer data to TFT screens efficiently.

#### Servo Motor
An actuator that can rotate to precise positions.

**Example:** Moving physical clock hands on a hybrid display.

#### Setting System Clock
Configuring the internal timekeeping system with accurate time.

**Example:** Updating RTC time from an external time source.

#### Setting Time with Buttons
Interface design and implementation for adjusting clock time using physical buttons.

**Example:** Using mode, increment, and decrement buttons to set hours and minutes.

#### Setting Up I²C Communication
Configuring and using the Inter-Integrated Circuit (I²C) protocol for connecting multiple devices.

**Example:** Initializing I²C bus for communicating with RTC and sensor modules.

#### Setting Up Wi‑Fi on the Pico W
Process of configuring wireless network connectivity on the Raspberry Pi Pico W microcontroller.

**Example:** Connecting to a local network using SSID and password credentials.

#### Seven-Segment Display
A display made of seven LED segments plus a decimal point that can show numbers and some letters.

**Example:** Creating patterns for digits using segments 'a' through 'g': `SEGMENTS = {'a': 4, 'b': 3, 'c': 2, 'd': 7, 'e': 6, 'f': 5, 'g': 1}`

#### Shift Register
An integrated circuit that converts serial data into parallel outputs, useful for controlling multiple LEDs with fewer pins.

**Example:** Using SR74HC595 shift register to control display segments.

#### Sleep Mode
A low-power state that reduces energy consumption.

**Example:** Entering deep sleep between display updates.

#### Sleep Scheduling
Managing when the device enters and exits low-power states.

**Example:** Programming wake-up times for hourly updates.

#### Smartwatch Displays
Advanced display modules designed specifically for wearable devices, optimizing size, power consumption, and readability.

**Example:** Using a small, high-resolution display with automatic brightness adjustment.

#### Sound Encoding
Methods for storing and playing audio data for alarms and notifications.

**Example:** Converting WAV files to suitable format for playback.

#### SPI
Serial Peripheral Interface - a fast communication protocol for connecting digital components using multiple signal lines.

#### SPI Interface
A high-speed serial communication protocol for connecting displays and sensors.

**Example:** Transferring data to TFT displays efficiently.

#### State Machine
A programming concept where a system can be in one of several defined states, with specific rules for transitioning between them.

**Example:** Clock modes including "run", "set hour", "set minute", and "set AM/PM".

#### Step Counting (Pedometer)
Using motion sensors to detect and count walking steps for fitness tracking.

**Example:** Processing accelerometer data to identify step patterns and maintain daily count.

#### Stopwatch
A timing device that measures elapsed time from a starting point, typically with precision to fractions of a second.

**Example:** Implementing start, stop, and lap timing functions with millisecond accuracy.

#### Synchronizing Time from the PC
The process of setting a microcontroller's clock using the connected computer's time.

**Example:** Using Thonny IDE to automatically update the Pico's RTC when uploading code.

#### Temperature and Humidity
Integration of environmental sensors to display current conditions alongside time.

**Example:** Reading DHT22 sensor data to show temperature and humidity with clock display.

#### Temperature Sensor
A component that measures ambient temperature.

**Example:** Displaying current temperature alongside time.

#### TFT Displays
Thin-film-transistor liquid crystal displays for showing color graphics.

**Example:** Using ST7735 or ILI9341 displays for watch faces.

#### Thonny IDE
An integrated development environment optimized for MicroPython programming.

**Example:** Using Thonny to upload code and debug timing issues.

#### Time Module
MicroPython library for handling time-related operations.

**Example:** Using scheduling functions for regular updates.

#### Time Synchronization
Process of updating device time from an accurate external source.

**Example:** Getting current time from network time servers.

#### Time Zone
A region that observes a uniform standard time.

**Example:** Converting between local time and UTC.

#### Time-Based Tasks with uasyncio
Scheduling and managing time-dependent operations using MicroPython's asynchronous I/O framework.

**Example:** Updating multiple display elements at different intervals without blocking.

#### Timer
A system resource that generates regular time-based events.

**Example:** Creating precise one-second update intervals.

#### Timer-Based Events
Actions triggered by internal timing mechanisms.

**Example:** Updating display elements at specific intervals.

#### Ultra-Low Power
Operating modes and techniques that minimize energy consumption.

**Example:** Using sleep modes and efficient screen updates.

#### USB Power
A 5-volt power source available through Universal Serial Bus connections, commonly used for powering small electronic projects.

#### Using 16 Bits to Represent Color
A color depth specification that allocates 16 bits per pixel, typically with 5 bits for red, 6 for green, and 5 for blue (RGB565 format).

**Example:** Converting RGB colors to 16-bit format for efficient storage and display.

#### UTC
Coordinated Universal Time, the primary time standard for global time coordination.

**Example:** Converting local time to UTC for synchronization.

#### Wake on Alarm
Feature that activates the device from sleep mode at specific times.

**Example:** Waking the display for scheduled notifications.

#### Watch Face Design
Principles and techniques for creating visually appealing and functional clock displays.

**Example:** Balancing aesthetics and readability in analog and digital layouts.

#### Watchdog Timer
A hardware feature that resets the system if the program stops responding.

**Example:** Ensuring reliability in long-running clock applications.

#### Weather Updates
Real-time environmental data obtained through internet services.

**Example:** Displaying current conditions alongside time.

#### Web Services
Online resources that provide data or functionality through standard internet protocols.

**Example:** Fetching current time from an internet time server for clock synchronization.

#### Wi-Fi Module
Hardware that enables wireless network connectivity.

**Example:** Connecting to the internet for time synchronization.

#### Wi‑Fi–Based Weather Updates
Retrieving and displaying current weather conditions using wireless internet connectivity.

**Example:** Fetching temperature, humidity, and forecast data from online weather services.

#### World Clock
A timepiece that displays times for multiple time zones simultaneously.

**Example:** Showing local time alongside other major cities' times.

