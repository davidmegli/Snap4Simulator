"""
@file    single_lane_simulation.py
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
    minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
    maxVehicleSpeed = 7#40/3.6 #80 km/h in m/s
    topVehicleSpeed = 150/3.6 #150 km/h in m/s
    speedLimit = 100/3.6 #100 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    vehicleLength = 5 #5m
    startingPosition = 0
    vehicleCount = 100
    timeStep = 1 #cycle steps in seconds
    spawningRate = 1 #instantiate one vehicle every x cycles
    sectorsPerLane = 10 #number of sectors in the lane
    laneLength = 500 #meters
    simulationCycles = 3600
    greenLight = 60 #seconds
    redLight = 30 #seconds
    semaphore = Semaphore(greenLight, redLight, 0, 0, -60)
    lane1 = Lane(0, laneLength, 1, speedLimit) #id, length, vehicleDistance, speedLimit
    #lane1.addSemaphore(semaphore)
    lane1History = LaneHistory(lane1, laneLength / sectorsPerLane) #lane, sectorLength
    outputFile = "single_lane_simulation_output.txt"
    cars = []
    f = open(outputFile, "w")
    print("Lane is %dm long, with a speed limit of %d" % (laneLength,speedLimit), file=f)
    print("Simulation cycles: %d, time step: %ds, total duration: %ds" % (simulationCycles, timeStep, simulationCycles * timeStep), file=f)
    print("Speed limit: %dm/s (%dkm/h), safety distance: %dm, vehicle length: %dm" % (speedLimit, speedLimit*3.6, 1, vehicleLength), file=f)
    print("Injecting vehicles in lane 0 with increasing speed from %dm/s (%dkm/h) each %d cycles" % (minVehicleSpeed, minVehicleSpeed*3.6,spawningRate), file=f)
    print("Adding semaphore at %d meters of Lane 0, green light: %ds, red light: %ds" % (laneLength/2, greenLight, redLight), file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        print("Time: %ds" % time, file=f)
        speed = random.uniform(minVehicleSpeed, maxVehicleSpeed)
        if i % spawningRate == 0 and i//spawningRate < vehicleCount:
            cars.append(Vehicle(i//spawningRate, vehicleLength, startingPosition, min(speed,speedLimit), 0, topVehicleSpeed, maxAcceleration, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            lane1.addVehicle(cars[i//spawningRate], time)
            print("Vehicle %d added to lane 0 at time %ds" % (cars[i//spawningRate].id, time), file=f)
        lane1.moveVehicles(time,timeStep)
        print("Moved vehicles in lane 0 at time %ds" % time, file=f)
        lane1History.saveState(lane1, time)
        for car in cars:
            if lane1.hasVehicle(car):
                print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in lane %d" % (car.id, car.position,laneLength, car.speed, car.speed*3.6, car.acceleration, lane1.id), file=f)
            elif car.position > laneLength:
                print("Vehicle %d: pos: %d/%dm, out of lane %d" % (car.id, car.position, laneLength, lane1.id), file=f)

    print("VEHICLES METRICS:", file=f)
    for car in cars:
        #if car.isArrived():
        print("Vehicle %d: " % car.id, end="", file=f)
        print(car.getMetricsAsString(), file=f)
    print()
    print(Vehicle.getVehiclesMetricsAsString(cars), file=f)
    #laneHistory.printHistory()
    lane1History.saveHistory("single_lane_lane1.json")

if __name__ == "__main__":
    simulate()