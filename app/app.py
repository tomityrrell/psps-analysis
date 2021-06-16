import pandas as pd

import pydeck as pdk
import streamlit as st

#
# DATA
#

# Import psps data
source = pd.read_csv("../data/source.csv", parse_dates=["start", "end"])

# Import weather station data
ws = pd.read_csv("../data/weather/weather_stations.csv", parse_dates=True)
# ws = ws.rename(columns={"Latitude": "lat", "Longitude": "lon"})
ws = ws.dropna(axis=1, how="all").dropna(axis=0, how="any")

# Import weather report data
wr = pd.read_csv("../data/weather/weather_report.csv", parse_dates=["Date"])

# Cross-reference Jan 2021 PSPS event against weather station list
notifications = pd.read_csv("../data/2021/deenergization_2021.csv", parse_dates=True)
notif_by_county = notifications.County.value_counts().sort_values()
counties = []
for county in notif_by_county.index:
    for c in county.split(";"):
        counties.append(c.title())
psps_county_stations = ws[ws.County.isin(counties)].StationNbr

# High-wind stations
high_wind_stations = wr[wr.Station.isin(psps_county_stations.values)][["Station", "HlyWindSpd (MPH)"]].groupby("Station").max()
high_wind_stations = high_wind_stations[(high_wind_stations > 20) & (high_wind_stations < 60)].dropna()

max_winds = wr.groupby("Station")["HlyWindSpd (MPH)"].max()
ws_wind = ws.merge(max_winds[max_winds < 150], left_on="StationNbr", right_on="Station")
ws_wind = ws_wind.rename(columns={"HlyWindSpd (MPH)": "WindSpd", "HlyRelHum (%)": "RelHum"})

# Midpoint for Visualizations
midpoint = ws[["Latitude", "Longitude"]].mean().values

#
# APP
#

st.write(ws)
#
# checkbox_psps_stations = st.checkbox("PSPS Impacted")
# checkbox_high_wind = st.checkbox("High Winds Observed")
# if checkbox_high_wind:
#     st.map(ws[ws.StationNbr.isin(high_wind_stations.index)])
# elif checkbox_psps_stations:
#     st.map(ws[ws.StationNbr.isin(psps_county_stations)])
# else:
#     st.map(ws)

initial_view = pdk.ViewState(latitude=midpoint[0],
                             longitude=midpoint[1],
                             zoom=6,
                             pitch=50,
                             bearing=0)

weather_station_layer = pdk.Layer(
                        type='ScatterplotLayer',
                        data=ws,
                        get_position=["Longitude", "Latitude"],
                        auto_highlight=True,
                        get_radius=5000,
                        get_fill_color=[180, 0, 200, 140],
                        pickable=True
                    )

max_wind_layer = pdk.Layer(
                    type='ColumnLayer',
                    data=ws_wind,
                    get_position=["Longitude", "Latitude"],
                    get_elevation="WindSpd",
                    elevation_scale=1000,
                    get_radius=1,
                    get_coverage=.5,
                    get_fill_color=["WindSpd > 20 ? 255 : 0", "WindSpd > 25 ? 0 : 255", 0, 200],
                    auto_highlight=True,
                    pickable=True,
                    extruded=True
                )

tooltip = {
    "html": "<b>{Name}</b> - <b>{WindSpd}</b> MPH max wind observed"
}

deck = pdk.Deck(
        layers=[max_wind_layer],
        initial_view_state=initial_view,
        tooltip=tooltip,
        # map_provider="mapbox",
        # map_style="satellite"
    )

deck.to_html("./map.html")

st.pydeck_chart(deck)
