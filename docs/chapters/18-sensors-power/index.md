---
title: Sensors, Power, and Low-Power Design
description: Light and motion sensors, ADC readings, auto brightness, batteries, current budgets, and low-power design.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:51:36
version: 1.10
---

# Sensors, Power, and Low-Power Design

## Summary

Students read analog sensors to adjust brightness automatically and explore accelerometers and gyroscopes. They compare battery types and estimate current draw. After this chapter they can make a clock that adapts to light and runs on battery power.

## Concepts Covered

This chapter covers the following 22 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Power Management | 12 |
| USB Power | 2 |
| Battery Power | 5 |
| Brownout Detection | 1 |
| ADC Reading | 10 |
| LiPo Battery | 2 |
| AA Battery Pack | 1 |
| USB Battery Pack | 1 |
| Photosensor | 4 |
| Current Draw Calculation | 1 |
| Light Dependent Resistor | 1 |
| Accelerometer Basics | 4 |
| Gyroscope Basics | 2 |
| Brightness Control | 3 |
| LilyGo RP2040 Board | 1 |
| Tilt Detection | 1 |
| Step Counter Concept | 1 |
| Auto Brightness | 2 |
| Waveshare RP2040 Board | 1 |
| Hysteresis | 1 |
| Sleep Mode Wake Source | 2 |
| Low Power Mode | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 7: Buttons, Interrupts, and State Machines](../07-buttons-state-machines/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)
- [Chapter 9: LED Displays and the First Digital Clock](../09-led-displays/index.md)
- [Chapter 15: Color Displays and Smartwatch Faces](../15-color-displays/index.md)

---

!!! mascot-welcome "A Clock That Notices"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Your clock can dim itself at night, notice when your wrist turns, and run on a battery for a day or more. This chapter gives it senses and stamina. Let's make time tick!

## Sensing and Powering a Clock

Two ideas turn a clock into a smart, portable gadget. **Sensors** let it respond to the world: room light, motion, and tilt. **Power management** lets it run away from the wall: choosing a battery, estimating how long it lasts, and sleeping to save energy. The chapter covers analog readings first, then light and motion sensors, then power sources and low-power design.

## ADC Reading

The world is not digital. Light, temperature, and battery voltage all vary smoothly. A GPIO pin can only tell 0 from 1, so to read a smooth voltage the Pico uses an **ADC** (analog-to-digital converter), which measures a voltage and turns it into a number.

The Pico's ADC has three inputs you can use, on **GP26, GP27, and GP28** (channels ADC0, ADC1, and ADC2). It measures voltages from 0 V to 3.3 V, and the RP2040 does it with 12 bits of resolution, giving \( 2^{12} = 4096 \) levels. MicroPython scales the result to 16 bits, so the value you read runs from 0 to 65,535 no matter how many bits the hardware has.

```python
from machine import ADC, Pin

adc = ADC(Pin(26))            # GP26, channel ADC0
raw = adc.read_u16()          # 0 to 65535
volts = raw * 3.3 / 65535     # convert to volts
print(raw, volts)
```

**Worked example.** A reading of 32,768 is about half of full scale, so the voltage is \( 32{,}768 \times 3.3 / 65{,}535 \approx 1.65 \) V.

!!! mascot-tip "Average Away the Noise"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    ADC readings jitter a little even when nothing changes. Read the pin 8 or 16 times and use the average, and your light-sensing clock will stop flickering between brightness levels.

```python
def read_average(adc, n=16):
    return sum(adc.read_u16() for _ in range(n)) // n
```

## Photosensor

A **photosensor** is a part whose electrical behavior changes with light. The simplest and cheapest is the **light-dependent resistor**.

### Light-Dependent Resistor

A **light-dependent resistor (LDR)**, also called a photoresistor, is a resistor whose resistance *falls* as light gets brighter. In the dark it can be over a megaohm, and in bright light it drops to a few kilohms.

