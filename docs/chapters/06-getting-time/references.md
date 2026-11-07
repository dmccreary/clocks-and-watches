# References: Getting the Time in MicroPython

1. [Unix time](https://en.wikipedia.org/wiki/Unix_time) - Wikipedia - Explains the count of seconds since the 1970 epoch and how timestamps are converted to dates. Directly supports this chapter's epoch time, Unix timestamp, and time math sections.

2. [12-hour clock](https://en.wikipedia.org/wiki/12-hour_clock) - Wikipedia - Covers the AM/PM convention, its history, and the ambiguity of noon and midnight. Useful background for the chapter's 12-hour versus 24-hour formatting and AM/PM conversion code.

3. [Leap year](https://en.wikipedia.org/wiki/Leap_year) - Wikipedia - Describes why calendars add an extra day and gives the Gregorian rule (divisible by 4, except centuries not divisible by 400). It is the basis for the chapter's leap year handling.

4. Calendrical Calculations (4th Edition) - Nachum Dershowitz and Edward M. Reingold - Cambridge University Press - The authors convert between calendars by mapping every date to one fixed day number (Rata Die). This single-counter idea mirrors epoch time and makes time math simple.

5. Automate the Boring Stuff with Python (3rd Edition) - Al Sweigart - No Starch Press - No single originator exists here; this is chosen as the beginner text most praised for clarity. Its chapter on keeping time shows epoch timestamps, time.sleep(), and readable date formatting.

6. [time - Time related functions](https://docs.micropython.org/en/latest/library/time.html) - MicroPython Documentation - Official reference for localtime(), sleep(), ticks_ms(), and ticks_diff() on the Pico. It also explains why tick values wrap and must be compared with ticks_diff().

7. [time - Time access and conversions](https://docs.python.org/3/library/time.html) - Python Documentation - Defines the time tuple fields, the epoch, and the strftime() format codes. It is a reliable way to compare full Python behavior with the smaller MicroPython time module.

8. [Raspberry Pi Pico: DS1307 RTC Module - Keep Track of Time (MicroPython)](https://randomnerdtutorials.com/raspberry-pi-pico-ds1307-rtc-micropython/) - Random Nerd Tutorials - Shows time.localtime() being converted into a tuple used to set a real-time clock, then read back. It previews the time-keeping problem this chapter introduces.

9. [Python strftime Cheatsheet](https://www.bairesdev.com/tools/strftime/) - BairesDev - A quick table of format codes such as %H, %I, %M, %S, and %p with examples. Handy for planning clock strings like 3:07 PM and for checking 12-hour output.

10. [Epoch Converter](https://www.epochconverter.com/) - EpochConverter - An interactive tool that turns Unix timestamps into readable dates and back, showing the current epoch count. Students can use it to check their own epoch and timestamp calculations.
