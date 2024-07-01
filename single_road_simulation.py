"""
@file    single_road_simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a lane
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
    spawningRate = 2 #instantiate one vehicle every x cycles
    sectorsPerLane = 10 #number of sectors in the lane
    laneLength = 1000 #meters
    simulationCycles = 250
    greenLight = 60 #seconds
    redLight = 30 #seconds
    semaphore = Semaphore(greenLight, redLight, laneLength/2, 0, 0)
    lane1 = Lane(0, laneLength, 1, 50/3.6,) #id, length, vehicleDistance, speedLimit
    #lane1.addSemaphore(semaphore)
    lane1History = LaneHistory(lane1, laneLength / sectorsPerLane) #lane, sectorLength
    cars = []
    f = open("single_road_simulation_output.txt", "w")
    print("Lane is 1000m long, with a speed limit of 50 km/h", file=f)
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep), file=f)
    print("Injecting vehicles in lane 0 with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate, file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, speed, 0, topVehicleSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            lane1.addVehicle(cars[i//spawningRate], time)
        lane1.moveVehicles(time,timeStep)
        lane1History.saveState(lane1, time)
        print("Time: %ds" % time, file=f)
        for car in cars:
            print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in lane %d" % (car.id, car.position, car.speed, car.acceleration, lane1.id), file=f)
    #laneHistory.printHistory()
    lane1History.saveHistory("single_road_lane1.json")

if __name__ == "__main__":
    simulate()