The ADC measures voltage, not resistance, so you put the LDR in a **voltage divider** (Chapter 2) with a fixed resistor. Connect 3.3 V to the LDR, the LDR to the ADC pin, and a 10 kΩ resistor from the ADC pin to ground:

\[ V_{out} = 3.3 \times \frac{R_{fixed}}{R_{LDR} + R_{fixed}} \]

In bright light, \( R_{LDR} \) is small, so \( V_{out} \) is high. In the dark, \( R_{LDR} \) is large, so \( V_{out} \) is low. With this wiring, a *bigger* ADC reading means *brighter* light.

**Worked example.** In a bright room the LDR is 2 kΩ: \( V_{out} = 3.3 \times 10 / (2 + 10) = 2.75 \) V. In a dim room it is 50 kΩ: \( V_{out} = 3.3 \times 10 / 60 = 0.55 \) V.

#### Diagram: LDR Light Sensor Lab

<details markdown="1">
<summary>LDR Light Sensor Lab</summary>
Type: MicroSim
**sim-id:** ldr-light-sensor-lab<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* the voltage divider formula to predict the ADC reading for different light levels (Bloom: Applying).

**Visual elements:** A schematic of 3.3 V, an LDR, a 10 kΩ resistor, and the ADC pin, next to a room scene with a lamp. A gauge shows the ADC value (0 to 65535).

**Controls:** A slider for room brightness (dark to sunlight), which maps to LDR resistance (1 MΩ down to 500 Ω); a slider for the fixed resistor (1 kΩ to 100 kΩ). Readouts show \( R_{LDR} \), \( V_{out} \), and the raw ADC value.

**Responsive design:** The schematic and scene stack on narrow screens.

Implementation: p5.js with the divider formula.
</details>

## Auto Brightness

**Auto brightness** adjusts the display's brightness to match the room. A bright display in a dark bedroom is glaring, and a dim display in daylight is unreadable. The recipe is a mapping from the light reading to a brightness level:

```python
def brightness_from_light(light, max_level=7):
    # light: 0..65535. Squeeze into 0..max_level
    return min(max_level, light * (max_level + 1) // 65536)
```

Because your eyes respond to light on a roughly logarithmic scale, a linear mapping works but can feel abrupt at the dark end. A simple improvement is to set a **minimum** brightness so the display never goes fully off, and use a lookup table to make the steps feel even.

### Brightness Control

How you set brightness depends on the display, so it is worth listing:

| Display | How to control brightness |
|---------|---------------------------|
| TM1637 LED | `tm.brightness(0..7)` |
| SSD1306 OLED | `oled.contrast(0..255)` |
| TFT LCD (backlight) | PWM the **BL** pin: `PWM(Pin(7)).duty_u16(level)` |
| NeoPixels | Scale the color values (or the HSV value) |

A PWM backlight is the most flexible, since it can dim smoothly across the whole range. The PWM frequency should be above about 1 kHz so the display does not visibly flicker.

### Hysteresis

If the room light hovers right at a threshold, the reading bounces above and below it, and the display flickers between two brightness levels. **Hysteresis** cures this by using **two thresholds** instead of one: a higher one to switch up, and a lower one to switch back down. The gap between them is a dead zone where nothing changes.

```python
HIGH, LOW = 30000, 26000       # switch up above HIGH, back down below LOW
bright = False

def update(light):
    global bright
    if not bright and light > HIGH:
        bright = True
    elif bright and light < LOW:
        bright = False
    return bright
```

Hysteresis is the same idea as debouncing in Chapter 7: both ignore small changes so that a noisy input gives a clean output. Thermostats use it, so the furnace does not switch on and off every few seconds.

!!! mascot-thinking "Two Thresholds Beat One"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    With a single threshold, noise near the line makes the output chatter. Add a gap between the "up" and "down" thresholds and the noise falls inside the gap, where nothing happens. That small gap is what makes automatic controls feel calm.

