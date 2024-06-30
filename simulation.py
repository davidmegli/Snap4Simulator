"""
@file    simulation.py
@author  David Megli
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Bifurcation
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
    semaphore = Semaphore(8, 2, roadLength/2, 0, 0)
    road1 = Road(0, roadLength, 1, 50/3.6,) #id, length, vehicleDistance, speedLimit
    road2 = Road(1, roadLength, 1, 50/3.6)
    road3 = Road(2, roadLength, 1, 50/3.6)
    road1History = RoadHistory(road1, roadLength / sectorsPerRoad) #road, sectorLength
    road2History = RoadHistory(road2, roadLength / sectorsPerRoad)
    road3History = RoadHistory(road3, roadLength / sectorsPerRoad)
    bifurcation1 = Bifurcation(0,road1,road2,road3,0.2)
    road1.addEndJunction(bifurcation1)
    cars = []
    road1.addSemaphore(semaphore)
    #road.add_vehicle(car) #TODO: adapt all to new code, implement separate classes to handle world state and sectors, then implement semaphores and junctions
    for i in range(60):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        cars.append(Vehicle(i, carLength, startingPosition, speed, 0, topSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
        road1.addVehicle(cars[i], time)
        road1.moveVehicles(time,timeStep)
        road2.moveVehicles(time,timeStep)
        road3.moveVehicles(time,timeStep)
        road1History.saveState(road1, time)
        road2History.saveState(road2, time)
        road3History.saveState(road3, time)
        print("Time: %d" % i)
        for c in cars:
            print("Car %d: position: %fm, speed: %fm/s" % (c.id, c.position, c.speed))

    #roadHistory.printHistory()
    road1History.saveHistory("road1.json")
    road2History.saveHistory("road2.json")
    road3History.saveHistory("road3.json")

if __name__ == "__main__":
    simulate()