import time
import requests
import json

import pandas as pd

from cimis_api_key import appKey

# stations = "6"
# stations = "6,  28,  58,  74,  98, 198, 217, 238, 250, 251, 255"
# startDate = "2021-01-12"
# endDate = "2021-01-21"

address = "http://et.water.ca.gov/api/data?appKey={}&targets={}&startDate={}&endDate={}&dataItems=hly-air-tmp,hly-dew-pnt,hly-eto,hly-net-rad,hly-asce-eto,hly-asce-etr,hly-precip,hly-rel-hum,hly-res-wind,hly-soil-tmp,hly-sol-rad,hly-vap-pres,hly-wind-dir,hly-wind-spd&unitOfMeasure=E"


def weather_station_query(queries, save=False, verbose=True):
    query_dfs = []
    for (station, startDate, endDate) in queries:
        if verbose:
            print("Querying", station, startDate, endDate)
        
        try:
            r = requests.get(address.format(appKey, station, startDate, endDate))
            j = json.loads(r.content)
        except json.JSONDecodeError:
            print("Failed to retrieve query:", station, startDate, endDate)
            continue

        query = j["Data"]["Providers"][0]["Records"]
        query_dfs.append(pd.DataFrame(query))

    data_df = pd.concat(query_dfs)

    hly_cols = data_df.columns[data_df.columns.str.contains("Hly")]
    hly_sample = data_df.iloc[0][hly_cols]
    hly_cols_units = map(lambda i: i[0] + " " + i[1], hly_sample.apply(lambda r: r["Unit"]).items())

    data_df[hly_cols] = data_df[hly_cols].applymap(lambda r: r["Value"])
    data_df.rename(columns={c: cu for (c, cu) in zip(hly_cols, hly_cols_units)}, inplace=True)

    if save:
        data_df.to_csv("./data/weather/weather_report_{}.csv".format(time.time()), index=False)

    return data_df
