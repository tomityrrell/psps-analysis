import pandas as pd

import pydeck as pdk
import streamlit as st

#
# DATA
#


# Import psps data
@st.cache()
def get_psps_data():
    source = pd.read_csv("../data/source.csv", parse_dates=["start", "end"])

    # Start/End Dates for recent PSPS events
    se_dates = source[["start", "end"]]
    se_dates = se_dates[~se_dates.duplicated()].sort_values(by="start")
    se_dates["label"] = se_dates.start.astype("str") + " - " + se_dates.end.astype("str")
    se_dates.set_index("label", inplace=True)

    return source, se_dates

source, se_dates = get_psps_data()

# Import CIMIS weather station/report data
@st.cache()
def get_cimis_data():
    ws = pd.read_csv("../data/weather/weather_stations.csv", parse_dates=True)
    ws.dropna(axis=1, how="any", inplace=True)
    ws.dropna(axis=0, how="any", inplace=True)
    ws.rename(columns={"StationNbr": "Station"}, inplace=True)
    ws.set_index("Station", inplace=True)

    wr = pd.read_csv("../data/weather/weather_report.csv", parse_dates=["Date"])
    wr = wr[(wr.Date >= "2020-12-01") & (wr["HlyWindSpd (MPH)"] < 100) & (wr["HlyRelHum (%)"] > 0)]
    wr.set_index(["Station", "Time"], inplace=True)

    return ws, wr

ws, wr = get_cimis_data()

# Midpoint for Visualizations
midpoint = ws[["Latitude", "Longitude"]].mean().values

# Import SCE data
@st.cache()
def get_sce_data():
    wr_mw = pd.read_csv("../loaders/mesowest/sce.csv", parse_dates=["Date"])
    # wr_mw.Time = wr_mw.Time.dt.tz_localize(None)
    # wr_mw["Date"] = wr_mw.Time.dt.date
    # wr_mw.rename(columns={"GustSpeed": "GustSpd", "WindSpeed": "WindSpd"}, inplace=True)

    ws_mw = wr_mw[["Station", "Name", "Latitude", "Longitude"]]
    ws_mw = ws_mw[~ws_mw.duplicated(subset="Station")]

    ws_mw.set_index("Station", inplace=True)
    wr_mw.set_index(["Station", "Time"], inplace=True)

    return ws_mw, wr_mw

ws_mw, wr_mw = get_sce_data()


# Import model output data
@st.cache()
def get_model_outputs():
    crossings = pd.read_csv("../data/metrics/summaries/crossings_Jan19_24.csv")
    crossings.rename(columns={"Prob of Crossing": "Crossing_Prob", "Actual Crossing Count": "Crossing_Count"}, inplace=True)

    predictions = pd.read_csv("../data/predictions/predictions_24hr_jan19.csv")

    return crossings, predictions

crossings, predictions = get_model_outputs()

#
# SIDEBAR
#

st.sidebar.subheader("Options")

option = st.sidebar.radio("Views", ["MesoWest Networks", "PSPS Events", "Wind/Humidity Warnings - Jan 19th, 2021"])

network, select_psps_date = "", ""
if option == "MesoWest Networks":
    network = st.sidebar.selectbox("MesoWest Networks", ["CIMIS", "SCE"])

if option == "PSPS Events":
    # PSPS Drop-down
    select_psps_date = st.sidebar.selectbox("PSPS Events", se_dates[se_dates.start >= "2020-12-04"].index)
    psps_network = "CIMIS"

    if "01-12" in select_psps_date:
        psps_network = st.sidebar.radio("Network", ["CIMIS", "SCE"])

#
# APP
#

layers = []
tooltip = {}

if network:
    weather_stations = None
    if network == "CIMIS":
        weather_stations = ws
        radius = 2500
    elif network == "SCE":
        weather_stations = ws_mw
        radius = 1000

    midpoint = weather_stations[["Latitude", "Longitude"]].mean().values

    weather_station_layer = pdk.Layer(
        type='ScatterplotLayer',
        data=weather_stations,
        get_position=["Longitude", "Latitude"],
        auto_highlight=True,
        get_radius=radius,
        get_fill_color=[180, 0, 200, 140],
        pickable=True
    )
    layers = [weather_station_layer]

    tooltip = {
        "html": "<b>{Name}</b>"
    }
