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
    # The order of variables in hourly or daily is the same as the returned order.
    if ARCHIVE:
        hourly_var_name = [
            "soil_moisture_0_to_7cm",
            "soil_moisture_7_to_28cm",
            "soil_moisture_28_to_100cm",
            "soil_moisture_100_to_255cm",
        ]
        daily_var_name: []

    else:
        hourly_var_name = [
            "soil_moisture_0_to_1cm",
            "soil_moisture_1_to_3cm",
            "soil_moisture_3_to_9cm",
            "soil_moisture_9_to_27cm",
            "soil_moisture_27_to_81cm",
        ]
        daily_var_name: []

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
