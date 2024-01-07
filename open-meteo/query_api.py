import argparse
import datetime as dt
from math import inf

import requests_cache
import openmeteo_requests
from retry_requests import retry

from locality import lat_long

parg = argparse.ArgumentParser(description="Downloads historical & forecasted weather.",
    usage=f"python {__file__}.py [-P number_of_days_into_the_past]"
    "[-F number_of_days_into_the_future] [-l location]",)
# optional flags
parg.add_argument('-P', dest='past_days', type=int, default=1,
    help="How many days back in time to get the historical data.")
parg.add_argument('-F', dest='forecast_days', type=int, default=0,
    help="How many days forward in time to predict the weather data.")
parg.add_argument('-l', dest='location', default="Didcot",
    choices=list(lat_long.keys()),
    help="Location at which the data is required")
parg.add_argument('-v', '--verbose', action="store_true")

forecast_url= "https://api.open-meteo.com/v1/forecast"
def get_response(cl_arg, variables, base_url=forecast_url):
    """Get the raw API response for the queried parameters, 
    and set-up the Open-Meteo API client with cache and retry on error"""
    today = dt.date.today()
    start_date = (today - dt.timedelta(days=cl_arg.past_days)).iso_format()
    end_date = (today + dt.timedelta(days=cl_arg.forecast_days)).iso_format()
    # set-up the cache's name
    cache_session = requests_cache.CachedSession(f'.{start_date}_{end_date}_cache',
                            expire_after=inf if cl_arg.forecast_days==0 else 3600)
    # set parameters for how many times to re-try the connection
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo_client = openmeteo_requests.Client(session=retry_session)
    params = {
        "latitude": lat_long[cl_arg.location][0],
        "longitude": lat_long[cl_arg.location][1],
        "past_days": cl_arg.past_days,
        "forecast_days": cl_arg.forecast_days,
        **variables,
        "timezone": dt.datetime.now().astimezone().tzinfo.tzname(None)
    }
    return openmeteo_client.weather_api(base_url, params=params)

def print_response_diagnostics(response):
    print(f"Coordinates: {response.Latitude()}°E {response.Longitude()}°N,")
    print(f"Elevation: {response.Elevation()} m above sea level.")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
