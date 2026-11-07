# records.py -- remember the highest and lowest readings, even after unplugging.
#
# The four records live in a tiny text file on the Pico, like this:
#
#     78.42 66.10 62.30 31.00
#
# That is: highest temperature (F), lowest temperature (F), highest humidity,
# lowest humidity.
#
# Flash memory wears out if you write to it too often, so we do NOT save on
# every new record. When a record changes we just make a note of it, and the
# note is saved when at least save_seconds have passed since the last save.
import time


class Records:
    def __init__(self, filename, save_seconds):
        self.filename = filename
        self.save_ms = save_seconds * 1000
        self.hi_f = None
        self.lo_f = None
        self.hi_h = None
        self.lo_h = None
        self.changed = False           # True when there is something to save
        self.last_save = time.ticks_ms()
        self.load()

    def load(self):
        """Read the records file. If it is missing or broken, start fresh."""
        try:
            with open(self.filename) as f:
                parts = f.read().split()
            values = [float(part) for part in parts]
            if len(values) == 4:
                self.hi_f, self.lo_f, self.hi_h, self.lo_h = values
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(self.filename, "w") as f:
                f.write("%.2f %.2f %.2f %.2f\n" % (
                    self.hi_f, self.lo_f, self.hi_h, self.lo_h))
            self.changed = False
        except OSError:
            pass                       # a full or busy disk must not stop the display
        self.last_save = time.ticks_ms()

    def update(self, temp_f, humidity):
        """Look at a new reading and keep the extremes."""
        if self.hi_f is None:
            self.hi_f = self.lo_f = temp_f
            self.hi_h = self.lo_h = humidity
            self.changed = True
            return
        if temp_f > self.hi_f:
            self.hi_f = temp_f
            self.changed = True
        if temp_f < self.lo_f:
            self.lo_f = temp_f
            self.changed = True
        if humidity > self.hi_h:
            self.hi_h = humidity
            self.changed = True
        if humidity < self.lo_h:
            self.lo_h = humidity
            self.changed = True

    def save_if_due(self, now):
        if self.changed and time.ticks_diff(now, self.last_save) >= self.save_ms:
            self.save()

    def clear(self):
        """Forget everything, and delete the file."""
        self.hi_f = self.lo_f = self.hi_h = self.lo_h = None
        self.changed = False
        try:
            import os
            os.remove(self.filename)
        except OSError:
            pass
