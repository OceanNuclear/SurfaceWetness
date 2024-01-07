import datetime as dt

import numpy as np
np.datetime64
from matplotlib.dates import DateFormatter
import pandas as pd
ARCHIVE = False
if ARCHIVE:
    from query_historical import parg, get_response, print_response_diagnostics
else:
    from query_api import parg, get_response, print_response_diagnostics

if __name__=="__main__":
    cl_arg = parg.parse_args()
    if ARCHIVE:
        hourly = [
            "rain",
            "precipitation", #
            "et0_fao_evapotranspiration", #
            "vapour_pressure_deficit",
            "wind_speed_10m",
            "wind_speed_100m",
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "sunshine_duration",
            "shortwave_radiation",
            "direct_radiation",
            "diffuse_radiation"
        ],
    else:
        hourly = [
            "rain",
            "precipitation", #
            "evapotranspiration", #
            "et0_fao_evapotranspiration",
        ]

# Process first location. Add a for-loop for multiple locations or weather models
response = get_response(cl_arg, {"hourly":hourly_var_name, "daily":daily_var_name})
if cl_arg.verbose:
    print_response_diagnostics(response)

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()

date_ticks = pd.date_range(
    start=pd.to_datetime(hourly.Time(), unit="s"),
    end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
    freq=dt.timedelta(seconds=hourly.Interval()),
    inclusive="left")

hourly_data = {column_name : hourly.Variables(n).ValuesAsNumpy() for n, column_name in enumerate(hourly_var_name)}

hourly_df = pd.DataFrame(hourly_data, index=date_ticks)

if cl_arg.verbose:
    print(hourly_df)
# ax.xaxis.set_major_formatter(DateFormatter("%d/%m(%a)"))