#### Diagram: Hysteresis Demonstrator

<details markdown="1">
<summary>Hysteresis Demonstrator</summary>
Type: MicroSim
**sim-id:** hysteresis-demonstrator<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* how a dead zone removes chatter from a noisy sensor (Bloom: Analyzing).

**Visual elements:** A scrolling line chart of a noisy light reading with two horizontal threshold lines, and below it, two on/off traces: "Single threshold" and "With hysteresis."

**Controls:** Sliders for the noise amount, the upper threshold, and the lower threshold; a "Lock thresholds together" toggle (which makes the gap zero). A counter shows how many times each output switched.

**Responsive design:** The charts scale to container width.

Implementation: p5.js with Gaussian noise around a slowly varying light level.
</details>

## Accelerometer Basics

An **accelerometer** measures acceleration along three axes: x, y, and z. It reports in units of **g**, where 1 g is the acceleration of gravity. A resting accelerometer does not read zero. It reads 1 g pointing "down," so it can tell which way is down and how the board is tilted.

Common accelerometer chips such as the MPU6050 connect over I2C (Chapter 8). The MPU6050's address is `0x68`, the same as the DS3231. If you use both on one bus, tie the MPU6050's AD0 pin high to move it to `0x69`.

```python
import struct
from machine import Pin, I2C

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
MPU = 0x69                                     # AD0 tied high

i2c.writeto_mem(MPU, 0x6B, b"\x00")            # wake the chip up
raw = i2c.readfrom_mem(MPU, 0x3B, 6)           # x, y, z acceleration
ax, ay, az = struct.unpack(">hhh", raw)        # three signed 16-bit numbers
print(ax / 16384, ay / 16384, az / 16384)      # convert to g (at the +/-2 g range)
```

The chip sends two bytes for each axis, high byte first, so `">hhh"` unpacks three signed 16-bit integers. At the default range of ±2 g, 16,384 counts equal 1 g.

### Gyroscope Basics

A **gyroscope** measures how fast the board is *rotating*, in degrees per second, around each axis. It responds to turning, not to which way is down. Its output is zero when the board is still, even if it is tilted. The MPU6050 has both sensors on one chip, and its gyroscope data starts at register `0x43`.

To get an angle from a gyroscope, add up (integrate) the rotation rate over time. The catch is drift: tiny errors add up, so the angle slowly wanders. Accelerometer and gyroscope complement each other: the accelerometer gives a stable but noisy tilt, and the gyroscope gives smooth but drifting rotation.

### Tilt Detection

**Tilt detection** uses the accelerometer to decide the orientation of the board. When the watch is flat and face-up, gravity is along z, so `az` is near 1 g and `ax` and `ay` near 0. When the wrist is raised to look at the watch, the 1 g shifts to another axis.

```python
def face_up(ax, ay, az):
    return az > 0.8                 # gravity mostly along z (values in g)

def wrist_raised(ax, ay, az):
    return ay < -0.5 and abs(az) < 0.6    # example rule; depends on how it is mounted
```

Use tilt to wake the screen when the wrist rises, to turn it off when the arm drops, or to rotate the display. Combine it with hysteresis so that small shakes do not flicker the screen.

### Step Counter Concept

A **step counter** counts steps by looking for the rhythmic bumps of walking in the accelerometer data. Combine the three axes into one **magnitude**:

\[ |a| = \sqrt{a_x^2 + a_y^2 + a_z^2} \]

At rest this is about 1 g. Each footstep makes it spike above roughly 1.2 g. Count each time the magnitude *crosses upward* through a threshold, and ignore any crossing within about 250 milliseconds of the last one, since people walk at about 2 steps per second. This is the same threshold-plus-debounce pattern used for buttons and light sensing. Real fitness watches use much smarter filtering, but this simple version is a good project.

#### Diagram: Tilt and Step Explorer

