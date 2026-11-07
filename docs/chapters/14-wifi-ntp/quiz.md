# Quiz: WiFi, NTP, and Time Accuracy

Test your understanding of WiFi connections, NTP time sync, time zones, daylight saving, and clock drift with these review questions.

---

#### 1. The timestamp in an NTP server's reply counts seconds from which starting date?

<div class="upper-alpha" markdown>
1. January 1, 1970
2. January 1, 2000
3. January 1, 1900
4. January 1, 1980
</div>

??? question "Show Answer"
    The correct answer is **C**. NTP counts from January 1, 1900. That is a third epoch beside the Unix epoch of 1970 and the MicroPython-on-the-Pico epoch of 2000. The `ntptime` library subtracts 3,155,673,600 seconds, the gap between 1900 and 2000, so you rarely handle this yourself. It does explain why raw NTP numbers look strange.

    **Concept Tested:** NTP Protocol

    **See:** [NTP Protocol](index.md#ntp-protocol)

---

#### 2. Which WiFi band can the Pico W connect to?

<div class="upper-alpha" markdown>
1. 2.4 GHz only
2. 5 GHz only
3. Both 2.4 GHz and 5 GHz
4. Neither, because it supports only Bluetooth
</div>

??? question "Show Answer"
    The correct answer is **A**. The Pico W supports 2.4 GHz WiFi only. If your network name exists only on the 5 GHz band, the Pico cannot see it. Networks that need a sign-in page or enterprise login also will not work directly. Ask your teacher for a compatible or guest network. The plain Pico has no wireless chip at all.

    **Concept Tested:** WiFi Connectivity

    **See:** [WiFi Connectivity](index.md#wifi-connectivity)

---

#### 3. Why is it recommended to keep the clock's internal time in UTC and convert to local time only when showing it?

<div class="upper-alpha" markdown>
1. UTC time is always shorter to store than local time
2. The Pico cannot store any time that has a time zone offset
3. UTC removes the need to ever sync with an NTP server
4. UTC is the same everywhere and ignores daylight saving, so changing zones changes one number
</div>

??? question "Show Answer"
    The correct answer is **D**. UTC is the same everywhere at any instant and does not change for daylight saving. If you store and compare times in UTC and convert only in the last step before drawing digits, moving the clock to another time zone or handling daylight saving changes one number in one place. The rule is to store and compare in UTC and convert to local time when showing it to a person.

    **Concept Tested:** UTC Time

    **See:** [UTC Time](index.md#utc-time)

---

#### 4. Why should WiFi credentials be kept in a separate `secrets.py` file that is listed in `.gitignore`?

<div class="upper-alpha" markdown>
1. Python cannot connect to WiFi unless the password is in its own file
2. It keeps the password out of code that may be shared or uploaded publicly
3. It makes the WiFi connection faster than typing the password in `main.py`
4. It lets the Pico use a 5 GHz network instead of 2.4 GHz
</div>

??? question "Show Answer"
    The correct answer is **B**. If you commit your password to a public Git repository, anyone can read it, and bots really do scan for such files. Keeping the SSID and password in `secrets.py` and adding it to `.gitignore` keeps them private. Commit a `secrets_example.py` with fake values so classmates know what to fill in. The separate file has no effect on connection speed or band.

    **Concept Tested:** Secrets File

    **See:** [Secrets File](index.md#secrets-file)

---

#### 5. A clock shows the right time while connected to Thonny but is several hours off when it runs alone. What explains this?

<div class="upper-alpha" markdown>
1. The WiFi chip adds a random offset to the time every few hours
2. Thonny stores the correct time in flash, and unplugging erases it
3. Thonny sets the Pico's clock to your computer's local time, while `ntptime` sets it to UTC
4. The Pico loses its DNS server as soon as the USB cable is removed
</div>

??? question "Show Answer"
    The correct answer is **C**. When Thonny connects, it sets the Pico's internal clock to your computer's local time. The `ntptime` library sets the same clock to UTC. A program written while connected to Thonny can therefore be off by the time zone offset when it runs alone. Pick one convention, preferably UTC inside with conversion for display, and test the program with Thonny unplugged.

    **Concept Tested:** Thonny Time Sync

    **See:** [Thonny Time Sync](index.md#thonny-time-sync)

---

#### 6. It is 02:40 UTC on the 10th. What is the local time in US Central Standard Time (UTC−6)?

<div class="upper-alpha" markdown>
1. 20:40 on the 9th
2. 08:40 on the 10th
3. 20:40 on the 10th
4. 02:40 on the 9th
</div>

??? question "Show Answer"
    The correct answer is **A**. Add the offset of −6 hours to 02:40 on the 10th. Going back six hours crosses midnight, so the local time is 20:40 on the previous day, the 9th. Because the conversion is done on a count of seconds, MicroPython carries the date back correctly without extra code. Option B wrongly adds six hours, and options C and D forget to change the date or the hour.

    **Concept Tested:** Timezone Conversion

    **See:** [Timezone Conversion](index.md#timezone-conversion)

---

#### 7. A clock is 2 seconds fast after 5 days (432,000 seconds). What is its drift?

<div class="upper-alpha" markdown>
1. About 0.46 ppm
2. About 2.0 ppm
3. About 46 ppm
4. About 4.6 ppm
</div>

??? question "Show Answer"
    The correct answer is **D**. Drift in ppm is the error divided by the elapsed time, times one million: 2 / 432,000 × 1,000,000 is about 4.6 ppm. That is a little worse than a DS3231 at room temperature. Measuring drift over several days like this is the first step in calibrating a clock, which is useful for an offline DS3231 clock that must be very accurate.

    **Concept Tested:** Clock Drift

    **See:** [Clock Drift](index.md#clock-drift)

---

#### 8. A clock drifts at 20 ppm and you can tolerate 0.5 seconds of error. About how often must it resynchronize?

<div class="upper-alpha" markdown>
1. About every hour
2. About every 7 hours
3. About every 24 hours
4. About every 3 days
</div>

??? question "Show Answer"
    The correct answer is **B**. The sync interval is the tolerated error divided by the drift rate. A drift of 20 ppm is 0.00002 seconds per second, so 0.5 / 0.00002 equals 25,000 seconds, which is about 7 hours. Syncing every hour is more often than needed, and syncing once a day or every three days would allow errors well above the 0.5 second limit.

    **Concept Tested:** Time Drift Compensation

    **See:** [Time Drift Compensation](index.md#time-drift-compensation)

---

#### 9. At startup, `ntptime.settime()` raises an `OSError` because the router is slow to answer. What is the best design?

<div class="upper-alpha" markdown>
1. Let the program crash so the user restarts the Pico
2. Remove the NTP code and set the time by hand every day
3. Wrap the call in `try/except`, retry a few times, then keep running and try again later
4. Call `ntptime.settime()` in a tight loop until it works
</div>

??? question "Show Answer"
    The correct answer is **C**. WiFi and NTP fail sometimes for ordinary reasons. A `try/except OSError` block with a few retries and a short sleep between them handles the failure. If it still fails, the clock should keep running on its own time and try again later. A clock that keeps ticking is better than one that stops to argue with the router, and hammering a shared server in a tight loop is impolite.

    **Concept Tested:** NTP Time Sync

    **See:** [NTP Time Sync](index.md#ntp-time-sync)

---

#### 10. A wall clock has no WiFi and must stay within about one minute per year. Which time source is the best choice?

<div class="upper-alpha" markdown>
1. A DS3231 with a coin-cell backup, which drifts about 5 seconds per month
2. The Pico's internal RTC, which drifts about 16 minutes per year
3. Thonny time sync, which sets the clock whenever the Pico loses power
4. NTP over WiFi, which gives millisecond accuracy with no network
</div>

??? question "Show Answer"
    The correct answer is **A**. A DS3231 at about 2 ppm drifts roughly 5 seconds a month, which is about one minute a year, and its battery lets it survive power-off. The internal RTC at 30 ppm drifts around 16 minutes a year and forgets the time at power-off. Thonny sync needs a computer over USB, and NTP needs WiFi, which this clock does not have.

    **Concept Tested:** Time Source Comparison

    **See:** [Time Source Comparison](index.md#time-source-comparison)
