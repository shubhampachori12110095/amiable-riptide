import pandas as pd
import json

acceptedStationNames = set()
rd = pd.read_csv("data/ride-data-q3-2017.csv")

for i, row in rd.iterrows():
    from_station = row['from_station_name']
    to_station = row['to_station_name']
    acceptedStationNames.add(from_station)
    acceptedStationNames.add(to_station)


with open('data/citybikeData.json') as f:
  data = json.load(f)

stations = data['network']['stations']

stationNames = []
stationLats = []
stationLongs = []
inventories = []
capacities = []

for station in stations:
    name = station['extra']['address']
    if name in acceptedStationNames:
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