<details markdown="1">
<summary>Tilt and Step Explorer</summary>
Type: MicroSim
**sim-id:** tilt-step-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* accelerometer axes to detect tilt and *analyze* a step-counting threshold (Bloom: Applying, Analyzing).

**Visual elements:** A 3D-style watch on the left that the student can drag to tilt, with the three g values shown as bars. On the right, a scrolling plot of acceleration magnitude with a threshold line and step markers.

**Controls:** Drag to rotate the watch; a "Walk" button that generates a simulated walking signal; sliders for the step threshold and the minimum time between steps; a step count readout.

**Responsive design:** The two panels stack below 600 px.

Implementation: p5.js with simulated accelerometer vectors.
</details>

## Power Management

**Power management** means choosing and controlling how a device gets and uses electricity, so it works reliably and lasts as long as needed. It has two sides: the **supply** (where the energy comes from) and the **load** (how much your clock uses). You control the load by choosing efficient parts and turning things off when they are not needed.

The main power source options for a clock are:

| Source | Voltage | Best for |
|--------|---------|----------|
| USB from a computer or wall adapter | 5 V | Desk and wall clocks |
| USB battery pack (power bank) | 5 V | Long-lasting portable clocks |
| LiPo battery | 3.7 V | Compact watches |
| AA battery pack | 3 to 4.5 V | Low cost, replaceable |

### USB Power

**USB power** is the simplest. The Pico takes 5 V from the USB connector and the board's regulator makes the 3.3 V it needs (Chapter 2). A computer port supplies about 500 mA and a wall adapter usually 1 A or more. A Pico by itself uses only a few tens of milliamps, so USB power is plenty unless you add many NeoPixels (Chapter 16).

### Battery Power

For portable clocks, energy is stored in a battery. Two numbers describe it. **Voltage** must be in the range the Pico accepts. The **capacity**, in milliamp-hours (mAh), is how much current it can supply for how long. A simple estimate of the runtime is

\[ \text{runtime (hours)} = \frac{\text{capacity (mAh)} \times 0.8}{\text{average current (mA)}} \]

The 0.8 factor allows for the fact that batteries never deliver their full labeled capacity. **Worked example.** A 500 mAh battery powering a clock that averages 30 mA runs for about \( 500 \times 0.8 / 30 \approx 13 \) hours.

The Pico's **VSYS** pin accepts anywhere from 1.8 V to 5.5 V, and the board's built-in regulator converts it to 3.3 V. That range is what lets several battery types work.

### LiPo Battery

A **LiPo (lithium polymer) battery** is a thin, rechargeable battery with high energy for its size, which is why phones and smartwatches use them. It is 3.7 V nominal, reads 4.2 V when full, and must never be discharged below about 3.0 V.

Handle LiPo cells with respect. They need a **charging circuit** designed for lithium cells, and ideally a **protection circuit** against over-discharge and short circuits. Their connectors are not always standardized, and connecting one with reversed polarity can destroy a board or start a fire. Do not puncture or crush a LiPo, and do not charge one that is swollen.

### AA Battery Pack

An **AA battery pack** holds AA cells in a plastic holder with a lead. Cells are cheap, easy to buy, and replaceable anywhere. The voltage depends on the count:

| Pack | Voltage (alkaline) | Works with VSYS? |
|------|-------------------|------------------|
| 2 × AA | 3.0 V | Yes; regulator boosts as needed |
| 3 × AA | 4.5 V | Yes; the recommended choice |
| 4 × AA | 6.0 V | **No**; exceeds the 5.5 V limit |

An AA cell holds roughly 2,000 to 3,000 mAh, much more than a small LiPo, so an AA pack can run a low-power clock for weeks.

### USB Battery Pack

A **USB battery pack** (power bank) is a rechargeable battery with a USB output, made to charge phones. It is the easiest way to run a Pico from a battery: plug in the cable and go. Packs hold thousands of mAh.

