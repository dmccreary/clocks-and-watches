# Quiz: Buttons, Interrupts, and State Machines

Test your understanding of button wiring, debouncing, interrupts, state machines, and rotary encoders with these review questions.

---

#### 1. What is contact bounce?

<div class="upper-alpha" markdown>
1. A wiring mistake that happens when both legs are on the same side of the button
2. The delay Python adds between two quick presses of the same button
3. A burst of rapid on/off pulses as metal contacts collide and spring apart
4. A voltage drop that appears when the internal pull-up is turned on
</div>

??? question "Show Answer"
    The correct answer is **C**. A mechanical switch is not a clean on/off device. When its contacts close they chatter for a few milliseconds up to about 20 ms before settling. A human sees one press, but the fast Pico can see the burst as ten presses. Debouncing is any technique that ignores the bounce so one physical press counts as exactly one event.

    **Concept Tested:** Button Debouncing

    **See:** [Button Debouncing](index.md#button-debouncing)

---

#### 2. Which trigger makes an interrupt handler run at the instant a pull-up button is pressed?

<div class="upper-alpha" markdown>
1. `Pin.IRQ_RISING`
2. `Pin.IRQ_FALLING`
3. `Pin.PULL_UP`
4. `Pin.OUT`
</div>

??? question "Show Answer"
    The correct answer is **B**. A pull-up button is active low, so the pin goes from 1 to 0 when it is pressed. That change from high to low is a falling edge. `Pin.IRQ_RISING` would fire when the button is released, and you can combine both constants with the `|` operator to hear press and release. `Pin.PULL_UP` and `Pin.OUT` configure the pin and are not interrupt triggers.

    **Concept Tested:** IRQ Falling Edge

    **See:** [IRQ Falling Edge](index.md#irq-falling-edge)

---

#### 3. Why should an interrupt handler just set a flag instead of drawing on the display?

<div class="upper-alpha" markdown>
1. Flags are the only variables that a handler is allowed to read
2. Handlers cannot be attached to pins that also drive displays
3. Drawing code stops working when a button has a pull-up resistor
4. A handler must finish quickly, so the main loop should do the heavy work
</div>

??? question "Show Answer"
    The correct answer is **D**. An interrupt handler pauses your main code, so it must be short and fast. Long work such as drawing or a `sleep()` call inside it causes trouble. The recommended pattern is to set `pressed = True` and return, then let the main loop notice the flag, clear it, and do the real work. This keeps handlers quick and your display code safe.

    **Concept Tested:** Callback Functions

    **See:** [Callback Functions](index.md#callback-functions)

---

#### 4. A four-leg tactile switch never seems to work when it is wired using two legs on the same side. Why?

<div class="upper-alpha" markdown>
1. Legs on the same side are always joined, so pressing the button changes nothing between them
2. The button needs an external resistor on each of the two legs that are used
3. Tactile switches work only when all four legs are connected to a pin
4. The two legs on the same side are connected only while the button is held
</div>

??? question "Show Answer"
    The correct answer is **A**. Inside the case, the four legs form two pairs, and the legs on the same side of each pair are always connected. Pressing the button joins the two pairs to each other. So a connection that uses two legs from the same pair will never see a change. Wire the button between a leg of one pair and a leg of the opposite pair, such as across the breadboard center gap.

    **Concept Tested:** Momentary Push Button

    **See:** [Momentary Push Button](index.md#momentary-push-button)

---

#### 5. How can the same Mode button do different things in a clock with RUN, SET_HOUR, and SET_MINUTE?

<div class="upper-alpha" markdown>
1. Each state has its own wire connected to a different GPIO pin
2. What a press does depends on the state the program is currently in
3. The button changes its resistance each time it is pressed
4. The interrupt handler is replaced by a new one after every press
</div>

??? question "Show Answer"
    The correct answer is **B**. A state machine organizes a program around named states, and each state defines what happens on an event. In RUN, a Mode press goes to SET_HOUR, and in SET_HOUR it goes to SET_MINUTE. The question to ask is "What state am I in, and what does this event do there?" That is how two buttons can control a whole clock interface.

    **Concept Tested:** State Machine

    **See:** [State Machine](index.md#state-machine)

---

#### 6. A software debounce window is 50 ms. A press was accepted at 1,000 ms. Later events arrive at 1,012 ms, 1,030 ms, and 1,200 ms. Which events are accepted?

<div class="upper-alpha" markdown>
1. Only the event at 1,012 ms
2. The events at 1,012 ms and 1,030 ms
3. Only the event at 1,200 ms
4. All three of the events
</div>

??? question "Show Answer"
    The correct answer is **C**. The `ticks_diff(now, last_press) > 50` test rejects anything that arrives within 50 ms of the last accepted press. The events at 1,012 ms and 1,030 ms are only 12 ms and 30 ms later, so they are bounce and are ignored. The event at 1,200 ms is 200 ms later, so it counts as a new press. A window of 20 to 50 ms stops bounce but still feels instant.

    **Concept Tested:** Software Debounce

    **See:** [Software Debounce](index.md#software-debounce)

---

#### 7. A clock uses `MODES = ["RUN", "SET_HOUR", "SET_MINUTE"]` and `mode = (mode + 1) % len(MODES)`. The current mode is SET_MINUTE. What happens when the Mode button is pressed?

<div class="upper-alpha" markdown>
1. The mode moves to SET_HOUR
2. The mode stays at SET_MINUTE
3. The program stops with an `IndexError`
4. The mode wraps back around to RUN
</div>

??? question "Show Answer"
    The correct answer is **D**. SET_MINUTE is at index 2, so `(2 + 1) % 3` equals 0, which is the index of RUN. The modulo operator makes the mode wrap from the last state back to the first, and no index ever goes past the end of the list. After three presses from RUN you are back to RUN. The Cycle button uses the same wrap trick with `% 24` for hours and `% 60` for minutes.

    **Concept Tested:** Mode Cycling

    **See:** [Mode Cycling](index.md#mode-cycling)

---

#### 8. A 0.1 µF capacitor is placed across a button that uses the internal 50 kΩ pull-up. What is the time constant R × C?

<div class="upper-alpha" markdown>
1. About 5 ms
2. About 50 ms
3. About 0.5 ms
4. About 500 ms
</div>

??? question "Show Answer"
    The correct answer is **A**. Multiply 50,000 Ω by 0.0000001 F to get 0.005 seconds, or 5 ms. That is on the same order as typical contact bounce, so the capacitor smooths the rapid changes with no extra code. This is hardware debouncing. In this course, software debouncing is more common because it needs no extra parts.

    **Concept Tested:** Hardware Debounce

    **See:** [Hardware Debounce](index.md#hardware-debounce)

---

#### 9. A decoder runs on each falling edge of signal A and reads signal B at that moment. Why does reading B reveal the direction of rotation?

<div class="upper-alpha" markdown>
1. A and B are offset by a quarter cycle, so B has a different level at A's edge for each direction
2. B stays at 1 when the knob turns clockwise and at 0 when it turns counterclockwise
3. B counts the number of clicks while A measures the speed of the turn
4. A and B always change at exactly the same instant in either direction
</div>

??? question "Show Answer"
    The correct answer is **A**. The two encoder switches produce a quadrature pattern in which A and B change in a fixed order, offset by a quarter of a cycle. Clockwise gives the sequence 00, 10, 11, 01, and counterclockwise gives it in reverse. So at a falling edge of A, B is high for one direction and low for the other. Swap the two directions if your knob feels backward.

    **Concept Tested:** Encoder Direction

    **See:** [Encoder Direction](index.md#encoder-direction)

---

#### 10. A time-setting program polls a button inside a loop that redraws the display and then sleeps for two seconds. Short presses are often missed. What is the best fix?

<div class="upper-alpha" markdown>
1. Add a larger capacitor across the button to stretch each press
2. Increase the debounce window to 500 ms so presses last longer
3. Attach an `irq()` handler on the falling edge that sets a flag for the main loop
4. Change the pull-up to a pull-down so the button reads 1 when pressed
</div>

??? question "Show Answer"
    The correct answer is **C**. Polling only sees the pin when the loop asks, so a press that starts and ends during the two-second sleep is never noticed. An interrupt lets the hardware watch the pin and run a short handler the moment it changes, so no press is missed. The handler sets a flag, and the main loop does the work. A longer debounce window or a different pull does not help with missed presses.

    **Concept Tested:** Interrupt Handlers

    **See:** [Interrupt Handlers](index.md#interrupt-handlers)
