"""
@file    merge.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a street merge (2 Lanes into 1 lane)
"""
from vehicle import Vehicle
from map import Lane, Semaphore, Junction, Bifurcation, NFurcation, Merge
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
    timeStep = 2 #cycle steps in seconds
    sectorsPerLane = 10 #number of sectors in the lane
    laneLength = 500 #meters
    outgoingLaneLength = 1000 #meters
    simulationCycles = 250
    spawningRate = 10 #instantiate one vehicle every x cycles
    numberOfLanes = 3
    outputFile = "merge_simulation_output.txt"
    lanes = []
    laneHistories = []
    for i in range(numberOfLanes):
        lanes.append(Lane(i, laneLength, 1, 50/3.6,)) #id, length, vehicleDistance, speedLimit
        laneHistories.append(LaneHistory(lanes[i], laneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    merge = Merge(0, lanes[0], lanes[1], lanes[2]) #id, incomingLane1, incomingLane2, outgoingLane
    f = open(outputFile, "w")
    print("Lanes are 1000m long, with a speed limit of 50 km/h", file=f)
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in lane 0 with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate, file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            lanes[0].addVehicle(cars[i//spawningRate], time)
        for lane in lanes:
            lane.moveVehicles(time,timeStep)
            laneHistories[lanes.index(lane)].saveState(lane, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            for lane in lanes:
                if lane.hasVehicle(car):
                    print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in lane %d" % (car.id, car.position, car.speed, car.acceleration, lane.id), file=f)
    #laneHistory.printHistory()
    #lane1History.saveHistory("single_lane_lane1.json")

if __name__ == "__main__":
    simulate()