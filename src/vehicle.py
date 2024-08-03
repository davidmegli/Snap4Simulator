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
import math
import json

# VehicleState represent the state of a vehicle at a given time, including the time, position, speed, acceleration and state of the vehicle
class VehicleState:
    def __init__(self, time, position, speed, acceleration, state, road = None):
        self.time = time
        self.position = position
        self.speed = speed
        self.acceleration = acceleration
        self.state = state
        self.road = road

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
    
    def getStateAsJSON(self):
        return {"Time": self.time, "Position": self.position, "Speed": self.speed, "Acceleration": self.acceleration, "State": self.state, "Road": self.road}

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
    STATE_BRAKING = "braking"
    DEFAULT_TIME_STEP = 1.0
    STATE_ARRIVED = "arrived"
    def __init__(self, id, length, initialPosition, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime = 0, sigma = 0.0, reactionTime = 0.8, reactionTimeAtSemaphore = 2.0, dampingFactor = 0.1):
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
        self.reactionTimeAtSemaphore: float = float(reactionTimeAtSemaphore) # seconds
        self.cumulativeDelay = 0.0
        self.maxCumulativeDelay = 20.0
        self.currentDelay = 0.0
        self.dampingFactor = dampingFactor if dampingFactor is not None else 0.1 # damping factor for the cumulative delay (fattore di smorzamento)
        self.isDeparted = False
        # represents the cumulative time delay to restart the vehicle
        # e.g. at a stop the vehicles will start one after the other with a delay
        #self.realReactionTime = min(random.gauss(reactionTime, 0.2),1)
        self.setPosition(initialPosition)
        self.setState(self.STATE_CREATED)
        self.setSpeed(initialSpeed) #m/s
        self.setAcceleration(initialAcceleration) #m/s^2
        self.pastState = self.STATE_CREATED
        self.arrivalTime = -1.0
        self.numberOfStops = 0.0
        self.timeWaited = 0.0
        self.departDelay = 0.0
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
        timeWaited = [v.timeWaited for v in vehicles if v.isArrived()]
        departDelays = [v.departDelay for v in vehicles if v.isArrived()]
        #for v in vehicles:
         #   print("Vehicle %d: %s" % (v.id, v.getMetricsAsString()))
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
        maxTimeWaited = max(timeWaited) if len(timeWaited) > 0 else 0 #note: I calculate the min and max time waited also for vehicles that are still running or waiting
        medianTimeWaited = median(timeWaited) if len(timeWaited) > 0 else 0
        avgTimeWaited = sum(timeWaited)/len(timeWaited) if len(timeWaited) > 0 else 0
        minDepartDelay = min(departDelays) if len(departDelays) > 0 else 0
        maxDepartDelay = max(departDelays) if len(departDelays) > 0 else 0
        medianDepartDelay = median(departDelays) if len(departDelays) > 0 else 0
        avgDepartDelay = sum(departDelays)/len(departDelays) if len(departDelays) > 0 else 0
        avgSpeed = 0
        avgAcc = 0
        for v in vehicles:
            m = v.getVehicleStateHistoryMetrics()
            avgSpeed += m[0]
            avgAcc += m[1]
        avgSpeed /= len(vehicles)
        avgAcc /= len(vehicles)
        arrivedVehicles = len([v for v in vehicles if v.isArrived()])
        return (minTravelTime, maxTravelTime, medianTravelTime, avgTravelTime, minStops, maxStops, medianStops, avgStops, minTimeWaited, maxTimeWaited, medianTimeWaited, avgTimeWaited, minDepartDelay, maxDepartDelay, medianDepartDelay, avgDepartDelay, avgSpeed, avgAcc, arrivedVehicles)

    @staticmethod
    def getVehiclesMetricsAsString(vehicles):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        return "Duration: min: %f, max: %f, median: %f, average: %f\nStops: min: %f, max: %f, median: %f, average: %f\nTime Waited: min: %f, max: %f, median: %f, average: %f\nDeparture Delay: min: %f, max: %f, median: %f, average: %f\nAverage Speed: %f\nAverage Acceleration: %f\nArrived Vehicles: %d" % metrics
    
    @staticmethod
    def getVehiclesMetricsAsJSON(vehicles):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        return {"Duration": {"min": metrics[0], "max": metrics[1], "median": metrics[2], "average": metrics[3]}, "Stops": {"min": metrics[4], "max": metrics[5], "median": metrics[6], "average": metrics[7]}, "TimeWaited": {"min": metrics[8], "max": metrics[9], "median": metrics[10], "average": metrics[11]}, "DepartureDelay": {"min": metrics[12], "max": metrics[13], "median": metrics[14], "average": metrics[15]}, "AverageSpeed": metrics[16], "AverageAcceleration": metrics[17], "ArrivedVehicles": metrics[18]}

    @staticmethod
    def saveVehiclesMetrics(vehicles, filename):
        metrics = Vehicle.getVehiclesMetrics(vehicles)
        with open(filename, "w") as f:
            json.dump(Vehicle.getVehiclesMetricsAsJSON(vehicles), f, indent = 4)

    @staticmethod
    def saveVehiclesStateHistory(vehicles, filename):
        vehiclesHistory = {"vehiclesHistory": []}
        for v in vehicles:
            vehiclesHistory["vehiclesHistory"].append(v.getVehicleStateHistoryAsJSON())
        with open(filename, "w") as f:
            json.dump(vehiclesHistory, f, indent = 4)

    @staticmethod
    def saveVehiclesStateHistoryGroupedByTime(vehicles, filename):
        vehiclesHistory = {"vehiclesHistory": []}
        maxTime = max([v.stateHistory[-1].time for v in vehicles])
        for t in range(maxTime):
            vehiclesHistory["vehiclesHistory"].append({"Time": t, "VehiclesStates": []})
            for v in vehicles:
                for state in v.stateHistory:
                    if state.time == t:
                        vehiclesHistory["vehiclesHistory"][-1]["VehiclesStates"].append({"VehicleID": v.id, "Position": state.position, "Speed": state.speed, "Acceleration": state.acceleration, "State": state.state, "Road": state.road})
        with open(filename, "w") as f:
            json.dump(vehiclesHistory, f, indent = 4)

    def getVehicleStateHistory(self):
        return self.stateHistory
    
    def getVehicleStateHistoryAsJSON(self):
        history = {"VehicleID": self.id, "History": []}
        for state in self.stateHistory:
            history["History"].append(state.getStateAsJSON())
        return history
    
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

    def saveVehicleStateHistory(self, filename):
        with open(filename, "w") as f:
            json.dump(self.getVehicleStateHistoryAsJSON(), f, indent = 4)

    def wasJustCreated(self):
        return self.pastState == self.STATE_CREATED

    # Returns true if the vehicle is in a moving state
    def movingState(self, state):
        return state == self.STATE_MOVING or state == self.STATE_FOLLOWING_VEHICLE
    
    # Returns true if the vehicle is in a waiting state
    def waitingState(self, state):
        return state == self.STATE_WAITING_SEMAPHORE or state == self.STATE_WAITING_VEHICLE or state == self.STATE_WAITING_TO_ENTER or state == self.STATE_GIVING_WAY or state == self.STATE_STOPPED or (state == self.STATE_ACCELERATING and self.speed == 0)

    # Function called to commit the state of the vehicle at a given time
    def update(self,currentTime,road=None):
        if self.waitingState(self.pastState) and self.getSpeed() == 0: #or self.pastState == self.STATE_CREATED: #if the vehicle was waiting, increment the time waited
            self.timeWaited += currentTime - self.lastUpdate
        if self.isStopped() and (self.movingState(self.pastState) or self.lastUpdate == self.creationTime): #if the vehicle was moving and now is stopped, increment the number of stops
            self.numberOfStops += 1
        if self.waitingState(self.state) and self.pastState == self.STATE_CREATED: #if the vehicle was created and now is waiting, set the departure delay
            self.departDelay = currentTime - self.creationTime
        
        self.pastState = self.state #update the past state
        self.lastUpdate = currentTime #update the last update time
        self.saveState(currentTime, road)

    def isArrived(self):
        return self.arrivalTime >= 0
    
    def setArrivalTime(self, time):
        self.arrivalTime = time
        self.state = self.STATE_ARRIVED
    
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
    
    def getBackPosition(self):
        return self.position - self.length
    
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
            if not self.isDeparted:
                self.departDelay = self.lastUpdate - self.creationTime + self.DEFAULT_TIME_STEP
            self.isDeparted = True

    def setAcceleration(self, acceleration):
        if acceleration <= self.maxAcceleration:
            self.acceleration = acceleration
        else:
            self.acceleration = self.maxAcceleration

    def setState(self, state):
        self.state = state
    
    def move(self, speedLimit, timeStep = 1.0, lane = -1):
        step = timeStep # max(timeStep - self.reactionTime, 1.0)#0.01)
        if self.id == 134 and self.position <=5: #DEBUG #print everything about the vehicle
            print("Move() step: %f [before] Vehicle %d: Position: %f, Speed: %f, Acceleration: %f, State: %s, Cumulative Delay: %f, Current Delay: %f" % (step, self.id, self.position, self.speed, self.acceleration, self.state, self.cumulativeDelay, self.currentDelay))
        if self.state == self.STATE_ACCELERATING:
            self.restart(speedLimit, step)
            return self.getPosition()
        acc = self.calculateAcceleration(step)
        speed = min(random.gauss(self.calculateSpeed(acc, step),self.sigma),speedLimit)
        pos = self.calculatePosition(acc, step)
        self.setPosition(pos)
        self.setSpeed(speed)
        self.setAcceleration(acc)
        if self.id == 134 and self.position <=5: #DEBUG #print everything about the vehicle
            print("Move() step: %f [after] Vehicle %d: Position: %f, Speed: %f, Acceleration: %f, State: %s, Cumulative Delay: %f, Current Delay: %f" % (step, self.id, self.position, self.speed, self.acceleration, self.state, self.cumulativeDelay, self.currentDelay))
        if lane >= 0:
            self.setLane(lane)
        return self.getPosition()

    def calculatePosition(self, acceleration, timeStep = 1.0):
        pos = self.position + self.speed * timeStep + 0.5 * acceleration * timeStep**2 #s = s0 + v0*t + 0.5*a*t^2
        if self.speed + acceleration * timeStep > self.maxSpeed:
            pos = self.position + self.speed * timeStep + 0.5 * (self.maxSpeed - self.speed) * timeStep
        return pos
    
    def calculateSpeed(self, acceleration, timeStep = 1.0):
        return min(self.speed + acceleration * timeStep, self.maxSpeed) #v = v0 + a*t
    
    def calculateAcceleration(self, timeStep = 1.0):
        '''if random.uniform(0, 1) < 0.5:
            return min(self.acceleration + random.gauss(0, self.sigma), self.maxAcceleration)
        else:
            return 0'''
        acc = self.maxAcceleration
        if self.speed + acc * timeStep > self.maxSpeed:
            acc = (self.maxSpeed - self.speed) / timeStep
        return acc

    def brakeToStopAt(self, position, timeStep = 1.0):
        if self.position >= position:
            self.stop()
            return self.position
        acc = - self.speed**2 / (2 * (position - self.position)) #v^2 = u^2 + 2*a*s, accelerazione in funzione di velocità e spazio di frenata
        speed = self.calculateSpeed(acc, timeStep)
        pos = self.calculatePosition(acc, timeStep)
        self.setPosition(pos)
        self.setSpeed(max(speed, 0))
        self.setAcceleration(acc)
        return self.getPosition()

    def slowDown(self):
        newSpeed = self.getSpeed() / 2
        self.setSpeed(newSpeed)
        self.setPosition(self.getPosition() - newSpeed)
        return self.getPosition()

    def stopAt(self, position):
        #TODO: everytime this func is called start to decelerate the vehicle
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

    def restart(self, speedLimit, timeStep = 1.0, precedingVehicle = None):
        # if the past state it was not accelerating it means that the current time is
        # the first time the vehicle is restarting, so I calculate the delay to restart
        # as a sum of the preveious vehicle dela plus the current vehicle's reaction time
        if self.id == 134: #DEBUG #print everything about the vehicle
            print("1.Vehicle %d: Position: %f, Speed: %f, Acceleration: %f, Past State: %s, State: %s, Cumulative Delay: %f, Current Delay: %f" % (self.id, self.position, self.speed, self.acceleration, self.pastState, self.state, self.cumulativeDelay, self.currentDelay))
        if self.pastState != self.STATE_ACCELERATING: # first time step in which the vehicle is restarting
            if self.isDeparted:
                if self.pastState == self.STATE_WAITING_SEMAPHORE: # if the vehicle was waiting at a semaphore (so it also was the first vehicle in the queue)
                    self.cumulativeDelay = self.reactionTimeAtSemaphore
                    self.currentDelay = self.cumulativeDelay
                else:
                    precCumulativeDelay = precedingVehicle.getCumulativeDelay() if precedingVehicle is not None else 0
                    #self.cumulativeDelay = self.reactionTime * ((self.maxCumulativeDelay - precCumulativeDelay)/self.maxCumulativeDelay) if self.maxCumulativeDelay != 0 else self.reactionTime # in any case I must add the reaction time to the cumulative delay
                    #if precedingVehicle is not None: # if there is a preceding vehicle
                        #self.cumulativeDelay += precCumulativeDelay # I also add its cumulative delay
                    damping1 = math.exp(-self.dampingFactor * precCumulativeDelay)
                    damping2 = 1 / math.log(self.dampingFactor * precCumulativeDelay + 2)
                    damping3 = 1 / math.sqrt(self.dampingFactor * precCumulativeDelay + 1)
                    self.cumulativeDelay = precCumulativeDelay + self.reactionTime * damping1
                    self.currentDelay = self.cumulativeDelay # I save in this attribute the updated cumulative delay
                    print("Vehicle %d: Reaction Time: %f, Prec Cumulative Delay: %f, Damping: %f, Cumulative Delay: %f" % (self.id, self.reactionTime, precCumulativeDelay, damping1, self.cumulativeDelay))
            else:
                self.cumulativeDelay = 0
                self.currentDelay = 0
        if self.id == 134: #DEBUG #print everything about the vehicle
            print("2.Vehicle %d: Position: %f, Speed: %f, Acceleration: %f, State: %s, Cumulative Delay: %f, Current Delay: %f" % (self.id, self.position, self.speed, self.acceleration, self.state, self.cumulativeDelay, self.currentDelay))
        step = max (timeStep - self.currentDelay, 0)
        if step > 0:
            self.cumulativeDelay = 0
        self.currentDelay = max (self.currentDelay - timeStep, 0)
        self.setState(self.STATE_ACCELERATING)
        acc = self.maxAcceleration
        speed = self.calculateSpeed(acc, step)
        if speed >= self.maxSpeed:
            self.setState(self.STATE_MOVING)
        self.setSpeed(min(speed,speedLimit))
        self.setAcceleration(acc)
        pos = self.calculatePosition(self.maxAcceleration, step)
        self.setPosition(pos)
        return self.getPosition()

    def getCumulativeDelay(self):
        return self.cumulativeDelay

    def getState(self):
        return (self.position, self.speed, self.acceleration)
    
    def getMetrics(self):
        return (self.creationTime, self.departDelay, self.initialPosition, self.initialSpeed, self.arrivalTime, self.getSpeed(), self.getTravelTime(), self.getNumberOfStops(), self.timeWaited)
    
    def getMetricsAsString(self):
        if self.isArrived():
            return "CreationTime: %d, DepartureDelay: %d, InitialPos: %d, InitialSpeed: %d, Arrival: %d, Final Speed: %d, Travel Time: %d, Stops: %d, Time Waited: %d" % self.getMetrics()
        else:
            metrics = self.getMetrics()
            return "CreationTime: %d, DepartureDelay: %d, InitialPos: %d, InitialSpeed: %d, Stops: %d, Time Waited: %d, not arrived" % (metrics[0], metrics[1], metrics[2], metrics[3], metrics[7], metrics[8])
        
    def getMetricsAsJSON(self):
        metrics = self.getMetrics()
        return {"CreationTime": metrics[0], "DepartureDelay": metrics[1], "InitialPos": metrics[2], "InitialSpeed": metrics[3], "Arrival": metrics[4], "FinalSpeed": metrics[5], "TravelTime": metrics[6], "Stops": metrics[7], "TimeWaited": metrics[8]}
    
    def isStopped(self):
        # the vehicle is considered stopped if the vehicle has speed = 0 or is braking
        # AND it's not accelerating.
        # The vehicle is considered NOT stopped if it's accelerating, even if it still has speed = 0
        return (self.speed == 0 or self.state == self.STATE_BRAKING) and self.state != self.STATE_ACCELERATING and self.state != self.STATE_CREATED
    
    def isMoving(self):
        return self.speed > 0 or self.state == self.STATE_ACCELERATING
    
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
    def saveState(self, time, road = None):
        pastTime = self.stateHistory[-1].time if len(self.stateHistory) > 0 else self.creationTime
        pastSpeed = self.stateHistory[-1].speed if len(self.stateHistory) > 0 else self.initialSpeed
        if time <= pastTime:
            return
        acceleration = (self.speed - pastSpeed) / (time - pastTime) if time > pastTime and time > self.creationTime else 0
        self.stateHistory.append(VehicleState(time, self.position, self.speed, acceleration, self.state, road.id if road is not None else None))

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