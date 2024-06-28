"""
@file    vehicle.py
@author  David Megli
"""

class VehicleState:
    def __init__(self, time, position, speed, acceleration, state = "Waiting"):
        self.time = time
        self.position = position
        self.speed = speed #m/s
        self.acceleration = acceleration #m/s^2
        self.state = state

class Vehicle:
    def __init__(self, id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration):
        self.id = id
        self.length = length #meters
        self.position = initialPosition
        self.maxSpeed = maxSpeed #m/s
        self.maxAcceleration = maxAcceleration #m/s^2
        self.states = [VehicleState(0, initialPosition, initialSpeed, 0)]
    
    def speedkmh(self):
        return self._speed * 3.6 #m/s to km/h
    
    def move(self, timeStep = 1):
        lastState = self.states[-1]
        newPosition = lastState.position + lastState.speed * timeStep + 0.5 * lastState.acceleration * timeStep**2 #s = ut + 0.5at^2
        newSpeed = min(lastState.speed + lastState.acceleration * timeStep, self.maxSpeed) #v = u + at
        newAcceleration = 0 #no acceleration for now
        newTime = lastState.time + timeStep
        self.states.append(VehicleState(newTime, newPosition, newSpeed, newAcceleration, "Traveling")) #add new state to states list

    def stopAt(self, position, timeStep = 1):
        lastState = self.states[-1]
        newPosition = position
        newSpeed = 0
        newAcceleration = 0
        newTime = lastState.time + timeStep
        self.states.append(VehicleState(newTime, newPosition, newSpeed, newAcceleration, "Waiting"))


    def futurePosition(self, timeStep = 1):
        lastState = self.states[-1]
        return lastState.position + lastState.speed * timeStep + 0.5 * lastState.acceleration * timeStep**2

    def stop(self):
        lastState = self.states[-1]
        newPosition = lastState.position
        newSpeed = 0
        newAcceleration = 0
        newTime = lastState.time
        self.states.append(VehicleState(newTime, newPosition, newSpeed, newAcceleration, "Waiting"))

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