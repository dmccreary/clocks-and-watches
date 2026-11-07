# References: Sensors, Power, and Low-Power Design

1. [Analog-to-digital converter](https://en.wikipedia.org/wiki/Analog-to-digital_converter) - Wikipedia - Explains how continuous voltages become digital numbers, and how resolution and sampling rate limit accuracy. It supports the chapter's ADC reading section and the 0 to 65535 values students see from a light sensor.

2. [Accelerometer](https://en.wikipedia.org/wiki/Accelerometer) - Wikipedia - Describes how accelerometers measure proper acceleration, why a device at rest reads about 1 g, and how tiny MEMS chips work. It underpins the chapter's tilt detection and step counter concepts.

3. [Hysteresis](https://en.wikipedia.org/wiki/Hysteresis) - Wikipedia - Covers systems whose output depends on history, including a thermostat with separate on and off thresholds and the Schmitt trigger. It explains why the chapter's auto brightness code uses two thresholds to avoid flicker.

4. Batteries in a Portable World (4th Edition) - Isidor Buchmann - Cadex Electronics - No single author originated battery basics; this handbook is chosen because its subtitle targets non-engineers and it devotes chapters to runtime and choosing a chemistry. That plain approach suits comparing LiPo, AA, and USB packs.

5. Practical Electronics for Inventors (4th Edition) - Paul Scherz and Simon Monk - McGraw-Hill Education - No single originator; chosen as a widely used hobbyist reference with a dedicated sensors chapter. It presents sensor circuits in a build-oriented style that helps students connect photoresistors and accelerometers to a microcontroller.

6. [machine.ADC](https://docs.micropython.org/en/latest/library/machine.ADC.html) - MicroPython Documentation - Official reference for the ADC class and read_u16(), which scales every reading to 0 through 65535. Students use it to read the light sensor voltage that drives auto brightness.

7. [Photocells](https://learn.adafruit.com/photocells) - Adafruit Learning System - Introduces the photocell, or light-dependent resistor, noting its resistance falls from about 200K ohms in dark to 10K ohms at 10 lux. It is cheap but imprecise, which supports the chapter's photosensor section.

8. [Accelerometer Basics](https://learn.sparkfun.com/tutorials/accelerometer-basics) - SparkFun Learn - Explains single, dual, and triple-axis sensing, gravity as a static force measured in g, and extras such as tap detection. It reinforces the chapter's accelerometer, tilt detection, and low-power wake ideas.

9. [Battery Technologies](https://learn.sparkfun.com/tutorials/battery-technologies) - SparkFun Learn - Compares LiPo, NiMH, coin cell, and alkaline batteries, covering mAh capacity, nominal voltage, protection circuits, and self-discharge. It supports the chapter's battery power and current draw calculation sections.

10. [machine module: sleep functions](https://docs.micropython.org/en/latest/library/machine.html) - MicroPython Documentation - Documents lightsleep(), deepsleep(), and reset_cause(), including which state survives each mode and how timeouts or pin changes wake the board. It is the reference for the chapter's low power mode and wake sources.
