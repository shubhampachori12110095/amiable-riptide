#THIS SCRIPT CREATES A DATAFRAME WITH STATION NAMES AND ESTIMATES FOR AVERAGE DAILY DEMAND BASES ON THE 2017 Qi RIDE DATA

import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm

rd = pd.read_csv("data/ride-data-q3-2017.csv")
newDf = pd.DataFrame(columns=rd.columns)
# Set the date - it must be in the file you are taking in.
setDate = '7/1/2017'

print('Por favor be patient - this takes a minute...')

# Loop through the already sorted mega table until it is no longer the first date.
for index, row in rd.iterrows():
    tmp = row['trip_start_time']
    dateString = tmp.split(' ')[0]
    if (dateString == setDate):
        newDf.loc[index] = row
    if (dateString != setDate):
        break

print(newDf)

# Get the unique stations for s's and g's. 
unique_stations = newDf.from_station_name.unique()
print(unique_stations)

# Count the number of departures from each station on the hardcoded Q3 2017 date.
counter = newDf['from_station_name'].value_counts()
print(counter)
