---
title: Computational Thinking and Physical Computing
description: How to think about a clock as a system of sensors, a controller, and actuators, and how the Raspberry Pi Pico brings that system to life.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 12:00:00
version: 1.10
---

# Computational Thinking and Physical Computing

## Summary

Students learn the four core computational thinking skills and how a clock is built from sensors, a microcontroller, and actuators. They meet the Raspberry Pi Pico and its RP2040 chip. After this chapter they can break a clock into parts and describe what each part does.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Computational Thinking | 161 |
| Microcontroller | 1509 |
| Decomposition | 67 |
| Pattern Recognition | 27 |
| Raspberry Pi Pico | 956 |
| Sensors | 74 |
| Actuators | 245 |
| Crystal Oscillator | 10 |
| Abstraction | 17 |
| Algorithmic Thinking | 25 |
| RP2040 Chip | 89 |
| Physical Computing | 1 |
| Dual Core Architecture | 2 |

## Prerequisites

This chapter assumes only the prerequisites listed in the [course description](../../course-description.md).

---

!!! mascot-welcome "Hi, I'm Chrono!"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Hi! I'm Chrono, a small robot with a smartwatch for a head, and I love figuring out how things tick. I'll pop up throughout this book in six ways:

    1. **Welcome:** I tell you why a chapter is worth your time.
    2. **Thinking:** I flag an idea that changes how you see a problem.
    3. **Tip:** I hand you a shortcut that saves effort.
    4. **Warning:** I point out a trap before you fall in it.
    5. **Encourage:** I remind you that hard parts are normal.
    6. **Celebrate:** I name what you just mastered.

    If I'm not doing one of those six things, I'm not in the chapter. Let's make time tick!

## Why Start With Thinking?

By the end of this course you will have built clocks that show the time on LED digits, a tiny OLED screen, a round smartwatch display, and even a strip of glowing NeoPixels. Before you touch a single wire, it helps to learn *how to think* about building such a device. That is what this chapter is for.

The chapter has two halves. The first half covers four thinking skills that programmers use every day. The second half meets the hardware: the microcontroller, its sensors and actuators, and the Raspberry Pi Pico board you will use for every project.

## Physical Computing

**Physical computing** means building systems that sense the real world, make a decision with a computer, and then change something in the real world. A regular program on a laptop lives inside the screen. A physical computing program reaches out: it reads a button press, measures light, spins a motor, or lights an LED.

A clock is a perfect first physical computing project. It has to *keep* time (a real-world process), *decide* what to show, and *display* the result where a person can see it. Every clock in this book follows that same pattern, and you will see it again in the section on sensors and actuators.

## Computational Thinking

**Computational thinking** is a way of solving problems so that a computer (or a person following clear steps) can carry out the solution. It is not the same as programming. You can think computationally with a pencil and paper before you write any code, and doing so makes the code much easier to write.

Computational thinking has four core skills:

- **Decomposition:** break a big problem into smaller, manageable pieces.
- **Pattern recognition:** notice what repeats or what is similar between pieces.
- **Abstraction:** focus on what matters and hide the details that do not.
- **Algorithmic thinking:** write the steps in a clear, ordered list that always works.

These skills are not a checklist you run through once. They work together. In practice you might decompose a clock, spot a pattern in the pieces, hide a messy detail behind a simple name, and then write out the steps. The next four sections take them one at a time, using a digital clock as the running example.

!!! mascot-thinking "One Big Idea"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of these four skills as a toolbox, not a recipe. When a problem feels too big to start, ask which tool fits: can I split it, spot a pattern, hide a detail, or list the steps?

### Decomposition

**Decomposition** is the skill of breaking a large problem into smaller problems that are each easy enough to solve on their own. If someone says "build a clock," you have no idea where to start. If you break it up, every piece becomes a task you can finish in an afternoon.

Here is one way to decompose a digital clock. Notice that each piece has a single job and can be tested by itself.

