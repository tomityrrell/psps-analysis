import requests
import os

import pandas as pd

from mesowest_token import API_TOKEN

API_ROOT = "https://api.synopticdata.com/v2/"

api_request_url = os.path.join(API_ROOT, "stations/timeseries")


def mesowest_req(start="202101170000", end="202101200000"):
    api_arguments = {
        "token": API_TOKEN,
        "network": 231,  # Southern California Edison'
        "start": start,
        "end": end,
        # "vars": "wind_speed,wind_gust,relative_humidity",
        "units": "english,speed|mph",
    }

    req = requests.get(api_request_url, params=api_arguments)
    res = req.json()

    # df = pd.json_normalize(res["STATION"]).apply(pd.Series.explode)
    # df.columns = df.columns.str.title()
    # # df["Station"] = df.Stid.str.replace("SE", "")
    # df.reset_index(inplace=True)
    #
    # df.to_csv("./sce_{}_{}.csv".format(start, end))

    return res
