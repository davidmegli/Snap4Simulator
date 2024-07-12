"""
@file    bifurcation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a bifurcation (1 road into 2 roads)
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Intersection
from data import RoadHistory
import random
import time as t

def simulate():
    minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 7#40/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    speedLimit = 100/3.6 #100 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    vehicleCount = 1000000
    timeStep = 1 #cycle steps in seconds
    spawningRate = 1 #instantiate one vehicle every x cycles
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 1000 #meters
    simulationCycles = 600
    greenLight = 40 #seconds
    redLight = 20 #seconds
    semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road1 = Road(0, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road2 = Road(1, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road3 = Road(2, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    bifurcation = Intersection(0, [road1],[road2,road3],[0.8,0.2]) #id, incomingRoads, outgoingRoads, probabilities
    #road1.addSemaphore(semaphore)
    road1History = RoadHistory(road1, roadLength / sectorsPerRoad) #road, sectorLength
    outputFile = "../output/bifurcation_simulation_output.txt"
    cars = []
    f = open(outputFile, "w")
    print("Roads are %dm long, with a speed limit of %d" % (roadLength,speedLimit), file=f)
    print("Road 0 has a bifurcation with roads 1 and 2, with probabilities 0.8 and 0.2", file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in road 0 with increasing speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    #print("Adding semaphore at %d meters of Road 0, green light: %ds, red light: %ds" % (roadLength/2, greenLight, redLight), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        print("Time: %ds" % time, file=f)
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0 and i//spawningRate < vehicleCount:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, min(speed,speedLimit), 0, topVehicleSpeed, maxAcceleration, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            road1.addVehicle(cars[i//spawningRate], time)
        for road in [road1,road2,road3]:
            road.moveVehicles(time,timeStep)
        road1History.saveState(road1, time)
        for car in cars:
            for road in [road1,road2,road3]:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,roadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
        print("Cycle %d/%d" % (i,simulationCycles), end="\r")

    print("VEHICLES METRICS:", file=f)
    for car in cars:
        if car.isArrived():
            print("Vehicle %d: " % car.id, end="", file=f)
            print(car.getMetricsAsString(), file=f)
    print()
    print("Simulation duration: %ds" % (simulationCycles * timeStep), file=f)
    print(Vehicle.getVehiclesMetricsAsString(cars), file=f)
    #roadHistory.printHistory()
    road1History.saveHistory("../output/single_road_road1.json")

if __name__ == "__main__":
    simulate()