| Piece | Job | Example question it answers |
|-------|-----|------------------------------|
| Keep time | Know what time it is right now | How many seconds have passed since midnight? |
| Split time | Turn the time into hours, minutes, seconds | What is the hour digit? |
| Format time | Choose 12-hour or 24-hour style | Should 15:05 show as 3:05 PM? |
| Draw time | Show the digits on the display | Which segments light up for a 7? |
| Handle input | React to button presses | Did the user press "set hour"? |

Decomposition has a big payoff when something breaks. If the clock shows the wrong hour, you do not have to search the whole program. You check "keep time," then "split time," then "format time," and the bug has nowhere to hide. Professional engineers decompose for exactly this reason.

**Worked example.** Suppose the display shows `3:05` when it should show `15:05`. Using the table, start with the piece closest to the symptom. "Draw time" is probably fine because it drew what it was told. "Format time" is the suspect: it may be converting to 12-hour style when the setting says 24-hour. You have narrowed a whole clock down to one small piece in two questions.

The interactive diagram below lets you explore the decomposition of a clock yourself.

#### Diagram: Clock Decomposition Explorer

<details markdown="1">
<summary>Clock Decomposition Explorer</summary>
Type: interactive diagram
**sim-id:** clock-decomposition-explorer<br/>
**Library:** vis-network<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* a digital clock by breaking it into sub-problems and identify which sub-problem a given symptom belongs to (Bloom: Analyzing).

**Layout:** A top-down tree. The root node is "Digital Clock" (large, purple). The second level has five child nodes: Keep Time, Split Time, Format Time, Draw Time, Handle Input (teal). Under each child, two to three grandchild nodes show smaller tasks (for example, under Draw Time: "Draw digits," "Flash the colon," "Set brightness").

**Interactions:**

- Clicking any node opens an infobox on the right with a one-sentence definition and a "Test it alone" hint.
- Hovering a node highlights its parent path back to the root.
- A dropdown labeled "Symptom" offers four bugs ("Wrong hour," "Colon does not flash," "Buttons ignored," "Clock runs slow"). Selecting one pulses the node most likely to contain the bug.

**Responsive design:** The canvas fills the container width, height 450 px, and redraws with `network.fit()` on window resize.

Implementation: vis-network hierarchical layout, direction "UD", with a small JavaScript object mapping node IDs to infobox text.
</details>

### Pattern Recognition

**Pattern recognition** means noticing similarities, repetitions, and regularities so you can solve a family of problems with one idea instead of many. Once you spot a pattern, you stop reinventing the wheel.

A clock is full of patterns. Minutes and seconds both count from 0 to 59 and then wrap back to 0. Hours wrap at 12 or 24. Every digit on a display is drawn from the same small set of shapes. A stopwatch, a countdown timer, and an alarm all do the same thing at heart: compare a number to a target as time passes.

The table below summarizes patterns you will meet again and again in this book.

| Pattern | Where it shows up |
|---------|-------------------|
| Count up and wrap around | Seconds, minutes, hours, days of the week |
| Repeat a step many times | Blinking a colon, scanning display digits |
| Compare a value to a limit | Alarms, timers, auto-brightness |
| Same shape, different size | Digit drawing at several scales |

**Try it.** Look at the numbers 0, 1, 2, ... 59. What happens after 59? Now look at the hours 1, 2, ... 12. What happens after 12? Both sequences "wrap," but one wraps to 0 and the other wraps to 1. Spotting that small difference early prevents a classic clock bug where midnight shows `0:00 PM`.

!!! mascot-tip "Pattern Spotting Shortcut"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When you write the same thing twice, stop and ask what is different between the two copies. Whatever stays the same is the pattern, and it usually becomes a single reusable piece of code.

### Abstraction

**Abstraction** means hiding the complicated details of something behind a simple description, so you can use it without knowing how it works inside. You use abstraction every time you drive a car: you press the pedal and the car goes faster, and you do not think about the fuel injectors.

In a clock program, abstraction lets you write `show_time(hour, minute)` and trust that the digits will appear. Whether the display is a four-digit LED module or a round smartwatch screen is a detail hidden inside that one name. You can swap displays later and the rest of your program stays the same.

