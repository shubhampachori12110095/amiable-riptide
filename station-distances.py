#THIS SCRIPT CREATES A DATAFRAME TO GET GEO DISTANCES BETWEEN EACH TERMINAL

import pandas as pd
import numpy as np
from geopy.distance import geodesic

sd = pd.read_csv("data/station-data.csv")
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


#Parsing through dataframe and getting distances between each Terminal
for x in range(0,sd_rows):
    for y in range(0,sd_rows):
        #Getting real world distance given latitudes
        coords_1 = (sd.loc[x,'Latitude'], sd.loc[x,'Longitude'])
        coords_2 = (sd.loc[y,'Latitude'], sd.loc[y,'Longitude'])

        distance = manhattanDistance(coords_1, coords_2)

        #Appending to dictionary
        key = sd.loc[x,'Terminal']
        sd_distances.setdefault(key, []).append(distance)

#Putting distances into dataframe
sdf = pd.DataFrame.from_dict(sd_distances)
print(sdf)
#sdf.to_csv('station-distances.csv', index =True, header=True) #Optional if you want the distances in CSV form

