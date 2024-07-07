"""
@file    intersection_simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a street intersection
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Bifurcation, NFurcation, Merge, Intersection
from data import RoadHistory
import random
import time as t

def simulate():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    incomingRoadLength = 500 #meters
    outgoingRoadLength = 1000 #meters
    roadLength = 500 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfIncomingRoads = 3
    numberOfOutgoingRoads = 3
    outputFile = "../output/intersection_simulation_output.txt"
    incomingRoads = []
    outgoingRoads = []
    outgoingFluxes = []
    roadHistories = []
    for i in range(numberOfIncomingRoads):
        incomingRoads.append(Road(i, incomingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(incomingRoads[i], incomingRoadLength / sectorsPerRoad)) #road, sectorLength
    for i in range(numberOfOutgoingRoads):
        outgoingRoads.append(Road(i, outgoingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        outgoingFluxes.append(1/numberOfOutgoingRoads) #equal probability of going to any road
        roadHistories.append(RoadHistory(outgoingRoads[i], outgoingRoadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    intersection = Intersection(0, incomingRoads, outgoingRoads,outgoingFluxes) #id, incomingRoads, outgoingRoads
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in incoming roads chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingRoads[random.randint(0,numberOfIncomingRoads)].addVehicle(cars[i//spawningRate], time)
        for road in incomingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[incomingRoads.index(road)].saveState(road, time)
        for road in outgoingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[outgoingRoads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in incomingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,roadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
    #roadHistory.printHistory()
    #road1History.saveHistory("single_road_road1.json")

def simulate_bifurcation():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    incomingRoadLength = 100 #meters
    outgoingRoadLength = 300 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingRoads = 1
    numberOfOutgoingRoads = 2
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingRoads = []
    outgoingRoads = []
    outgoingFluxes = []
    roadHistories = []
    for i in range(numberOfIncomingRoads):
        incomingRoads.append(Road(i, incomingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(incomingRoads[i], incomingRoadLength / sectorsPerRoad)) #road, sectorLength
    for i in range(numberOfOutgoingRoads):
        outgoingRoads.append(Road(numberOfIncomingRoads + i, outgoingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        outgoingFluxes.append(1/numberOfOutgoingRoads) #equal probability of going to any road
        roadHistories.append(RoadHistory(outgoingRoads[i], outgoingRoadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    intersection = Intersection(0, incomingRoads, outgoingRoads, outgoingFluxes) #id, incomingRoads, outgoingRoads
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming roads, %d outgoing roads" % (numberOfIncomingRoads, numberOfOutgoingRoads), file=f)
    print("Incoming roads are %dm long, outgoing roads are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingRoadLength, outgoingRoadLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming roads chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingRoads[random.randint(0,numberOfIncomingRoads-1)].addVehicle(cars[i//spawningRate], time)
        for road in incomingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[incomingRoads.index(road)].saveState(road, time)
        for road in outgoingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[outgoingRoads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in incomingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,incomingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
            for road in outgoingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,outgoingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
    #roadHistory.printHistory()
    #road1History.saveHistory("single_road_road1.json")

def simulate_bifurcation_different_probabilities():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    incomingRoadLength = 100 #meters
    outgoingRoadLength = 300 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingRoads = 1
    numberOfOutgoingRoads = 2
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingRoads = []
    outgoingRoads = []
    outgoingFluxes = []
    roadHistories = []
    for i in range(numberOfIncomingRoads):
        incomingRoads.append(Road(i, incomingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(incomingRoads[i], incomingRoadLength / sectorsPerRoad)) #road, sectorLength
    for i in range(numberOfOutgoingRoads):
        outgoingRoads.append(Road(numberOfIncomingRoads + i, outgoingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(outgoingRoads[i], outgoingRoadLength / sectorsPerRoad)) #road, sectorLength
    outgoingFluxes.append(0.8) #equal probability of going to any road
    outgoingFluxes.append(0.2) #equal probability of going to any road
    cars = []
    intersection = Intersection(0, incomingRoads, outgoingRoads, outgoingFluxes) #id, incomingRoads, outgoingRoads
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming roads, %d outgoing roads" % (numberOfIncomingRoads, numberOfOutgoingRoads), file=f)
    print("Incoming roads are %dm long, outgoing roads are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingRoadLength, outgoingRoadLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming roads chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingRoads[random.randint(0,numberOfIncomingRoads-1)].addVehicle(cars[i//spawningRate], time)
        for road in incomingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[incomingRoads.index(road)].saveState(road, time)
        for road in outgoingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[outgoingRoads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in incomingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,incomingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
            for road in outgoingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,outgoingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
    
def simulate_bifurcation_4_out():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    incomingRoadLength = 50 #meters
    outgoingRoadLength = 150 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingRoads = 1
    numberOfOutgoingRoads = 4
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingRoads = []
    outgoingRoads = []
    outgoingFluxes = []
    roadHistories = []
    for i in range(numberOfIncomingRoads):
        incomingRoads.append(Road(i, incomingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(incomingRoads[i], incomingRoadLength / sectorsPerRoad)) #road, sectorLength
    for i in range(numberOfOutgoingRoads):
        outgoingRoads.append(Road(numberOfIncomingRoads + i, outgoingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        outgoingFluxes.append(1/numberOfOutgoingRoads) #equal probability of going to any road
        roadHistories.append(RoadHistory(outgoingRoads[i], outgoingRoadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    intersection = Intersection(0, incomingRoads, outgoingRoads, outgoingFluxes) #id, incomingRoads, outgoingRoads
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming roads, %d outgoing roads" % (numberOfIncomingRoads, numberOfOutgoingRoads), file=f)
    print("Incoming roads are %dm long, outgoing roads are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingRoadLength, outgoingRoadLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming roads chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingRoads[random.randint(0,numberOfIncomingRoads-1)].addVehicle(cars[i//spawningRate], time)
        for road in incomingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[incomingRoads.index(road)].saveState(road, time)
        for road in outgoingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[outgoingRoads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in incomingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,incomingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
            for road in outgoingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,outgoingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)

def simulate_merge():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerRoad = 10 #number of sectors in the road
    incomingRoadLength = 100 #meters
    outgoingRoadLength = 150 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfIncomingRoads = 2
    numberOfOutgoingRoads = 1
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingRoads = []
    outgoingRoads = []
    outgoingFluxes = []
    roadHistories = []
    for i in range(numberOfIncomingRoads):
        incomingRoads.append(Road(i, incomingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        roadHistories.append(RoadHistory(incomingRoads[i], incomingRoadLength / sectorsPerRoad)) #road, sectorLength
    for i in range(numberOfOutgoingRoads):
        outgoingRoads.append(Road(numberOfIncomingRoads + i, outgoingRoadLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, road priority
        outgoingFluxes.append(1/numberOfOutgoingRoads) #equal probability of going to any road
        roadHistories.append(RoadHistory(outgoingRoads[i], outgoingRoadLength / sectorsPerRoad)) #road, sectorLength
    cars = []
    intersection = Intersection(0, incomingRoads, outgoingRoads, outgoingFluxes) #id, incomingRoads, outgoingRoads
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming roads, %d outgoing roads" % (numberOfIncomingRoads, numberOfOutgoingRoads), file=f)
    print("Incoming roads are %dm long, outgoing roads are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingRoadLength, outgoingRoadLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming roads chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingRoads[random.randint(0,numberOfIncomingRoads-1)].addVehicle(cars[i//spawningRate], time)
            #FIXME: roads must be updated in descending order! otherwise vehicles going to new roads can be blocked by vehicles in that road not yet moved
            #Order: outgoing roads first, then incoming roads. Higher priority roads first for outgoing Roads.
        orderedOutgoingRoads = intersection.outgoingRoadsOrderedByPriority()
        for road in orderedOutgoingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[outgoingRoads.index(road)].saveState(road, time)
        for road in incomingRoads:
            road.moveVehicles(time,timeStep)
            roadHistories[incomingRoads.index(road)].saveState(road, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for road in incomingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,incomingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)
            for road in outgoingRoads:
                if road.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d" % (car.id, car.position,outgoingRoadLength, car.speed, car.speed*3.6, car.acceleration, road.id), file=f)

if __name__ == "__main__":
    simulate_merge()