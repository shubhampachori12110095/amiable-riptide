# THIS SCRIPT CREATES A DATAFRAME WITH STATION NAMES AND ESTIMATES FOR AVERAGE DAILY DEMAND BASES ON THE 2017 Qi RIDE DATA

import pandas as pd
import pickle

rd = pd.read_csv("data/ride-data-q3-2017.csv")

# Set the date - it must be in the file you are taking in.
today = '7/1/2017'

print('Por favor be patient - this takes a minute...')

# read from known station data
sd = pd.read_pickle("data/station-data.pkl")
stationNames = set(sd['station_name'].tolist())

# track all dates covered
dates = [today]

# { 'station' : outgoing trips } counts the outgoing trips in a day
outgoingTripsPerDay = {key: 0 for key in stationNames}

# { 'station' : incoming trips } counts incoming trips in a day
incomingTripsPerDay = {key: 0 for key in stationNames}

# { 'station' : incoming - outgoing trips } counts delta trips in a day
deltaPerDay = {key: 0 for key in stationNames}

allOutgoingTrips = []
allIncomingTrips = []
allDeltas = []


def addOutgoingTrip(station):
    if station in outgoingTripsPerDay:
        outgoingTripsPerDay[station] += 1
        deltaPerDay[station] -= 1


def addIncomingTrip(station):
    if station in incomingTripsPerDay:
        incomingTripsPerDay[station] += 1
        deltaPerDay[station] += 1


for index, row in rd.iterrows():
    date = row['trip_start_time'].split(' ')[0]
    from_station = row['from_station_name']
    to_station = row['to_station_name']

    if date == today:
        addOutgoingTrip(from_station)
        addIncomingTrip(to_station)

    if date != today:
        dates.append(date)
        today = date
        # add days worth of data to all data
        allOutgoingTrips.append(outgoingTripsPerDay)
        allIncomingTrips.append(incomingTripsPerDay)
        allDeltas.append(deltaPerDay)
        # new day so reset dicts
        outgoingTripsPerDay = {key: 0 for key in stationNames}
        incomingTripsPerDay = {key: 0 for key in stationNames}
        deltaPerDay = {key: 0 for key in stationNames}
        addOutgoingTrip(from_station)
        addIncomingTrip(to_station)

# add the last day in there
allOutgoingTrips.append(outgoingTripsPerDay)
allIncomingTrips.append(incomingTripsPerDay)
allDeltas.append(deltaPerDay)

# Create data frames
outgoingDf = pd.DataFrame(data=allOutgoingTrips, columns=stationNames, index=dates)
incomingDf = pd.DataFrame(data=allIncomingTrips, columns=stationNames, index=dates)
deltaDf = pd.DataFrame(data=allDeltas, columns=stationNames, index=dates)

# remove any column of all zeros
outgoingDf = outgoingDf.loc[:, (outgoingDf != 0).any(axis=0)]
incomingDf = incomingDf.loc[:, (incomingDf != 0).any(axis=0)]
deltaDf = deltaDf.loc[:, (deltaDf != 0).any(axis=0)]

#write data to pickle file for easy access
pd.to_pickle(outgoingDf, "data/outgoingTrips.pkl")
pd.to_pickle(incomingDf, "data/incomingTrips.pkl")
pd.to_pickle(deltaDf, "data/deltaIncomingOutgoing.pkl")

# find the average incoming and outgoing rounded down
averageOutgoing = outgoingDf.mean(axis=0).to_frame().round(decimals=0)
averageIncoming = incomingDf.mean(axis=0).to_frame().round(decimals=0)
averageDelta = deltaDf.mean(axis=0).to_frame().round(decimals=0)

# write averages to pickle file
pd.to_pickle(averageOutgoing, "data/averageOutgoing.pkl")
pd.to_pickle(averageIncoming, "data/averageIncoming.pkl")
pd.to_pickle(averageDelta, "data/averageDelta.pkl")

print(outgoingDf)
print(incomingDf)
