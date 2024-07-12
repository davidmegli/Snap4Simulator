"""
@file    single_road_simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a road
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Intersection
from data import RoadHistory, MapHistory
import random
import time as t

def single_road_semaphore():
    minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 7#40/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    topAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    vehicleCount = 1000000
    timeStep = 1 #cycle steps in seconds
    spawningRate = 1 #instantiate one vehicle every x cycles
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 1000 #meters
    simulationCycles = 3600
    greenLight = 40 #seconds
    redLight = 20 #seconds
    semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road1 = Road(0, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    #road1.addSemaphore(semaphore)
    history = MapHistory([road1], roadLength / sectorsPerRoad) #road, sectorLength
    outputFile = "../output/single_road_simulation_output.txt"
    cars = []
    f = open(outputFile, "w")
    print("Road is %dm long, with a speed limit of %d" % (roadLength,speedLimit), file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in road 0 with increasing speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    print("Adding semaphore at %d meters of Road 0, green light: %ds, red light: %ds" % (roadLength/2, greenLight, redLight), file=f)
    log = True
    for i in range(simulationCycles):
        time = i * timeStep
        if log:
            print("Time: %ds" % time, file=f)
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0 and i//spawningRate < vehicleCount:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, min(speed,speedLimit), topAcceleration, topVehicleSpeed, maxAcceleration, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            road1.addVehicle(cars[i//spawningRate], time)
        road1.moveVehicles(time,timeStep)
        history.saveState(time)
        if log:
            for car in cars:
                if road1.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,roadLength, car.speed, car.speed*3.6, car.acceleration, road1.id), file=f)
                elif car.position > roadLength:
                    print("Vehicle %d: pos: %d/%dm, out of road %d" % (car.id, car.position, roadLength, road1.id), file=f)
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
    history.saveHistory("../output/single_road_road1.json")
    history.saveMetrics("../output/single_road_road1_metrics.json")

def bifurcation():
    minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 7#40/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    topAcceleration = 0#.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    vehicleCount = 1000000
    timeStep = 1 #cycle steps in seconds
    spawningRate = 1 #instantiate one vehicle every x cycles
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 500 #meters
    simulationCycles = 3600
    greenLight = 40 #seconds
    redLight = 20 #seconds
    #semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road1 = Road(0, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road2 = Road(1, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road3 = Road(2, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    #road1.addSemaphore(semaphore)
    bifurcation = Intersection(0, [road1],[road2,road3],[0.66,0.33]) #id, incomingRoads, outgoingRoads, probabilities
    history = MapHistory([road1, road2, road3], roadLength / sectorsPerRoad) #road, sectorLength
    outputFile = "../output/bifurcation.txt"
    cars = []
    f = open(outputFile, "w")
    print("Road is %dm long, with a speed limit of %d" % (roadLength,speedLimit), file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in road 0 with increasing speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    #print("Adding semaphore at %d meters of Road 0, green light: %ds, red light: %ds" % (roadLength/2, greenLight, redLight), file=f)
    log = True
    for i in range(simulationCycles):
        time = i * timeStep
        if log:
            print("Time: %ds" % time, file=f)
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0 and i//spawningRate < vehicleCount:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, min(speed,speedLimit), topAcceleration, topVehicleSpeed, maxAcceleration, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            road1.addVehicle(cars[i//spawningRate], time)
        road1.moveVehicles(time,timeStep)
        road2.moveVehicles(time,timeStep)
        road3.moveVehicles(time,timeStep)
        history.saveState(time)
        if log:
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
    #road1History.saveHistory("../output/bifurcation.json")
    history.saveMetrics("../output/bifurcation_road1_metrics.json")

def merge():
    minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 7#40/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    topAcceleration = 0#.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    vehicleCount = 1000000
    timeStep = 1 #cycle steps in seconds
    spawningRate = 1 #instantiate one vehicle every x cycles
    sectorsPerRoad = 10 #number of sectors in the road
    roadLength = 500 #meters
    simulationCycles = 3600
    greenLight = 40 #seconds
    redLight = 20 #seconds
    #semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road1 = Road(0, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road2 = Road(1, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    road3 = Road(2, roadLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    #road1.addSemaphore(semaphore)
    bifurcation = Intersection(0, [road1, road2],[road3],[1]) #id, incomingRoads, outgoingRoads, probabilities
    history = MapHistory([road1, road2, road3], roadLength / sectorsPerRoad) #road, sectorLength
    outputFile = "../output/merge.txt"
    cars = []
    f = open(outputFile, "w")
    print("Road is %dm long, with a speed limit of %d" % (roadLength,speedLimit), file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in road 0 and 1 with speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    #print("Adding semaphore at %d meters of Road 0, green light: %ds, red light: %ds" % (roadLength/2, greenLight, redLight), file=f)
    log = True
    addToRoad0 = True
    for i in range(simulationCycles):
        time = i * timeStep
        if log:
            print("Time: %ds" % time, file=f)
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0 and i//spawningRate < vehicleCount:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, min(speed,speedLimit), topAcceleration, topVehicleSpeed, maxAcceleration, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            if addToRoad0:
                road1.addVehicle(cars[i//spawningRate], time)
                addToRoad0 = False
            else:
                road2.addVehicle(cars[i//spawningRate], time)
                addToRoad0 = True
        road1.moveVehicles(time,timeStep)
        road2.moveVehicles(time,timeStep)
        road3.moveVehicles(time,timeStep)
        history.saveState(time)
        if log:
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
    #road1History.saveHistory("../output/bifurcation.json")
    history.saveMetrics("../output/merge_metrics.json")

if __name__ == "__main__":
    #single_road_semaphore()
    #bifurcation()
    merge()