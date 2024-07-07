"""
@file    intersection_simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a street intersection
"""
from vehicle import Vehicle
from map import Lane, Semaphore, Junction, Bifurcation, NFurcation, Merge, Intersection
from data import LaneHistory
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
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 500 #meters
    outgoingLaneLength = 1000 #meters
    laneLength = 500 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 3
    numberOfOutgoingLanes = 3
    outputFile = "../output/intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(i, outgoingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        outgoingFluxes.append(1/numberOfOutgoingLanes) #equal probability of going to any lane
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes,outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in incoming lanes chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingLanes[random.randint(0,numberOfIncomingLanes)].addVehicle(cars[i//spawningRate], time)
        for lane in incomingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[incomingLanes.index(lane)].saveState(lane, time)
        for lane in outgoingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[outgoingLanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in incomingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,laneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
    #laneHistory.printHistory()
    #lane1History.saveHistory("single_lane_lane1.json")

def simulate_bifurcation():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 100 #meters
    outgoingLaneLength = 300 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 1
    numberOfOutgoingLanes = 2
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(numberOfIncomingLanes + i, outgoingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        outgoingFluxes.append(1/numberOfOutgoingLanes) #equal probability of going to any lane
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes, outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming lanes, %d outgoing lanes" % (numberOfIncomingLanes, numberOfOutgoingLanes), file=f)
    print("Incoming lanes are %dm long, outgoing lanes are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingLaneLength, outgoingLaneLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming lanes chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingLanes[random.randint(0,numberOfIncomingLanes-1)].addVehicle(cars[i//spawningRate], time)
        for lane in incomingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[incomingLanes.index(lane)].saveState(lane, time)
        for lane in outgoingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[outgoingLanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in incomingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,incomingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
            for lane in outgoingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,outgoingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
    #laneHistory.printHistory()
    #lane1History.saveHistory("single_lane_lane1.json")

def simulate_bifurcation_different_probabilities():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 100 #meters
    outgoingLaneLength = 300 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 1
    numberOfOutgoingLanes = 2
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(numberOfIncomingLanes + i, outgoingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    outgoingFluxes.append(0.8) #equal probability of going to any lane
    outgoingFluxes.append(0.2) #equal probability of going to any lane
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes, outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming lanes, %d outgoing lanes" % (numberOfIncomingLanes, numberOfOutgoingLanes), file=f)
    print("Incoming lanes are %dm long, outgoing lanes are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingLaneLength, outgoingLaneLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming lanes chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingLanes[random.randint(0,numberOfIncomingLanes-1)].addVehicle(cars[i//spawningRate], time)
        for lane in incomingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[incomingLanes.index(lane)].saveState(lane, time)
        for lane in outgoingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[outgoingLanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in incomingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,incomingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
            for lane in outgoingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,outgoingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
    
def simulate_bifurcation_4_out():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 50 #meters
    outgoingLaneLength = 150 #meters
    simulationCycles = 250
    spawningRate = 2 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 1
    numberOfOutgoingLanes = 4
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(numberOfIncomingLanes + i, outgoingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        outgoingFluxes.append(1/numberOfOutgoingLanes) #equal probability of going to any lane
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes, outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming lanes, %d outgoing lanes" % (numberOfIncomingLanes, numberOfOutgoingLanes), file=f)
    print("Incoming lanes are %dm long, outgoing lanes are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingLaneLength, outgoingLaneLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming lanes chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingLanes[random.randint(0,numberOfIncomingLanes-1)].addVehicle(cars[i//spawningRate], time)
        for lane in incomingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[incomingLanes.index(lane)].saveState(lane, time)
        for lane in outgoingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[outgoingLanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in incomingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,incomingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
            for lane in outgoingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,outgoingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)

def simulate_merge():
    minVehicleSpeed = 40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 80/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    speedLimit = 100/3.6 #100 km/h in m/s
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 100 #meters
    outgoingLaneLength = 150 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 2
    numberOfOutgoingLanes = 1
    outputFile = "../output/bifurcation_intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(numberOfIncomingLanes + i, outgoingLaneLength, 1, speedLimit,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        outgoingFluxes.append(1/numberOfOutgoingLanes) #equal probability of going to any lane
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes, outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Intersection: %d incoming lanes, %d outgoing lanes" % (numberOfIncomingLanes, numberOfOutgoingLanes), file=f)
    print("Incoming lanes are %dm long, outgoing lanes are %dm long, with a speed limit of %dm/s (%dkm/h)" % (incomingLaneLength, outgoingLaneLength, speedLimit, speedLimit*3.6), file=f)
    print("Injecting vehicles in incoming lanes chosen with random probability, with random speed between %dm/s (%dkm/h) and %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6, maxVehicleSpeed, maxVehicleSpeed*3.6, spawningRate), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            incomingLanes[random.randint(0,numberOfIncomingLanes-1)].addVehicle(cars[i//spawningRate], time)
            #FIXME: lanes must be updated in descending order! otherwise vehicles going to new lanes can be blocked by vehicles in that lane not yet moved
            #Order: outgoing lanes first, then incoming lanes. Higher priority lanes first for outgoing Lanes.
        orderedOutgoingLanes = intersection.outgoingLanesOrderedByPriority()
        for lane in orderedOutgoingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[outgoingLanes.index(lane)].saveState(lane, time)
        for lane in incomingLanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[incomingLanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in incomingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,incomingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)
            for lane in outgoingLanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,outgoingLaneLength, car.speed, car.speed*3.6, car.acceleration, lane.id), file=f)

if __name__ == "__main__":
    simulate_merge()