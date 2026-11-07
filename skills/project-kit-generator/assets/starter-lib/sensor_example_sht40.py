# sht40.py -- talk to the SHT40 temperature and humidity sensor.
#
# Labs 02 to 07 each carry their own copy of this code so you can read one
# file from top to bottom. Lab 09 has six modes that all need the sensor, so
# the code lives here, in one place, instead.
#
#     sensor = SHT40(i2c, 0x44, 0xFD, 0x94, 15)
#     temperature_c, humidity = sensor.read()
import time


def crc8(data):
    """Check that the bytes we read were not scrambled on the way."""
    crc = 0xFF
    for byte in data:
        crc = crc ^ byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x31) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc


class SHT40:
    def __init__(self, i2c, address, cmd_measure, cmd_reset, measure_ms):
        self.i2c = i2c
        self.address = address
        self.cmd_measure = cmd_measure
        self.cmd_reset = cmd_reset
        self.measure_ms = measure_ms

    def reset(self):
        """Give the sensor a clean start. Raises OSError if it will not answer."""
        self.i2c.writeto(self.address, bytes([self.cmd_reset]))
        time.sleep_ms(10)

    def read(self):
        """Return one (temperature_c, humidity_percent) reading.

        Raises OSError if the sensor does not answer, and ValueError if the
        bytes arrive scrambled."""
        self.i2c.writeto(self.address, bytes([self.cmd_measure]))
        time.sleep_ms(self.measure_ms)
        data = self.i2c.readfrom(self.address, 6)

        if crc8(data[0:2]) != data[2]:
            raise ValueError("Temperature checksum failed")
        if crc8(data[3:5]) != data[5]:
            raise ValueError("Humidity checksum failed")

        temp_ticks = (data[0] << 8) | data[1]
        humidity_ticks = (data[3] << 8) | data[4]

        temperature_c = -45.0 + 175.0 * temp_ticks / 65535.0
        humidity = -6.0 + 125.0 * humidity_ticks / 65535.0

        if humidity > 100.0:
            humidity = 100.0
        if humidity < 0.0:
            humidity = 0.0

        return temperature_c, humidity
