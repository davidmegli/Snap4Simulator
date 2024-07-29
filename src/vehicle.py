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
import json

# VehicleState represent the state of a vehicle at a given time, including the time, position, speed, acceleration and state of the vehicle
class VehicleState:
    def __init__(self, time, position, speed, acceleration, state):
        self.time = time
        self.position = position
        self.speed = speed
        self.acceleration = acceleration
        self.state = state

    def setTime(self, time):
        self.time = time

    def setPosition(self, position):
        self.position = position

    def setSpeed(self, speed):
        self.speed = speed

    def setAcceleration(self, acceleration):
        self.acceleration = acceleration

    def setState(self, state):
        self.state = state

    def getPosition(self):
        return self.position

    def getSpeed(self):
        return self.speed

    def getAcceleration(self):
        return self.acceleration

    def getState(self):
        return self.state

    def getMetrics(self):
        return (self.time, self.position, self.speed, self.acceleration, self.state)

    def getMetricsAsString(self):
        return "Time: %d, Position: %d, Speed: %d, Acceleration: %d, State: %s" % self.getMetrics()

    def getMetricsAsJSON(self):
        metrics = self.getMetrics()
        return {"Time": metrics[0], "Position": metrics[1], "Speed": metrics[2], "Acceleration": metrics[3], "State": metrics[4]}