Abstraction always trades detail for simplicity. The table shows the same clock described at three levels.

| Level | Description | Who cares |
|-------|-------------|-----------|
| Top | "It shows the time." | A user |
| Middle | "It reads the time, then draws digits." | A programmer |
| Bottom | "It sends bytes over the bus to the display chip." | A driver author |

Good engineers move between levels on purpose. They work at the top level while designing and drop down to the bottom level only when something breaks. Later chapters on modules and display drivers depend on this idea, so it is worth getting comfortable with it now.

### Algorithmic Thinking

**Algorithmic thinking** is the skill of writing a clear, ordered list of steps that solves a problem and always finishes. That list of steps is called an **algorithm**. A recipe is an algorithm. So is a set of directions to a friend's house.

A good algorithm is precise (each step has one meaning), ordered (steps happen in a fixed sequence), and finite (it ends). Here is an algorithm for turning a count of seconds since midnight into a clock reading, written in plain English before any code:

1. Start with the total seconds since midnight.
2. Divide by 3600 and keep the whole number. That is the hour.
3. Take what is left over and divide by 60. That is the minute.
4. Whatever is left after that is the second.

**Worked example.** Take 45,296 seconds. Step 2: 45,296 divided by 3600 is 12 with a remainder of 2,096, so the hour is 12. Step 3: 2,096 divided by 60 is 34 with a remainder of 56, so the minute is 34. Step 4: the second is 56. The time is 12:34:56. Writing the steps first, then checking them by hand on a real number, catches mistakes long before you type any code.

The clickable flowchart below shows the same algorithm as a diagram.

#### Diagram: Seconds-to-Clock Flowchart

<details markdown="1">
<summary>Seconds-to-Clock Flowchart</summary>
Type: workflow diagram
**sim-id:** seconds-to-clock-flowchart<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *apply* an algorithm by tracing a number of seconds through each step (Bloom: Applying).

**Nodes (top to bottom):** "Start: total seconds," "hours = seconds // 3600," "left = seconds % 3600," "minutes = left // 60," "seconds = left % 60," "Show hours:minutes:seconds."

**Interactions:**

- Every node has a Mermaid `click` directive that opens an infobox explaining the step in one sentence.
- A number input labeled "Seconds since midnight" (default 45296, range 0 to 86399) runs the algorithm. Each node shows the intermediate value it produces, and the current node is highlighted as the user presses "Next step."

**Responsive design:** The diagram scales to container width; the input panel stacks under the diagram on screens narrower than 600 px.

Implementation: Mermaid flowchart plus a small JavaScript stepper that updates node labels.
</details>

The `//` and `%` symbols in that diagram are MicroPython operators you will study in Chapter 3. For now, read `//` as "divide and keep the whole number" and `%` as "the remainder."

## The Microcontroller

Now for the hardware. A **microcontroller** is a tiny computer on a single chip that is designed to control something. It contains a processor, memory, and input/output connections all together. That is different from the computer in a laptop, which needs separate parts for each of those jobs.

Microcontrollers are everywhere. One runs your microwave, another runs a TV remote, and another runs the anti-lock brakes in a car. They are cheap (often under a dollar), they use very little power, and they start running your program the moment power arrives.

The table compares a microcontroller with a laptop computer.

| Feature | Microcontroller | Laptop |
|---------|-----------------|--------|
| Purpose | Control one device | Do many general tasks |
| Memory | Kilobytes to a few megabytes | Gigabytes |
| Operating system | Often none | Windows, macOS, Linux |
| Power | Milliwatts | Tens of watts |
| Typical cost | \$1 to \$10 | Hundreds of dollars |

The small memory is not a weakness for clocks. Telling time takes very little computing, so a microcontroller is exactly the right size.

!!! mascot-thinking "Small on Purpose"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A microcontroller is not a weak laptop. It is a tool sized for one job, which is why a clock can run for months on a small battery.

## Sensors and Actuators

A microcontroller by itself cannot see, hear, or move. It needs help from two kinds of parts that connect it to the world.

