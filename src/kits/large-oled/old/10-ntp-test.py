# Lab #10 - test that the ntptime is working within the Pico W Runtime
# Note this only works on v1.20.0 or later.  Make sure your W runtime is up-to-date.
import ntptime, network
from time import sleep_ms, localtime
import secrets

# get the local wifi credental
import secrets
wifi_ssid = secrets.wifi_ssid
wifi_pass = secrets.wifi_pass

def wifiConnect():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.config(pm = 0xa11140) # disables wifi sleep mode
    if not wifi.isconnected():
        wifi.connect(wifi_ssid, wifi_pass)
        print('Connecting..', end='')
        max_wait = 10
        while max_wait > 0:
            if wifi.status() < 0 or wifi.status() >= 3: break
            sleep_ms(200)
            print(10 - max_wait, ' ', end='')
            max_wait -= 1
        print()
        if wifi.status() != 3: print('Could not connect to wifi!')
    # print('Connected: ',wifi.isconnected(),'\nIP: ',wifi.ifconfig()[0])
    sleep_ms(100)
    return wifi

wifiConnect()

print("Local time before synchronization：%s" %str(localtime()))
ntptime.settime()
print("Local time after synchronization：%s" %str(localtime()))