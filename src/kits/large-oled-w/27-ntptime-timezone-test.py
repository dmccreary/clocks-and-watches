# WiFi Time Synchronization using ntptime module
# This code connects to WiFi and syncs the Pico W's clock with internet time servers

import network
import ntptime
import utime
import secrets
from machine import RTC

# Get the WiFi credentials from the secrets.py file
WIFI_SSID = secrets.wifi_ssid
WIFI_PASSWORD = secrets.wifi_pass

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print("Waiting for connection...")
            utime.sleep(1)
        
        if wlan.status() != 3:
            print("Failed to connect to WiFi")
            return False
        else:
            print("Connected to WiFi")
            print("IP address:", wlan.ifconfig()[0])
            return True
    else:
        print("Already connected to WiFi")
        return True

def sync_time():
    """Synchronize time using NTP"""
    try:
        print("\nSyncing time with NTP server...")
        
        # Show time before sync
        rtc = RTC()
        print("Time before sync (Central):", format_time())
        
        # Sync with NTP server (automatically updates RTC)
        ntptime.settime()
        
        # Show time after sync
        print("Time after sync (Central):", format_time())
        print("Time sync successful!")
        
        return True
        
    except Exception as e:
        print("Failed to sync time:", str(e))
        return False

def day_of_week(year, month, day):
    """Calculate day of week (0=Monday, 6=Sunday) using Zeller's congruence"""
    if month < 3:
        month += 12
        year -= 1
    
    k = year % 100
    j = year // 100
    
    h = (day + ((13 * (month + 1)) // 5) + k + (k // 4) + (j // 4) - 2 * j) % 7
    
    # Convert to Python's format (0=Monday, 6=Sunday)
    return (h + 5) % 7

def is_daylight_saving_time(year, month, day):
    """Check if given date is during daylight saving time in US"""
    # DST starts second Sunday in March at 2:00 AM
    # DST ends first Sunday in November at 2:00 AM
    
    if month < 3 or month > 11:
        return False
    if month > 3 and month < 11:
        return True
    
    if month == 3:
        # Find second Sunday in March
        # Start from March 8th (earliest possible second Sunday)
        for d in range(8, 15):
            if day_of_week(year, month, d) == 6:  # Sunday
                return day >= d
    
    if month == 11:
        # Find first Sunday in November
        # Start from November 1st
        for d in range(1, 8):
            if day_of_week(year, month, d) == 6:  # Sunday
                return day < d
    
    return False

def utc_to_central_time():
    """Convert current UTC time to US Central time"""
    utc_time = utime.localtime()
    year, month, day, hour, minute, second = utc_time[0:6]
    
    # Determine if we're in daylight saving time
    is_dst = is_daylight_saving_time(year, month, day)
    
    # Central Standard Time (CST) = UTC - 6 hours
    # Central Daylight Time (CDT) = UTC - 5 hours
    offset_hours = -5 if is_dst else -6
    
    # Convert to timestamp, adjust, then back to time tuple
    timestamp = utime.mktime(utc_time)
    central_timestamp = timestamp + (offset_hours * 3600)
    central_time = utime.localtime(central_timestamp)
    
    timezone_name = "CDT" if is_dst else "CST"
    
    return central_time, timezone_name

def format_time():
    """Format current time as readable string in Central Time"""
    central_time, tz_name = utc_to_central_time()
    year, month, day, hour, minute, second = central_time[0:6]
    
    # Convert to 12-hour format
    am_pm = "AM"
    if hour >= 12:
        am_pm = "PM"
        if hour > 12:
            hour = hour - 12
    elif hour == 0:
        hour = 12
    
    return f"{month}/{day}/{year} {hour}:{minute:02d}:{second:02d} {am_pm} {tz_name}"

def main():
    """Main program"""
    print("WiFi Time Sync Demo")
    print("=" * 30)
    
    # Connect to WiFi
    if not connect_wifi():
        print("Cannot proceed without WiFi connection")
        return
    
    # Sync time
    if sync_time():
        print(f"\nCurrent time in Central Time Zone: {format_time()}")
        
        # Show time updates every 5 seconds
        print("\nShowing live Central time (press Ctrl+C to stop):")
        try:
            while True:
                print(format_time())
                utime.sleep(5)
        except KeyboardInterrupt:
            print("\nTime demo stopped")
    else:
        print("Time sync failed - check internet connection")

# Optional: Set custom NTP server (default uses pool.ntp.org)
# ntptime.host = "time.google.com"

# Note: Create a secrets.py file with your WiFi credentials:
# wifi_ssid = "YourWiFiName"
# wifi_pass = "YourWiFiPassword"

# Run the program
if __name__ == "__main__":
    main()