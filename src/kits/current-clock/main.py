VERSION = "1.0"

from machine import Pin, I2C, SPI
from utime import sleep, sleep_ms, time, localtime, mktime
from ds3231 import DS3231
import ntptime
import network
import ssd1306
import config
import secrets

# Onboard LED
led = Pin('LED', Pin.OUT)

# SPI Display setup
SCL = Pin(config.SPI_SCL_PIN)
SDA = Pin(config.SPI_SDA_PIN)
DC = Pin(config.SPI_DC_PIN)
RES = Pin(config.SPI_RESET_PIN)
CS = Pin(config.SPI_CS_PIN)
WIDTH = config.DISPLAY_WIDTH
HEIGHT = config.DISPLAY_HEIGHT

spi = SPI(config.SPI_BUS, sck=SCL, mosi=SDA, baudrate=1000000)
oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, DC, RES, CS)

# I2C and RTC setup — same as working main-old.py
i2c_sda = Pin(config.I2C_SDA_PIN)
i2c_scl = Pin(config.I2C_SCL_PIN)
I2C_BUS = config.I2C_BUS
i2c = I2C(I2C_BUS, scl=i2c_scl, sda=i2c_sda, freq=200000)
rtc = DS3231(addr=config.RTC_I2C_ADDR, i2c=i2c)

