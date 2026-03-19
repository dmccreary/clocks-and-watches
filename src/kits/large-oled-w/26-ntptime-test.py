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
        print("Time before sync:", utime.localtime())
        
        # Sync with NTP server (automatically updates RTC)
        ntptime.settime()
        
        # Show time after sync
        print("Time after sync:", utime.localtime())
        print("Time sync successful!")
        
        return True
        
    except Exception as e:
        print("Failed to sync time:", str(e))
        return False

def format_time():
    """Format current time as readable string"""
    current_time = utime.localtime()
    year, month, day, hour, minute, second = current_time[0:6]
    
    # Convert to 12-hour format
    am_pm = "AM"
    if hour >= 12:
        am_pm = "PM"
        if hour > 12:
            hour = hour - 12
    elif hour == 0:
        hour = 12
    
    return f"{month}/{day}/{year} {hour}:{minute:02d}:{second:02d} {am_pm}"

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
        print(f"\nCurrent time: {format_time()}")
        
        # Show time updates every 5 seconds
        print("\nShowing live time (press Ctrl+C to stop):")
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

# Run the program
if __name__ == "__main__":
    main()