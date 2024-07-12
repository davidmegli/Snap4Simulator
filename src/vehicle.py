"""
@file    vehicle.py
@author  David Megli

Desctiption:
This file the classes to handle vehicles in the simulation.
Class Vehicle handles the state of the vehicle (position on the road, speed, acceleration) and its movement.
The class has methods to calculate the position, speed and acceleration of the vehicle in the next time step (default time step is 1 second).
The class has methods to stop the vehicle, move it to a given position, restart it, follow another vehicle at a given distance, stop at a given position,
stop at a semaphore, stop at a vehicle, give way to another vehicle, and restart the vehicle.
I used constants to define the states a vehicle can be in
"""
import random
from statistics import median

class Vehicle:
    STATE_STOPPED = "stopped"
    STATE_MOVING = "moving"
    STATE_WAITING_SEMAPHORE = "semaphore"
    STATE_WAITING_VEHICLE = "vehicle"
    STATE_WAITING_TO_ENTER = "entering"
    STATE_FOLLOWING_VEHICLE = "following"
    STATE_GIVING_WAY = "giving_way" #"precedenza"
    STATE_CREATED = "created"
    def __init__(self, id, length, initialPosition, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime = 0, sigma = 0.0, reactionTime = 1):
        self.id = id
        self.length = length #meters
        self.initialPosition = initialPosition
        self.initialSpeed = initialSpeed if initialSpeed > 0 else 0
        self.initialSpeed = min(self.initialSpeed, maxSpeed)
        self.initialAcceleration = initialAcceleration
        self.maxSpeed = maxSpeed #m/s
        self.maxAcceleration = maxAcceleration #m/s^2
        self.creationTime = creationTime
        self.lastUpdate = creationTime
        self.sigma = sigma
        self.reactionTime = reactionTime #seconds
        self.realReactionTime = min(random.gauss(reactionTime, 0.2),1)
        self.setPosition(initialPosition)
        self.setSpeed(initialSpeed) #m/s
        self.setAcceleration(initialAcceleration) #m/s^2
        self.pastState = self.STATE_CREATED
        self.arrivalTime = -1
        self.numberOfStops = 0
        self.timeWaited = 0
        self.departDelay = 0
        self.lane = 0
        #TODO: add time waited at semaphores, time waited at junctions, time waited at vehicles, time waited at merges, time waited at bifurcations
        #TODO: increment time waited and number of stops each time the vehicle stops, i.e. each time the speed was >0 and is set to 0
        #be careful, sometimes in moveVehicle the vehicle is moved just to check if the next position would collide, in those case it shouldn't count as stop, since
        #the vehicle was already stopped. Maybe use the lastUpdate attribute to check if the vehicle was already stopped in the previous cycle?
        #or just count the time stopped

    #crea funzione che restituisce true se stato è uno di quelli che aspetta

    @staticmethod
    def getVehiclesMetrics(vehicles): #returns the min, max and average travel time, the min, max and average number of stops, the min, max and average time waited, the min, max and average departure delay
        travelTimes = [v.getTravelTime() for v in vehicles if v.isArrived()]
        stops = [v.getNumberOfStops() for v in vehicles]
        timeWaited = [v.timeWaited for v in vehicles]
        departDelays = [v.departDelay for v in vehicles]
        if len(travelTimes) == 0:
            travelTimes = [0]
        return (min(travelTimes), max(travelTimes), median(travelTimes), sum(travelTimes)/len(travelTimes), min(stops), max(stops), median(stops), sum(stops)/len(stops), min(timeWaited), max(timeWaited), median(timeWaited), sum(timeWaited)/len(timeWaited) if len(timeWaited) > 0 else 0 , min(departDelays), max(departDelays), median(departDelays), sum(departDelays)/len(departDelays) if len(departDelays) > 0 else 0)

    def getVehiclesMetricsAsString(vehicles):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        return "Duration: min: %d, max: %d, median: %d, average: %d\nStops: min: %d, max: %d, median: %d, average: %d\nTime Waited: min: %d, max: %d, median: %d, average: %d\nDeparture Delay: min: %d, max: %d, median: %d, average: %d" % metrics

    def movingState(self, state):
        return state == self.STATE_MOVING or state == self.STATE_FOLLOWING_VEHICLE
    
    def waitingState(self, state):
        return state == self.STATE_WAITING_SEMAPHORE or state == self.STATE_WAITING_VEHICLE or state == self.STATE_WAITING_TO_ENTER or state == self.STATE_GIVING_WAY or state == self.STATE_STOPPED

    def update(self,currentTime):
        if self.waitingState(self.pastState): #or self.pastState == self.STATE_CREATED: #if the vehicle was waiting, increment the time waited
            self.timeWaited += currentTime - self.lastUpdate
        if self.isStopped() and (self.movingState(self.pastState) or self.lastUpdate == self.creationTime): #if the vehicle was moving and now is stopped, increment the number of stops
            self.numberOfStops += 1
        if self.waitingState(self.state) and self.pastState == self.STATE_CREATED: #if the vehicle was created and now is waiting, set the departure delay
            self.departDelay = currentTime - self.creationTime
        else:
            self.pastState = self.state #update the past state
        self.lastUpdate = currentTime #update the last update time

    def isArrived(self):
        return self.arrivalTime >= 0
    
    def setArrivalTime(self, time):
        self.arrivalTime = time
    
    def getArrivalTime(self):
        return self.arrivalTime
    
    def getDepartureTime(self):
        return self.creationTime
    
    def getNumberOfStops(self):
        return self.numberOfStops
    
    def incrementNumberOfStops(self):
        self.numberOfStops += 1

    def getTravelTime(self):
        return self.arrivalTime - self.creationTime - self.departDelay
    
    def getPosition(self):
        return self.position
    
    def getSpeed(self):
        return self.speed
    
    def getAcceleration(self):
        return self.acceleration
    
    def setPosition(self, position):
        self.position = position

    def setSpeed(self, speed):
        if speed > self.maxSpeed:
            speed = self.maxSpeed
        if speed <= 0:
            speed = 0
            self.setState(self.STATE_STOPPED)
        else:
            self.setState(self.STATE_MOVING)
        self.speed = speed

    def setAcceleration(self, acceleration):
        if acceleration <= self.maxAcceleration:
            self.acceleration = acceleration
        else:
            self.acceleration = self.maxAcceleration

    def setState(self, state):
        self.state = state
    
    def move(self, speedLimit, timeStep = 1, lane = -1):
        self.setPosition(self.calculatePosition(timeStep))
        self.setSpeed(min(random.gauss(self.calculateSpeed(timeStep),self.sigma),speedLimit))
        self.setAcceleration(self.calculateAcceleration(timeStep))
        if lane >= 0:
            self.setLane(lane)
        return self.getPosition()

    def calculatePosition(self, timeStep = 1):
        return self.position + self.speed * timeStep + 0.5 * self.acceleration * timeStep**2 #s = s0 + v0*t + 0.5*a*t^2
    
    def calculateSpeed(self, timeStep = 1):
        return min(self.speed + self.acceleration * timeStep, self.maxSpeed) #v = v0 + a*t
    
    def calculateAcceleration(self, timeStep = 1):
        '''if random.uniform(0, 1) < 0.5:
            return min(self.acceleration + random.gauss(0, self.sigma), self.maxAcceleration)
        else:
            return 0'''
        return 0

    def stopAt(self, position):
        self.setPosition(position)
        self.stop()

    def stopAtSemaphore(self,semPos):
        self.stopAt(semPos)
        self.setState(self.STATE_WAITING_SEMAPHORE)

    def stopAtVehicle(self, stopPos):
        self.stopAt(stopPos)
        self.setState(self.STATE_WAITING_VEHICLE)
        
    def giveWay(self, pos):
        self.stopAt(pos)
        self.setState(self.STATE_GIVING_WAY)

    def stop(self):
        self.setSpeed(0)
        self.setAcceleration(0)

    def moveTo(self, position):
        self.setPosition(position)
        self.setState(self.STATE_MOVING)

    def restart(self, speedLimit, timeStep = 1):
        self.setSpeed(min(self.initialSpeed,speedLimit))
        self.setAcceleration(0)
        self.setPosition(self.calculatePosition(timeStep))
        return self.getPosition()

    def getState(self):
        return (self.position, self.speed, self.acceleration)
    
    def getMetrics(self):
        return (self.creationTime, self.initialPosition, self.initialSpeed, self.arrivalTime, self.getSpeed(), self.getTravelTime(), self.getNumberOfStops(), self.timeWaited)
    
    def getMetricsAsString(self):
        if self.isArrived():
            return "Departure: %d, InitialPos: %d, InitialSpeed: %d, Arrival: %d, Final Speed: %d, Travel Time: %d, Stops: %d, Time Waited: %d" % self.getMetrics()
        else:
            metrics = self.getMetrics()
            return "Departure: %d, InitialPos: %d, InitialSpeed: %d, Stops: %d, Time Waited: %d, not arrived" % (metrics[0], metrics[1], metrics[2], metrics[6], metrics[7])
        
    def getMetricsAsJSON(self):
        metrics = self.getMetrics()
        return {"Departure": metrics[0], "InitialPos": metrics[1], "InitialSpeed": metrics[2], "Arrival": metrics[3], "FinalSpeed": metrics[4], "TravelTime": metrics[5], "Stops": metrics[6], "TimeWaited": metrics[7]}
    
    def isStopped(self):
        return self.speed == 0
    
    def isMoving(self):
        return self.speed > 0
    
    def isFollowing(self):
        return self.state == self.STATE_FOLLOWING_VEHICLE
    
    def isWaitingSemaphore(self):
        return self.state == self.STATE_WAITING_SEMAPHORE
    
    def isWaitingVehicle(self):
        return self.state == self.STATE_WAITING_VEHICLE
    
    def isGivingWay(self):
        return self.state == self.STATE_GIVING_WAY
    
    def isWaitingToEnter(self):
        return self.state == self.STATE_WAITING_TO_ENTER
    
    def followVehicle(self, vehicle, distance):
        self.setPosition(vehicle.getPosition() - vehicle.length - distance)
        self.setSpeed(vehicle.speed)
        self.setAcceleration(0)
        if self.getSpeed() > 0:
            self.setState(self.STATE_FOLLOWING_VEHICLE)
        else:
            self.setState(self.STATE_WAITING_VEHICLE)

    def setLane(self, lane):
        self.lane = lane

    def getLane(self):
        return self.lane

class Car(Vehicle):
    def __init__(self, id, initialSpeed, initialPosition):
        length = 5
        maxSpeed = 41.67 #m/s = 150 km/h
        maxAcceleration = 0.8 #m/s^2
        super().__init__(id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration)


class Bus(Vehicle):
    def __init__(self, id, initialSpeed, initialPosition):
        length = 10
        maxSpeed = 33.33 #m/s = 120 km/h
        maxAcceleration = 0.6 #m/s^2
        super().__init__(id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration)


class Bicicle(Vehicle):
    def __init__(self, id, initialSpeed, initialPosition):
        length = 2
        maxSpeed = 16.67 #m/s = 60 km/h
        maxAcceleration = 0.4 #m/s^2
        super().__init__(id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration)


class Pedestrian(Vehicle):
    def __init__(self, id, initialSpeed, initialPosition):
        length = 1
        maxSpeed = 5.56 #m/s = 20 km/h
        maxAcceleration = 0.2 #m/s^2
        super().__init__(id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration)


        
#TODO: add counters to count time waited (stopped, speed=0), time waited at semaphores (in class Vehicle or in VehicleState in data.py?)