# Vehicle is one of the main classes, it represents a vehicle in the simulation, with its states (time, position, speed, acceleration)
class Vehicle:
    # Constants that represent the states a vehicle can be in
    STATE_STOPPED = "stopped"
    STATE_MOVING = "moving"
    STATE_WAITING_SEMAPHORE = "semaphore"
    STATE_WAITING_VEHICLE = "vehicle"
    STATE_WAITING_TO_ENTER = "entering"
    STATE_FOLLOWING_VEHICLE = "following"
    STATE_GIVING_WAY = "giving_way" #"precedenza"
    STATE_CREATED = "created"
    STATE_ACCELERATING = "accelerating"
    STATE_BREAKING = "breaking"
    def __init__(self, id, length, initialPosition, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime = 0, sigma = 0.0, reactionTime = 1):
        self.id = id
        self.length = length # vehicle length in meters
        self.initialPosition = initialPosition # initial position in meters
        self.initialSpeed: float = float(initialSpeed) if initialSpeed > 0 else 0.0
        self.initialSpeed = min(self.initialSpeed, maxSpeed)
        self.initialAcceleration = initialAcceleration
        self.maxSpeed = maxSpeed # vehicle top speed in m/s
        self.maxAcceleration = maxAcceleration if maxAcceleration is not None else 1 # m/s^2
        self.creationTime = creationTime
        self.lastUpdate = creationTime # last time the vehicle was updated
        self.sigma = sigma
        self.reactionTime: float = float(reactionTime) # seconds
        #self.realReactionTime = min(random.gauss(reactionTime, 0.2),1)
        self.setPosition(initialPosition)
        self.setState(self.STATE_CREATED)
        self.setSpeed(initialSpeed) #m/s
        self.setAcceleration(initialAcceleration) #m/s^2
        self.pastState = self.STATE_CREATED
        self.arrivalTime = -1
        self.numberOfStops = 0
        self.timeWaited = 0
        self.departDelay = 0
        self.lane = 0
        self.stateHistory: list[VehicleState] = []
        #TODO: add time waited at semaphores, time waited at junctions, time waited at vehicles, time waited at merges, time waited at bifurcations
        #TODO: increment time waited and number of stops each time the vehicle stops, i.e. each time the speed was >0 and is set to 0
        #be careful, sometimes in moveVehicle the vehicle is moved just to check if the next position would collide, in those case it shouldn't count as stop, since
        #the vehicle was already stopped. Maybe use the lastUpdate attribute to check if the vehicle was already stopped in the previous cycle?
        #or just count the time stopped

    #crea funzione che restituisce true se stato è uno di quelli che aspetta

    # Static method that returns the metrics of a given list of vehicles
    @staticmethod
    def getVehiclesMetrics(vehicles):
        travelTimes = [v.getTravelTime() for v in vehicles if v.isArrived()]
        stops = [v.getNumberOfStops() for v in vehicles]
        timeWaited = [v.timeWaited for v in vehicles]
        departDelays = [v.departDelay for v in vehicles]
        if len(travelTimes) == 0:
            travelTimes = [0]
        minTravelTime = min(travelTimes) if len(travelTimes) > 0 else 0
        maxTravelTime = max(travelTimes) if len(travelTimes) > 0 else 0
        medianTravelTime = median(travelTimes) if len(travelTimes) > 0 else 0
        avgTravelTime = sum(travelTimes)/len(travelTimes) if len(travelTimes) > 0 else 0
        minStops = min(stops) if len(stops) > 0 else 0
        maxStops = max(stops) if len(stops) > 0 else 0
        medianStops = median(stops) if len(stops) > 0 else 0
        avgStops = sum(stops)/len(stops) if len(stops) > 0 else 0
        minTimeWaited = min(timeWaited) if len(timeWaited) > 0 else 0
        maxTimeWaited = max(timeWaited) if len(timeWaited) > 0 else 0
        medianTimeWaited = median(timeWaited) if len(timeWaited) > 0 else 0
        avgTimeWaited = sum(timeWaited)/len(timeWaited) if len(timeWaited) > 0 else 0
        minDepartDelay = min(departDelays) if len(departDelays) > 0 else 0
        maxDepartDelay = max(departDelays) if len(departDelays) > 0 else 0
        medianDepartDelay = median(departDelays) if len(departDelays) > 0 else 0
        avgDepartDelay = sum(departDelays)/len(departDelays) if len(departDelays) > 0 else 0
        return (minTravelTime, maxTravelTime, medianTravelTime, avgTravelTime, minStops, maxStops, medianStops, avgStops, minTimeWaited, maxTimeWaited, medianTimeWaited, avgTimeWaited, minDepartDelay, maxDepartDelay, medianDepartDelay, avgDepartDelay)

    @staticmethod
    def getVehiclesMetricsAsString(vehicles):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        return "Duration: min: %d, max: %d, median: %d, average: %d\nStops: min: %d, max: %d, median: %d, average: %d\nTime Waited: min: %d, max: %d, median: %d, average: %d\nDeparture Delay: min: %d, max: %d, median: %d, average: %d" % metrics
    
    @staticmethod
    def getVehiclesMetricsAsJSON(vehicles):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        return {"Duration": {"min": metrics[0], "max": metrics[1], "median": metrics[2], "average": metrics[3]}, "Stops": {"min": metrics[4], "max": metrics[5], "median": metrics[6], "average": metrics[7]}, "TimeWaited": {"min": metrics[8], "max": metrics[9], "median": metrics[10], "average": metrics[11]}, "DepartureDelay": {"min": metrics[12], "max": metrics[13], "median": metrics[14], "average": metrics[15]}}

    @staticmethod
    def saveVehiclesMetrics(vehicles, filename):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        with open(filename, "w") as f:
            json.dump(Vehicle.getVehiclesMetricsAsJSON(vehicles), f, indent = 4)

    def getVehicleStateHistory(self):
        return self.stateHistory
    
    def getVehicleStateHistoryAsJSON(self):
        return [state.getMetricsAsJSON() for state in self.stateHistory]
    
    def getVehicleStateHistoryMetrics(self):
        avgSpeed = sum([state.speed for state in self.stateHistory])/len(self.stateHistory) if len(self.stateHistory) > 0 else 0
        avgAcceleration = sum([state.acceleration for state in self.stateHistory])/len(self.stateHistory) if len(self.stateHistory) > 0 else 0
        timeWaitingSemaphore = 0
        for i in range(1,len(self.stateHistory)):
            if self.stateHistory[i].state == self.STATE_WAITING_SEMAPHORE:
                timeWaitingSemaphore += self.stateHistory[i].time - self.stateHistory[i-1].time
        return (avgSpeed, avgAcceleration)
    
    def getVehicleStateHistoryMetricsAsJSON(self):
        metrics = self.getVehicleStateHistoryMetrics()
        return {"VehicleID": self.id, "AverageSpeed": metrics[0], "AverageAcceleration": metrics[1]}
    
    def saveVehicleStateHistoryMetrics(self, filename):
        metrics = self.getVehicleStateHistoryMetrics()
        with open(filename, "w") as f:
            json.dump(self.getVehicleStateHistoryMetricsAsJSON(), f, indent = 4)

    def wasJustCreated(self):
        return self.pastState == self.STATE_CREATED

    # Returns true if the vehicle is in a moving state
    def movingState(self, state):
        return state == self.STATE_MOVING or state == self.STATE_FOLLOWING_VEHICLE
    
    # Returns true if the vehicle is in a waiting state
    def waitingState(self, state):
        return state == self.STATE_WAITING_SEMAPHORE or state == self.STATE_WAITING_VEHICLE or state == self.STATE_WAITING_TO_ENTER or state == self.STATE_GIVING_WAY or state == self.STATE_STOPPED

    # Function called to commit the state of the vehicle at a given time
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
        self.saveState(currentTime)

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
        self.speed = float(speed)
        if self.state == self.STATE_ACCELERATING:
            return
        if speed <= 0:
            speed = 0
            self.setState(self.STATE_STOPPED)
        else:
            self.setState(self.STATE_MOVING)

    def setAcceleration(self, acceleration):
        if acceleration <= self.maxAcceleration:
            self.acceleration = acceleration
        else:
            self.acceleration = self.maxAcceleration

    def setState(self, state):
        self.state = state
    
    def move(self, speedLimit, timeStep = 1.0, lane = -1):
        step = timeStep # max(timeStep - self.reactionTime, 1.0)#0.01)
        if self.state == self.STATE_ACCELERATING:
            if self.id <=3:  #DEBUG
                print("move() restarting veh: %s"%self.id)
            self.restart(speedLimit, step)
            return self.getPosition()
        acc = self.calculateAcceleration(step)
        speed = min(random.gauss(self.calculateSpeed(acc, step),self.sigma),speedLimit)
        pos = self.calculatePosition(acc, step)
        self.setPosition(pos)
        self.setSpeed(speed)
        self.setAcceleration(acc)
        if lane >= 0:
            self.setLane(lane)
        return self.getPosition()

    def calculatePosition(self, acceleration, timeStep = 1.0):
        return self.position + self.speed * timeStep + 0.5 * acceleration * timeStep**2 #s = s0 + v0*t + 0.5*a*t^2
    
    def calculateSpeed(self, acceleration, timeStep = 1.0):
        if self.id <=3: #DEBUG
            print("calculateSpeed() Speed: %s, Acc: %s, Time: %s" % (self.speed, acceleration, timeStep))
        return min(self.speed + acceleration * timeStep, self.maxSpeed) #v = v0 + a*t
    
    def calculateAcceleration(self, timeStep = 1.0):
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

    def restart(self, speedLimit, timeStep = 1.0):
        self.setState(self.STATE_ACCELERATING)
        acc = self.maxAcceleration
        if self.id <= 3: #DEBUG
            print("Vehicle: %s acc: %s" % (self.id, acc))
        speed = self.calculateSpeed(acc, timeStep)
        if self.id <=3: #DEBUG
            print("Vehicle: %s, pos: %s, speed: %s, acc: %s" % (self.id, self.position,speed,acc))
        if speed >= self.maxSpeed:
            self.setState(self.STATE_MOVING)
        self.setSpeed(min(speed,speedLimit))
        self.setAcceleration(acc)
        pos = self.calculatePosition(self.maxAcceleration, timeStep)
        self.setPosition(pos)
        return self.getPosition()#NEW _> FIXME: THE PROBLEM IS HERE!!!
    def restarte(self, speedLimit, timeStep = 1): #OLD
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
        return (self.speed == 0 or self.state == self.STATE_BREAKING) and self.state != self.STATE_ACCELERATING
    
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
        #self.setAcceleration(0)
        if self.getSpeed() > 0:
            self.setState(self.STATE_FOLLOWING_VEHICLE)
        else:
            self.setState(self.STATE_WAITING_VEHICLE)

    def setLane(self, lane):
        self.lane = lane

    def getLane(self):
        return self.lane
    
    # Function called in the update function to save the state of the vehicle at a given time in the vehicle state history
    def saveState(self, time):
        pastTime = self.stateHistory[-1].time if len(self.stateHistory) > 0 else self.creationTime
        pastSpeed = self.stateHistory[-1].speed if len(self.stateHistory) > 0 else self.initialSpeed
        acceleration = (self.speed - pastSpeed) / (time - pastTime) if time - pastTime > 0 else 0
        self.stateHistory.append(VehicleState(time, self.position, self.speed, acceleration, self.state))