!!! mascot-warning "Power Banks Can Switch Off"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Many power banks shut themselves off when the current draw is very low, because they think nothing is connected. A Pico clock uses so little that the bank may turn off after a minute and your clock stops. Choose a pack with an "always on" or low-current mode, or add a small extra load such as a resistor that draws about 100 mA.

#### Diagram: Battery Drain

<iframe src="../../sims/battery-drain/battery-drain.html" width="100%" height="460px" scrolling="no"></iframe>

[Run the Battery Drain MicroSim fullscreen](../../sims/battery-drain/battery-drain.html){ .md-button }

<details markdown="1">
<summary>Battery Drain (existing MicroSim)</summary>
Type: MicroSim
**sim-id:** battery-drain<br/>
**Library:** p5.js<br/>
**Status:** Reused<br/>
**Source:** docs/sims/battery-drain/

This MicroSim is already part of this book. Learning objective: students will *apply* capacity and current draw to estimate battery life (Bloom: Applying).
</details>

## Current Draw Calculation

To predict battery life you need the total current your clock uses. **Current draw calculation** is adding up the current of each part. The values below are typical; parts vary, so measure your own by placing a multimeter in series with the power wire (Chapter 2).

| Part | Typical current |
|------|-----------------|
| Pico running MicroPython | 20 to 30 mA |
| Pico W with WiFi active | 40 to 100 mA |
| Small OLED | 10 to 20 mA |
| Color TFT backlight | 20 to 80 mA |
| DS3231 RTC | under 1 mA |
| Piezo buzzer | 5 to 30 mA |
| NeoPixel, each, at full white | up to 60 mA |

**Worked example.** A smartwatch with a Pico (25 mA), a round display backlight (60 mA), and an RTC (0.2 mA) draws about 85 mA. A 500 mAh LiPo gives \( 500 \times 0.8 / 85 \approx 4.7 \) hours. Dimming the backlight to 20 mA drops the total to about 45 mA and roughly doubles the runtime to 8.9 hours. The display is the biggest target for savings.

#### Diagram: Battery Life Calculator

<details markdown="1">
<summary>Battery Life Calculator</summary>
Type: MicroSim
**sim-id:** battery-life-calculator<br/>
**Library:** Chart.js<br/>
**Status:** Specified

**Learning objective:** Students will *calculate* battery life and *evaluate* which design changes save the most energy (Bloom: Applying, Evaluating).

**Visual elements:** A stacked bar showing each part's current, a total current readout, and a large "Estimated runtime" label.

**Controls:** Checkboxes to include each part in the table, sliders for the backlight brightness and the fraction of time asleep, and a dropdown for battery capacity (150, 500, 1000, 2500 mAh). A bar chart compares runtime before and after the student's changes.

**Responsive design:** The chart resizes to the container.

Implementation: Chart.js with the runtime formula.
</details>

### Brownout Detection

A **brownout** is when the supply voltage sags below what the chip needs, but not all the way to zero. The Pico may reset, freeze, or behave strangely, and a display can show garbage. Brownouts happen when a load surges (a backlight, WiFi transmission, or a bank of NeoPixels turning on) and the battery or a thin wire cannot deliver the current, or when a battery is nearly empty.

The RP2040 has hardware to detect a low supply and reset safely. You can find out why the Pico last restarted with `machine.reset_cause()`, and print it at startup to see whether a mysterious reboot was a power problem. Signs of brownout are resets when the backlight or WiFi turns on. Fixes include a larger capacitor near the Pico's power pins (Chapter 2), a fresher battery, shorter and thicker power wires, and lowering the peak current.

## Sleep Mode Wake Source

Even a Pico that does nothing uses power, so the most effective saving is to **sleep** between tasks. A clock that only needs to update once per minute can sleep for most of that minute. In **sleep mode**, the processor stops running your program and draws much less current. Something must wake it, and the thing that wakes it is called a **wake source**.

The common wake sources are:

