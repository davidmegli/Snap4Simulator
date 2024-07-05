"""
@file    simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a lane with a semaphore and a bifurcation, going back to the original lane.
"""
from vehicle import Vehicle
from map import Lane, Semaphore, Junction, Bifurcation, NFurcation, Merge
from data import LaneHistory
import random
import time as t

def simulate():
    minSpeed = 40/3.6 #40 km/h in m/s
    maxSpeed = 80/3.6 #80 km/h in m/s
    topSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    carLength = 5 #5m
    startingPosition = 0
    timeStep = 2 #seconds
    sectorsPerLane = 10
    laneLength = 500 #meters
    simulationCycles = 250
    greenLight = 60 #seconds
    redLight = 30 #seconds
    semaphorePosition = laneLength/2
    spawningRate = 60
    semaphore = Semaphore(greenLight, redLight, semaphorePosition, 0, 0)
    lane1 = Lane(0, laneLength, 1, 50/3.6,) #id, length, vehicleDistance, speedLimit
    lane2 = Lane(1, laneLength, 1, 50/3.6)
    lane3 = Lane(2, laneLength, 1, 50/3.6)
    lane1History = LaneHistory(lane1, laneLength / sectorsPerLane) #lane, sectorLength
    lane2History = LaneHistory(lane2, laneLength / sectorsPerLane)
    lane3History = LaneHistory(lane3, laneLength / sectorsPerLane)
    bifurcation1 = NFurcation(0,lane1)#= Bifurcation(0,lane1,lane2,lane3,0.2)
    #lane 1 goes into 2 and 3 with 20% and 80% probability
    bifurcation1.addOutgoingLane(lane2, 0.2)
    bifurcation1.addOutgoingLane(lane3, 0.8)
    #lane1.addEndJunction(bifurcation1)
    #lane 2 and 3 merge into 1 (loop)
    merge = Merge(1, lane2, lane3, lane1)
    cars = []
    lane1.addSemaphore(semaphore)
    f = open("output.txt", "w")
    #lane.add_vehicle(car) #TODO: adapt all to new code, implement separate classes to handle world state and sectors, then implement semaphores and junctions
    print("Lane 0 goes to lane 1 and 2, lane 1 and 2 merge back into lane 0", file=f)
    print("Lane 0 goes to lane 1 and 2, lane 1 and 2 merge back into lane 0")
    print("Lanes are 1000m long, with a speed limit of 50 km/h")
    print("Semaphore at %d meters of Lane 0, green light: %ds, red light: %ds" % (semaphorePosition, greenLight, redLight))
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep))
    print("Injecting vehicles in lane 0 with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate)
    print("Simulation started", file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, carLength, startingPosition, speed, 0, topSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            lane1.addVehicle(cars[i//spawningRate], time)
        lane1.moveVehicles(time,timeStep)
        lane2.moveVehicles(time,timeStep)
        lane3.moveVehicles(time,timeStep)
        lane1History.saveState(lane1, time)
        lane2History.saveState(lane2, time)
        lane3History.saveState(lane3, time)
        print("Time: %ds" % time, file=f)
        print("Time: %ds" % time)
        lane = lane1 if lane1.hasVehicle(cars[0]) else lane2 if lane2.hasVehicle(cars[0]) else lane3 if lane3.hasVehicle(cars[0]) else None
        print("Vehicle 0: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in lane %d" % (cars[0].position, cars[0].speed, cars[0].acceleration, lane.id), file=f)
        for car in cars:
            lane = lane1 if lane1.hasVehicle(car) else lane2 if lane2.hasVehicle(car) else lane3 if lane3.hasVehicle(car) else None
            print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in lane %d" % (car.id, car.position, car.speed, car.acceleration, lane.id))
        #in this example car 0 only goes to lane 2
        #for c in cars:
            #if c.position < 0:
                #print("Car %d: position: %fm, speed: %fm/s" % (c.id, c.position, c.speed))

    #laneHistory.printHistory()
    lane1History.saveHistory("lane1.json")
    lane2History.saveHistory("lane2.json")
    lane3History.saveHistory("lane3.json")

if __name__ == "__main__":
    simulate()