A **sensor** is a component that measures something in the real world and turns it into an electrical signal the microcontroller can read. A button is a sensor: it reports "pressed" or "not pressed." A light sensor reports how bright the room is. A real-time clock chip reports the current time.

An **actuator** is a component that turns an electrical signal from the microcontroller into a real-world effect. An LED that lights up, a buzzer that beeps, a motor that turns, and a display that shows digits are all actuators.

Together these form the pattern behind every device in this book: **sense, think, act**. The sensor gathers information, the microcontroller decides what to do, and the actuator makes it happen.

| Part | Role | Clock examples |
|------|------|----------------|
| Sensor | Input: measures the world | Push button, light sensor, real-time clock, temperature sensor |
| Microcontroller | Thinks: runs your program | Raspberry Pi Pico |
| Actuator | Output: changes the world | LED display, OLED screen, buzzer, NeoPixel strip |

**Worked example.** Follow one auto-dimming clock through the cycle. The light sensor reports "the room is dark" (sense). The program compares that reading to a limit and decides the display is too bright (think). It tells the display to lower its brightness (act). One second later the loop repeats.

!!! mascot-warning "Which Side Is It?"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A display can look like both an input and an output because it "shows" the time, but it only receives signals from the Pico, so it is an actuator. Ask "does information flow toward the microcontroller or away from it?" to sort any part correctly.

#### Diagram: Sense-Think-Act Infographic

<details markdown="1">
<summary>Sense-Think-Act Infographic</summary>
Type: interactive infographic
**sim-id:** sense-think-act-clock<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *classify* clock components as sensors, controller, or actuators and *explain* the flow of information among them (Bloom: Understanding).

**Layout:** Three columns on a 700 x 400 canvas: Sensors (left), Microcontroller (center), Actuators (right). Arrows point left to right.

**Interactions:**

- A tray of eight draggable component cards (button, light sensor, DS3231 RTC, Pico, LED display, OLED, buzzer, NeoPixel strip) sits at the bottom. The student drags each card into a column.
- A correct drop snaps into place with a green outline and an infobox; an incorrect drop bounces back with a hint ("Does this part send data to the Pico or receive it?").
- Hovering any placed card shows a one-line tooltip consistent with the glossary.
- When all eight are placed correctly, an animated dot travels along the arrows to show sense, think, act.

**Responsive design:** Canvas width follows the container; card sizes scale with `windowWidth`.

Implementation: p5.js with mouse events for drag and drop and a small array of card objects.
</details>

## The Crystal Oscillator

A clock needs a steady beat, and that beat has to come from something extremely regular. A **crystal oscillator** is an electronic part that uses a tiny slice of quartz crystal to make a very steady repeating signal. When you apply electricity to quartz, it vibrates at a precise frequency, much like a tuning fork rings at one pitch.

Frequency is how many times something repeats each second, measured in **hertz (Hz)**. One kilohertz (kHz) is 1,000 Hz and one megahertz (MHz) is 1,000,000 Hz. The Raspberry Pi Pico has a 12 MHz crystal, so its signal ticks 12 million times every second. The chip multiplies that up internally to run at 125 MHz by default.

Watch and clock chips often use a different crystal that vibrates at 32,768 Hz. That number is \(2^{15}\), which is convenient because a chain of 15 "divide by two" steps turns it into exactly one tick per second:

\[ \frac{32{,}768\ \text{Hz}}{2^{15}} = 1\ \text{Hz} \]

**Worked example: how wrong can a crystal be?** Crystals are precise but not perfect. A typical low-cost crystal is accurate to about 30 parts per million (ppm), which means it may be off by 30 ticks in every million. Over one day (86,400 seconds):

\[ 86{,}400 \times \frac{30}{1{,}000{,}000} \approx 2.6\ \text{seconds} \]

So a crystal-driven clock might drift about 2.6 seconds per day, or roughly a minute a month. That is why later chapters add real-time clock chips and internet time sync to correct the drift.

#### Diagram: Crystal Divider MicroSim