| Wake source | Example use |
|-------------|-------------|
| Timer | Wake every second or minute to update the display |
| GPIO pin change | Wake when a button is pressed |
| RTC alarm pin | The DS3231's INT pin wakes the Pico at an alarm time (Chapter 17) |

In MicroPython, `machine.lightsleep(ms)` sleeps for a number of milliseconds:

```python
import machine
machine.lightsleep(60_000)      # sleep for 60 seconds, then continue running
```

Which wake sources are available, and how much current you actually save, depends on your board and MicroPython version, so check the documentation for your firmware and **measure**. Peripherals that stay powered, such as a display backlight, can use more energy than the sleeping chip does.

### Low Power Mode

**Low power mode** is a design approach that combines every trick to make a battery last. A low-power clock does several things at once:

- Sleeps between updates with `lightsleep()` and a timer or RTC alarm wake source.
- Dims or turns off the backlight when no one is looking (using the tilt or auto brightness ideas above).
- Turns off WiFi (`wlan.active(False)`) except during the short sync described in Chapter 14.
- Updates the display only when something has changed (partial updates, Chapter 12).
- Uses a lower CPU speed if the program allows.

Sleeping fits the sense-think-act loop of Chapter 1 nicely: most of the time the clock is doing nothing at all.

## All-in-One Watch Boards

Instead of wiring a Pico, display, sensors, and battery charger together, some boards combine them on one small circuit board. They are handy for wearable projects because they are compact and include a LiPo charger.

### LilyGo RP2040 Board

The **LilyGo RP2040 boards** put an RP2040, a built-in color display, and a battery connection on a single board. They plug in with a USB cable and run the same MicroPython code as the Pico, though the display pin numbers differ from a wired build, so check the vendor's pinout.

### Waveshare RP2040 Board

The **Waveshare RP2040 boards**, such as the round LCD models, combine the RP2040, a round color display, a motion sensor (accelerometer and gyroscope), and a LiPo charger in a watch-sized package. They are a shortcut to a finished smartwatch. As with any all-in-one board, read the vendor documentation to get the exact chips, pin assignments, and driver libraries for the model you buy.

## Putting It Together

| Goal | Tool |
|------|------|
| Read a smooth voltage | `ADC(Pin(26)).read_u16()`, averaged |
| Sense light | LDR in a voltage divider |
| Adjust brightness without flicker | Auto brightness with hysteresis |
| Sense motion or tilt | Accelerometer over I2C |
| Choose a battery | Match voltage to VSYS; capacity ÷ current for runtime |
| Save power | Sleep, dim, WiFi off, update less often |

## Key Takeaways

- The ADC turns a voltage from 0 to 3.3 V into a number; average several readings to reduce noise.
- An LDR in a voltage divider senses light; auto brightness maps that reading to display brightness.
- Hysteresis uses two thresholds so a noisy sensor does not make the display flicker.
- An accelerometer reads gravity and motion; a gyroscope reads rotation; together they enable tilt and step detection.
- Battery life is capacity × 0.8 ÷ average current; the display backlight is usually the biggest load.
- LiPo cells need proper charging and care, 4 × AA is too much voltage, and power banks may shut off at low current.
- Sleeping between updates, with a timer, button, or RTC alarm as wake source, saves the most power.

!!! mascot-celebration "Smart and Portable"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now read analog sensors, dim the display automatically without flicker, detect tilt, and predict how long a battery will last. Your clock can sense its world and go anywhere. Every second counts!

## Practice Questions

1. An ADC reads 49,152. What voltage is that, and is the room brighter or darker than when it read 16,384 with an LDR divider?
2. Explain why adding hysteresis to auto brightness stops the display from flickering.
3. A clock draws 40 mA on average. How long will a 1,000 mAh battery run it, using the 0.8 factor?
4. Why is a 4 × AA alkaline pack unsuitable for the VSYS pin?
5. List three things you would do to make a smartwatch last longer on its battery.
