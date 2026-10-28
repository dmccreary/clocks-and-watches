# Quiz: Computational Thinking and Physical Computing

Test your understanding of computational thinking, sensors and actuators, and the Raspberry Pi Pico with these review questions.

---

#### 1. What does decomposition mean in computational thinking?

<div class="upper-alpha" markdown>
1. Writing the steps of a solution in a fixed order that always finishes
2. Noticing what repeats between different parts of a problem
3. Breaking a large problem into smaller pieces that can each be solved on their own
4. Hiding messy details behind a simple name so they can be ignored
</div>

??? question "Show Answer"
    The correct answer is **C**. Decomposition splits a big problem, such as "build a clock," into small pieces like keeping time, splitting time, formatting time, drawing time, and handling input. Each piece has one job and can be tested alone. Option A describes algorithmic thinking, option B describes pattern recognition, and option D describes abstraction.

    **Concept Tested:** Decomposition

    **See:** [Decomposition](index.md#decomposition)

---

#### 2. Which chip is the microcontroller at the heart of the Raspberry Pi Pico?

<div class="upper-alpha" markdown>
1. RP2040
2. ESP32
3. ATmega328
4. DS3231
</div>

??? question "Show Answer"
    The correct answer is **A**. The RP2040 was designed by the Raspberry Pi Foundation and powers every Pico board. It has two Arm Cortex-M0+ cores, 264 KB of RAM, and a 3.3 V logic level. The ESP32 and ATmega328 are other microcontrollers found on different boards, and the DS3231 is a real-time clock chip you will add to projects later, not a microcontroller.

    **Concept Tested:** RP2040 Chip

    **See:** [The RP2040 Chip](index.md#the-rp2040-chip)

---

#### 3. Why is a clock's display classified as an actuator rather than a sensor?

<div class="upper-alpha" markdown>
1. It uses more power than any other part of the clock
2. It is connected to the Pico with more than one wire
3. It measures how bright the room is around the clock
4. It receives signals from the Pico and changes something in the real world
</div>

??? question "Show Answer"
    The correct answer is **D**. An actuator turns an electrical signal from the microcontroller into a real-world effect, such as lit digits. A sensor does the opposite: it measures the world and sends information toward the microcontroller. A handy test is to ask whether information flows toward the Pico or away from it. A display only receives, so it is an actuator.

    **Concept Tested:** Actuators

    **See:** [Sensors and Actuators](index.md#sensors-and-actuators)

---

#### 4. Which statement best describes how a microcontroller differs from a laptop computer?

<div class="upper-alpha" markdown>
1. It runs a full desktop operating system but with less memory
2. It is a small computer on one chip that is sized to control a single device
3. It has more memory than a laptop but runs much more slowly
4. It needs separate chips for its processor, memory, and input/output pins
</div>

??? question "Show Answer"
    The correct answer is **B**. A microcontroller puts a processor, memory, and input/output connections on a single chip, and it often runs no operating system at all. It has kilobytes to a few megabytes of memory, uses milliwatts of power, and costs a few dollars. Telling time takes very little computing, so this small size is exactly right for a clock.

    **Concept Tested:** Microcontroller

    **See:** [The Microcontroller](index.md#the-microcontroller)

---

#### 5. Why do watch and clock chips often use a crystal that vibrates at 32,768 Hz?

<div class="upper-alpha" markdown>
1. The number is 2 to the 15th power, so 15 divide-by-two steps give exactly one tick per second
2. It is the fastest frequency that a quartz crystal can physically vibrate
3. It matches the 3.3 V logic level used by the RP2040 chip
4. It is the default clock speed of the Raspberry Pi Pico processor
</div>

??? question "Show Answer"
    The correct answer is **A**. Because 32,768 equals 2^15, a chain of 15 "divide by two" circuits turns the crystal's vibration into a signal of exactly 1 Hz, which is one tick per second. This makes the crystal ideal for timekeeping. The Pico itself uses a 12 MHz crystal that is multiplied internally to 125 MHz, and logic voltage has nothing to do with frequency.

    **Concept Tested:** Crystal Oscillator

    **See:** [The Crystal Oscillator](index.md#the-crystal-oscillator)

---

#### 6. In the sense, think, act pattern used by every device in this book, which part performs the "think" step?

<div class="upper-alpha" markdown>
1. The push button that reports when it is pressed
2. The buzzer that beeps when the alarm time arrives
3. The microcontroller that runs your program and decides what to do
4. The crystal that supplies the steady beat for timekeeping
</div>

??? question "Show Answer"
    The correct answer is **C**. In a physical computing system, sensors gather information, the microcontroller decides what to do by running your program, and actuators carry out the decision. The button is a sensor and the buzzer is an actuator. The crystal supplies the regular beat that timekeeping depends on, but it does not make decisions about what the clock should show or do.

    **Concept Tested:** Physical Computing

    **See:** [Sensors and Actuators](index.md#sensors-and-actuators)

---

#### 7. A low-cost crystal is accurate to 30 parts per million. About how many seconds could a clock driven by it gain or lose in one day?

<div class="upper-alpha" markdown>
1. About 0.26 seconds
2. About 2.6 seconds
3. About 26 seconds
4. About 259 seconds
</div>

??? question "Show Answer"
    The correct answer is **B**. One day has 86,400 seconds, and 30 ppm means 30 errors in every million ticks. Multiply 86,400 by 30 and divide by 1,000,000 to get about 2.6 seconds, or roughly a minute per month. This drift is why later chapters add real-time clock chips and internet time sync. The other options are off by a factor of 10 or more.

    **Concept Tested:** Crystal Oscillator

    **See:** [The Crystal Oscillator](index.md#the-crystal-oscillator)

---

#### 8. Using the seconds-to-clock algorithm, what time does 3,725 seconds since midnight represent?

<div class="upper-alpha" markdown>
1. 0:37:25
2. 1:05:02
3. 1:20:25
4. 1:02:05
</div>

??? question "Show Answer"
    The correct answer is **D**. Divide 3,725 by 3,600 to get 1 hour with 125 seconds left over. Divide 125 by 60 to get 2 minutes with 5 seconds left over. The result is 1:02:05. Writing the algorithm as ordered steps and checking it by hand on a real number, as the chapter does with 45,296 seconds, catches mistakes before any code is typed.

    **Concept Tested:** Algorithmic Thinking

    **See:** [Algorithmic Thinking](index.md#algorithmic-thinking)

---

#### 9. Which list names the four core skills of computational thinking?

<div class="upper-alpha" markdown>
1. Decomposition, debugging, abstraction, and iteration
2. Decomposition, pattern recognition, abstraction, and algorithmic thinking
3. Sensing, thinking, acting, and repeating
4. Planning, coding, testing, and deploying
</div>

??? question "Show Answer"
    The correct answer is **B**. The four skills are decomposition (split the problem), pattern recognition (notice what repeats), abstraction (hide details that do not matter), and algorithmic thinking (write clear ordered steps). Option C describes the sense, think, act cycle of a physical computing device, and option D describes stages of a software project. Debugging and iteration are useful habits but are not among the four skills.

    **Concept Tested:** Computational Thinking

    **See:** [Computational Thinking](index.md#computational-thinking)

---

#### 10. A clock shows `3:05` when it should show `15:05`. Using the clock decomposition table, which piece is the most likely culprit, and why?

<div class="upper-alpha" markdown>
1. Keep time, because the Pico has lost track of the seconds since midnight
2. Draw time, because the segments for the digit 5 are not lighting up
3. Format time, because it may be converting to 12-hour style when 24-hour is wanted
4. Handle input, because a button press has changed the current minute
</div>

??? question "Show Answer"
    The correct answer is **C**. The display drew exactly what it was told, so "draw time" is probably fine, and the minutes are correct, so timekeeping is probably fine too. The hour is the only wrong value, which points to the piece that chooses between 12-hour and 24-hour style. Decomposition lets you narrow a whole clock down to one small piece in just two questions.

    **Concept Tested:** Decomposition

    **See:** [Decomposition](index.md#decomposition)
