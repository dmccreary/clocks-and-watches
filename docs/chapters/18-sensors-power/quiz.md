# Quiz: Sensors, Power, and Low-Power Design

Test your understanding of ADC readings, light and motion sensors, hysteresis, batteries, and low-power design with these review questions.

---

#### 1. Which Pico pins can be used as analog (ADC) inputs?

<div class="upper-alpha" markdown>
1. GP0, GP1, and GP2
2. GP26, GP27, and GP28
3. GP14, GP15, and GP16
4. Any GPIO pin on the board
</div>

??? question "Show Answer"
    The correct answer is **B**. The Pico's ADC has three usable inputs on GP26, GP27, and GP28, which are channels ADC0, ADC1, and ADC2. They measure voltages from 0 V to 3.3 V. The other pins can only tell 0 from 1. Because ADC readings jitter a little even when nothing changes, it helps to read the pin 8 or 16 times and use the average.

    **Concept Tested:** ADC Reading

    **See:** [ADC Reading](index.md#adc-reading)

---

#### 2. The RP2040 ADC has 12 bits of resolution, yet `read_u16()` returns values from 0 to 65,535. Why?

<div class="upper-alpha" markdown>
1. The RP2040 hardware contains a separate 16-bit converter for each pin
2. The value is the voltage in millivolts, which can reach 65,535
3. The reading counts the number of times the pin was sampled each second
4. MicroPython scales the 12-bit result up to 16 bits so the range is always the same
</div>

??? question "Show Answer"
    The correct answer is **D**. The hardware gives 2^12 = 4,096 levels, and MicroPython scales the result to a 16-bit range, so the value runs from 0 to 65,535 no matter how many bits the hardware has. To convert to volts, multiply by 3.3 and divide by 65,535. A reading of 32,768 is about half of full scale, or 1.65 V.

    **Concept Tested:** ADC Reading

    **See:** [ADC Reading](index.md#adc-reading)

---

#### 3. How does hysteresis stop a display from flickering when the room light hovers near a threshold?

<div class="upper-alpha" markdown>
1. It uses two thresholds with a dead zone, so noise near the line does not toggle the output
2. It averages 16 readings so the sensor value never changes at all
3. It slows the PWM frequency of the backlight below 1 kHz
4. It rounds the light reading to the nearest whole brightness level
</div>

??? question "Show Answer"
    The correct answer is **A**. With one threshold, noise near the line makes the output chatter. Hysteresis uses a higher threshold to switch up and a lower one to switch back down. The gap between them is a dead zone where nothing changes, so small noise falls inside it. This is the same idea as debouncing a button in Chapter 7, and thermostats use it so a furnace does not switch on and off every few seconds.

    **Concept Tested:** Hysteresis

    **See:** [Hysteresis](index.md#hysteresis)

---

#### 4. An LDR is wired in a divider with a 10 kΩ fixed resistor between the ADC pin and ground, and 3.3 V on the LDR side. What is Vout when the LDR is 5 kΩ?

<div class="upper-alpha" markdown>
1. 1.1 V
2. 3.3 V
3. 2.2 V
4. 0.55 V
</div>

??? question "Show Answer"
    The correct answer is **C**. The formula is Vout = 3.3 × R_fixed / (R_LDR + R_fixed), which gives 3.3 × 10 / (5 + 10) = 2.2 V. With this wiring a brighter room lowers the LDR's resistance and raises Vout, so a bigger ADC reading means brighter light. The value 0.55 V is the output for a dim room, where the LDR is about 50 kΩ.

    **Concept Tested:** Light Dependent Resistor

    **See:** [Light-Dependent Resistor](index.md#light-dependent-resistor)

---

#### 5. A clock draws an average of 50 mA from a 2,000 mAh battery. Using the 0.8 factor, about how long will it run?

<div class="upper-alpha" markdown>
1. About 40 hours
2. About 32 hours
3. About 25 hours
4. About 16 hours
</div>

??? question "Show Answer"
    The correct answer is **B**. The runtime formula is capacity × 0.8 divided by average current, so 2,000 × 0.8 / 50 = 32 hours. The 0.8 factor allows for the fact that batteries never deliver their full labeled capacity. Leaving it out would give 40 hours, which is too optimistic. Measure your own current by placing a multimeter in series with the power wire.

    **Concept Tested:** Current Draw Calculation

    **See:** [Battery Power](index.md#battery-power)

---

#### 6. Which of these power sources should NOT be connected to the Pico's VSYS pin, whose limit is 5.5 V?

<div class="upper-alpha" markdown>
1. A 2 × AA pack at 3.0 V
2. A 3 × AA pack at 4.5 V
3. A single LiPo cell at 3.7 V
4. A 4 × AA alkaline pack at 6.0 V
</div>

??? question "Show Answer"
    The correct answer is **D**. The VSYS pin accepts 1.8 V to 5.5 V, and the board's regulator converts that to 3.3 V. Four alkaline AA cells give 6.0 V, which exceeds the limit. A 3 × AA pack at 4.5 V is the recommended choice, and the 2 × AA pack and the LiPo cell are both inside the allowed range.

    **Concept Tested:** AA Battery Pack

    **See:** [AA Battery Pack](index.md#aa-battery-pack)

---

#### 7. A LiPo battery is wired to a watch board that has no protection circuit. Why is it risky to connect the connector with reversed polarity?

<div class="upper-alpha" markdown>
1. Reversed polarity can destroy the board or even start a fire
2. Reversed polarity only makes the battery charge more slowly
3. Reversed polarity makes the display show colors in the wrong order
4. Reversed polarity is harmless because LiPo cells are 3.7 V
</div>

??? question "Show Answer"
    The correct answer is **A**. LiPo connectors are not always standardized, and reversing the polarity can destroy a board or start a fire. LiPo cells also need a charging circuit designed for lithium cells, ideally with a protection circuit against over-discharge and short circuits. Never discharge one below about 3.0 V, puncture or crush it, or charge one that is swollen.

    **Concept Tested:** LiPo Battery

    **See:** [LiPo Battery](index.md#lipo-battery)

---

#### 8. A battery-powered Pico runs fine until the WiFi sync starts, and then it resets. The battery is nearly empty. What is the most likely cause?

<div class="upper-alpha" markdown>
1. The hysteresis thresholds are set too close together
2. The ADC reading has overflowed its 16-bit range
3. A brownout: the WiFi surge makes the weak battery sag below what the chip needs
4. The LDR divider has a fixed resistor that is too small
</div>

??? question "Show Answer"
    The correct answer is **C**. A brownout is when the supply voltage sags below what the chip needs, but not all the way to zero. It often happens when a load surges, such as WiFi transmission, a backlight, or NeoPixels turning on, and the battery or a thin wire cannot deliver the current. Print `machine.reset_cause()` at startup to see if resets are power problems. Fixes include a fresher battery and a capacitor near the power pins.

    **Concept Tested:** Brownout Detection

    **See:** [Brownout Detection](index.md#brownout-detection)

---

#### 9. A student integrates a gyroscope's rotation rate to estimate an angle. After a minute with the board sitting still, the angle has slowly wandered. What explains this, and what is a good remedy?

<div class="upper-alpha" markdown>
1. The gyroscope measures gravity, so it cannot ever be still
2. Tiny errors add up as the rate is integrated, so combine it with the accelerometer's stable tilt
3. The I2C address conflicts with the DS3231, so the gyroscope returns random values
4. The ADC noise adds to the rate, so the reading should be averaged 16 times
</div>

??? question "Show Answer"
    The correct answer is **B**. A gyroscope reports how fast the board is rotating, not which way is down. Adding up (integrating) the rate gives an angle, but tiny errors accumulate, so the angle drifts. An accelerometer gives a stable but noisy tilt from gravity. The two sensors complement each other: the gyroscope is smooth but drifts, and the accelerometer is stable but noisy.

    **Concept Tested:** Gyroscope Basics

    **See:** [Gyroscope Basics](index.md#gyroscope-basics)

---

#### 10. A smartwatch draws about 85 mA, and its backlight alone uses about 60 mA. Which change would save the most battery life?

<div class="upper-alpha" markdown>
1. Replace the DS3231 with a different RTC chip
2. Use shorter wires between the display and the Pico
3. Raise the CPU speed so that the program finishes sooner
4. Dim the backlight and sleep between updates
</div>

??? question "Show Answer"
    The correct answer is **D**. The display is the biggest target for savings. In the chapter's example, dimming the backlight from 60 mA to 20 mA cuts the total from 85 mA to about 45 mA and roughly doubles the runtime. Sleeping between updates with a timer or RTC alarm as the wake source saves still more. The DS3231 uses under 1 mA, so replacing it would save almost nothing.

    **Concept Tested:** Low Power Mode

    **See:** [Low Power Mode](index.md#low-power-mode)
