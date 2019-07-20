#THIS SCRIPT CREATES A DATAFRAME TO GET GEO DISTANCES BETWEEN EACH TERMINAL

import pandas as pd
from geopy.distance import geodesic

sd = pd.read_pickle("data/station-data.pkl")
sd1 = pd.read_pickle("data/station-data.pkl")
sd_rows = sd.shape[0]
sd_distances = {}

def manhattanDistance(coords_1, coords_2):
    x1, y1 = coords_1
    x2, y2 = coords_2

    # keep ycoord constant
    xdistance = geodesic((x1, y1), (x2, y1)).m
    # keep xcoord constant
    ydistance = geodesic((x1, y1), (x1, y2)).m

    return xdistance + ydistance


# Parsing through dataframe and getting distances between each Terminal
for x in range(0,sd_rows):
    distances = []
    coords_1 = (sd.loc[x, 'latitude'], sd.loc[x, 'longitude'])
    for y in range(0,sd_rows):
        #Getting real world distance given latitudes
        coords_2 = (sd.loc[y,'latitude'], sd.loc[y,'longitude'])

        distances.append(manhattanDistance(coords_1, coords_2))

    #Appending to dictionary
    key = sd.loc[x,'station_name']
    sd_distances[key] = distances
    # print(len(distances))

# Putting distances into dataframe
# print(sd_distances)

sdf = pd.DataFrame(sd_distances, index=sd['station_name'].tolist())

print(sdf)
pd.to_pickle(sdf, "data/distances.pkl")
