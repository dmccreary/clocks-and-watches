# Lab 08: Set the Clock from the Internet

![The screen shows "Setting clock", "Time set 10:10:25", then 10:10:25 in big green numbers and the date 2026-09-25](img/08-wifi-sync-time.png){ width="360" }

The Pico forgets the time whenever it loses power. Real clocks that hang
in stations don't have this problem, because a master clock keeps them
all right. Your clock will do the next best thing: ask the internet.

!!! mascot-welcome "Welcome to Lab 08"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the lab where your clock goes online. After this, it can set
    its own time anywhere there's WiFi, the same way a phone does. Let's
    make time tick!

## What You Will Learn

- how the Pico joins a WiFi network
- what a **time server** is
- what **time zones** and **daylight saving time** are
- how to keep a password out of your code

## Before You Run It

The Pico needs the name and password of your WiFi network. They go in a
special file called `secrets.py`:

1. Find the file `secrets-template.py` in the kit folder.
2. Copy it, and name the copy `secrets.py`.
3. Type in your network's name and password:

```python
wifi_ssid = "your-network-name"
wifi_pass = "your-network-password"
```

4. Save `secrets.py` to the Pico.

!!! mascot-warning "Keep Secrets Secret"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Never put a password right inside a program, because programs get
    shared. Keeping it in its own file means you can share every program
    without sharing your password. This repository's `.gitignore` keeps
    `secrets.py` from ever being uploaded to the internet.

## Run It

Open `08-wifi-sync-time.py` in Thonny and click **Run**. The screen tells
you what's happening, one step at a time:

1. `Joining your-network-name`
2. `IP 10.0.0.22`, which means your Pico is on the network
3. `Asking pool.ntp.org`, which means it's asking a time server
4. `Time set 10:10:25`, and the time appears in big green numbers

## How It Works

Special computers on the internet called **time servers** do nothing but
tell other computers the exact time. They follow a set of rules called
**NTP**, the *Network Time Protocol*. The Pico asks one, and in a fraction
of a second it gets the answer.

All of that happens in one line of the program:

```python
if wifi_time.sync_time(display):
```

`sync_time()` lives in the kit's file `wifi_time.py`. It joins your WiFi,
asks a time server, fixes the time zone, sets the Pico's clock, and then
turns the WiFi off again to save power.

### Time zones

A time server answers in **UTC**, the time in London, England (in
winter). So the program adds the number of hours in `TIMEZONE_HOURS` from
`config.py`:

| Time zone | TIMEZONE_HOURS | When it's noon UTC, it's... |
|---|---|---|
| Eastern | -5 | 7 AM |
| Central | -6 | 6 AM |
| Mountain | -7 | 5 AM |
| Pacific | -8 | 4 AM |

### Daylight saving time

In most of the United States, clocks "spring forward" one hour in March
and "fall back" one hour in November. The program works out whether today
is in daylight saving time and adds the extra hour when it is. If you
live in Arizona or Hawaii, where clocks don't change, set
`USE_US_DST = False` in `config.py`.

!!! tip "Try This"
    1. Change `TIMEZONE_HOURS` to -8 and run the program again. What time
       does it say now?
    2. After this lab finishes, run [Lab 07](07-read-the-time.md). The face
       shows the right time, because the Pico's clock keeps going until the
       power is unplugged.

## If It Doesn't Work

- **`No secrets.py on the Pico`.** You forgot step 4: save `secrets.py`
  to the Pico.
- **`WiFi failed`.** Check the spelling of the network name and password.
  Capital letters matter! Also, the Pico only connects to 2.4 GHz
  networks.
- **The time is off by exactly one hour.** Check `TIMEZONE_HOURS` and
  `USE_US_DST` in `config.py`.

!!! mascot-celebration "Your Clock Is Online!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You joined a WiFi network, asked a time server for the exact time, and
    kept your password out of your code. Next, you'll set the red hand in
    motion.

**Next:** [Lab 09: Tick Tock](09-tick-tock.md)
