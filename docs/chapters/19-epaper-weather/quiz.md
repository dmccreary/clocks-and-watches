# Quiz: E-Paper and Weather Displays

Test your understanding of e-paper technology, refresh strategies, ghosting, and weather station design with these review questions.

---

#### 1. Which signal on an e-paper module tells the Pico that the display is still refreshing?

<div class="upper-alpha" markdown>
1. D/C
2. /RST
3. BUSY
4. /CS
</div>

??? question "Show Answer"
    The correct answer is **C**. Most e-paper modules connect over SPI with one extra signal, BUSY. Refreshing takes a while, and the display raises BUSY to say it is still updating. Your program should wait for BUSY to clear before sending more data. The D/C pin separates commands from data, /RST restarts the chip, and /CS selects the device on the SPI bus.

    **Concept Tested:** E-Paper Display

    **See:** [E-Paper Display](index.md#e-paper-display)

---

#### 2. What does it mean to say that an e-paper display is bistable?

<div class="upper-alpha" markdown>
1. It has two backlights, one for the day and one for the night
2. It has two stable states that it keeps without power, so power is needed only to change a pixel
3. It can show only two colors, black and white, at the same time
4. It uses two SPI buses to double the speed of each refresh
</div>

??? question "Show Answer"
    The correct answer is **B**. A bistable display, like a light switch that stays where you flip it, holds either state with no power at all. E-paper particles stay where the electric field left them, so energy is used only to change a pixel, never to hold one. A clock that updates once a minute therefore spends nearly all its time drawing zero power, and a small battery can last for months.

    **Concept Tested:** Bistable Display

    **See:** [Bistable Display](index.md#bistable-display)

---

#### 3. What is e-paper ghosting, and what clears it?

<div class="upper-alpha" markdown>
1. A burn-in that is permanent and requires replacing the panel
2. A flicker caused by a backlight that is dimmed with PWM
3. A color shift that appears when the panel is viewed from the side
4. A faint shadow of the previous image, which a full refresh clears
</div>

??? question "Show Answer"
    The correct answer is **D**. Ghosting is a faint shadow of the previous image that remains after a refresh, because the particles do not move all the way each time. It is most noticeable in a large dark area that was replaced with white. It is not permanent: a full refresh clears it. The best defense is a schedule that mixes quick partial updates with an occasional full one.

    **Concept Tested:** E-Paper Ghosting

    **See:** [E-Paper Ghosting](index.md#e-paper-ghosting)

---

#### 4. A DHT22 sensor reports 25 °C. What is that in degrees Fahrenheit, using F = C × 9/5 + 32?

<div class="upper-alpha" markdown>
1. 77 °F
2. 57 °F
3. 45 °F
4. 98 °F
</div>

??? question "Show Answer"
    The correct answer is **A**. Multiply 25 by 9/5 to get 45, then add 32 to get 77 °F. The value 45 results from forgetting the final 32, and 57 comes from simply adding 32 to the Celsius number. For display, round the result with `round(f)`. The built-in 8 by 8 font has no degree symbol, so draw a small circle next to the number or use a custom font.

    **Concept Tested:** Temperature Display

    **See:** [Temperature Display](index.md#temperature-display)

---

#### 5. A clock redraws its e-paper display once every minute, but only when the minute changes. How many refreshes happen in one day?

<div class="upper-alpha" markdown>
1. 24
2. 60
3. 1,440
4. 86,400
</div>

??? question "Show Answer"
    The correct answer is **C**. There are 24 hours of 60 minutes each in a day, so 24 × 60 = 1,440 refreshes, which is well within a panel's rating of about a million updates. The test `if m != last_minute` is what turns a loop that runs every second into a refresh that happens once a minute. Refreshing 86,400 times a day, once per second, would wear the panel and waste energy.

    **Concept Tested:** E-Paper Refresh

    **See:** [E-Paper Refresh](index.md#e-paper-refresh)

---

#### 6. A weather display reads its indoor sensor every 5 minutes. How many indoor readings occur in one hour?

<div class="upper-alpha" markdown>
1. 1
2. 12
3. 60
4. 5
</div>

??? question "Show Answer"
    The correct answer is **B**. An hour has 60 minutes, and 60 / 5 = 12 readings. Indoor temperature and humidity change slowly, so reading every 5 to 10 minutes is enough. The time display updates every minute, and the outdoor forecast every 1 to 3 hours. Matching each item's update schedule to how fast it changes saves power, especially for the forecast, since each fetch needs WiFi.

    **Concept Tested:** Humidity Display

    **See:** [Weather Station Display](index.md#weather-station-display)

---

#### 7. An e-paper clock loses power and keeps showing 10:42 while the real time is 11:30. What design risk does this show?

<div class="upper-alpha" markdown>
1. The panel holds its image without power, so a stopped clock looks normal but is wrong
2. The panel loses its image immediately, so the display goes blank
3. The panel keeps updating itself from the internet without any power
4. The panel is showing ghosting, which will clear on its own after a few minutes
</div>

??? question "Show Answer"
    The correct answer is **A**. Because e-paper is bistable, it still shows the last time it drew when power fails, looking perfectly normal but wrong. A clock that cannot show it has stopped is confusing. A robust design also shows when it last synced, or displays a small warning if the time source fails. Ghosting is a different effect, a faint remnant of an earlier image.

    **Concept Tested:** Bistable Display

    **See:** [Bistable Display](index.md#bistable-display)

---

#### 8. After several days of partial refreshes only, an e-paper clock shows faint old digits smeared behind the current time. What is the cause and the fix?

<div class="upper-alpha" markdown>
1. The BUSY pin is not wired, so the fix is to add a pull-up resistor
2. The SPI baudrate is too high, so the fix is to lower it to 1 MHz
3. The panel is a three-color model, so the fix is to switch to black and white
4. Partial updates build up ghosting, so force a full refresh about every 30 partials and once a day
</div>

??? question "Show Answer"
    The correct answer is **D**. Partial updates are fast and quiet, but each one leaves a little more ghosting. A good strategy is a partial refresh each minute, a full refresh after about 30 partial updates, and a full refresh at least once a day. Keeping a counter of partial refreshes takes only two lines of code. A wiring or baudrate problem would corrupt the whole image, not leave faint old digits.

    **Concept Tested:** Partial E-Paper Refresh

    **See:** [Partial E-Paper Refresh](index.md#partial-e-paper-refresh)

---

#### 9. Which display is the best choice for a clock on a sunny porch that must run for weeks on a small battery and updates once a minute?

<div class="upper-alpha" markdown>
1. A TM1637 LED module
2. A round GC9A01 color TFT
3. An e-paper display
4. A NeoPixel ring
</div>

??? question "Show Answer"
    The correct answer is **C**. E-paper reflects room light, so it is readable in bright sun, and it uses power only when the picture changes, so a once-a-minute clock can last weeks or months on a small battery. LEDs and NeoPixels are hard to read in direct sunlight and draw power all the time they are lit. A color TFT's backlight is the largest power consumer on the display.

    **Concept Tested:** E-Paper Display

    **See:** [Choosing a Display](index.md#choosing-a-display)

---

#### 10. Which design is the most appropriate plan for a battery-powered weather station display?

<div class="upper-alpha" markdown>
1. Update time every minute, indoor readings every 5 to 10 minutes, and the forecast every 1 to 3 hours with WiFi on only during the fetch and the last good value kept on failure
2. Fetch the forecast every second so that the display is always up to date
3. Keep WiFi on all the time and stop the program if a fetch ever fails
4. Redraw every item with a full refresh each second to avoid ghosting
</div>

??? question "Show Answer"
    The correct answer is **A**. Each piece of data should have its own update schedule matched to how fast it changes. WiFi should be on only for the brief moment of a fetch, and the program should plan for failure by keeping the last good value or showing dashes such as `--`. Fetching every second wastes power and burdens the service, and refreshing a whole panel every second would wear it out quickly.

    **Concept Tested:** Weather Station Display

    **See:** [Weather Station Display](index.md#weather-station-display)
