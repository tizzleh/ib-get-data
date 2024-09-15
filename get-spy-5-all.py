# Install ib_insync if not already installed
# !pip install ib_insync
# !pip install nest_asyncio

import nest_asyncio

nest_asyncio.apply()  # Allows the asyncio event loop to run within Jupyter

from ib_insync import *
import pandas as pd
from datetime import datetime, timedelta

# Connect to IB Gateway or TWS
ib = IB()
ib.connect("127.0.0.1", 4002, clientId=5)  # Adjust port and clientId as needed

# Define the VIX contract (Symbol: VIX, Exchange: CBOE)
contract = Index("VIX", "CBOE")


# Helper function to download historical data in chunks
def download_intraday_data(
    contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH
):
    """
    Download historical intraday data from Interactive Brokers.

    Args:
    contract: The contract for which to download data (e.g., Index('VIX', 'CBOE')).
    endDateTime: The end date/time for the data.
    durationStr: The duration of data to download (e.g., '1 D' for 1 day).
    barSizeSetting: The bar size (e.g., '1 min', '5 mins').
    whatToShow: The data type (e.g., 'TRADES' or 'BID_ASK').
    useRTH: Whether to use regular trading hours (True or False).

    Returns:
    pd.DataFrame: A dataframe containing the historical data.
    """
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=endDateTime,
        durationStr=durationStr,
        barSizeSetting=barSizeSetting,
        whatToShow=whatToShow,
        useRTH=useRTH,
        formatDate=1,
    )

    # Convert to pandas DataFrame
    df = util.df(bars)
    return df


# Set the time range: Go back as far as possible with 5-minute bars
end_date = datetime.now()
start_date = end_date - timedelta(
    days=365 * 10
)  # Adjust to go back further (up to 10 years)

# Initialize an empty DataFrame to hold the results
all_data_5min = pd.DataFrame()

# Download the data in chunks (IB limits the amount of data per request)
while end_date > start_date:
    print(f"Downloading 5-minute data up to {end_date}")

    # Download the data in chunks of 1 day at a time
    data = download_intraday_data(
        contract=contract,
        endDateTime=end_date.strftime("%Y%m%d %H:%M:%S"),
        durationStr="1 D",  # 1 day of data per request
        barSizeSetting="5 mins",  # 5-minute bars
        whatToShow="TRADES",  # Download trade data for VIX
        useRTH=False,
    )  # False means include premarket and aftermarket data

    # Append the downloaded data to the result DataFrame
    all_data_5min = pd.concat([data, all_data_5min])

    # Move the end date back by 1 day for the next download
    end_date = end_date - timedelta(days=1)

# Save the 5-minute data to a CSV file
all_data_5min.to_csv("VIX_5min_data.csv", index=False)

print("Download complete!")

# Display the first few rows of the DataFrame
all_data_5min.head()
