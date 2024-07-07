"""
@file    simulation.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a road with a semaphore and a bifurcation, going back to the original road.
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Bifurcation, NFurcation, Merge
from data import RoadHistory
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
    sectorsPerRoad = 10
    roadLength = 500 #meters
    simulationCycles = 250
    greenLight = 60 #seconds
    redLight = 30 #seconds
    semaphorePosition = roadLength/2
    spawningRate = 60
    semaphore = Semaphore(greenLight, redLight, semaphorePosition, 0, 0)
    road1 = Road(0, roadLength, 1, 50/3.6,) #id, length, vehicleDistance, speedLimit
    road2 = Road(1, roadLength, 1, 50/3.6)
    road3 = Road(2, roadLength, 1, 50/3.6)
    road1History = RoadHistory(road1, roadLength / sectorsPerRoad) #road, sectorLength
    road2History = RoadHistory(road2, roadLength / sectorsPerRoad)
    road3History = RoadHistory(road3, roadLength / sectorsPerRoad)
    bifurcation1 = NFurcation(0,road1)#= Bifurcation(0,road1,road2,road3,0.2)
    #road 1 goes into 2 and 3 with 20% and 80% probability
    bifurcation1.addOutgoingRoad(road2, 0.2)
    bifurcation1.addOutgoingRoad(road3, 0.8)
    #road1.addEndJunction(bifurcation1)
    #road 2 and 3 merge into 1 (loop)
    merge = Merge(1, road2, road3, road1)
    cars = []
    road1.addSemaphore(semaphore)
    f = open("output.txt", "w")
    #road.add_vehicle(car) #TODO: adapt all to new code, implement separate classes to handle world state and sectors, then implement semaphores and junctions
    print("Road 0 goes to road 1 and 2, road 1 and 2 merge back into road 0", file=f)
    print("Road 0 goes to road 1 and 2, road 1 and 2 merge back into road 0")
    print("Roads are 1000m long, with a speed limit of 50 km/h")
    print("Semaphore at %d meters of Road 0, green light: %ds, red light: %ds" % (semaphorePosition, greenLight, redLight))
    print("Simulation cycles: %d, time step: %ds" % (simulationCycles, timeStep))
    print("Injecting vehicles in road 0 with random speed between 40 km/h and 80 km/h each %d cycles" % spawningRate)
    print("Simulation started", file=f)
    for i in range(simulationCycles):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        if i % spawningRate == 0:
            cars.append(Vehicle(i//spawningRate, carLength, startingPosition, speed, 0, topSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            road1.addVehicle(cars[i//spawningRate], time)
        road1.moveVehicles(time,timeStep)
        road2.moveVehicles(time,timeStep)
        road3.moveVehicles(time,timeStep)
        road1History.saveState(road1, time)
        road2History.saveState(road2, time)
        road3History.saveState(road3, time)
        print("Time: %ds" % time, file=f)
        print("Time: %ds" % time)
        road = road1 if road1.hasVehicle(cars[0]) else road2 if road2.hasVehicle(cars[0]) else road3 if road3.hasVehicle(cars[0]) else None
        print("Vehicle 0: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in road %d" % (cars[0].position, cars[0].speed, cars[0].acceleration, road.id), file=f)
        for car in cars:
            road = road1 if road1.hasVehicle(car) else road2 if road2.hasVehicle(car) else road3 if road3.hasVehicle(car) else None
            print("Vehicle %d: position: %fm, speed: %fm/s, acceleration: %fm/s^2, in road %d" % (car.id, car.position, car.speed, car.acceleration, road.id))
        #in this example car 0 only goes to road 2
        #for c in cars:
            #if c.position < 0:
                #print("Car %d: position: %fm, speed: %fm/s" % (c.id, c.position, c.speed))

    #roadHistory.printHistory()
    road1History.saveHistory("road1.json")
    road2History.saveHistory("road2.json")
    road3History.saveHistory("road3.json")

if __name__ == "__main__":
    simulate()