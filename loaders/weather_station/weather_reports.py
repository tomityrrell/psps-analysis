import requests
import json

import pandas as pd


with open('cimis_api_key', 'r') as f:
    appKey = f.readline()

stations = "6"
# stations = "6,  28,  58,  74,  98, 198, 217, 238, 250, 251, 255"
startDate = "2021-01-12"
endDate = "2021-01-21"

address = "https://et.water.ca.gov/api/data?appKey={}&targets={}&startDate={}&endDate={}&dataItems=hly-air-tmp,hly-dew-pnt,hly-eto,hly-net-rad,hly-asce-eto,hly-asce-etr,hly-precip,hly-rel-hum,hly-res-wind,hly-soil-tmp,hly-sol-rad,hly-vap-pres,hly-wind-dir,hly-wind-spd&unitOfMeasure=E"

r = requests.get(address.format(appKey, stations, startDate, endDate))
j = json.loads(r.content)

data = j["Data"]["Providers"]
data_df = pd.DataFrame(data)

hly_cols = data_df.columns[data_df.columns.str.contains("Hly")]
hly_sample = data_df.iloc[0][hly_cols]
hly_cols_units = map(lambda i: i[0] + " " + i[1], hly_sample.apply(lambda r: r["Unit"]).items())

data_df[hly_cols] = data_df[hly_cols].applymap(lambda r: r["Value"])
data_df.rename(columns={c: cu for (c, cu) in zip(hly_cols, hly_cols_units)}, inplace=True)

data_df.to_csv("./data/weather/weather_report.csv", index=False)