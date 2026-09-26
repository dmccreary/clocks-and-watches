# forecast.py -- today's and tomorrow's weather, from Open-Meteo.
#
# Open-Meteo (https://open-meteo.com) is a free weather service that needs
# no account and no API key, so there is nothing to add to secrets.py. You
# ask for exactly the numbers you want, and it sends back only those: for
# two days of highs, lows, and weather codes the whole answer is about
# 450 bytes of JSON, small enough for a Pico to fetch and read in about
# a second.
#
#     import forecast
#     days = forecast.fetch()
#     # [(high, low, code), (high, low, code)] -- today, then tomorrow --
#     # or None if the WiFi or the service did not answer.
#     icon, words = forecast.describe(days[0][2])
#
# The code is a WMO weather code, a numbering the World Meteorological
# Organization uses for weather conditions. describe() turns it into one
# of five icon names and a few words for the screen.
#
# Try the same request from a computer to see what comes back:
#     curl "http://api.open-meteo.com/v1/forecast?latitude=44.98&longitude=-93.27&daily=weather_code,temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&timezone=auto&forecast_days=2"

import requests

import config
import wifi_time

# timezone=auto tells the service to split the days at YOUR midnight,
# worked out from the latitude and longitude -- so "today" means today.
URL = ("http://api.open-meteo.com/v1/forecast"
       "?latitude={}&longitude={}"
       "&daily=weather_code,temperature_2m_max,temperature_2m_min"
       "&temperature_unit={}&timezone=auto&forecast_days=2")

# Icon names.
SUNNY = "sunny"
PARTLY_CLOUDY = "partly cloudy"
CLOUDY = "cloudy"
RAIN = "rain"
SNOW = "snow"


def describe(code):
    """Turn a WMO weather code into (icon name, words, 9 characters or
    fewer). Fog uses the cloud icon; drizzle, showers, and thunderstorms
    use the rain icon."""
    if code <= 1:
        return SUNNY, "Sunny"            # 0 clear, 1 mainly clear
    if code == 2:
        return PARTLY_CLOUDY, "Pt cloudy"
    if code == 3:
        return CLOUDY, "Cloudy"
    if code in (45, 48):
        return CLOUDY, "Fog"
    if code in (56, 57, 66, 67):
        return RAIN, "Frz rain"          # freezing drizzle and rain
    if 51 <= code <= 55:
        return RAIN, "Drizzle"
    if 61 <= code <= 65:
        return RAIN, "Rain"
    if 71 <= code <= 77 or code in (85, 86):
        return SNOW, "Snow"
    if 80 <= code <= 82:
        return RAIN, "Showers"
    if code >= 95:
        return RAIN, "T-storms"
    return CLOUDY, "?"


def fetch(display=None, disconnect=True):
    """Get today's and tomorrow's forecast. Returns
    [(high, low, code), (high, low, code)] with whole-number temperatures,
    or None if it could not get one.

    Pass the display to see WiFi progress on the screen. Pass
    disconnect=False to leave WiFi on for something else, like
    wifi_time.sync_time(), which reuses the connection."""
    wlan = wifi_time.connect(display)
    if wlan is None:
        return None
    try:
        url = URL.format(config.LATITUDE, config.LONGITUDE,
                         config.TEMPERATURE_UNIT)
        response = requests.get(url, timeout=10)
        try:
            if response.status_code != 200:
                print("Forecast failed: HTTP", response.status_code)
                return None
            daily = response.json()["daily"]
        finally:
            response.close()
        days = []
        for i in range(2):
            days.append((round(daily["temperature_2m_max"][i]),
                         round(daily["temperature_2m_min"][i]),
                         daily["weather_code"][i]))
        print("Forecast:", days)
        return days
    except (OSError, ValueError, KeyError, IndexError) as error:
        print("Forecast failed:", error)
        return None
    finally:
        if disconnect:
            wlan.disconnect()
            wlan.active(False)
