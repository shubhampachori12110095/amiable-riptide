from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import random
import pickle

def create_model():

    # Import all data needed. 
    distances = pd.read_pickle('data/distances.pkl').astype(int)
    stationData = pd.read_pickle('data/station-data.pkl')
    averageDelta = pd.read_pickle('data/averageDelta.pkl')
    ## Add the DC to the average deltas.
    listOfDemands = averageDelta[0].tolist()

    # Make all the demands into integers
    listOfDemands = [round(x) for x in listOfDemands]
    # Change all negative values in list of demands to zero.
    listOfDemands = [0 if i > 0 else i for i in listOfDemands]

    # Find all the zero demands (because we won't want to visit these nodes), and drop them from the demand list.
    # Save the indices of these dropped nodes and drop them from the distance matrix also.

    demandIndicesToDrop = [i for i in range(len(listOfDemands)) if listOfDemands[i] == 0]
    # print(demandIndicesToDrop)
    
    distances.drop(distances.index[demandIndicesToDrop], inplace=True)
    distances.drop(distances.columns[demandIndicesToDrop], axis=1, inplace=True)

    # station data cleaned of stations with 0 demand
    stationData.drop(stationData.index[demandIndicesToDrop], inplace=True)

    # map indicies to station names
    stationNames = stationData['station_name'].tolist()

    # prepend DC
    stationNames.insert(0, 'DC')

    #pickle stations names
    pickle.dump(stationNames, open("station-node-mapping.p", "wb"))

    
    # Remove zero values from demand list
    listOfDemands = list(filter(lambda a: a != 0, listOfDemands))

    # Add DC to list of demands
    listOfDemands.insert(0, 0)

    # flip negative values
    listOfDemands = [abs(value) for value in listOfDemands]

    # Create the array of arrays for the distances.
    distanceList = distances.values.tolist()

    data = {}

    # TODO
    #1 Import distance matrix and make it in list of lists (A, B, C, D, ..., DC) 2D m * n 
    #2 Have an input vector of the demands at each point (A, B, C, D, ..., DC) 1D
    #3 Tweak the constraint for pickups
    
    randomDemands = []
    numberOfStations = 81
    for i in range(numberOfStations):
        randomDemands.append(random.randint(3, 10))

    # Hardcode the vehicle capacity for the moment.
    vehicleCapacity = 35
    # Find the total demand that will have to be distributed.
    totalDemand = sum(listOfDemands) # sum(randomDemands)
    # Create the vehicle capacities array...
        # But first, excuse the funky way of doing ceiling divisions in Python.
    numberOfVehicles = ((totalDemand - 1) // vehicleCapacity) + 1
    vehicleCapacityList = [vehicleCapacity] * (numberOfVehicles + 1)

    # The distance_matrix is a list of lists.
    data['distance_matrix'] = distanceList #cleanData
    data['demands'] = listOfDemands #randomDemands
    data['vehicle_capacities'] = vehicleCapacityList # vehicleCapacityList * 2
    data['num_vehicles'] = numberOfVehicles + 1 # numberOfVehicles * 2 
    data['depot'] = 0
    # print(randomDemands)
    return data

def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    print('made it')
    stationNames = pickle.load(open("station-node-mapping.p", "rb"))
    total_distance = 0
    total_load = 0
    all_nodes_visited = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            all_nodes_visited.append(stationNames[node_index])
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(stationNames[node_index], route_load)
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(
            manager.IndexToNode(index), route_load)
        all_nodes_visited.append(stationNames[0])
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    pickle.dump(all_nodes_visited, open("data/all-stations-visited-inorder.p", "wb"))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
    # TODO This mf is the one blocking to tweak for pickup routing
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)

if __name__ == '__main__':
    main()