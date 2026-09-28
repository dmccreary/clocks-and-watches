---
title: Electronics Fundamentals and Breadboard Wiring
description: The electronics behind every clock: voltage, current, Ohm's Law, LEDs, resistors, breadboards, and safe wiring.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:28:05
version: 1.10
---

# Electronics Fundamentals and Breadboard Wiring

## Summary

Students learn how voltage, current, and resistance relate and how to size a resistor for an LED. They practice breadboard wiring, reading circuit diagrams, and using a multimeter. After this chapter they can wire a safe, correct circuit from a diagram.

## Concepts Covered

This chapter covers the following 24 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Breadboard | 61 |
| Ohms Law | 647 |
| Power Supply | 62 |
| Voltage Levels | 284 |
| Ground Connection | 1 |
| Capacitors | 2 |
| Resistor Values | 8 |
| Wire Color Coding | 1 |
| Connector Types | 18 |
| Clock Architecture | 47 |
| 3.3V vs 5V Logic | 1 |
| CR2032 Coin Cell | 2 |
| Current Limiting | 5 |
| Voltage Divider | 2 |
| LED Basics | 263 |
| Multimeter Usage | 5 |
| Jumper Wires | 16 |
| Header Pins | 1 |
| Voltage Regulator | 2 |
| Breadboard Wiring | 11 |
| Soldering Skills | 4 |
| LED Current Draw | 4 |
| Circuit Diagrams | 3 |
| Acrylic Mounting | 3 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)

---

!!! mascot-welcome "Wire Up With Confidence"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter you'll be able to look at a circuit diagram, wire it on a breadboard, and know it's safe before you plug in power. That's the skill that turns a pile of parts into a working clock. Let's make time tick!

## Electronics for Clock Builders

In Chapter 1 you learned that every clock senses, thinks, and acts. This chapter covers the electrical side of that loop: how power reaches each part, how to keep parts from burning out, and how to connect everything without soldering. You do not need any prior electronics experience. Each idea is explained in plain words first, then practiced with a small worked example.

## Clock Architecture

**Clock architecture** is the big-picture plan showing which parts a clock needs and how they connect. Think of it as the floor plan of a house: it shows the rooms and doors before anyone picks paint colors.

Every clock in this book has the same five blocks:

