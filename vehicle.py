"""
@file    vehicle.py
@author  David Megli
"""
import random

class Vehicle:
    def __init__(self, id, length, initialPosition, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, moving = False, creationTime = 0, sigma = 0.3):
        self.id = id
        self.length = length #meters
        self.position = initialPosition
        self.speed = initialSpeed #m/s
        self.acceleration = initialAcceleration #m/s^2
        self.maxSpeed = maxSpeed #m/s
        self.maxAcceleration = maxAcceleration #m/s^2
        self.moving = False
        self.sigma = sigma
    
    def setSpeed(self, speed):
        if speed <= self.maxSpeed:
            self.speed = speed
        else:
            self.speed = self.maxSpeed

    def speedkmh(self):
        return self._speed * 3.6 #m/s to km/h
    
    def move(self, timeStep = 1):
        self.position = self.nextPosition(timeStep)
        self.speed = self.nextSpeed(timeStep)
        self.acceleration = self.calculateAcceleration(timeStep)

    def calculateAcceleration(self, timeStep = 1):
        if random.uniform(0, 1) < 0.5:
            return min(self.acceleration + random.gauss(0, self.sigma), self.maxAcceleration)
        else:
            return 0

    def stopAt(self, position, timeStep = 1):
        self.position = position
        self.stop()

    def nextPosition(self, timeStep = 1):
        return self.position + self.speed * timeStep + 0.5 * self.acceleration * timeStep**2 #s = s0 + v0*t + 0.5*a*t^2
    
    def nextSpeed(self, timeStep = 1):
        return min(self.speed + self.acceleration * timeStep, self.maxSpeed) #v = v0 + a*t

    def stop(self):
        self.speed = 0
        self.acceleration = 0

    def moveTo(self, position, timeStep = 1):
        self.position = position

    def getState(self):
        return (self.position, self.speed, self.acceleration)

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