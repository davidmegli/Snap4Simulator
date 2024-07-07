"""
@file    bifurcation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a bifurcation (1 road into 2 roads)
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
    timeStep = 2 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 500 #meters
    speedLimit = 100/3.6 #100 km/h in m/s
    simulationCycles = 250
    spawningRate = 10 #instantiate one vehicle every x cycles
    numberOfRoads = 3
    outputFile = "../output/bifurcation_simulation_output.txt"
    roads = []
    roadHistories = []
    for i in range(numberOfRoads):
        roads.append(Road(i, roadLength, 1, speedLimit,)) #id, length, vehicleDistance, speedLimit
        roadHistories.append(RoadHistory(roads[i], roadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    bifurcation = Bifurcation(0, roads[0], roads[1], roads[2], 0.2) #id, incomingRoad, outgoingRoad1, outgoingRoad2, flux1 (probability to go to road 1)
    f = open(outputFile, "w")
    print("Roads are %dm long, with a speed limit of %dm/s (%dkm/h)" % (roadLength,speedLimit,speedLimit*3.6), file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in road 0 with increasing speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            roads[0].addVehicle(cars[i//spawningRate], time)
        for road in roads:
            road.moveVehicles(time,timeStep)
            roadHistories[roads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in roads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,roadLength, car.speed, car.speed*3.6, car.acceleration, road1.id), file=f)
    #roadHistory.printHistory()
    #road1History.saveHistory("single_road_road1.json")
    #FIXME: sometimes when giving way to another vehicle at the end of a road in a merge, the vehicle remains stopped for some (2?) cycles, then moves again
if __name__ == "__main__":
    simulate()