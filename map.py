"""
@file    map.py
@author  David Megli
"""

class Road:
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None):
        self.id = id
        self.length = length
        self.vehicles = [] #list of vehicles on the road
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.semaphores = semaphores if semaphores else []  # list of semaphores on the road
        self.startJunction = None #TODO: implement junctions
        self.endJunction = None

    def addVehicle(self, vehicle, currentTime, position = 0): #add vehicle to the road
        # I check if there is a vehicle too close
        previousVehicle = self.previousVehicle(vehicle)
        nextSem = self.getNextSemaphore(position)
        if previousVehicle != None:
            safetyPosition = self.safetyDistanceFrom(previousVehicle)
            if safetyPosition <= 0:
                vehicle.stopAtVehicle(previousVehicle)
        elif nextSem != None and nextSem.isRed(currentTime) and position >= nextSem.position:
            vehicle.stopAtSemaphore(nextSem.position)
        else:
            self.limitSpeed(vehicle)
        self.vehicles.append(vehicle)

    def addSemaphore(self, position, greenTime, redTime, yellowTime = 0, startTime = 0): #MUST add semaphores in order of position
        self.semaphores.append(Semaphore(greenTime, redTime, position, yellowTime, startTime))

    def addSemaphore(self, semaphore): #MUST add semaphores in order of position
        self.semaphores.append(semaphore)

    def moveVehicle(self, vehicle, currentTime, timeStep = 1):
        # If the vehicle is in the road, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        if vehicle in self.vehicles: #if the vehicle is on the road
            currentPos = vehicle.getPosition()
            nextPos = vehicle.calculatePosition(timeStep) #I get the future position of the vehicle based on current speed and acceleration
            precedingVeh = self.previousVehicle(vehicle) #I get the previous vehicle
            nextSem = self.getNextSemaphore(vehicle.getPosition()) #I get the next semaphore
            nextSemPos = self.getSemaphorePosition(nextSem) if nextSem != None else -2 #I get the position of the semaphore
            redSemInFront = nextSem != None and nextSem.isRed(currentTime) and nextPos >= nextSemPos
            vehicleInFront = precedingVeh != None and nextPos > self.safetyDistanceFrom(precedingVeh)
            freeRoad = not redSemInFront and not vehicleInFront

            if vehicle.isStopped():
                if freeRoad: #if the road is free
                    vehicle.restart(timeStep)
                elif redSemInFront: #if the next semaphore is red
                    pass
                elif not precedingVeh.isStopped(): #if there is a vehicle in front and it's moving
                    vehicle.followVehicle(precedingVeh,self.vehicleDistance) #follow the vehicle in front
            else: #if the vehicle is moving
                if freeRoad: #if the road is free
                    vehicle.move(timeStep)
                elif redSemInFront and vehicleInFront: #if the next semaphore is red and there is a vehicle in front
                    if nextSemPos < self.safetyDistanceFrom(precedingVeh): #if the red semaphore is closer
                        vehicle.stopAtSemaphore(nextSemPos) #stop at the semaphore
                    else: #if the vehicle in front is closer
                        vehicle.followVehicle(precedingVeh,self.vehicleDistance) #follow the vehicle in front
                elif redSemInFront: #if the next semaphore is red but there is no vehicle in front
                    vehicle.stopAtSemaphore(nextSemPos)
                elif vehicleInFront: #if there is a vehicle in front
                    vehicle.followVehicle(precedingVeh,self.vehicleDistance)
    
            ExceedingDistance = vehicle.getPosition() - self.length
            if ExceedingDistance > 0: #if the vehicle reach the end of the road
                self.endOfRoadHandler(vehicle, ExceedingDistance, currentTime, timeStep)
            return True
        return False
    
    def endOfRoadHandler(self, vehicle, ExceedingDistance, currentTime, timeStep = 1):
        if ExceedingDistance > 0:
            self.removeVehicle(vehicle)
            print("Car %d reached the end of the road" % vehicle.id)
            #TODO: implement junctions, call the junction method to handle the vehicle

    def moveVehicles(self, time, timeStep = 1):
        tmp = self.vehicles[:] #I iterate over a copy of the list
        for vehicle in tmp:
            self.moveVehicle(vehicle, time, timeStep)
    
    def limitSpeed(self, vehicle):
        if vehicle.getSpeed() > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def previousVehicle(self, vehicle): #I get the previous vehicle of the current vehicle, Vehicles must be ordered by position
        for i in range(len(self.vehicles)):
            if self.vehicles[i] == vehicle:
                if i > 0:
                    return self.vehicles[i-1]
                return None
        return None
    
    def safetyDistanceFrom(self, vehicle):
        return vehicle.position - self.vehicleDistance - vehicle.length

    def removeVehicle(self, vehicle):
        self.vehicles.remove(vehicle)

    def vehicleDensity(self):
        return len(self.vehicles) / self.length
    
    def vehiclesAt(self, start, end):
        vehicles = []
        for vehicle in self.vehicles:
            if vehicle.position > start and vehicle.position <= end:
                vehicles.append(vehicle)
        return vehicles
    
    def getNextSemaphore(self, position):
        sem = None
        for semaphore in self.semaphores: # If there are multiple semaphores, they must be ordered by position
            if semaphore.position >= position:
                return semaphore
            if semaphore.position == -1:
                sem = semaphore
        return sem
    
    def getSemaphorePosition(self, semaphore):
        if semaphore in self.semaphores:
            return semaphore.position if semaphore.position != -1 else self.length #if the semaphore is at the end of the road, I return the length of the road

class Semaphore:
    def __init__(self, greenTime, redTime, position = -1, yellowTime = 0, startTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.position = position #position of the semaphore on the road, -1 = end of the road, 0 = start of the road
        self.yellowTime = yellowTime
        self.startTime = startTime
        self.totalCycleTime = self.greenTime + self.redTime + self.yellowTime

    def getState(self, currentTime):
        if currentTime >= self.startTime:
            timeInCycle = (currentTime - self.startTime) % self.totalCycleTime
            if timeInCycle < self.greenTime:
                return "green"
            elif timeInCycle < self.greenTime + self.yellowTime:
                return "yellow"
            else:
                return "red"
        return "red"
    
    def isGreen(self, currentTime):
        return self.getState(currentTime) == "green"
    
    def isRed(self, currentTime):
        return self.getState(currentTime) == "red"
    
    def isYellow(self, currentTime):
        return self.getState(currentTime) == "yellow"
    
    def isAtEnd(self):
        return self.position == -1


#class Junction:

# carreggiata, è composta da n corsie
#class Roadway:



