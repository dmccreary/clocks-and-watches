# Portable SmartWatch Kits

Our current SmartWatch kits (the [GC9A01](../gc9a01/index.md) and
[Waveshare LCD](../waveshare-lcd/index.md) round displays) are wired to a
Raspberry Pi Pico on a breadboard and powered over USB. They are great for
learning how to draw clock and watch faces with MicroPython, but they are
not wearable — there is no onboard battery, so the display goes dark the
moment you unplug the USB cable.

This page surveys options for a **portable** SmartWatch kit: one that keeps
a MicroPython-programmable round display but adds its own rechargeable
battery so a student can walk around wearing (or carrying) a working clock.

## Recommended: Waveshare ESP32-S3-Touch-LCD-1.28

The closest drop-in upgrade to our existing kits. It uses the same GC9A01
family round display and MicroPython workflow students already know, but
adds an onboard battery charging circuit.

- 1.28" round IPS touch LCD (240x240), same display family as our GC9A01 kit
- ESP32-S3 with WiFi/BLE, 16MB flash, 2MB PSRAM
- Built-in Li-ion charging chip with an MX1.25 2-pin JST connector for a
  3.7V LiPo battery (supports both charging and discharging)
- Onboard 6-axis IMU (accelerometer + gyroscope)
- Battery voltage readable through a voltage divider on GPIO1
- Official MicroPython firmware and getting-started docs from Waveshare
- Approx. $15-20 for the board plus a small 3.7V LiPo battery
- A "-B" variant ships in a CNC metal watch-style case

This is the option we plan to build a kit page for, since it minimizes the
jump in cost, wiring, and code compared to our current lessons.

## Other options considered

### LILYGO T-Watch-S3 / T-Watch 2020 V3

A fully-enclosed, wearable watch case (not a breadboard kit) built around
an ESP32. Comes with its own 400mAh battery (1100mAh on the newer T-Watch
Ultra). Community MicroPython ports exist:

- [y0no/lilygo-ttgo-twatch-2020-micropython](https://github.com/y0no/lilygo-ttgo-twatch-2020-micropython)
- [antirez/t-watch-s3-micropython](https://github.com/antirez/t-watch-s3-micropython)

More "watch-shaped" and immediately wearable than a teaching kit, but
higher cost (~$40-50) and a bigger jump from our current lessons.

### PineTime + wasp-os

A $25-27 open-source smartwatch (nRF52832) with a built-in battery, running
[wasp-os](https://github.com/wasp-os/wasp-os), a MicroPython-based watch
OS. It's a fixed appliance rather than a breadboard-and-code teaching kit,
and wasp-os is its own MicroPython fork rather than stock MicroPython, so
it's a poor fit for lessons that have students write their own display code
from scratch.

### NASA Artemis Watch 2.0

A $129 fully-assembled kids' programmable watch built on a dual-core ESP32
with a full-color LCD, accelerometer, gyroscope, compass, and temperature
sensor. Marketed as "runs Python," but pricier than the alternatives and
less clear on giving students raw MicroPython REPL access to the display.

## Comparison

| Option | Display | Battery | MicroPython | Approx. Cost | Fit for this course |
|---|---|---|---|---|---|
| Waveshare ESP32-S3-Touch-LCD-1.28 | 1.28" round LCD | Onboard LiPo charging (JST) | Official firmware | $15-20 + battery | Best - same display family as current kits |
| LILYGO T-Watch-S3 / Ultra | Square/round touch | Onboard 400-1100mAh | Community ports | $40-50 | Good, but bigger jump |
| PineTime + wasp-os | Round LCD | Onboard | wasp-os fork | $25-27 | Fair - fixed appliance, not stock MicroPython |
| NASA Artemis Watch 2.0 | Color LCD | Onboard | "Runs Python" | $129 | Weak - expensive, less DIY access |

## References

1. [ESP32-S3-Touch-LCD-1.28 - Waveshare Wiki](https://www.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.28)
2. [ESP32-S3-Touch-LCD-1.28 product page](https://www.waveshare.com/esp32-s3-touch-lcd-1.28.htm)
3. [ESP32-S3-LCD-1.28-B (with case)](https://www.waveshare.com/esp32-s3-lcd-1.28-b.htm)
4. [Waveshare ESP32 MicroPython Getting Started](https://docs.waveshare.com/ESP32-MicroPython-Tutorials)
5. [LILYGO T-Watch Ultra - Hackster.io](https://www.hackster.io/news/lilygo-unveils-the-t-watch-ultra-now-featuring-an-amoled-display-esp32-s3-and-lora-transceiver-498585fbd063)
6. [LILYGO T-Watch-S3 on Tindie](https://www.tindie.com/products/lilygo/lilygo-t-watch-s3-programmable-touchable-watch/)
7. [y0no/lilygo-ttgo-twatch-2020-micropython (GitHub)](https://github.com/y0no/lilygo-ttgo-twatch-2020-micropython)
8. [antirez/t-watch-s3-micropython (GitHub)](https://github.com/antirez/t-watch-s3-micropython)
9. [wasp-os (GitHub)](https://github.com/wasp-os/wasp-os)
10. [PineTime - Liliputing](https://liliputing.com/the-27-pinetime-smartwatch-runs-open-source-software-and-now-its-ready-for-non-developers/)
11. [NASA Artemis 2.0 Smartwatch - Yanko Design](https://www.yankodesign.com/2026/04/05/the-nasa-artemis-2-0-smartwatch-runs-python-and-lets-kids-code-their-own-wearable/)
