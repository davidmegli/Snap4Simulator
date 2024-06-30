"""
@file    vehicle.py
@author  David Megli
"""
import random

class Vehicle:
    STATE_STOPPED = "stopped"
    STATE_MOVING = "moving"
    STATE_WAITING_SEMAPHORE = "semaphore"
    STATE_WAITING_VEHICLE = "vehicle"
    STATE_FOLLOWING_VEHICLE = "following"
    STATE_GIVING_WAY = "giving_way" #"precedenza"
    def __init__(self, id, length, initialPosition, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime = 0, sigma = 0.3):
        self.id = id
        self.length = length #meters
        self.initialSpeed = initialSpeed
        self.initialAcceleration = initialAcceleration
        self.maxSpeed = maxSpeed #m/s
        self.maxAcceleration = maxAcceleration #m/s^2
        self.creationTime = creationTime
        self.sigma = sigma
        self.setPosition(initialPosition)
        self.setSpeed(initialSpeed) #m/s
        self.setAcceleration(initialAcceleration) #m/s^2

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
    
    def move(self, timeStep = 1):
        self.setPosition(self.calculatePosition(timeStep))
        self.setSpeed(self.calculateSpeed(timeStep))
        self.setAcceleration(self.calculateAcceleration(timeStep))

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

    def restart(self, timeStep = 1):
        self.setSpeed(self.initialSpeed)
        self.setAcceleration(0)
        self.setPosition(self.calculatePosition(timeStep))

    def getState(self):
        return (self.position, self.speed, self.acceleration)
    
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
    
    def followVehicle(self, vehicle, distance):
        self.setPosition(vehicle.position - vehicle.length - distance)
        self.setSpeed(vehicle.speed)
        self.setAcceleration(0)
        if self.getSpeed() > 0:
            self.setState(self.STATE_FOLLOWING_VEHICLE)
        else:
            self.setState(self.STATE_WAITING_VEHICLE)

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