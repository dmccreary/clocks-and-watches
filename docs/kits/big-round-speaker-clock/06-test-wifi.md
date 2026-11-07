# Lab 06: Check Your WiFi

The clock sets itself from the internet, so it needs two settings files
filled in correctly. This lab checks both, then joins your WiFi network.
Everything is printed in Thonny's shell, so it works even before the
display is wired.

!!! mascot-welcome "Welcome to Lab 06"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A clock that sets itself is never wrong, but first it has to get
    online. This lab finds any typo in your settings before it can
    confuse the clock. Let's make time tick!

## What You Will Learn

- what goes in `secrets.py` and `config.py`
- how a Pico W joins a WiFi network
- what signal strength numbers mean

## Before You Run It

1. Copy `secrets-template.py` to a new file called `secrets.py`.
2. Type your WiFi network's name in `wifi_ssid` and its password in
   `wifi_pass`.
3. Check `CITY`, `TIMEZONE_HOURS`, and `USE_US_DST` in `config.py`.

!!! mascot-warning "Keep secrets secret"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    `secrets.py` holds your WiFi password, so never post it or share it.
    The kit is set up so it is never uploaded to the internet with the
    rest of the code. Keep the password only in that one file.

## Run It

Open `06-test-wifi.py` and click **Run**. A good run looks like this (the
network name, address, and numbers here are made-up examples):

```text
1. secrets.py
  ok  wifi_ssid = 'MyHomeWiFi'
  ok  wifi_pass is set (19 characters)

2. config.py
  ok  CITY = 'Minneapolis'
  ok  TIMEZONE_HOURS = -6
  ok  USE_US_DST = True

3. WiFi
  MAC address: 28:cd:c1:00:00:00
  ok  'MyHomeWiFi' is in range at -59 dBm (-50 strong, -80 weak)
  joining ...
  ok  connected in 2140 ms
      IP 10.0.0.99  gateway 10.0.0.1  DNS 10.0.0.1
  ok  pool.ntp.org is at 10.0.0.123

All good. Run 07-get-time.py next.
```

Anything that is wrong is printed as a **PROBLEM** line that says what to
fix.

## Signal Strength

`-59 dBm` measures how strong your network's signal is. The numbers are
negative, and **closer to zero is stronger**: −50 is strong, −80 is weak.
If the signal is weak, move the clock closer to the router.

## If It Doesn't Work

- **"network not found".** The Pico W only uses **2.4 GHz** WiFi. If your
  router has a separate 5 GHz network name, use the 2.4 GHz one.
- **"wrong password".** Passwords are case-sensitive. Check capital
  letters and spaces in `secrets.py`.
- **"there is no secrets.py on the Pico".** Make the file and upload it.

!!! mascot-celebration "You're Online!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    Your settings are checked and your Pico W joined the network. Now it
    can ask the internet for the time.

**Next:** [Lab 07: Get the Time](07-get-time.md)
