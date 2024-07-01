"""
@file    bifurcation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a bifurcation (1 lane into 2 lanes)
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
    simulationCycles = 250
    spawningRate = 10 #instantiate one vehicle every x cycles
    numberOfLanes = 3
    outputFile = "bifurcation_simulation_output.txt"
    lanes = []
    laneHistories = []
    for i in range(numberOfLanes):
        lanes.append(Lane(i, laneLength, 1, 50/3.6,)) #id, length, vehicleDistance, speedLimit
        laneHistories.append(LaneHistory(lanes[i], laneLength / sectorsPerLane)) #lane, sectorLength
    cars = []
    bifurcation = Bifurcation(0, lanes[0], lanes[1], lanes[2], 0.2) #id, incomingLane, outgoingLane1, outgoingLane2, flux1 (probability to go to lane 1)
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
    #FIXME: sometimes when giving way to another vehicle at the end of a lane in a merge, the vehicle remains stopped for some (2?) cycles, then moves again
if __name__ == "__main__":
    simulate()