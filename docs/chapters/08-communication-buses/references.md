# References: Communication Buses: I2C, SPI, and UART

1. [I²C](https://en.wikipedia.org/wiki/I%C2%B2C) - Wikipedia - Details the two-wire SDA and SCL bus, 7-bit device addressing, open-drain signaling, and required pull-up resistors. It matches the chapter's I2C wiring, addresses, and scanner material.

2. [Serial Peripheral Interface](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) - Wikipedia - Explains the clock, data lines, and chip select of SPI, along with clock polarity and phase modes. It supports the chapter's SPI pins, baudrate, and clock polarity topics.

3. [Universal asynchronous receiver-transmitter](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter) - Wikipedia - Describes how a UART sends bytes one bit at a time using start and stop bits and an agreed baud rate. It backs up the chapter's UART protocol section.

4. Code: The Hidden Language of Computer Hardware and Software (2nd Edition) - Charles Petzold - Microsoft Press - Petzold builds binary, bytes, and signaling up from flashlight messages and telegraph relays, so bits on a wire feel intuitive. This makes the chapter's bit, byte, and MSB ideas approachable.

5. Making Embedded Systems (1st Edition) - Elecia White - O'Reilly Media - No single originator is claimed here; this is chosen as the book most praised for practical embedded writing. Its chapter on communicating with peripherals surveys common serial buses and how software should handle them.

6. [machine.I2C - a two-wire serial protocol](https://docs.micropython.org/en/latest/library/machine.I2C.html) - MicroPython Documentation - The official reference for creating an I2C bus, running scan() to find addresses, setting freq, and using readfrom_mem() and writeto_mem(). It is the code-level companion to the chapter's I2C scanner.

7. [I2C Tutorial](https://learn.sparkfun.com/tutorials/i2c) - SparkFun Learn - Explains 7-bit addressing, start and stop conditions, open-drain lines, and why pull-up resistors around 4.7 kilohms are used. It deepens the chapter's I2C pull-up and device addressing sections.

8. [I2C Addresses](https://learn.adafruit.com/i2c-addresses) - Adafruit Learning System - Explains why every device on a bus needs a unique address and how jumpers or multiplexers solve conflicts. It helps students interpret the chapter's scanner output and fix two-device collisions.

9. [Understanding the I2C Bus (SLVA704)](https://ti.com/document-viewer/lit/html/SLVA704) - Texas Instruments - A manufacturer application note covering open-drain signaling, START and STOP conditions, data bytes, and ACK/NACK. It shows the professional view of the data packet structure the chapter introduces.

10. [Basics of the SPI Communication Protocol](https://www.circuitbasics.com/basics-of-the-spi-communication-protocol/) - Circuit Basics - Illustrates how a controller pulls chip select low and clocks bits to a peripheral, including multi-device wiring. It supports the chapter's SPI chip select and bus speed comparison material.
