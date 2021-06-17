import requests
import os

from mesowest_token import API_TOKEN

API_ROOT = "https://api.synopticdata.com/v2/"

api_request_url = os.path.join(API_ROOT, "stations/timeseries")


def mesowest_req(start="202101180000", end="202101220000"):
    api_arguments = {
        "token": API_TOKEN,
        "network": 231,  # Southern California Edison
        "start": start,
        "end": end,
        "vars": "wind_speed,wind_gust,relative_humidity",
        "units": "english,speed|mph",
    }

    req = requests.get(api_request_url, params=api_arguments)
    return req
