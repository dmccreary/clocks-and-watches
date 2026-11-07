# Quiz: Electronics Fundamentals and Breadboard Wiring

Test your understanding of voltage, current, resistors, LEDs, and breadboard wiring with these review questions.

---

#### 1. Which equation expresses Ohm's Law?

<div class="upper-alpha" markdown>
1. V = I + R
2. V = I × R
3. I = V × R
4. R = V × I
</div>

??? question "Show Answer"
    The correct answer is **B**. Ohm's Law says the voltage across a part equals the current through it times its resistance. Rearranged, it gives I = V / R and R = V / I, so you can find whichever value is missing. In a 3.3 V circuit with a 330 Ω resistor, the current is 3.3 / 330 = 10 mA. The other options mix up the operations and would give wrong units.

    **Concept Tested:** Ohms Law

    **See:** [Ohm's Law](index.md#ohms-law)

---

#### 2. By common convention, which wire color is used for a ground connection?

<div class="upper-alpha" markdown>
1. Red
2. Yellow
3. Green
4. Black
</div>

??? question "Show Answer"
    The correct answer is **D**. Black wires carry ground, red wires carry power (3.3 V or 5 V), and other colors such as yellow, green, and blue are used for signals like data or clock lines. There is no law requiring this, but nearly everyone follows it, so a circuit can be understood at a glance. The display cable harness in this book uses the same scheme.

    **Concept Tested:** Wire Color Coding

    **See:** [Wire Color Coding](index.md#wire-color-coding)

---

#### 3. Why should a 5 V output never be wired directly into a Raspberry Pi Pico input pin?

<div class="upper-alpha" markdown>
1. The GPIO pins are not 5 V tolerant, so the signal can permanently damage the pin
2. A 5 V signal changes too slowly for the RP2040 chip to read it
3. The Pico can only use its pins as outputs and never as inputs
4. The Pico always reads a 5 V signal as a logical 0
</div>

??? question "Show Answer"
    The correct answer is **A**. The Pico uses 3.3 V logic, and its GPIO pins can be damaged by a 5 V signal. Going from the Pico to a 5 V part usually works, but the reverse direction is dangerous. Use a voltage divider or a level shifter to bring a 5 V output down to a safe level. Always check a part's datasheet for its logic level before wiring it.

    **Concept Tested:** 3.3V vs 5V Logic

    **See:** [3.3 V vs 5 V Logic](index.md#33-v-vs-5-v-logic)

---

#### 4. A red LED drops about 2.0 V and should run at about 10 mA from a 3.3 V pin. Which standard resistor value is the best choice?

<div class="upper-alpha" markdown>
1. 100 Ω
2. 130 Ω
3. 150 Ω
4. 47 Ω
</div>

??? question "Show Answer"
    The correct answer is **C**. The formula R = (3.3 − 2.0) / 0.010 gives 130 Ω, but resistors are sold only in standard values, and 130 Ω is not one of them. You choose the next standard value up, 150 Ω, which gives about 8.7 mA. A smaller resistor such as 100 Ω or 47 Ω lets more current flow than planned and risks the LED.

    **Concept Tested:** Current Limiting

    **See:** [Current Limiting](index.md#current-limiting)

---

#### 5. A voltage divider uses R1 = 1 kΩ on the input side and R2 = 2 kΩ on the ground side. What is the output voltage when the input is 5 V?

<div class="upper-alpha" markdown>
1. 1.67 V
2. 2.50 V
3. 5.00 V
4. 3.33 V
</div>

??? question "Show Answer"
    The correct answer is **D**. The divider formula is Vout = Vin × R2 / (R1 + R2). With the numbers given, that is 5 × 2000 / 3000 = 3.33 V, which is a safe level for a Pico pin. If you swapped the two resistors you would get 1.67 V instead. The output is always taken from the point between the two resistors.

    **Concept Tested:** Voltage Divider

    **See:** [Voltage Divider](index.md#voltage-divider)

---

#### 6. A resistor has the color bands red, violet, brown, gold. What is its value?

<div class="upper-alpha" markdown>
1. 2.7 kΩ
2. 270 Ω
3. 27 Ω
4. 2,710 Ω
</div>

??? question "Show Answer"
    The correct answer is **B**. Read the first two bands as digits: red is 2 and violet is 7, giving 27. The third band is the multiplier, and brown means ×10, so the value is 27 × 10 = 270 Ω. The gold band means the real value is within ±5% of that. Forgetting the multiplier would give 27 Ω, and a multiplier of ×100 would give 2.7 kΩ.

    **Concept Tested:** Resistor Values

    **See:** [Resistor Values](index.md#resistor-values)

---

#### 7. Why does an LED connected directly across a power source usually burn out?

<div class="upper-alpha" markdown>
1. Its voltage stays nearly fixed as current rises, so nothing limits the current
2. It becomes a very high resistance that blocks the current
3. Its anode and cathode swap places when the power is turned on
4. It converts the supply voltage into a higher voltage by itself
</div>

??? question "Show Answer"
    The correct answer is **A**. An LED has a roughly fixed forward voltage, so unlike a resistor its voltage does not rise with current. That means the current is not self-limiting, and far too much can flow. A series resistor uses Ohm's Law on the extra voltage the LED does not use and sets the current to a safe level, often 330 Ω is a safe choice on a 3.3 V pin.

    **Concept Tested:** LED Basics

    **See:** [LED Basics](index.md#led-basics)

---

#### 8. Two part legs are pushed into holes a10 and c10 in the same terminal strip of a breadboard. What is the result?

<div class="upper-alpha" markdown>
1. They are not connected because they sit in different holes
2. They are connected only if a jumper crosses the center gap
3. They are electrically connected because the holes in a strip are joined
4. They are connected only through the power rail at the board edge
</div>

??? question "Show Answer"
    The correct answer is **C**. Each row of five holes in a terminal strip is connected underneath as one conductor, so two legs in the same strip are shorted together. This is why parts must be placed so each leg lands in a different strip. The center gap separates the two halves so chips can straddle it, and power rails run along the edges as separate long lines.

    **Concept Tested:** Breadboard

    **See:** [Breadboard](index.md#breadboard)

---

#### 9. Why is the switching regulator on the Pico better for battery power than a linear regulator?

<div class="upper-alpha" markdown>
1. It converts voltage efficiently and wastes little energy as heat
2. It burns off extra voltage as heat so the output stays smooth
3. It raises the 3.3 V logic level up to 5 V for the GPIO pins
4. It stores charge in a coin cell so the board never loses power
</div>

??? question "Show Answer"
    The correct answer is **A**. A switching regulator rapidly turns current on and off to convert voltage with little waste. A linear regulator simply burns the extra voltage as heat, so dropping 5 V to 3.3 V at 100 mA wastes about 0.17 W. Efficiency matters on a battery, which is why the Pico can run well from one. The Pico's pins stay at 3.3 V logic, and coin cells are used only for real-time clocks.

    **Concept Tested:** Voltage Regulator

    **See:** [Voltage Regulator](index.md#voltage-regulator)

---

#### 10. A display shows nothing. A multimeter set to DC voltage across the display's VCC and GND pins reads 3.3 V. What does this reading most strongly suggest?

<div class="upper-alpha" markdown>
1. Power never arrived at the display, so the power wire is broken
2. The ground wire is missing, so the display has no return path
3. The Pico is damaged, so the display cannot be powered
4. Power is arriving correctly, so the fault is elsewhere, such as a data wire
</div>

??? question "Show Answer"
    The correct answer is **D**. A reading of 3.3 V between VCC and GND proves the display has both power and ground. A reading of 0 V would mean power never arrived, and a missing ground would also prevent a proper reading. With power confirmed, you continue the search at the next suspect, such as a loose or misplaced data wire. A multimeter turns guessing into a step-by-step diagnosis.

    **Concept Tested:** Multimeter Usage

    **See:** [Multimeter Usage](index.md#multimeter-usage)