<details markdown="1">
<summary>Crystal Divider MicroSim</summary>
Type: MicroSim
**sim-id:** crystal-divider<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* frequency division to see how a fast crystal signal becomes a one-second tick, and *calculate* daily drift from a ppm error (Bloom: Applying).

**Visual elements:** A row of 15 small boxes, each labeled with a frequency starting at 32,768 Hz and halving each box down to 1 Hz. A pulse animation runs through the chain; each box flashes at its own rate.

**Controls:**

- Slider "Crystal error (ppm)," range 0 to 100, default 30.
- Button "Run one day" that displays the computed drift in seconds.
- Toggle "Slow motion" that slows the animation so the fast boxes are visible.

**Behavior:** Changing the ppm slider updates a readout, "Drift per day: X seconds." The last box, at 1 Hz, flashes once per second and a digital clock beside it counts up, gaining or losing time visibly when ppm is high.

**Responsive design:** Boxes shrink to fit the container width; the layout stacks vertically under 600 px.

Implementation: p5.js with `frameRate` control and a simple accumulator per box.
</details>

## The RP2040 Chip

The **RP2040** is the microcontroller chip designed by the Raspberry Pi Foundation that powers the Raspberry Pi Pico. It is the "brain" of every project in this book. Here are its key facts:

- **Processor:** two Arm Cortex-M0+ cores that run at up to 133 MHz.
- **Memory:** 264 kilobytes of fast working memory (RAM).
- **Inputs and outputs:** 30 general-purpose pins on the chip, of which 26 are available on the Pico board.
- **Built-in helpers:** hardware for the I2C, SPI, and UART communication buses, PWM (used for sound and dimming), and analog-to-digital conversion.
- **Logic level:** it works at 3.3 volts, so its signals are 3.3 V, not 5 V.

To put 264 KB in perspective, a single photo from a phone is several megabytes, so the whole RAM of the RP2040 is smaller than one small photo. Your clock programs still fit easily because text and small numbers take very little space.

!!! mascot-encourage "Lots of New Words?"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Terms like "Cortex-M0+" and "PWM" can feel like a wall of jargon. You do not need to memorize them now; you'll meet each one again in a lab, and using it once makes it stick far better than reading it.

### Dual Core Architecture

A **dual core architecture** means a chip has two independent processors, called cores, that can each run instructions at the same time. The RP2040 has two cores, named core 0 and core 1.

Think of two cooks in one kitchen. One can chop while the other stirs, and together they finish faster than one cook alone. In a clock, one core could keep time while the other draws animations.

Most beginner MicroPython programs run on core 0 only, and that is plenty for a clock. Later, in the Pico platform chapter, you will see how to start work on the second core if you ever need it.

## The Raspberry Pi Pico

The **Raspberry Pi Pico** is a small, low-cost circuit board built around the RP2040 chip. It adds everything the chip needs to be useful: a USB connector for power and programming, a voltage regulator, flash memory to store your programs, and 40 pins along the edges where you attach wires, sensors, and displays.

It is a very different product from the "Raspberry Pi" computers that run Linux. The Pico has no operating system, no desktop, and no video port. It runs one program at a time, starts in a fraction of a second, and is designed to be plugged into other electronics.

| Feature | Raspberry Pi Pico | Raspberry Pi Pico W |
|---------|-------------------|----------------------|
| Chip | RP2040 | RP2040 |
| Flash memory | 2 MB | 2 MB |
| Wireless | None | WiFi and Bluetooth |
| Typical price | about \$4 | about \$6 |
| Used for | LED, OLED, button clocks | Same, plus internet time sync |

This course uses the **Pico W** for any project that needs WiFi, such as setting the clock from the internet.

!!! mascot-tip "Check the Label"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Pico and Pico W look almost identical, so read the tiny text printed on the board before you plug it in. A plain Pico cannot connect to WiFi, no matter what the code says.

**Your first program.** Before you run code, here is what it does: it makes the Pico's built-in LED turn on and off once per second. The line `Pin("LED", Pin.OUT)` gives the on-board LED a name and tells the Pico to use that pin as an **output** (a pin that sends a signal out). The `toggle()` method flips the LED to the opposite state, and `sleep(0.5)` waits half a second. Together they make one full blink each second.

