# Quiz: Sound, Alarms, and Timers

Test your understanding of PWM sound, I2S audio, alarms with snooze, stopwatches, and countdown timers with these review questions.

---

#### 1. What setting determines the pitch of a tone made with PWM?

<div class="upper-alpha" markdown>
1. The duty cycle of the signal
2. The supply voltage of the Pico
3. The GPIO pin number that is used
4. The frequency of the signal
</div>

??? question "Show Answer"
    The correct answer is **D**. Pitch depends on frequency, the number of vibrations per second, so `buzzer.freq(440)` plays the note A above middle C. The duty cycle sets the tone's character and, to a small extent, its loudness. A higher note is nothing more than a faster wiggle, and doubling the frequency raises the pitch by one octave.

    **Concept Tested:** PWM Sound

    **See:** [PWM Sound](index.md#pwm-sound)

---

#### 2. Which type of piezo buzzer needs a PWM signal and lets you play melodies?

<div class="upper-alpha" markdown>
1. A passive buzzer
2. An active buzzer
3. Both types, equally
4. Neither type
</div>

??? question "Show Answer"
    The correct answer is **A**. A passive buzzer has no oscillator of its own, so it needs a PWM signal and you choose the pitch. An active buzzer has a built-in oscillator and beeps at one fixed pitch when powered. A quick test tells them apart: an active buzzer connected to 3.3 V beeps by itself, but a passive one only clicks.

    **Concept Tested:** Piezo Buzzer

    **See:** [Piezo Buzzer](index.md#piezo-buzzer)

---

#### 3. Why should an 8 ohm speaker not be connected directly to a GPIO pin?

<div class="upper-alpha" markdown>
1. Speakers only work with 5 V signals and cannot use 3.3 V
2. A pin cannot produce frequencies in the range that speakers need
3. The speaker would ask for about 410 mA, far more than a pin can safely supply
4. Speakers need an I2S connection and cannot work with PWM
</div>

??? question "Show Answer"
    The correct answer is **C**. By Ohm's Law, 3.3 V across 8 Ω asks for roughly 410 mA, many times what a GPIO pin can give, and it can damage the pin. Use a small amplifier module or a transistor between the pin and the speaker. A piezo buzzer draws only a few milliamps and can be wired straight to a pin.

    **Concept Tested:** Speaker Output

    **See:** [Speaker Output](index.md#speaker-output)

---

#### 4. At a sampling rate of 16,000 samples per second, what is the highest pitch that can be reproduced?

<div class="upper-alpha" markdown>
1. 16,000 Hz
2. 8,000 Hz
3. 32,000 Hz
4. 4,000 Hz
</div>

??? question "Show Answer"
    The correct answer is **B**. The Nyquist limit says the highest reproducible frequency is half the sampling rate, so 16,000 / 2 = 8,000 Hz. That is plenty for beeps and speech. CDs use 44,100 samples per second so they can reach 22,050 Hz, above human hearing. Higher rates cost more memory and bus time because each sample must be delivered on time.

    **Concept Tested:** Audio Sampling Rate

    **See:** [Audio Sampling Rate](index.md#audio-sampling-rate)

---

#### 5. Why does an alarm program use a `fired` flag?

<div class="upper-alpha" markdown>
1. It speeds up the comparison between the current time and the alarm time
2. It stores the snooze time so the alarm can ring again later
3. It lets the alarm ring even when the seconds are not exactly 0
4. It makes the alarm ring once during the matching minute instead of restarting after being stopped
</div>

??? question "Show Answer"
    The correct answer is **D**. The alarm condition `h == alarm_h and m == alarm_m` stays true for a whole minute. Without a flag, the alarm would start ringing again right after you stopped it, until the minute passed. The `fired` flag is set when the alarm starts and cleared once the minute is over. Comparing only the hour and minute is what lets the alarm still fire if the loop was busy at second 0.

    **Concept Tested:** Alarm Clock Features

    **See:** [Alarm Clock Features](index.md#alarm-clock-features)

---

#### 6. Using f = 440 × 2^(n/12), what is the frequency of the note 12 semitones below A440?

<div class="upper-alpha" markdown>
1. 220 Hz
2. 110 Hz
3. 330 Hz
4. 261.6 Hz
</div>

??? question "Show Answer"
    The correct answer is **A**. With n = −12 the formula gives 440 × 2^(−1) = 220 Hz. Going up or down by an octave, which is 12 semitones, exactly doubles or halves the frequency. The value 261.6 Hz is middle C, which is 9 semitones below A440, and 110 Hz would be two octaves down.

    **Concept Tested:** Alarm Tones

    **See:** [PWM Sound](index.md#pwm-sound)

---

#### 7. What does `snooze(22, 58, 9)` return if it adds minutes using seconds since midnight and wraps at 86,400?

<div class="upper-alpha" markdown>
1. (22, 67)
2. (23, 7)
3. (0, 7)
4. (23, 67)
</div>

??? question "Show Answer"
    The correct answer is **B**. The alarm at 22:58 is 82,680 seconds after midnight, and adding 9 minutes (540 seconds) gives 83,220. Dividing by 3,600 gives hour 23 with 420 seconds left over, which is 7 minutes. Working in seconds handles the carry automatically, and the `% 86400` wraps correctly past midnight. A minute value of 67 is impossible on a clock.

    **Concept Tested:** Snooze Function

    **See:** [Snooze Function](index.md#snooze-function)

---

#### 8. How many bytes per second does 22,050 Hz, 16-bit, stereo (2 channels) audio need?

<div class="upper-alpha" markdown>
1. 22,050 bytes per second
2. 44,100 bytes per second
3. 88,200 bytes per second
4. 352,800 bytes per second
</div>

??? question "Show Answer"
    The correct answer is **C**. Use data rate = rate × (bits / 8) × channels. Here that is 22,050 × 2 × 2 = 88,200 bytes per second. Mono audio would need half as much, 44,100 bytes per second. These numbers show why a long recording will not fit in the Pico's RAM and must be generated on the fly or streamed from flash.

    **Concept Tested:** Audio Sampling Rate

    **See:** [Audio Sampling Rate](index.md#audio-sampling-rate)

---

#### 9. An alarm plays its tone list with `sleep_ms()` between notes, and pressing snooze does nothing until the whole tune ends. What is the cause and the fix?

<div class="upper-alpha" markdown>
1. The sleeps stop the loop from checking buttons; step through the tones with `ticks_diff()` instead
2. The buzzer is an active type; replace it with a passive one
3. The snooze button needs an external pull-up resistor to be read
4. The tones are too long; shorten each note to under 50 ms
</div>

??? question "Show Answer"
    The correct answer is **A**. While the program sleeps, it does nothing else, so it cannot read buttons or update the display. A better design keeps an index into the tone list and a start time, and moves on when `ticks_diff()` says the current note is finished, checking the buttons on every pass of the loop. An alarm that freezes the whole clock while beeping is a bad alarm.

    **Concept Tested:** Alarm Tones

    **See:** [Alarm Tones](index.md#alarm-tones)

---

#### 10. A stopwatch resumes after a pause but the displayed total jumps back to near zero. What is the most likely bug?

<div class="upper-alpha" markdown>
1. The `ticks_ms()` counter wrapped around during the pause
2. The loop delay of 50 ms is too short to measure time
3. The button was configured without `Pin.PULL_UP`
4. The elapsed time was not saved into the accumulated total before the pause
</div>

??? question "Show Answer"
    The correct answer is **D**. When the stopwatch stops, it must save the elapsed time so far into a `saved` value. On restart it takes a new start tick and adds the saved time to what has elapsed since. If the pause step skips the save, the total restarts from the new start tick. The `ticks_ms()` counter wraps only after about 12.4 days, and `ticks_diff()` handles that anyway.

    **Concept Tested:** Stopwatch

    **See:** [Stopwatch](index.md#stopwatch)