elif select_psps_date and psps_network == "CIMIS":
    psps_date = se_dates.loc[select_psps_date]

    idx_wind_max = wr[(wr.Date >= psps_date.start) & (wr.Date <= psps_date.end)].groupby("Station")["HlyWindSpd (MPH)"].idxmax()
    idx_wind_max.dropna(inplace=True)

    extreme_values = wr.loc[idx_wind_max, ["HlyRelHum (%)", "HlyWindSpd (MPH)"]]
    extreme_values["MaxTime"] = extreme_values.index.get_level_values(1)

    ws_data = ws.merge(extreme_values.droplevel(1), on="Station")
    ws_data = ws_data.rename(columns={"HlyWindSpd (MPH)": "WindSpd", "HlyRelHum (%)": "RelHum"})

    wind_layer = pdk.Layer(
                        type='ColumnLayer',
                        data=ws_data,
                        get_position=["Longitude", "Latitude"],
                        get_elevation="WindSpd",
                        elevation_scale=1000,
                        # get_radius=1000,
                        get_fill_color=["WindSpd > 15 ? 255 : 0", "WindSpd > 25 ? 0 : 255", 0, 200],
                        auto_highlight=True,
                        pickable=True,
                        extruded=True
                    )

    hum_layer = pdk.Layer(
                        type='ColumnLayer',
                        data=ws_data,
                        get_position=["Longitude", "Latitude"],
                        get_elevation="RelHum",
                        elevation_scale=100,
                        # radius=1000,
                        offset=[1.414, 1.414],
                        get_fill_color=["RelHum < 23 ? 255 : 0", "RelHum < 34 ? 0 : 255", 0, 200],
                        auto_highlight=True,
                        pickable=True,
                        extruded=True
                    )

    layers = [wind_layer, hum_layer]
    tooltip = {
        "html": "<b>{Name}</b> - <b> {MaxTime}</b> <br> "
                "<b>{WindSpd}</b> MPH max wind observed <br> "
                "<b>{RelHum}</b> % relative humidity observed"
    }
elif select_psps_date and psps_network == "SCE":
    psps_date = se_dates.loc[select_psps_date]

    wr = wr_mw
    ws = ws_mw

    idx_wind_max = wr[(wr.Date >= psps_date.start) & (wr.Date <= psps_date.end)].groupby("Station")["WindSpd"].idxmax()
    idx_wind_max.dropna(inplace=True)
    
    extreme_values = wr.loc[idx_wind_max, ["WindSpd", "RelHum"]]
    extreme_values["MaxTime"] = extreme_values.index.get_level_values(1)

    ws_data = ws.merge(extreme_values.droplevel(1), on="Station")

    wind_layer = pdk.Layer(
                        type='ColumnLayer',
                        data=ws_data,
                        get_position=["Longitude", "Latitude"],
                        get_elevation="WindSpd",
                        elevation_scale=1000,
                        # get_radius=1000,
                        get_fill_color=["WindSpd > 15 ? 255 : 0", "WindSpd > 25 ? 0 : 255", 0, 200],
                        auto_highlight=True,
                        pickable=True,
                        extruded=True
                    )

    hum_layer = pdk.Layer(
                        type='ColumnLayer',
                        data=ws_data,
                        get_position=["Longitude", "Latitude"],
                        get_elevation="RelHum",
                        elevation_scale=100,
                        # radius=1000,
                        offset=[1.414, 1.414],
                        get_fill_color=["RelHum < 10 ? 255 : 0", "RelHum < 17 ? 0 : 255", 0, 200],
                        auto_highlight=True,
                        pickable=True,
                        extruded=True
                    )

    layers = [wind_layer, hum_layer]
    tooltip = {
        "html": "<b>{Name}</b> - <b>{MaxTime}</b> <br> "
                "<b>{WindSpd}</b> MPH max wind observed <br> "
                "<b>{RelHum}</b> % relative humidity observed"
    }
elif "Warning" in option:
    ws_data = ws.merge(crossings, on="Station")
    # ws_data

    crossings_layer = pdk.Layer(
        type='ColumnLayer',
        data=ws_data,
        get_position=["Longitude", "Latitude"],
        get_elevation="Crossing_Prob * 100",
        elevation_scale=1000,
        # get_radius=1000,
        get_fill_color=["Crossing_Prob > .50 ? 255 : 0", "Crossing_Prob > .75 ? 0 : 255", 0, 200],
        auto_highlight=True,
        pickable=True,
        extruded=True
    )
    layers = [crossings_layer]

    tooltip = {
        "html": "<b>{Name} - {Station}</b><br> "
                "<b>{Crossing_Prob}</b> probability of crossing <br> "
                "<b>{Crossing_Count}</b> crossings observed"
    }

initial_view = pdk.ViewState(latitude=midpoint[0],
                             longitude=midpoint[1],
                             zoom=6,
                             pitch=50,
                             bearing=0)

deck = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view,
        tooltip=tooltip,
        # map_provider="mapbox",
        # map_style="satellite"
    )

st.pydeck_chart(deck)

if st.button("Save map"):
    deck.to_html("map_{}.html".format(option.replace("/", "")))

