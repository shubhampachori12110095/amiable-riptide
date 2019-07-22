import pandas as pd
import pickle
import random
import numpy
import matplotlib.pyplot as plt
import geopandas as gpd


sd = pd.read_pickle("data/station-data.pkl")

sd.drop(['inventory', 'capacity'], axis=1, inplace=True)

sd.loc[-1] = ['DC', 43.645609, -79.380386]
sd.index = sd.index + 1
sd.sort_index(inplace=True)
sd_rows = sd.shape[0]

sd = sd.set_index('station_name')

# sd.to_csv("data/map_data.csv")

stations_visited = pickle.load(open("data/all-stations-visited-inorder.p", "rb"))

def makeLine(path):
    res = {
        "type": "Feature",
        "properties": {
            "stroke": "#41b740",
            "stroke-width": 2,
            "stroke-opacity": 1
        },
        "geometry": {
            "type": "LineString",
            "coordinates": path
        }
    }
    return res

path = []
isStart = -1
for sv in stations_visited:
    if sv == 'DC':
        isStart = isStart*(-1)

    lat = sd.loc[sv]['latitude']
    long = sd.loc[sv]['longitude']
    path.append([long, lat])

    if isStart == -1:
        print(makeLine(path))
        print(",")
        path = []

print(path)