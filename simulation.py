"""
@file    simulation.py
@author  David Megli
"""
from vehicle import Vehicle
from map import Lane, Semaphore, Junction, Bifurcation, NFurcation, Merge
from data import LaneHistory
import random

def simulate():
    minSpeed = 40/3.6 #40 km/h in m/s
    maxSpeed = 80/3.6 #80 km/h in m/s
    topSpeed = 150/3.6 #150 km/h in m/s
    maxAcceleration = 0.8 #0.8 m/s^2
    carLength = 5 #5m
    startingPosition = 0
    timeStep = 2 #seconds
    sectorsPerLane = 10
    laneLength = 1000 #meters
    semaphore = Semaphore(8, 2, laneLength/2, 0, 0) 
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
    lane1.addEndJunction(bifurcation1)
    #lane 2 and 3 merge into 1 (loop)
    merge = Merge(1, lane2, lane3, lane1)
    lane2.addEndJunction(merge)
    lane3.addEndJunction(merge)
    cars = []
    lane1.addSemaphore(semaphore)
    #lane.add_vehicle(car) #TODO: adapt all to new code, implement separate classes to handle world state and sectors, then implement semaphores and junctions
    for i in range(600):
        time = i * timeStep
        speed = random.uniform(minSpeed, maxSpeed)
        if i < 5:
            cars.append(Vehicle(i, carLength, startingPosition, speed, 0, topSpeed, maxAcceleration, True, time)) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
            lane1.addVehicle(cars[i], time)
        lane1.moveVehicles(time,timeStep)
        lane2.moveVehicles(time,timeStep)
        lane3.moveVehicles(time,timeStep)
        lane1History.saveState(lane1, time)
        lane2History.saveState(lane2, time)
        lane3History.saveState(lane3, time)
        print("Time: %d" % i)
        lane = lane1 if lane1.hasVehicle(i) else lane2 if lane2.hasVehicle(i) else lane3
        print("Car 0: position: %fm, speed: %fm/s, in lane %d" % (cars[0].position, cars[0].speed, lane.id))
        #for c in cars:
            #if c.position < 0:
                #print("Car %d: position: %fm, speed: %fm/s" % (c.id, c.position, c.speed))

    #laneHistory.printHistory()
    lane1History.saveHistory("lane1.json")
    lane2History.saveHistory("lane2.json")
    lane3History.saveHistory("lane3.json")

if __name__ == "__main__":
    simulate()