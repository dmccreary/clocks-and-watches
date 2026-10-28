# References: WiFi, NTP, and Time Accuracy

1. [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol) - Wikipedia - Explains how NTP synchronizes clocks across networks and organizes time sources into numbered strata from atomic reference clocks outward. It supports the chapter's NTP protocol, client-server, and stratum hierarchy sections.

2. [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) - Wikipedia - Describes UTC as the global time standard computed from atomic clocks, including leap seconds. It explains why NTP delivers UTC and why every local time zone is calculated from it.

3. [Daylight saving time](https://en.wikipedia.org/wiki/Daylight_saving_time) - Wikipedia - Covers the history and rules of shifting clocks forward in spring and back in autumn, and where it is used. It gives context for the chapter's daylight saving time function.

4. Computer Network Time Synchronization: The Network Time Protocol on Earth and in Space (2nd Edition) - David L. Mills - CRC Press - Written by the original developer of NTP, it explains the clock filtering, selection, and stratum design behind internet time. An authoritative source for how the ntptime library gets accurate time.

5. Computer Networking: A Top-Down Approach (8th Edition) - James F. Kurose and Keith W. Ross - Pearson - The authors' signature innovation is teaching networks starting from familiar applications and moving down to hardware. That order suits beginners wondering how a Pico W reaches an NTP server.

6. [network.WLAN](https://docs.micropython.org/en/latest/library/network.WLAN.html) - MicroPython Documentation - The official reference for the WLAN class, including connect, isconnected, scan, and status. It is the exact interface students use to join WiFi with an SSID and password.

7. [ntptime.py source](https://github.com/micropython/micropython-lib/blob/master/micropython/net/ntptime/ntptime.py) - MicroPython micropython-lib, GitHub - Short readable source of the ntptime module, showing the UDP request to port 123, the epoch offset, and settime setting the clock to UTC. Reading it demystifies the chapter's NTP sync example.

8. [Using pool.ntp.org](https://www.ntppool.org/en/use.html) - NTP Pool Project - Explains the public server pool, its continental and country zones, and good habits such as using a few servers and not polling too fast. Guides which host name the Pico should query.

9. [NIST Internet Time Service](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/internet-time-service-its) - NIST - Describes the government time servers linked directly to UTC(NIST) and the NTP, Daytime, and Time protocols they offer. It shows where accurate internet time originates and supports the stratum discussion.

10. [Local Time FAQs](https://www.nist.gov/pml/time-and-frequency-division/local-time-faqs) - NIST - Answers common questions about time zones, UTC offsets, and daylight saving rules in the United States, including who observes them. It helps students write correct timezone conversion and daylight saving logic.