```python
NAME = "01-blink.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)   # the LED soldered on the Pico W board

while True:
    led.toggle()            # flip: off becomes on, on becomes off
    sleep(0.5)              # wait half a second
```

This tiny program is a full sense-think-act loop with no sensor: the loop is the "think," and the LED is the actuator. Notice how it also uses the four thinking skills from earlier in the chapter. The blink was decomposed into "flip the LED" and "wait." The repeated flip is a pattern. `Pin("LED", Pin.OUT)` is an abstraction that hides which chip pin drives the LED. And the loop is a tiny algorithm.

!!! note "Setup Comes Next"
    You will install Thonny and run this program in Chapter 3. For now, just read it and predict what it will do. On a plain Pico (not W), the LED pin is `Pin(25, Pin.OUT)` instead.

#### Diagram: Pico Board Explorer

<details markdown="1">
<summary>Pico Board Explorer</summary>
Type: interactive infographic
**sim-id:** pico-board-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *identify* the main parts of the Raspberry Pi Pico and *recall* the purpose of each (Bloom: Remembering).

**Visual elements:** A top-down drawing of the Pico W on a 600 x 450 canvas, with hotspots on the RP2040 chip, USB connector, BOOTSEL button, on-board LED, wireless module, and the two rows of 20 pins.

**Interactions:**

- Hovering a hotspot shows a tooltip with the part name.
- Clicking a hotspot opens an infobox with a two-sentence description and a "Used in this book for..." line.
- A "Quiz me" button hides all labels and asks the student to click a named part; the score is shown and the sim tracks which parts were missed.

**Responsive design:** The board image scales to canvas width and hotspots reposition proportionally on resize.

Implementation: p5.js with an array of hotspot rectangles in normalized coordinates.
</details>

## Putting It All Together

You now have the two toolkits you need for the rest of the course. The thinking toolkit (decomposition, pattern recognition, abstraction, and algorithms) tells you *how to plan*. The hardware toolkit (microcontroller, sensors, actuators, crystal, RP2040, Pico) tells you *what to build with*.

The table below connects each idea from this chapter to a piece of your first clock.

| Idea | Where it appears in a clock |
|------|------------------------------|
| Decomposition | Splitting the clock into keep, split, format, draw, and input |
| Pattern recognition | Every counter wraps around |
| Abstraction | `show_time()` hides the display details |
| Algorithmic thinking | Turning seconds into hours, minutes, seconds |
| Sensor | Buttons, real-time clock, light sensor |
| Actuator | LED digits, OLED, buzzer |
| Crystal oscillator | The steady beat behind all timekeeping |
| RP2040 and Pico | The brain that runs your program |

## Key Takeaways

- Physical computing systems sense, think, and act.
- The four computational thinking skills are decomposition, pattern recognition, abstraction, and algorithmic thinking.
- A microcontroller is a small computer on one chip, sized for a single job.
- Sensors send information in; actuators turn signals into real-world effects.
- A crystal oscillator provides the precise beat clocks depend on, but even a good crystal drifts a few seconds a day.
- The RP2040 has two cores, 264 KB of RAM, and 26 usable pins, and the Pico board packages it for easy use.

!!! mascot-celebration "Foundation Built"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now break a clock into parts, tell a sensor from an actuator, and explain why a crystal keeps time. That is the foundation every later chapter stands on. Every second counts!

## Practice Questions

1. Decompose a **kitchen timer** into at least four pieces, and name one sensor and one actuator it needs.
2. A clock shows `12:00 AM` twice in one day. Which computational thinking skill would you use to look for the bug, and why?
3. Calculate the drift per day of a crystal that is accurate to 20 ppm.
4. Explain in your own words why a microcontroller with 264 KB of RAM is enough for a clock.
5. In the blink program, which line is the sensor, which is the actuator, and which is the "think" part? (Hint: one of these does not exist.)
