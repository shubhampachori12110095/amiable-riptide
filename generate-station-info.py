import pandas as pd
import json

with open('data/citybikeData.json') as f:
  data = json.load(f)

stations = data['network']['stations']

currentNumBikes = 5000.0
previousNumBikes = 2750.0
ratio = previousNumBikes/currentNumBikes

stationNames = []
stationLats = []
stationLongs = []
inventories = []
capacities = []

for station in stations:
    name = station['extra']['address']
    lat = station['latitude']
    long = station['longitude']
    inventory = station['free_bikes']
    empty = station['empty_slots']
    capacity = inventory + empty

    stationNames.append(name)
    stationLats.append(lat)
    stationLongs.append(long)
    inventories.append(inventory)
    capacities.append(capacity)

data = {
    'station_name': stationNames,
    'latitude': stationLats,
    'longitude': stationLongs,
    'inventory': inventories,
    'capacity': capacities
}

df = pd.DataFrame(data)

# pickle the data
pd.to_pickle(df, "data/station-data.pkl")

print("done")
