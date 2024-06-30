"""
@file    map.py
@author  David Megli
"""
import random

class Road:
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0):
        self.id = id
        self.length = length
        self.vehicles = [] #list of vehicles on the road
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.semaphores = semaphores if semaphores else []  # list of semaphores on the road
        self.startJunction = startJunction
        self.endJunction = endJunction
        self.priority = priority

    def addVehicle(self, vehicle, currentTime, position = 0): #add vehicle to the road
        # I check if there is a vehicle too close
        self.resetVehiclePosition(vehicle) #vehicle's position represents the position on the road, so I reset it to 0
        precedingVehicle = self.precedingVehicle(vehicle)
        firstSem = self.getFirstSemaphore()
        if precedingVehicle != None:
            safetyPosition = self.safetyDistanceFrom(precedingVehicle)
            if safetyPosition <= 0:
                vehicle.stopAtVehicle(safetyPosition)
            else:
                self.limitSpeed(vehicle)
        elif firstSem != None and firstSem.isRed(currentTime) and position >= firstSem.position:
            vehicle.stopAtSemaphore(firstSem.position)
        else:
            self.limitSpeed(vehicle)
        self.vehicles.append(vehicle)

    def addSemaphore(self, position, greenTime, redTime, yellowTime = 0, startTime = 0): #MUST add semaphores in order of position
        self.semaphores.append(Semaphore(greenTime, redTime, position, yellowTime, startTime))

    def addSemaphore(self, semaphore): #MUST add semaphores in order of position
        self.semaphores.append(semaphore)

    def setSemaphoreAtEnd(self, semaphore):
        self.removeSemaphoreAtEnd()
        self.addSemaphoreAtEnd(semaphore)

    def addSemaphoreAtEnd(self, semaphore):
        self.semaphores.append(semaphore)
        semaphore.position = -1
    
    def addSemaphoreAtEnd(self, greenTime, redTime, yellowTime = 0, startTime = 0):
        self.semaphores.append(Semaphore(greenTime, redTime, -1, yellowTime, startTime))

    def addStartJunction(self, junction):
        self.startJunction = junction

    def addEndJunction(self, junction):
        self.endJunction = junction

    def moveVehicle(self, vehicle, currentTime, timeStep = 1):
        # If the vehicle is in the road, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        if vehicle in self.vehicles: #if the vehicle is on the road
            currentPos = vehicle.getPosition()
            nextPos = vehicle.calculatePosition(timeStep) #I get the future position of the vehicle based on current speed and acceleration
            precedingVeh = self.precedingVehicle(vehicle) #I get the previous vehicle
            nextSem = self.getNextSemaphore(vehicle.getPosition()) #I get the next semaphore
            nextSemPos = self.getSemaphorePosition(nextSem) if nextSem != None else -2 #I get the position of the semaphore
            redSemInFront = nextSem != None and nextSem.isRed(currentTime) and nextPos >= nextSemPos
            vehicleInFront = precedingVeh != None and nextPos > self.safetyDistanceFrom(precedingVeh)
            freeRoad = not redSemInFront and not vehicleInFront

            if not vehicle.isGivingWay(): #if the vehicle is not giving way
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

            else: #if the vehicle is giving way
                vehicle.restart(timeStep) #I try to restart the vehicle
                ExceedingDistance = vehicle.getPosition() - self.length #I know the vehicle is at the end of the road
                self.endOfRoadHandler(vehicle, ExceedingDistance, currentTime, timeStep) #endOfRoadHandler will decide if the vehicle can go or has to keep waiting

            return True
        return False
    
    def endOfRoadHandler(self, vehicle, ExceedingDistance, currentTime, timeStep = 1):
        if ExceedingDistance > 0:
            if self.endJunction != None: #if there is a junction at the end of the road
                self.endJunction.handleVehicle(vehicle, ExceedingDistance,currentTime, timeStep)
                print("Car %d reached the end of road %d" % (vehicle.id, self.id))

    def hasOutgoingVehicles(self, timeStep = 1):
        for vehicle in self.vehicles:
            if vehicle.calculatePosition(timeStep) > self.length:
                return True

    def moveVehicles(self, time, timeStep = 1):
        tmp = self.vehicles[:] #I iterate over a copy of the list
        for vehicle in tmp:
            print("Moving car %d" % vehicle.id)
            self.moveVehicle(vehicle, time, timeStep)

    def giveWay(self, vehicle): #check if the vehicle stops everytime without checking if the road is free
        vehicle.giveWay(self.length)
    
    def limitSpeed(self, vehicle):
        if vehicle.getSpeed() > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def precedingVehicle(self, vehicle): #I get the previous vehicle of the current vehicle, Vehicles must be ordered by position
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
    
    def getFirstSemaphore(self):
        return self.getNextSemaphore(0)

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
    
    def getEndSemaphore(self):
        for semaphore in self.semaphores:
            if semaphore.position == -1:
                return semaphore
        return None
        
    def isGreen(self, currentTime):
        LastSemaphore = self.getLastSemaphore()
        if LastSemaphore != None:
            return LastSemaphore.isGreen(currentTime)
        return True
        
    def removeSemaphore(self, semaphore):
        self.semaphores.remove(semaphore)
    
    def removeSemaphoreAtEnd(self):
        semaphores = self.semaphores
        for semaphore in semaphores:
            if semaphore.position == -1:
                self.semaphores.remove(semaphore)
                return semaphore
        
    def getPriority(self):
        return self.priority
        
    def resetVehiclePosition(self, vehicle):
        vehicle.setPosition(0)

