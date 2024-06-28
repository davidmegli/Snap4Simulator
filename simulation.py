"""
@file    simulation.py
@author  David Megli
"""
from vehicle import Vehicle
from map import Road
import random
    
def simulate():
    minSpeed = 40/3.6 #40 km/h in m/s
    maxSpeed = 80/3.6 #80 km/h in m/s
    topSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    carLength = 5 #5m
    startingPosition = 0
    timeStep = 2 #seconds
    sectorsPerRoad = 6
    roadLength = 100 #meters
    road = Road(0, sectorsPerRoad, roadLength, 100/3) #id, numSectors, length, capacity, each sector is 100m long and can hold 50 vehicles (5m lenght + 1 ms gap between vehicles)
    cars = []
    #road.add_vehicle(car)
    for i in range(12):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        cars.append(Vehicle(i, carLength, speed, startingPosition, topSpeed, maxAcceleration)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
        road.add_vehicle(cars[i], time)
        road.move_vehicles(timeStep)
        road.update_sector_densities(time)
        # print for each time i the position and speed of the cars
        print("Time: %d" % i)
        for veh in cars:
            print("Car %d: position: %fm, speed: %fm/s, at time %ds" % (veh.id, veh.states[-1].position, veh.states[-1].speed, veh.states[-1].time))
        for sector in road.sectors: #print the number of vehicles in each sector at current time
            print("Sector %d: %d vehicles/length" % (sector.id, sector.get_density(time)))

if __name__ == "__main__":
    simulate()