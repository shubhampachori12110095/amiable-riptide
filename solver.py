from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pandas as pd
import random

def create_model():

    # Import all data needed. (TODO)
    # distances = pd.read_pickle('data/distances.pkl').astype(int)
    # averageDelta = pd.read_pickle('data/averageDelta.pkl')
    # distanceList = distances.values.tolist()
    # print(distances.shape)
    # print(distanceList)
    # print(averageDelta)
    
    data = {}
    # Grab the distance and demand data
    importData = pd.read_csv('station-distances.csv', index_col=None)
    importData = importData.astype(int)
    print(importData)
    importDataAux = importData.drop(importData.columns[0], axis=1)
    cleanData = importDataAux.values.tolist()

    # TODO
    #1 Import distance matrix and make it in list of lists (A, B, C, D, ..., DC) 2D m * n 
    #2 Have an input vector of the demands at each point (A, B, C, D, ..., DC) 1D
    #3 Tweak the constraint for pickups
    
    randomDemands = []
    numberOfStations = 81
    for i in range(numberOfStations):
        randomDemands.append(random.randint(3, 10))

    # Hardcode the vehicle capacity for the moment.
    vehicleCapacity = 25
    # Find the total demand that will have to be distributed.
    totalDemand = sum(randomDemands)
    # Create the vehicle capacities array...
        # But first, excuse the funky way of doing ceiling divisions in Python.
    numberOfVehicles = ((totalDemand - 1) // vehicleCapacity) + 1
    vehicleCapacityList = [vehicleCapacity] * numberOfVehicles

    # The distance_matrix is a list of lists.
    data['distance_matrix'] = cleanData
    data['demands'] = randomDemands
    # print(cleanData)
    # print(len(cleanData))
    # print(len(randomDemands))
    # print(vehicleCapacity)
    # print(len(vehicleCapacityList))
    data['vehicle_capacities'] = vehicleCapacityList * 2
    data['num_vehicles'] = numberOfVehicles * 2 
    data['depot'] = 0
    print(randomDemands)
    return data

def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    print('made it')
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(
            manager.IndexToNode(index), route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    print('#1 ****')

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

    print('#2 ****')
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)

if __name__ == '__main__':
    main()