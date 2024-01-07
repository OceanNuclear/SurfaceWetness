import argparse
import datetime as dt

import requests_cache
import openmeteo_requests
from retry_requests import retry

import pandas as pd

parg = argparse.ArgumentParser(description="Downloads historical soil moisture readings.",
    usage="""python soil_moisture.py -c [-l location]; or
python soil_moisture.py -d start_date end_date [-l location]""",)
# required flag
dates = parg.add_mutually_exclusive_group(required=True)
dates.add_argument('-c', dest='current', action='store_true',
    help="Find the most current historical soil-moisture data")
dates.add_argument('-d', dest='historical', nargs=2, metavar=('start_date','end_date'),
    help="Specify the start and end date of the period of soil-moisture data required.")
# optional flag
parg.add_argument('-l', dest='location', default="Didcot",
    help="Location at which the soil-moisture data is required")
lat_long = {
    "Appleford": (51.6399, -1.2423),
    "Oxford": (51.7537, -1.2610),
    "Didcot": (51.6093, -1.2421),
    # "Didcot_Culham_commute": (51.6301, -1.2352),
    "Tilehurst": (51.4710, -1.0292),
    "Upton": (51.5765, -1.2626),
}

archive_url = "https://archive-api.open-meteo.com/v1/archive"
def get_response(params, base_url=archive_url):
    """Get the raw API response for the queried parameters."""
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo_client = openmeteo_requests.Client(session = retry_session)
    return openmeteo_client.weather_api(base_url, params=params)

if __name__=="__main__":
    cl_arg = parg.parse_args()
    if cl_arg.current:
        today = dt.date.today()
        start_date = ( - dt.timedelta(days=1))
        end_date = dt.date.today()
    else:
        start_date = cl_arg.historical.start_date
        end_date = cl_arg.historical.end_date
    params = {
        "latitude": lat_long[cl_arg.location][0],
        "longitude": lat_long[cl_arg.location][1],
        "start_date": cl_arg.start_date,
        "end_date": cl_arg.end_date,
        # The order of variables in hourly or daily is the same as the returned order.
        "hourly": ["soil_moisture_0_to_7cm",
                    "soil_moisture_7_to_28cm",
                    "soil_moisture_28_to_100cm",
                    "soil_moisture_100_to_255cm"],
        # "daily": [],
        "timezone": dt.datetime.now().astimezone().tzinfo.tzname(None)
    }

# Process first location. Add a for-loop for multiple locations or weather models
response = get_response()
print(f"Coordinates: {response.Latitude()}°E {response.Longitude()}°N,")
print(f"Elevation: {response.Elevation()} m above sea level.")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_soil_moisture_0_to_7cm = hourly.Variables(0).ValuesAsNumpy()
hourly_soil_moisture_7_to_28cm = hourly.Variables(1).ValuesAsNumpy()
hourly_soil_moisture_28_to_100cm = hourly.Variables(2).ValuesAsNumpy()
hourly_soil_moisture_100_to_255cm = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(hourly.Time(), unit="s"),
    end = pd.to_datetime(hourly.TimeEnd(), unit="s"),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)}
hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)
