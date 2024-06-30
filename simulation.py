"""
@file    simulation.py
@author  David Megli
"""
from vehicle import Vehicle
from map import Road, Semaphore
from data import RoadHistory
import random

def simulate():
    minSpeed = 40/3.6 #40 km/h in m/s
    maxSpeed = 80/3.6 #80 km/h in m/s
    topSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    carLength = 5 #5m
    startingPosition = 0
    timeStep = 2 #seconds
    sectorsPerRoad = 10
    roadLength = 1000 #meters
    road = Road(0, roadLength, 1, 50/3.6) #id, length, vehicleDistance, speedLimit
    roadHistory = RoadHistory(road, roadLength / sectorsPerRoad) #road, sectorLength
    cars = []
    semaphore = Semaphore(8, 2, roadLength/2, 0, 0)
    road.addSemaphore(semaphore)
    #road.add_vehicle(car) #TODO: adapt all to new code, implement separate classes to handle world state and sectors, then implement semaphores and junctions
    for i in range(60):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        cars.append(Vehicle(i, carLength, startingPosition, speed, 0, topSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
        road.addVehicle(cars[i], time)
        road.moveVehicles(time,timeStep)
        roadHistory.saveState(road, time)
        print("Time: %d" % i)
        for c in cars:
            print("Car %d: position: %fm, speed: %fm/s" % (c.id, c.position, c.speed))

    #roadHistory.printHistory()
    roadHistory.saveHistory("history.json")

if __name__ == "__main__":
    simulate()