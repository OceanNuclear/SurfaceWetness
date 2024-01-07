import argparse
import datetime as dt
from math import inf

import requests_cache
import openmeteo_requests
from retry_requests import retry

from locality import lat_long

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
    choices=list(lat_long.keys()),
    help="Location at which the data is required")
parg.add_argument('-v', '--verbose', action="store_true")

archive_url = "https://archive-api.open-meteo.com/v1/archive"
def get_response(cl_arg, variables, base_url=archive_url):
    """Get the raw API response for the queried parameters, 
    and set-up the Open-Meteo API client with cache and retry on error"""
    # calculate start- and end-dates
    today = dt.date.today()
    if cl_arg.current:
        today = dt.date.today()
        start_date = (today - dt.timedelta(days=1))
        end_date = dt.date.today()
    else:
        start_date = cl_arg.historical.start_date
        end_date = cl_arg.historical.end_date
    # set-up the cache's name
    cache_session = requests_cache.CachedSession(f'.{start_date}_{end_date}_cache_hist',
                            expire_after=inf)
    # set parameters for how many times to re-try the connection
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo_client = openmeteo_requests.Client(session=retry_session)
    params = {
        "latitude": lat_long[cl_arg.location][0],
        "longitude": lat_long[cl_arg.location][1],
        "start_date": start_date,
        "end_date": end_date,
        **variables,
        "timezone": dt.datetime.now().astimezone().tzinfo.tzname(None)
    }
    return openmeteo_client.weather_api(base_url, params=params)

def print_response_diagnostics(response):
    print(f"Coordinates: {response.Latitude()}°E {response.Longitude()}°N,")
    print(f"Elevation: {response.Elevation()} m above sea level.")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