- **Power supply:** provides the electricity everything else needs.
- **Microcontroller:** runs the program (the Raspberry Pi Pico).
- **Time source:** tells the program what time it is (the Pico's internal clock, a real-time clock chip, or the internet).
- **Display:** an actuator that shows the time.
- **Input:** sensors such as buttons that let a person set the time.

Different projects swap parts inside these blocks. A simple LED clock uses a four-digit display and no time chip. A smartwatch adds a battery, a round screen, and WiFi. The blocks stay the same, and that is what makes them a useful planning tool. The [Timekeeping Architecture lesson](../../lessons/01-timekeeping-architecture.md) shows how the blocks map onto real kits.

#### Diagram: Clock Architecture Explorer

<details markdown="1">
<summary>Clock Architecture Explorer</summary>
Type: interactive diagram
**sim-id:** clock-architecture-explorer<br/>
**Library:** vis-network<br/>
**Status:** Specified

**Learning objective:** Students will *understand* the five blocks of a clock and *compare* how three different clocks fill those blocks (Bloom: Understanding).

**Layout:** Five boxes (Power Supply, Microcontroller, Time Source, Display, Input) connected by arrows. Power Supply has arrows to every other box (labeled "power"); Time Source and Input point to the Microcontroller (labeled "data in"); the Microcontroller points to Display ("data out").

**Interactions:**

- A dropdown "Choose a clock" offers *4-digit LED clock*, *OLED clock with RTC*, and *Smartwatch*. Selecting one relabels each box with the actual part (for example, Time Source becomes "DS3231 RTC").
- Clicking a box opens an infobox with one sentence on its job and a link to the chapter that covers it.

**Responsive design:** The canvas fills the container width at 400 px tall and calls `network.fit()` on resize.

Implementation: vis-network with a JavaScript object mapping each clock to its labels.
</details>

## Voltage Levels

**Voltage** is the electrical "push" that moves charge through a circuit, measured in **volts (V)**. A good mental picture is water pressure in a pipe: higher pressure pushes more water through. Voltage does not flow; it is the *difference* in push between two points.

A **voltage level** is the specific voltage a part uses to represent a signal or to run. You will meet three levels again and again in this book:

| Level | Where you find it | What it is for |
|-------|-------------------|----------------|
| 0 V | Ground pins | The reference point everything is measured from |
| 3.3 V | Pico GPIO pins and the 3V3 pin | Signals and power for most chips |
| 5 V | USB power (VBUS pin) | Power for LEDs, some displays, NeoPixels |

A digital signal uses two voltage levels to mean two things. On the Pico, about 3.3 V means "on" (a logical 1) and about 0 V means "off" (a logical 0). This is how your program tells an LED to light or reads whether a button is pressed.

!!! mascot-thinking "Pressure, Not Flow"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Voltage is like water pressure: it exists even when nothing is flowing. A battery sitting on a table still has 3 V across it. Current only flows when you give it a path.

## Ground Connection

A **ground connection** is the shared 0 V reference that every part in a circuit connects to. It is also the path electricity uses to return to the power source. Voltage is always a measurement *between two points*, and ground is the point everyone agrees to measure from.

The most common wiring mistake in this book is forgetting the ground wire. If a display has power but no ground, it acts as if it were broken. Every part in your clock needs two things: a power connection and a ground connection to the same ground as the Pico. The Pico has eight ground pins, so you will always find one nearby.

## Ohm's Law

**Ohm's Law** describes how voltage, current, and resistance are related. It is the most useful equation in electronics, and you will use it in almost every lab.

Two more terms first. **Current** is the amount of electric charge flowing past a point each second, measured in **amperes (A)**. Small circuits use **milliamps (mA)**, where 1 A = 1,000 mA. **Resistance** is how much a part opposes the flow of current, measured in **ohms (Ω)**. In the water picture, current is how much water flows and resistance is how narrow the pipe is.

Ohm's Law says the voltage across a part equals the current through it times its resistance:

\[ V = I \times R \]

Rearranged, it lets you find whichever value you are missing:

\[ I = \frac{V}{R} \qquad R = \frac{V}{I} \]

**Worked example.** A 3.3 V supply pushes current through a 330 Ω resistor. How much current flows?

\[ I = \frac{3.3\ \text{V}}{330\ \Omega} = 0.010\ \text{A} = 10\ \text{mA} \]

Now double the resistor to 660 Ω. The current halves to 5 mA. More resistance means less current, and less resistance means more. That single idea explains why an LED with no resistor is in trouble.

Electric **power** is how fast energy is used, measured in **watts (W)**. It is \( P = V \times I \). The 10 mA example uses \( 3.3 \times 0.010 = 0.033 \) W, or 33 milliwatts.

!!! mascot-encourage "Math Anxiety Check"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Three letters and one equation is all Ohm's Law is. If the rearranging feels shaky, cover the letter you want to find in the triangle V over I times R and read off the rest. You've solved harder puzzles than this.

#### Diagram: Ohm's Law Explorer

<details markdown="1">
<summary>Ohm's Law Explorer</summary>
Type: MicroSim
**sim-id:** ohms-law-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* \( V = IR \) by changing two values and predicting the third (Bloom: Applying).

**Visual elements:** A simple loop circuit (battery, resistor, wire) drawn on a 700 x 400 canvas. Animated dots travel around the loop; their speed and count represent current. The resistor changes width to show resistance.

**Controls:**

- Slider "Voltage (V)": 0 to 5 V, default 3.3, step 0.1.
- Slider "Resistance (Ω)": 10 to 1000, default 330.
- Readouts for current in mA and power in mW, updating live.
- A "Quiz me" button hides the current readout, picks new V and R, and asks the student to type the current, then reveals the answer.

**Responsive design:** The circuit scales to container width and sliders stack under the canvas below 600 px.

Implementation: p5.js with a dot-particle system whose speed is proportional to the computed current.
</details>

## Power Supply

A **power supply** is any source that provides the voltage and current a circuit needs. For your clocks there are three common choices:

- **USB from a computer or wall adapter:** 5 V, easy, and what you will use in most labs.
- **A battery:** a lithium polymer (LiPo) pack for a portable watch, or AA batteries for a wall clock.
- **A coin cell:** a small 3 V battery used only to keep a real-time clock alive.

Two numbers describe a supply: its voltage and how much current it can deliver. A USB port on a computer can supply about 500 mA, which is far more than a clock needs. Problems appear when a load asks for more current than the supply can give. LED strips are the usual culprit, and we will size them carefully in a later chapter.

On the Pico, USB power arrives on the **VBUS** pin at 5 V. From there the board makes the 3.3 V that the chip uses. You can also feed the board through the **VSYS** pin from a battery.

| Pico pin | Voltage | Purpose |
|----------|---------|---------|
| VBUS | 5 V (from USB) | Power 5 V parts |
| VSYS | 1.8 to 5.5 V in | Main power input (battery) |
| 3V3(OUT) | 3.3 V out | Power 3.3 V parts |
| GND | 0 V | Ground return |

## Voltage Regulator

A **voltage regulator** is a circuit that takes an input voltage and produces a steady, lower (or sometimes higher) output voltage. The Pico needs a smooth 3.3 V, but USB gives 5 V and a battery might give 3.7 V that slowly falls as it drains. The regulator hides those changes.

There are two types. A **linear regulator** simply burns off the extra voltage as heat. It is simple but wasteful: dropping 5 V to 3.3 V at 100 mA wastes \( (5 - 3.3) \times 0.1 = 0.17 \) W. A **switching regulator** rapidly turns current on and off to convert voltage efficiently, wasting little. The Pico uses a switching regulator on the board, which is why it runs well from a battery.

## 3.3 V vs 5 V Logic

**Logic level** is the voltage a chip uses for its "on" signal. Some parts use 3.3 V logic and others use 5 V. The Pico uses **3.3 V** logic.

The rule is simple and important: **the Pico's GPIO pins are not 5 V tolerant.** Connecting a 5 V signal directly to one can damage the chip.

!!! mascot-warning "Watch Your Voltage"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A part that outputs a 5 V signal, wired straight into a Pico pin, can permanently damage the pin. Check each part's datasheet for its logic level; if it says 5 V, use a voltage divider or a level shifter between the part and the Pico.

Signals going *from* the Pico *to* a 5 V part usually work without help, because most 5 V chips read 3.3 V as "on." It is the reverse direction that is dangerous.

| Direction | Safe? | Fix if not |
|-----------|-------|------------|
| Pico (3.3 V) → 3.3 V part | Yes | None |
| Pico (3.3 V) → 5 V part | Usually | Check the part's minimum "on" voltage |
| 5 V part → Pico | **No** | Voltage divider or level shifter |

## Voltage Divider

A **voltage divider** uses two resistors in series to produce a smaller voltage from a bigger one. The output is taken from the point between the resistors:

\[ V_{out} = V_{in} \times \frac{R_2}{R_1 + R_2} \]

Here \( R_1 \) is the resistor connected to the input voltage and \( R_2 \) is the one connected to ground.

**Worked example.** Shrink a 5 V signal to a safe level for the Pico using \( R_1 = 1\ \text{k}\Omega \) and \( R_2 = 2\ \text{k}\Omega \):

\[ V_{out} = 5 \times \frac{2000}{1000 + 2000} = 3.33\ \text{V} \]

That is safe for a Pico pin. Voltage dividers also appear inside light sensors, where one of the two resistors changes with brightness and the middle voltage tells the Pico how bright the room is.

#### Diagram: Voltage Divider Lab

<details markdown="1">
<summary>Voltage Divider Lab</summary>
Type: MicroSim
**sim-id:** voltage-divider-lab<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* the divider formula and *evaluate* whether an output is safe for a 3.3 V input (Bloom: Evaluating).

**Visual elements:** Two resistors stacked between a top rail (Vin) and ground, with a probe wire at the midpoint and a voltmeter bar graph showing Vout. A colored zone on the bar graph turns red above 3.3 V.

**Controls:** Sliders for Vin (0 to 5 V), R1 and R2 (100 Ω to 10 kΩ, log scale). A label reads "Safe for Pico" or "Too high!" based on Vout.

**Responsive design:** Layout is a single column under 600 px.

Implementation: p5.js drawing plus a computed readout.
</details>

## Capacitors

A **capacitor** is a small part that stores electric charge and releases it quickly, like a tiny rechargeable battery that fills and empties in a fraction of a second. It is measured in **farads (F)**; practical values are microfarads (µF) and nanofarads (nF).

Capacitors do two jobs in clock circuits. First, they smooth out power: when a chip suddenly needs a burst of current, the nearby capacitor supplies it so the supply voltage does not dip. A 0.1 µF capacitor placed close to a chip's power pin is standard practice. Second, they filter noise. Some capacitors, called electrolytic capacitors, are **polarized**, so the marked leg must go to the more negative side.

## Resistor Values

A **resistor** is a part that limits current by adding a known resistance. Resistors are tiny, so instead of printing numbers they wear colored bands. To read a four-band resistor, take the first two bands as digits and the third as a multiplier.

| Color | Digit | Multiplier |
|-------|-------|------------|
| Black | 0 | ×1 |
| Brown | 1 | ×10 |
| Red | 2 | ×100 |
| Orange | 3 | ×1,000 |
| Yellow | 4 | ×10,000 |
| Green | 5 | ×100,000 |
| Blue | 6 | ×1,000,000 |
| Violet | 7 | |
| Gray | 8 | |
| White | 9 | |

The fourth band is tolerance: gold means the real value is within ±5% of the marked value.

**Worked example.** Orange, orange, brown, gold reads as 3, 3, then ×10, so \( 33 \times 10 = 330\ \Omega \) with ±5% tolerance. Brown, black, orange, gold reads 1, 0, ×1,000, so 10 kΩ.

Resistors are sold only in standard values, such as 100, 150, 220, 330, 470, 680, and 1,000 Ω. When a calculation gives an odd answer, you pick the next standard value up, since a bit more resistance is safer than a bit less.

#### Diagram: Resistor Color Code Decoder

<details markdown="1">
<summary>Resistor Color Code Decoder</summary>
Type: MicroSim
**sim-id:** resistor-color-decoder<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *recall* the color code and *apply* it to read resistor values (Bloom: Remembering, Applying).

**Visual elements:** A large four-band resistor drawing. Clicking a band cycles its color. A readout shows the value, for example "330 Ω ±5%".

**Controls:** A "Random resistor" button, an "Enter value" mode where the student types an ohm value and must set the bands, and a score counter.

**Responsive design:** The resistor scales to container width.

Implementation: p5.js with a lookup table of band colors.
</details>

## Current Limiting

**Current limiting** means adding resistance so that the current through a part stays at a safe level. Many parts, especially LEDs, will draw as much current as they can and destroy themselves. A resistor placed in series with the part sets the current, using Ohm's Law on the *extra* voltage the part does not use.

The resistor formula for an LED is:

\[ R = \frac{V_{supply} - V_{LED}}{I_{LED}} \]

**Worked example.** A red LED drops about 2.0 V and should run at 10 mA from a 3.3 V pin:

\[ R = \frac{3.3 - 2.0}{0.010} = 130\ \Omega \]

The nearest standard value at or above that is 150 Ω, giving \( (3.3 - 2.0)/150 \approx 8.7 \) mA. Many builders use 220 Ω or 330 Ω to be extra safe; the LED is just a little dimmer.

!!! mascot-tip "Can't Decide? Go Bigger"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If you are unsure which resistor to use with an LED, pick 330 Ω. It is safe for nearly any LED on a 3.3 V pin, and the LED will still be clearly visible.

## LED Basics

An **LED** (light-emitting diode) is a small component that gives off light when current flows through it in the correct direction. A **diode** lets current pass one way only, so an LED has two legs with fixed roles: the **anode** (positive, usually the longer leg) and the **cathode** (negative, usually the shorter leg, next to a flat spot on the plastic case).

An LED has a **forward voltage**: the fixed voltage it drops when it is on. Unlike a resistor, its voltage does not rise with current, which is why the current is not self-limiting. Forward voltage depends on color.

| LED color | Typical forward voltage |
|-----------|------------------------|
| Red | 1.8 to 2.0 V |
| Yellow, green | 2.0 to 2.2 V |
| Blue, white | 3.0 to 3.3 V |

Blue and white LEDs are close to the Pico's 3.3 V, so there is little "extra" voltage left, and a small resistor is enough.

!!! mascot-warning "LEDs Need a Resistor"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Connecting an LED straight across a power source lets far too much current flow, and the LED can burn out in an instant. It happens because an LED's voltage stays nearly fixed no matter how much current flows. Always put a resistor in series, and if an LED is dead, replace it and add the resistor first.

Here is a program that lights an LED on pin GP15 and blinks it. The wiring is: GP15 goes to a 330 Ω resistor, the resistor goes to the LED's anode (long leg), and the LED's cathode (short leg) goes to a GND pin. The code sets pin 15 as an output, and each `value()` call sets it to 1 (3.3 V, on) or 0 (0 V, off).

```python
NAME = "02-led-resistor.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

led = Pin(15, Pin.OUT)   # GP15 drives the LED through a resistor

while True:
    led.value(1)         # 3.3 V: LED on
    sleep(0.5)
    led.value(0)         # 0 V: LED off
    sleep(0.5)
```

## LED Current Draw

**LED current draw** is the amount of current an LED, or a group of them, takes from the supply. It matters because every pin and every supply has a limit. The RP2040 can drive only a few milliamps per pin by default, and the whole chip has a total limit, so a single pin should never drive a large load directly.

Add up current when you use many LEDs. A seven-segment digit with all 7 segments on at 8 mA each needs about \( 7 \times 8 = 56 \) mA. Four digits lit at once would need about 224 mA. That is why displays like the TM1637 have their own chip to handle the current instead of connecting segments straight to Pico pins.

| Load | Approximate current |
|------|--------------------|
| One indicator LED | 5 to 10 mA |
| One 7-segment digit (all segments) | 50 to 60 mA |
| One NeoPixel at full white | up to 60 mA |

A strip of 30 NeoPixels at full white could ask for 1.8 A. That is more than a USB port provides, which is why brightness limits matter.

#### Diagram: LED Resistor Calculator

<details markdown="1">
<summary>LED Resistor Calculator</summary>
Type: MicroSim
**sim-id:** led-resistor-calculator<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* the current-limiting formula and *analyze* how resistor choice changes brightness and current (Bloom: Applying, Analyzing).

**Visual elements:** An LED circuit with battery, resistor, and LED. The LED glows more brightly with higher current and turns red with a warning icon above the safe maximum (20 mA).

**Controls:** Dropdown for LED color (sets forward voltage), slider for supply voltage (3.3 or 5 V), and a resistor selector limited to standard values. A readout shows current in mA and the calculated resistor needed.

**Responsive design:** The circuit scales to canvas width.

Implementation: p5.js with brightness mapped to current.
</details>

## Breadboard

A **breadboard** is a plastic board with rows of small connected holes that lets you build circuits without soldering. You push part legs and wires into the holes, and metal strips underneath connect certain holes together. Breadboards make it easy to change your mind, so they are the standard tool for learning.

Understanding what is connected to what is the whole skill. A breadboard has three regions:

- **Terminal strips:** the main area. Each row of five holes (columns a to e, or f to j) is connected as one strip.
- **Center gap:** a channel that splits the two halves so chips can straddle it without shorting their pins.
- **Power rails:** the long lines of holes along the edges. Each rail runs the full length, and you normally use one for 3.3 V and one for ground.

The half-size breadboards in the Large OLED Kit have about 400 connection points, plenty for a clock.

#### Diagram: Breadboard Connectivity Explorer

<details markdown="1">
<summary>Breadboard Connectivity Explorer</summary>
Type: interactive infographic
**sim-id:** breadboard-connectivity<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* which holes are electrically connected on a breadboard (Bloom: Analyzing).

**Visual elements:** A top-down half-size breadboard with 30 columns, two center halves, and power rails. Hidden metal strips are shown as faint lines when "X-ray" is on.

**Interactions:**

- Hovering a hole highlights every hole it is connected to.
- The student can click to place a jumper between two holes; the sim reports whether they are now connected.
- A "Challenge" mode shows two holes and asks "Connected: yes or no?" and scores the answers.

**Responsive design:** The board scales to container width and scrolls horizontally below 500 px if needed.

Implementation: p5.js grid with a connectivity map for each strip and rail.
</details>

## Breadboard Wiring

**Breadboard wiring** is the practice of placing parts and wires on a breadboard so the circuit matches your plan. A neat build is far easier to debug than a tangle.

Follow these steps for every build:

1. Connect the Pico's GND pin to the ground rail and its 3V3 pin to the power rail before anything else.
2. Place parts in rows so each leg lands in a *different* strip (two legs in the same strip are shorted together).
3. Use short jumper wires and keep them flat against the board.
4. Check each connection against your diagram before applying power.

**Worked example.** To wire the LED circuit above: put the resistor across the center of the board with one leg in row 10 and another in row 14. Put the LED's anode in row 14 and its cathode in row 15 (a different strip). A jumper from row 15 to the ground rail closes the loop, and a jumper from GP15 to row 10 completes the connection.

!!! mascot-tip "Debug With Your Eyes First"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Most "dead" circuits have one loose or misplaced wire. Before changing any code, touch each wire and trace the path from power to ground with a fingertip.

## Jumper Wires

**Jumper wires** are short insulated wires with connectors on the ends that link points on a breadboard or between boards. They come in three types depending on the ends.

| Type | Ends | Typical use |
|------|------|-------------|
| Male to male | Pin, pin | Breadboard to breadboard |
| Male to female | Pin, socket | Breadboard to a board's header pins |
| Female to female | Socket, socket | Board to board |

Jumper wires are cheap and fail often, usually because the crimp inside breaks. If a circuit works when you hold the wire and fails when you let go, replace the wire.

## Wire Color Coding

**Wire color coding** is the habit of using specific colors for specific jobs so a circuit can be understood at a glance. There is no law, but nearly everyone follows the same conventions.

| Color | Meaning |
|-------|---------|
| Red | Power (3.3 V or 5 V) |
| Black | Ground |
| Other colors (yellow, green, blue) | Signals such as data or clock lines |

The display cable harness in the setup section uses this scheme so that ribbon cables can be plugged in the right way around. See [Display Cable Harness](../../setup/03-display-cable-harness.md) for an example.

## Header Pins

**Header pins** are rows of metal pins spaced 2.54 mm (0.1 inch) apart that give a board a way to plug into breadboards and sockets. That spacing matches a breadboard's holes exactly. The Pico is often sold with header pins soldered on so it plugs right into a breadboard, and the pins are numbered along each edge.

## Connector Types

A **connector** is a part that lets you join and separate two circuits without soldering. Beyond header pins and jumper wires you will see a few others.

| Connector | Where it appears |
|-----------|------------------|
| Dupont (jumper) | Breadboard wires and display cables |
| Micro-USB | Powering and programming the Pico |
| JST | Small battery and sensor connectors |
| Screw terminal | Larger wires and power input |

Always check the orientation of a connector before pushing it in. Many JST connectors and battery plugs are **not** protected against being reversed, and reversing one can destroy a chip.

## Circuit Diagrams

A **circuit diagram** (also called a **schematic**) is a drawing that uses standard symbols to show how parts are connected. Unlike a photograph of a breadboard, a schematic shows *what* is connected and ignores where parts sit physically. This makes it far easier to read.

The symbols you will see most often:

| Part | Symbol idea |
|------|-------------|
| Wire | Straight line; a dot marks a junction |
| Resistor | Zigzag line or a small rectangle |
| LED | Triangle pointing at a bar, with two arrows leaving |
| Battery | Long and short parallel lines |
| Ground | Three shrinking horizontal lines |

To read a schematic, start at the power source and follow the wire through each part until you reach ground.

#### Diagram: Schematic Symbol Matcher

<details markdown="1">
<summary>Schematic Symbol Matcher</summary>
Type: MicroSim
**sim-id:** schematic-symbol-matcher<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *recall* schematic symbols and *interpret* a simple circuit diagram (Bloom: Remembering, Understanding).

**Visual elements:** A schematic of the LED circuit with GP15, resistor, LED, and ground. Each symbol has a hidden label.

**Interactions:** Clicking a symbol reveals its name and photo; a "Match" mode shows a part photo and asks the student to click its symbol; and a "Trace the current" button animates a dot from GP15 through each part to ground.

**Responsive design:** Diagram scales to container width.

Implementation: p5.js with SVG-like drawing helpers.
</details>

## Multimeter Usage

A **multimeter** is a handheld tool that measures voltage, resistance, and continuity, and it is the best way to check a circuit. Turn the dial to the setting you need, then touch the two probes (red and black) to two points.

Three measurements are all you need:

- **DC voltage (V with a straight line):** touch the probes across a part, red on the more positive side. Use it to confirm a pin really has 3.3 V.
- **Continuity (a sound-wave symbol):** the meter beeps when two points are connected. Use it to check wires and solder joints with the power **off**.
- **Resistance (Ω):** identify an unknown resistor. Measure it out of the circuit and with the power off.

**Worked example.** A display does not light up. Set the meter to DC voltage and measure between the display's VCC and GND pins. Reading 0 V means power never arrived, so check the wire back to the Pico. Reading 3.3 V means power is fine, so the fault is somewhere else, such as a data wire.

## Soldering Skills

**Soldering** is joining metal parts by melting a metal alloy (solder) onto them so that it hardens into a strong electrical connection. You will solder header pins onto boards and wires onto connectors, and later NeoPixel strips.

A good joint takes four steps:

1. Heat both the pad and the pin with the iron tip for about two seconds.
2. Touch the solder to the joint (not the iron) and let it flow.
3. Remove the solder, then the iron, and do not move the joint while it cools.
4. Inspect: a good joint is shiny and shaped like a small cone.

A dull, lumpy joint is a **cold joint** and may conduct poorly. Reheat it and add a little fresh solder.

!!! note "Soldering Safety"
    The iron reaches about 350 °C, hot enough to cause a serious burn. Wear safety glasses, work in a ventilated area, always return the iron to its stand, and wash your hands afterward, especially if you use leaded solder.

## Acrylic Mounting

**Acrylic mounting** means fixing your breadboard and Pico onto a flat sheet of acrylic plastic to make a sturdy, portable clock. Acrylic is easy to cut and drill, it does not conduct electricity, and it looks clean.

A typical mount uses a base plate drilled to match the Pico's mounting holes. Small screws (M2 size) and nylon standoffs hold the board a few millimeters above the plate so solder joints do not touch it. The breadboard has an adhesive backing that sticks directly to the acrylic. Keep cables tidy with a couple of cable ties.

## Putting It Together

You now have the electrical toolkit for every lab that follows.

| If you need to... | Use... |
|-------------------|--------|
| Find current, voltage, or resistance | Ohm's Law |
| Protect an LED | A series resistor from the current-limiting formula |
| Connect a 5 V signal to the Pico | Voltage divider or level shifter |
| Build without soldering | Breadboard and jumper wires |
| Check your work | Circuit diagram and multimeter |

## Key Takeaways

- Voltage is push, current is flow, and resistance is opposition, tied together by \( V = IR \).
- Every part needs power and a shared ground.
- The Pico's pins use 3.3 V logic and are not 5 V tolerant.
- An LED needs a series resistor; choose it with \( R = (V_{supply} - V_{LED})/I \).
- A breadboard connects holes in short strips, and a multimeter tells you what is really happening.

!!! mascot-celebration "Circuit Ready"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now size an LED resistor with Ohm's Law, read a resistor's color bands, wire a breadboard, and protect a Pico pin from 5 V. Every second counts, and yours just powered up a whole toolkit!

## Practice Questions

1. A 5 V supply feeds a 1 kΩ resistor. How much current flows? How much power is used?
2. Choose a resistor for a green LED (2.1 V forward voltage) running at 8 mA from a 3.3 V pin. Which standard value would you use?
3. A resistor has the bands red, violet, brown, gold. What is its value?
4. A sensor outputs 5 V. Design a divider using 1 kΩ and 2 kΩ resistors and state the output voltage.
5. Your LED circuit is wired correctly but stays dark. List three things you would check with a multimeter.