class Car(Vehicle):
    LENGTH = 5
    MAX_SPEED = 41.67 #m/s = 150 km/h
    MAX_ACCELERATION = 0.8 #m/s^2
    REACTION_TIME = 1
    def __init__(self, id, initialSpeed, initialPosition, creationTime = 0, sigma = 0.0, reactionTime = REACTION_TIME):
        super().__init__(id, Car.LENGTH, initialPosition, initialSpeed, 0, Car.MAX_SPEED, Car.MAX_ACCELERATION, creationTime, sigma, reactionTime)

class Bus(Vehicle):
    LENGTH = 12
    MAX_SPEED = 33.33 #m/s = 120 km/h
    MAX_ACCELERATION = 0.6 #m/s^2
    REACTION_TIME = 1
    def __init__(self, id, initialSpeed, initialPosition, creationTime = 0, sigma = 0.0, reactionTime = REACTION_TIME):
        super().__init__(id, Bus.LENGTH, initialPosition, initialSpeed, 0, Bus.MAX_SPEED, Bus.MAX_ACCELERATION, creationTime, sigma, reactionTime)

class Bicicle(Vehicle):
    LENGTH = 2
    MAX_SPEED = 13.89 #m/s = 50 km/h
    MAX_ACCELERATION = 0.4 #m/s^2
    REACTION_TIME = 1
    def __init__(self, id, initialSpeed, initialPosition, creationTime = 0, sigma = 0.0, reactionTime = REACTION_TIME):
        super().__init__(id, Bicicle.LENGTH, initialPosition, initialSpeed, 0, Bicicle.MAX_SPEED, Bicicle.MAX_ACCELERATION, creationTime, sigma, reactionTime)

class Pedestrian(Vehicle):
    LENGTH = 1
    MAX_SPEED = 2.78 #m/s = 10 km/h
    MAX_ACCELERATION = 0.2 #m/s^2
    REACTION_TIME = 1
    def __init__(self, id, initialSpeed, initialPosition, creationTime = 0, sigma = 0.0, reactionTime = REACTION_TIME):
        super().__init__(id, Pedestrian.LENGTH, initialPosition, initialSpeed, 0, Pedestrian.MAX_SPEED, Pedestrian.MAX_ACCELERATION, creationTime, sigma, reactionTime)


        
#TODO: add counters to count time waited (stopped, speed=0), time waited at semaphores (in class Vehicle or in VehicleState in data.py?)