# forecast.py -- the weather now, and today's and tomorrow's forecast,
# from Open-Meteo.
#
# Open-Meteo (https://open-meteo.com) is a free weather service that needs
# no account and no API key, so there is nothing to add to secrets.py. You
# ask for exactly the numbers you want and it sends back only those, about
# 600 bytes of JSON here.
#
#     import forecast
#     weather = forecast.fetch()
#     # {"temp": 41, "code": 3,                       <- right now
#     #  "days": [(54, 38, 3), (49, 33, 61)]}         <- (high, low, code)
#     # or None if the WiFi or the service did not answer.
#     forecast.describe(3)                           # -> "Cloudy"
#
# A "code" is a WMO weather code, the numbering the World Meteorological
# Organization uses for weather conditions.
#
# Adapted from the sw-gc9b72 kit's forecast.py, which fetches only the two
# days; this one also asks for "current" conditions.
#
# Try the same request from a computer to see what comes back:
#     curl "http://api.open-meteo.com/v1/forecast?latitude=44.98&longitude=-93.27&current=temperature_2m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto&forecast_days=2"

import requests

import config
import wifi_time

# timezone=auto splits the days at YOUR midnight, worked out from the
# latitude and longitude -- so "today" means today.
URL = ("http://api.open-meteo.com/v1/forecast"
       "?latitude={}&longitude={}"
       "&current=temperature_2m,weather_code"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min"
       "&temperature_unit={}&timezone=auto&forecast_days=2")


def describe(code):
    """A WMO weather code in a few words (9 characters or fewer)."""
    if code <= 1:
        return "Clear"                   # 0 clear, 1 mainly clear
    if code == 2:
        return "Pt cloudy"
    if code == 3:
        return "Cloudy"
    if code in (45, 48):
        return "Fog"
    if code in (56, 57, 66, 67):
        return "Frz rain"
    if 51 <= code <= 55:
        return "Drizzle"
    if 61 <= code <= 65:
        return "Rain"
    if 71 <= code <= 77 or code in (85, 86):
        return "Snow"
    if 80 <= code <= 82:
        return "Showers"
    if code >= 95:
        return "T-storms"
    return "?"


def unit_letter():
    return "C" if config.TEMPERATURE_UNIT == "celsius" else "F"


def fetch(display=None):
    """Join WiFi, get the weather, and switch WiFi off again. Returns the
    dict described at the top of this file, or None."""
    wlan = wifi_time.connect(display)
    if wlan is None:
        return None
    try:
        url = URL.format(config.LATITUDE, config.LONGITUDE,
                         config.TEMPERATURE_UNIT)
        response = requests.get(url, timeout=10)
        try:
            if response.status_code != 200:
                print("Weather failed: HTTP", response.status_code)
                return None
            data = response.json()
        finally:
            response.close()
        daily = data["daily"]
        weather = {
            "temp": round(data["current"]["temperature_2m"]),
            "code": data["current"]["weather_code"],
            "days": [(round(daily["temperature_2m_max"][i]),
                      round(daily["temperature_2m_min"][i]),
                      daily["weather_code"][i]) for i in range(2)],
        }
        print("Weather:", weather)
        return weather
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        print("Weather failed:", error)
        return None
    finally:
        wlan.disconnect()
        wlan.active(False)
