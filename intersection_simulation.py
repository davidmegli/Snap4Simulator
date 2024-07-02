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
    vehicleLength = 5 #5m
    startingPosition = 0
    timeStep = 1 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    incomingLaneLength = 500 #meters
    outgoingLaneLength = 1000 #meters
    simulationCycles = 250
    spawningRate = 1 #instantiate one vehicle every x cycles
    numberOfIncomingLanes = 3
    numberOfOutgoingLanes = 3
    outputFile = "intersection_simulation_output.txt"
    incomingLanes = []
    outgoingLanes = []
    outgoingFluxes = []
    laneHistories = []
    for i in range(numberOfIncomingLanes):
        incomingLanes.append(Lane(i, incomingLaneLength, 1, 50/3.6,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        laneHistories.append(LaneHistory(incomingLanes[i], incomingLaneLength / sectorsPerLane)) #lane, sectorLength
    for i in range(numberOfOutgoingLanes):
        outgoingLanes.append(Lane(i, outgoingLaneLength, 1, 50/3.6,None,None,None,i)) #id, length, vehicleDistance, speedLimit, semaphore, endJunction, startJunction, lane priority
        outgoingFluxes.append(1/numberOfOutgoingLanes) #equal probability of going to any lane
        laneHistories.append(LaneHistory(outgoingLanes[i], outgoingLaneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    intersection = Intersection(0, incomingLanes, outgoingLanes,outgoingFluxes) #id, incomingLanes, outgoingLanes
    f = open(outputFile, "w")
    #print("Lanes are 1000m long, with a speed limit of 50 km/h", file=f)
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in incomin lanes chosen with random probability, with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate, file=f)
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
                    print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in lane %d" % (car.id, car.position, car.speed, car.acceleration, lane.id), file=f)
    #laneHistory.printHistory()
    #lane1History.saveHistory("single_lane_lane1.json")

if __name__ == "__main__":
    simulate()