# Button setup (active low with internal pull-up)
btn_mode = Pin(config.BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
btn_inc = Pin(config.BUTTON_INCREMENT_PIN, Pin.IN, Pin.PULL_UP)
btn_dec = Pin(config.BUTTON_DECREMENT_PIN, Pin.IN, Pin.PULL_UP)

# NTP configuration
ntptime.host = config.NTP_HOST
ntptime.timeout = config.NTP_TIMEOUT

# Sync state
last_ntp_sync = None  # tuple: (year, month, day, hour, minute, second) of last successful sync
ntp_sync_ok = False

segmentMapping = [
    #a, b, c, d, e, f, g
    [1, 1, 1, 1, 1, 1, 0], # 0
    [0, 1, 1, 0, 0, 0, 0], # 1
    [1, 1, 0, 1, 1, 0, 1], # 2
    [1, 1, 1, 1, 0, 0, 1], # 3
    [0, 1, 1, 0, 0, 1, 1], # 4
    [1, 0, 1, 1, 0, 1, 1], # 5
    [1, 0, 1, 1, 1, 1, 1], # 6
    [1, 1, 1, 0, 0, 0, 0], # 7
    [1, 1, 1, 1, 1, 1, 1], # 8
    [1, 1, 1, 1, 0, 1, 1]  # 9
]

def day_to_str(day_num):
    # The day_num returned by the RTC is from 1 to 7
    day_num = day_num - 1
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if not 0 <= day_num <= 6:
        raise ValueError("Day number must be between 0 and 6")
    return days[day_num]

def month_to_str(month_num):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if not 0 <= month_num <= 11:
        raise ValueError("Month number must be between 0 and 11")
    return months[month_num]

def drawDigit(digit, x, y, width, height, thickness, color):
    if digit < 0 or digit > 9:
        return
    segmentOn = segmentMapping[digit]

    for i in [0, 3, 6]:
        if segmentOn[i]:
            if i == 0:
                yOffset = 0
            elif i == 3:
                yOffset = height - thickness
            else:
                yOffset = height // 2 - thickness // 2
            oled.fill_rect(x, y+yOffset, width, thickness, color)

    for i in [1, 2, 4, 5]:
        if segmentOn[i]:
            if i == 1 or i == 5:
                startY = y
                endY = y + height // 2
            else:
                startY = y + height // 2
                endY = y + height
            xOffset = 0 if (i == 4 or i == 5) else width-thickness
            oled.fill_rect(x+xOffset, startY, thickness, endY-startY, color)

def draw_colon(x, y):
    oled.fill_rect(x, y, 3, 3, 1)
    oled.fill_rect(x, y+14, 3, 3, 1)

def read_temperature():
    try:
        temp_msb = i2c.readfrom_mem(0x68, 0x11, 1)[0]
        temp_lsb = i2c.readfrom_mem(0x68, 0x12, 1)[0] >> 6
        if temp_msb & 0x80:
            temp_msb = -(~temp_msb & 0x7F) - 1
        temp_c = temp_msb + ((temp_lsb & 0x03) * 0.25)
        temp_f = (temp_c * 9/5) + 32
        return temp_f
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return 0

def is_dst(year, month, day, hour):
    """Check if current date/time is in US Daylight Saving Time.
    DST starts 2nd Sunday of March at 2am, ends 1st Sunday of November at 2am."""
    if month < 3 or month > 11:
        return False
    if month > 3 and month < 11:
        return True
    if month == 3:
        t = mktime((year, 3, 1, 0, 0, 0, 0, 0))
        dow = localtime(t)[6]  # 0=Monday
        first_sunday = 1 + (6 - dow) % 7
        second_sunday = first_sunday + 7
        if day > second_sunday:
            return True
        if day < second_sunday:
            return False
        return hour >= 2
    if month == 11:
        t = mktime((year, 11, 1, 0, 0, 0, 0, 0))
        dow = localtime(t)[6]
        first_sunday = 1 + (6 - dow) % 7
        if day < first_sunday:
            return True
        if day > first_sunday:
            return False
        return hour < 2

def display_msg(msg):
    """Display a message on the OLED, wrapping at 16 chars per line."""
    print(msg)
    oled.fill(0)
    chunk = 16
    lines = [msg[i:i+chunk] for i in range(0, len(msg), chunk)]
    for i, line in enumerate(lines):
        oled.text(line, 0, i * 9)
    oled.show()

def wifi_connect():
    """Connect to WiFi, returns the WLAN object."""
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.config(pm=0xa11140)  # disable wifi sleep mode
    if not wifi.isconnected():
        wifi.connect(secrets.wifi_ssid, secrets.wifi_pass)
        display_msg('WiFi: ' + secrets.wifi_ssid)
        max_wait = 10
        while max_wait > 0:
            if wifi.status() < 0 or wifi.status() >= 3:
                break
            sleep_ms(1000)
            max_wait -= 1
        if wifi.status() != 3:
            display_msg('WiFi connect failed!')
            return wifi
    display_msg('IP: ' + wifi.ifconfig()[0])
    sleep_ms(500)
    return wifi

def wifi_disconnect(wifi):
    """Disconnect WiFi to save power."""
    try:
        wifi.disconnect()
        wifi.active(False)
    except:
        pass

def set_ds3231_time(year, month, day, hour, minute, second, weekday):
    """Write time to DS3231 using raw I2C to avoid driver issues."""
    from ds3231 import dectobcd
    buf = bytearray(7)
    buf[0] = dectobcd(second)
    buf[1] = dectobcd(minute)
    buf[2] = dectobcd(hour)       # 24h format
    buf[3] = dectobcd(weekday)    # 1-7
    buf[4] = dectobcd(day)
    buf[5] = dectobcd(month)
    buf[6] = dectobcd(year % 100)
    i2c.writeto_mem(config.RTC_I2C_ADDR, 0, buf)

def sync_ntp():
    """Connect to WiFi, sync time from NTP, set DS3231 RTC, disconnect WiFi.
    Returns True on success."""
    global last_ntp_sync, ntp_sync_ok

    wifi = wifi_connect()
    if not wifi.isconnected():
        wifi_disconnect(wifi)
        return False

    success = False
    for attempt in range(3):
        try:
            ntptime.settime()
            success = True
            break
        except Exception as e:
            print(f"NTP attempt {attempt+1} failed: {e}")
            if attempt < 2:
                sleep_ms(2000)

    if not success:
        display_msg('NTP sync failed!')
        sleep(1)
        wifi_disconnect(wifi)
        ntp_sync_ok = False
        return False

    # NTP sets Pico internal clock to UTC. Calculate local time.
    utc = localtime()
    tz_offset = config.TIMEZONE_OFFSET
    if is_dst(utc[0], utc[1], utc[2], utc[3] + tz_offset):
        tz_offset += 1

    local_t = localtime(time() + tz_offset * 3600)
    year, month, day = local_t[0], local_t[1], local_t[2]
    hour, minute, second = local_t[3], local_t[4], local_t[5]
    weekday = local_t[6]  # 0=Monday in MicroPython

    # Disconnect WiFi
    wifi_disconnect(wifi)

    # Write NTP time to DS3231 using raw I2C
    # weekday for DS3231: 1-7, so add 1 to MicroPython's 0-6
    try:
        set_ds3231_time(year, month, day, hour, minute, second, weekday + 1)
    except OSError as e:
        print(f"DS3231 write failed: {e}")
        display_msg('RTC write failed!')
        sleep(1)
        ntp_sync_ok = False
        return False

    last_ntp_sync = (year, month, day, hour, minute, second)
    ntp_sync_ok = True
    display_msg('NTP sync OK!')
    print(f"NTP synced: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
    sleep_ms(500)

    return True

def show_sync_status():
    """Display NTP sync status on the OLED."""
    oled.fill(0)
    oled.text('=== NTP Status ==', 0, 0, 1)
    oled.text('Net:' + secrets.wifi_ssid[:12], 0, 12, 1)
    oled.text('Host:' + config.NTP_HOST[:11], 0, 22, 1)
    if last_ntp_sync:
        yr, mo, dy, hr, mi, se = last_ntp_sync
        am_pm = 'AM' if hr < 12 else 'PM'
        dh = hr if hr <= 12 else hr - 12
        if dh == 0:
            dh = 12
        oled.text('Last sync:', 0, 34, 1)
        oled.text(f'{mo}/{dy}/{yr}', 0, 44, 1)
        oled.text(f'{dh}:{mi:02d}:{se:02d} {am_pm}', 0, 54, 1)
    else:
        oled.text('No sync yet', 0, 34, 1)
        if ntp_sync_ok:
            oled.text('Status: OK', 0, 44, 1)
        else:
            oled.text('Status: FAILED', 0, 44, 1)
    oled.show()

def update_screen(year, month, day, hour, minute, second, weekday):
    left_margin = -28
    y_offset = 11
    digit_width = 33
    digit_height = 40
    digit_spacing = 41
    digit_thickness = 5

    oled.fill(0)

    date_str = f"{day_to_str(weekday)} {month_to_str(month-1)} {day} {year}"
    oled.text(date_str, 0, 0, 1)

    if hour > 12:
        display_hour = hour - 12
    else:
        display_hour = hour
    if display_hour == 0:
        display_hour = 12

    if display_hour < 10:
        hour_ten = -1
    else:
        hour_ten = display_hour // 10

    hour_right = display_hour % 10
    minute_ten = minute // 10
    minute_right = minute % 10

    drawDigit(hour_ten, left_margin, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(hour_right, left_margin + digit_spacing-2, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_ten, left_margin + 2*digit_spacing, y_offset, digit_width, digit_height, digit_thickness, 1)
    drawDigit(minute_right, left_margin + 3*digit_spacing, y_offset, digit_width, digit_height, digit_thickness, 1)

    if second % 2:
        draw_colon(47, 20)

    am_pm_x_offset = 112
    if hour >= 12:
        oled.text("PM", am_pm_x_offset, 55, 1)
    else:
        oled.text("AM", am_pm_x_offset, 55, 1)

    oled.text(str(second), 0, 54, 1)
    temperature = read_temperature()
    if temperature > 0:
        oled.text(str(temperature)+"F", 30, 54, 1)
    oled.show()

def any_button_pressed():
    """Return True if any button is pressed (active low)."""
    return btn_mode.value() == 0 or btn_inc.value() == 0 or btn_dec.value() == 0

# === Boot sequence ===
led.on()
print(f"NTP Clock v{VERSION}")
display_msg('Booting v' + VERSION)
sleep(0.5)

display_msg('Syncing NTP...')
sync_ntp()
sleep(0.5)

ntp_synced_this_hour = False

# === Main loop ===
while True:
    now = rtc.datetime()
    year = now[0]
    month = now[1]
    day = now[2]
    weekday = now[3]
    hour = now[4]
    minute = now[5]
    second = now[6]

    # Check if any button is pressed to show sync status
    if any_button_pressed():
        show_sync_status()
        # Wait for button release + display for 3 seconds
        while any_button_pressed():
            sleep_ms(50)
        sleep(3)
        continue

    # Nightly NTP sync at configured hour (default 3am)
    if hour == config.NTP_SYNC_HOUR and not ntp_synced_this_hour:
        display_msg('Nightly NTP sync')
        sync_ntp()
        ntp_synced_this_hour = True
    elif hour != config.NTP_SYNC_HOUR:
        ntp_synced_this_hour = False

    update_screen(year, month, day, hour, minute, second, weekday)
    print("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d} weekday:{}".format(
        year, month, day, hour, minute, second, weekday))
    led.toggle()
    sleep(1)