class Semaphore:
    def __init__(self, greenTime, redTime, position = -1, yellowTime = 0, startTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.position = position #position of the semaphore on the road, -1 = end of the road, 0 = start of the road
        self.yellowTime = yellowTime
        self.startTime = startTime
        self.totalCycleTime = self.greenTime + self.redTime + self.yellowTime

    @staticmethod
    def createOppositeSemaphore(sem): #this function is used to create a semaphore for an X intersection
        #I create a semaphore with the same start time, yellow time and position, but with red = green and green = red - yellow
        newGreen = sem.redTime - sem.yellowTime
        newYellow = sem.yellowTime
        if newGreen <= 0:
            newGreen = sem.redTime
            newYellow = 0
        newRed = sem.greenTime
        return Semaphore(newGreen, newRed, sem.position, newYellow, sem.startTime)

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


class Junction:
    #TODO: handleVehicle virtual function to override. Add other types of junctions, implement the handleVehicle method foreach type of junction
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        pass

class Bifurcation(Junction): #I can use NFurcation instead of Bifurcation with 2 outgoing roads
    def __init__(self, id, incomingRoad, outgoingRoad1, outgoingRoad2, flux1):
        self.id = id
        self.incomingRoad = incomingRoad
        self.outgoingRoad1 = outgoingRoad1
        self.outgoingRoad2 = outgoingRoad2
        self.flux1 = flux1
        if incomingRoad != None:
            incomingRoad.addEndJunction(self)
        if outgoingRoad1 != None:
            outgoingRoad1.addStartJunction(self)
        if outgoingRoad2 != None:
            outgoingRoad2.addStartJunction(self)

    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingRoad.vehicles:
            print("Car %d is at the bifurcation" % vehicle.id)
            nextRoad = self.outgoingRoad1 if random.uniform(0,1) < self.flux1 else self.outgoingRoad2
            print("Removing car %d from road %d" % (vehicle.id, self.incomingRoad.id))
            self.incomingRoad.removeVehicle(vehicle)
            print("Adding car %d to road %d" % (vehicle.id, nextRoad.id))
            nextRoad.addVehicle(vehicle, currentTime, position)

class NFurcation(Junction): #1 incoming road, n outgoing roads
    def __init__(self, id, incomingRoad = None, outgoingRoads = [], fluxes = []):
        self.id = id
        self.incomingRoad = incomingRoad
        if incomingRoad != None:
            incomingRoad.addEndJunction(self)
        self.outgoingRoads = outgoingRoads
        if outgoingRoads != None:
            for road in outgoingRoads:
                road.addStartJunction(self)
        self.fluxes = fluxes

    def addOutgoingRoad(self, road, flux):
        self.outgoingRoads.append(road)
        self.fluxes.append(flux)
        road.addStartJunction(self)
    
    def addIncomingRoad(self, road):
        self.incomingRoad = road
        road.addEndJunction(self)

    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingRoad.vehicles:
            print("Car %d is at the n-furcation" % vehicle.id)
            if self.outgoingRoads == None or self.fluxes == None:
                if self.incomingRoad != None:
                    self.incomingRoad.removeVehicle(vehicle)
                print("Error: n-furcation has no outgoing roads")
                return
            randomValue = random.uniform(0,1)
            #fluxes represent the probability of going to each road, given randomValue I choose the next road
            chosenRoad = 0
            for i in range(len(self.fluxes)):
                if randomValue < self.fluxes[i]:
                    chosenRoad = i
                    break
                randomValue -= self.fluxes[i]
            nextRoad = self.outgoingRoads[chosenRoad]
            print("Removing car %d from road %d" % (vehicle.id, self.incomingRoad.id))
            self.incomingRoad.removeVehicle(vehicle)
            print("Adding car %d to road %d" % (vehicle.id, nextRoad.id))
            nextRoad.addVehicle(vehicle, currentTime, position)

class Merge(Junction): #2 incoming roads, 1 outgoing road
    def __init__(self, id, incomingRoad1, incomingRoad2, outgoingRoad):
        self.id = id
        self.incomingRoad1 = incomingRoad1
        self.incomingRoad2 = incomingRoad2
        self.outgoingRoad = outgoingRoad
        self.priorityRoad = self.priorityRoad()
        if incomingRoad1 != None:
            incomingRoad1.addEndJunction(self)
        if incomingRoad2 != None:
            incomingRoad2.addEndJunction(self)
        if outgoingRoad != None:
            outgoingRoad.addStartJunction(self)
        
    def priorityRoad(self):
        if self.incomingRoad1.getPriority() <= self.incomingRoad2.getPriority():
            return self.incomingRoad1
        return self.incomingRoad2

    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingRoad1.vehicles or vehicle in self.incomingRoad2.vehicles:
            fromRoad = self.incomingRoad1 if vehicle in self.incomingRoad1.vehicles else self.incomingRoad2 #I get the road from which the vehicle comes

            if fromRoad == self.priorityRoad or not self.priorityRoad.hasOutgoingVehicles(timeStep): #if the vehicle comes from the priority road or the priority road is free
                fromRoad.removeVehicle(vehicle)
                self.outgoingRoad.addVehicle(vehicle, currentTime, position)
            else:
                fromRoad.giveWay(vehicle)

class Intersection(Junction): #n incoming roads, n outgoing roads
    def __init__(self, id, incomingRoads = [], outgoingRoads = [], incomingRoadsFluxes = [], outgoingRoadsFluxes = []):
        self.id = id
        self.incomingRoads = incomingRoads
        self.outgoingRoads = outgoingRoads
        self.incomingRoadsFluxes = incomingRoadsFluxes
        self.outgoingRoadsFluxes = outgoingRoadsFluxes

    def addIncomingRoad(self, road, semaphore = None): #semaphores must be synchronized setting same start time and opposite green and red times
        self.incomingRoads.append(road)
        road.addEndJunction(self)
        if semaphore != None:
            road.addSemaphoreAtEnd(semaphore)
    
    def addOutgoingRoad(self, road, flux):
        self.outgoingRoads.append(road)
        self.outgoingRoadsFluxes.append(flux)
        road.addStartJunction(self)

    def incomingRoad(self, vehicle):
        for road in self.incomingRoads:
            if vehicle in road.vehicles:
                return road
        return None

    def getPriorityRoad(self):
        if self.incomingRoads == None:
            print("Error: intersection has no incoming roads")
            return None
        priorityRoad = None
        for road in self.incomingRoads: #get the first road that is not red
            if road.isGreen():
                priorityRoad = road
                break
        if priorityRoad == None:
            return None
        for road in self.incomingRoads:
            if road.getPriority() < priorityRoad.getPriority() and road.isGreen():
                priorityRoad = road
        return priorityRoad

    def getNextRoad(self):
        chosenRoad = 0
        for i in range(len(self.outgoingRoadsFluxes)):
            if randomValue < self.outgoingRoadsFluxes[i]:
                chosenRoad = i
                break
            randomValue -= self.outgoingRoadsFluxes[i]
        nextRoad = self.outgoingRoads[chosenRoad]
        return nextRoad
    
    def canGo(self, road):
        #I take every road with highest priority (lowest number) that has Green and has outgoing vehicles, if there is no such road I return True
        if self.incomingRoads == None:
            return False
        for r in self.incomingRoads:
            if r.getPriority() < road.getPriority() and r.isGreen() and r.hasOutgoingVehicles():
                return False
        return True
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if self.incomingRoads == None:
            print("Error: intersection has no incoming roads")
            return
        incRoad = self.incomingRoad(vehicle)
        if incRoad != None:
            if self.outgoingRoads == None or self.outgoingRoadsFluxes == None:
                if incRoad != None:
                    incRoad.removeVehicle(vehicle)
                print("Error: intersection has no outgoing roads")
                return
            randomValue = random.uniform(0,1)
            #fluxes represent the probability of going to each road, given randomValue I choose the next road
            nextRoad = self.getNextRoad()
            priorityRoad = self.getPriorityRoad()
            canGo = self.canGo(incRoad)
            if canGo:
                nextRoad.addVehicle(vehicle, currentTime, position)
                incRoad.removeVehicle(vehicle)
            else:
                incRoad.giveWay(vehicle)


#TODO: add intersection with semaphores, add priority to roads, add priority to vehicles, add vehicle types, add vehicle types to roads, add vehicle types to junctions

#TODO: Factory classes with functions to handle initialization of networks

# carreggiata, è composta da n corsie
#class Roadway:



