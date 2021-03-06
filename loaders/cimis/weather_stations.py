import requests
import json

import pandas as pd

from cimis.cimis_api_key import appKey

address = "https://et.water.ca.gov/api/station?appKey={}"
res = requests.get(address.format(appKey))
json_res = json.loads(res.content)
stations = json_res["Stations"]
stations_df = pd.DataFrame(stations)
stations_df.to_csv("./data/weather/weather_stations.csv", index=False)
