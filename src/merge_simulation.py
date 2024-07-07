"""
@file    merge_simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a street merge (2 Roads into 1 road)
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Bifurcation, NFurcation, Merge
from data import RoadHistory
import random
import time as t

def simulate():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 500 #meters
    outgoingRoadLength = 1000 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfRoads = 3
    outputFile = "../output/merge_simulation_output.txt"
    roads = []
    roadHistories = []
    for i in range(numberOfRoads):
        roads.append(Road(i, roadLength, 1, 50/3.6,None,None,None,numberOfRoads-i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(roads[i], roadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    merge = Merge(0, roads[0], roads[1], roads[2]) #id, incomingRoad1, incomingRoad2, outgoingRoad
    f = open(outputFile, "w")
    print("Roads are 1000m long, with a speed limit of 50 km/h", file=f)
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in a random road between 0 and 1 with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate, file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            roads[random.randint(0,1)].addVehicle(cars[i//spawningRate], time)
        for road in roads:
            road.moveVehicles(time,timeStep)
            roadHistories[roads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in roads:
                if road.hasVehicle(car):
                    print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in road %d" % (car.id, car.position, car.speed, car.acceleration, road.id), file=f)
    #roadHistory.printHistory()
    #road1History.saveHistory("single_road_road1.json")

if __name__ == "__main__":
    simulate()