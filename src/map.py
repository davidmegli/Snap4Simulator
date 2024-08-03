"""
@file    map.py
@author  David Megli

Description:
This file contains the classes that represent the map of the simulation.
The map is composed of roads, semaphores and junctions.
Roads have length and speed limit properties. They handle all the vehicles that are on them, stored in a list, throught the moveVehicle method.
A Road can contain a Semaphore, in the moveVehicles is checked the presence of red semaphores and vehicles in front of the current vehicle.
A Road can also contain a Junction, that can be a Bifurcation, NFurcation, Merge or Intersection, and handle the vehicles that reach it and the subsequent roads.
Bifurcation = 1 incoming road, 2 outgoing roads
NFurcation = 1 incoming road, n outgoing roads
Merge = 2 incoming roads, 1 outgoing road
Intersection = n incoming roads, n outgoing roads
Junctions have a handleVehicle method that is called when a vehicle reaches the junction.
"""
import random

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

class Shape:
    def __init__(self, coordinates: list[Coordinates] = None):
        self.coordinates = coordinates if coordinates else []
    
    def addCoordinate(self, coordinate):
        self.coordinates.append(coordinate)
    
    def getCoordinates(self):
        return self.coordinates
    
    def calculateCoordinatesOnShape(self, position): #returns the coordinates of the shape at the given position
        if len(self.coordinates) <= 1:
            return None
        # for each couple of coordinates
        # if the position exceeds the segment length I calculate the difference and go to next cycle
        # otherwise I calculate the position of the point in the segment between the two points
        for i in range(1, len(self.coordinates)):
            x1 = self.coordinates[i-1].getX()
            y1 = self.coordinates[i-1].getY()
            x2 = self.coordinates[i].getX()
            y2 = self.coordinates[i].getY()
            length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            if position <= length:
                x = x1 + (x2 - x1) * position / length
                y = y1 + (y2 - y1) * position / length
                return Coordinates(x, y)
            position -= length
        return None
    
    @staticmethod
    def getShapeByCoordinates(coordinates):
        shape = Shape()
        for coordinate in coordinates:
            shape.addCoordinate(coordinate)
        return shape

class Lane:
    def __init__(self, vehicles = None):
        self.vehicles = vehicles if vehicles else []

    def append(self, vehicle):
        self.vehicles.append(vehicle)
                             
    def remove(self, vehicle):
        self.vehicles.remove(vehicle)

    def getVehicles(self):
        return self.vehicles
    
    def getVehicle(self, index):
        return self.vehicles[index]
    
    def getVehicleCount(self):
        return len(self.vehicles)


#TODO: I must implement roadway/multilane with polimorphism, so I can keep calling the same methods in junctions
#the multilane will handle its lanes and call the lane methods. I must handle multilane going into junctions and merging into a single lane
#the junction must handle all the lanes of a multilane as different lanes
class Road:
    SAFETY_DISTANCE_TO_INTERSECTION = 10 #distance before the intersection where the vehicle is considered to be at the intersection and the next vehicle is not allowed to enter
    SAFETY_DISTANCE_AFTER_INTERSECTION = 5 #distance after the intersection where the vehicle is considered to have passed it and the next vehicle is allowed to enter
    BRAKING_DISTANCE  = 20 #distance from stop/semaphore before the vehicle starts braking
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0, shape: Shape = None):
        self.id = id
        self.length = length
        self.lanes: list[Lane] = [Lane()]
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.semaphores = semaphores if semaphores else []  # list of semaphores on the road
        self.startJunction: Junction = startJunction
        self.endJunction: Junction = endJunction
        self.priority = priority
        if shape is None:
            self.Shape = Shape.getShapeByCoordinates([Coordinates(0,0), Coordinates(self.length,0)])
            self.hasDefaultShape = True
        else:
            self.Shape = shape
            self.hasDefaultShape = False
        #FIXME: priority should not be assigned to the lane, but to the lane reference in the junction, because the lane can be used in multiple junctions and have different priorities
#FIXME: vehicles are added through addVehicle, then moveVehicles is called, so the vehicles instead of spawning at position 0 spawn at speed * timeStep position
#one possible solution is to not call moveVehicles in the first cycle
    def addVehicle(self, vehicle, currentTime, position = 0): #add vehicle to the road and returns the position of the vehicle
        # I check if there is a vehicle too close
        self.resetVehiclePosition(vehicle) #vehicle's position represents the position on the road, so I reset it to 0 in case it's coming from another road
        for i in range(len(self.lanes)):
            pos = self.addVehicleToLane(vehicle, currentTime, position, i)
            if pos >= 0:
                return pos
        return pos
    
    def setShape(self, shape: Shape):
        self.Shape = shape
        self.hasDefaultShape = False

    def addVehicleToLane(self, vehicle, currentTime, position, laneIndex):
        precedingVehicle = self.precedingVehicle(vehicle, laneIndex)
        hasPrecedingVehicle = precedingVehicle is not None
        firstSem = self.getFirstSemaphore()
        if hasPrecedingVehicle:
            precedingVehiclePosition = precedingVehicle.getPosition()
            safetyPosition = self.safetyPositionFrom(precedingVehicle)
            if precedingVehiclePosition < 0:
                position = safetyPosition
                if not vehicle.wasJustCreated():
                    return position
            if safetyPosition <= 0:
                position = safetyPosition
                if not vehicle.wasJustCreated():
                    return position
                vehicle.stopAtVehicle(0) #solve increasing negative position problem
            else:
                if position > safetyPosition:
                    vehicle.followVehicle(precedingVehicle,self.vehicleDistance)
                else:
                    vehicle.setPosition(position)
            self.limitSpeed(vehicle)
        elif firstSem != None and firstSem.isRed(currentTime) and position >= firstSem.position:
            vehicle.stopAtSemaphore(firstSem.position)
        else:
            vehicle.setPosition(position)
            self.limitSpeed(vehicle)
        self.appendVehicle(vehicle, laneIndex)
        return position

    def tryAddVehicle(self, vehicle, currentTime, position = 0): #only adds the vehicle if there is enough space, returns the position of the vehicle
        pos = self.addVehicle(vehicle, currentTime, position)
        if pos < 0:
            self.removeVehicle(vehicle)
        return pos

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
        if vehicle.lastUpdate == currentTime and not vehicle.wasJustCreated():
            return False
        if not self.hasVehicle(vehicle): #no vehicle no party
            return False
        laneIndex = self.getLaneWhereVehicleIs(vehicle)
        vehicles = self.getVehiclesInLane(laneIndex)
        nextPos = vehicle.calculatePosition(timeStep) #I get the future position of the vehicle based on current speed and acceleration
        precedingVehicle = self.precedingVehicle(vehicle) #I get the previous vehicle
        hasPrecedingVehicle = precedingVehicle is not None
        isPrecedingVehicleStopped = precedingVehicle.isStopped() if hasPrecedingVehicle else False
        nextSem = self.getNextSemaphore(vehicle.getPosition()) #I get the next semaphore
        nextSemPos = self.getSemaphorePosition(nextSem) if nextSem != None else -2 #I get the position of the semaphore
        IsNextSemRed = nextSem is not None and nextSem.isRed(currentTime)
        hasCloseRedSem = IsNextSemRed and nextPos >= nextSemPos
        safetyPositionFromPrecedingVehicle = self.safetyPositionFrom(precedingVehicle) if hasPrecedingVehicle else 0
        hasClosePrecVehicle = precedingVehicle is not None and nextPos > safetyPositionFromPrecedingVehicle
        hasNoCloseVehiclesOrRedSemaphores = not hasCloseRedSem and not hasClosePrecVehicle
        if vehicle.id == 134:
            print("Time: %d, Vehicle 134: pos: %d, speed: %d, acc: %d, lane: %d, nextPos: %d, safetyPos: %d, hasPrec: %s, isPrecStopped: %s, hasClosePrec: %s, hasCloseRedSem: %s, hasNoClose: %s" % (currentTime, vehicle.position, vehicle.speed, vehicle.acceleration, laneIndex, nextPos, safetyPositionFromPrecedingVehicle, hasPrecedingVehicle, isPrecedingVehicleStopped, hasClosePrecVehicle, hasCloseRedSem, hasNoCloseVehiclesOrRedSemaphores))
        if not vehicle.isGivingWay(): #if the vehicle is not giving way
            if vehicle.isStopped():
                if hasNoCloseVehiclesOrRedSemaphores: #if the lane is free
                    if safetyPositionFromPrecedingVehicle < 0:
                        vehicle.stopAtVehicle(0)
                    else:
                        self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=False)
                elif hasCloseRedSem: #if the next semaphore is red
                    pass #wait
                elif hasPrecedingVehicle and not isPrecedingVehicleStopped: #if there is a vehicle in front and it's moving
                    if safetyPositionFromPrecedingVehicle >= 0:
                        self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=False)
            else: #if the vehicle is moving
                if hasNoCloseVehiclesOrRedSemaphores: #if the lane is free
                    #I check if there is a vehicle in front or a red semaphore at breaking distance
                    posOfNextStoppedVehicle = safetyPositionFromPrecedingVehicle if isPrecedingVehicleStopped else 9999999
                    posOfNextRedSemaphore = nextSemPos if IsNextSemRed else 9999999
                    minPos = min(posOfNextStoppedVehicle, posOfNextRedSemaphore)
                    if minPos < vehicle.getPosition() + self.BRAKING_DISTANCE: #if there is a vehicle or a red semaphore at breaking distance
                        vehicle.brakeToStopAt(minPos)
                    self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=True)
                elif hasCloseRedSem and hasClosePrecVehicle: #if the next semaphore is red and there is a vehicle in front
                    if nextSemPos < safetyPositionFromPrecedingVehicle: #if the red semaphore is closer
                        vehicle.stopAtSemaphore(nextSemPos) #stop at the semaphore
                    else: #if the vehicle in front is closer. Note: I don't make the vehicle surpasse the other one, since there's a close red semaphore
                        vehicle.followVehicle(precedingVehicle,self.vehicleDistance) #follow the vehicle in front
                elif hasCloseRedSem: #if the next semaphore is red but there is no vehicle in front
                    vehicle.stopAtSemaphore(nextSemPos)
                elif hasClosePrecVehicle: #if there is a vehicle in front but the semaphore is green
                    self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=True)
    
            ExceedingDistance = vehicle.getPosition() - self.length
            if ExceedingDistance > 0: #if the vehicle reach the end of the lane
                self.endOfRoadHandler(vehicle, ExceedingDistance, currentTime, timeStep)
                '''newPos = vehicle.slowDown()
                if newPos > self.length:
                    self.endOfRoadHandler(vehicle, ExceedingDistance, currentTime, timeStep)'''

        else: #if the vehicle is giving way
            oldPosition = vehicle.getPosition()
            vehicle.restart(self.speedLimit, timeStep)
            ExceedingDistance = vehicle.getPosition() - self.length
            self.endOfRoadHandler(vehicle, ExceedingDistance, currentTime, timeStep) #endOfRoadHandler will decide if the vehicle can go or has to keep waiting
            vehicles = self.getAllVehicles()
            if vehicle in vehicles and vehicle.isGivingWay():
                vehicle.setPosition(oldPosition) #if the vehicle has to keep waiting, I reset its position to the previous one
        vehicle.update(currentTime, self)
        return True
    
    def endOfRoadHandler(self, vehicle, ExceedingDistance, currentTime, timeStep = 1):
        if ExceedingDistance > 0:
            if self.endJunction != None: #if there is a junction at the end of the road
                self.endJunction.handleVehicle(vehicle, ExceedingDistance,currentTime, timeStep)
            else: # if there is no junction at the end of the road I assume the road is a dead end, so the vehicle is removed
                self.removeVehicle(vehicle)
                vehicle.setArrivalTime(currentTime)
                vehicle.update(currentTime, self)

    def moveAndOvertakeIfPossible(self, vehicle, precedingVehicle, laneIndex, currentTime, timeStep = 1, wasMoving = True):
        hasPrecedingVehicle = precedingVehicle is not None
        safetyPositionFromPrecedingVehicle = self.safetyPositionFrom(precedingVehicle) if hasPrecedingVehicle else 0
        if currentTime == 148 and vehicle.id == 134: #debug
            print("moveAndOvertakeIfPossible: Time: %d, Vehicle 134: pos: %d, speed: %d, acc: %d, lane: %d, wasMoving: %s" % (currentTime, vehicle.position, vehicle.speed, vehicle.acceleration, laneIndex, wasMoving))
        if wasMoving:
            newPosition = vehicle.move(self.speedLimit, timeStep)
        else:
            newPosition = vehicle.restart(self.speedLimit, timeStep, precedingVehicle)
        if hasPrecedingVehicle and newPosition > safetyPositionFromPrecedingVehicle:
            nextLaneIndex = laneIndex + 1
            nextLaneIsFree = self.isLaneFreeAtPosition(newPosition, nextLaneIndex)
            if nextLaneIsFree:
                vehicle.setLane(nextLaneIndex)
            elif precedingVehicle.isStopped():
                vehicle.stopAtVehicle(safetyPositionFromPrecedingVehicle)
            else:
                vehicle.followVehicle(precedingVehicle,self.vehicleDistance)
        self.limitSpeed(vehicle)

    def isLaneFreeAtPosition(self, position, laneIndex):
        if len(self.lanes) <= 0 or laneIndex >= len(self.lanes):
            return False
        vehicles = self.getVehiclesInLane(laneIndex)
        if vehicles is None:
            return True
        precedingVehicle = self.getNextVehicleAtPosition(position, laneIndex)
        return precedingVehicle is None or self.safetyPositionFrom(precedingVehicle) > position


    def getNextVehicleAtPosition(self, position, laneIndex):
        vehicles = self.getVehiclesInLane(laneIndex)
        #return the vehicle with minimum position greater than the given position
        if vehicles == None:
            return None
        nextVehicle = vehicles[0]
        minPosition = nextVehicle.getPosition()
        for vehicle in vehicles:
            if vehicle.getPosition() > position and vehicle.getPosition() < minPosition:
                nextVehicle = vehicle
                minPosition = vehicle.getPosition()
        return nextVehicle
    
    def getLastVehicle(self):
        vehicles = self.getAllVehicles().sort(key=lambda vehicle: vehicle.position, reverse=False)
        return vehicles[0] if vehicles else None

    def hasOutgoingVehicles(self, timeStep = 1):
        vehicles = self.getAllVehicles()
        for vehicle in vehicles:
            position = vehicle.calculatePosition(timeStep)
            positionToIntersection = self.length - self.SAFETY_DISTANCE_TO_INTERSECTION
            if position > self.length:
                return True
            elif position > positionToIntersection:
                if random.uniform(0,1) < (position - positionToIntersection) / self.SAFETY_DISTANCE_TO_INTERSECTION:
                    return True
        return False
    
    def moveVehicles(self, time, timeStep = 1):
        tmp = self.getAllVehicles()#.copy()
        for vehicle in tmp:
            #print("Moving vehicle %d" % vehicle.id)
            self.moveVehicle(vehicle, time, timeStep)

    def waitForNextRoad(self, vehicle, posToWaitAt):
        followingVehicle = self.followingVehicle(vehicle)
        safePos = self.safetyPositionFromFollowingVehicleOf(followingVehicle) if followingVehicle != None else 0
        if posToWaitAt >= safePos:
            vehicle.giveWay(posToWaitAt)
        elif safePos < self.length:
            vehicle.giveWay(safePos)
        else:
            vehicle.giveWay(self.length)

    def giveWay(self, vehicle): #check if the vehicle stops everytime without checking if the road is free
        vehicle.giveWay(self.length)
    
    def limitSpeed(self, vehicle):
        if vehicle.getSpeed() > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def precedingVehicle(self, vehicle, laneIndex = 0): #I get the preceding vehicle of the current vehicle, Vehicles must be ordered by position
        vehicles = self.getVehiclesInLane(laneIndex)
        if vehicles is None or len(vehicles) <= 0: #no vehicles
            return None
        if len(vehicles) == 1: #one vehicle
            if vehicles[0] == vehicle:
                return None
            return vehicles[0]
        for i in range(len(vehicles)):
            if vehicles[i] == vehicle:
                if i >= 1:
                    return vehicles[i-1]
                return None
        #if there are more than 1 vehicles and the vehicle is not in the list, I return the first vehicle
        return vehicles[-1]
        return None

    def followingVehicle(self, vehicle): #I get the following vehicle of the current vehicle, Vehicles must be ordered by position
        vehicles = self.getAllVehicles()
        for i in range(len(vehicles)):
            if vehicles[i] == vehicle:
                if i < len(vehicles) - 1:
                    return vehicles[i+1]
                return None
        return None
    
    def safetyPositionFrom(self, vehicle):
        return vehicle.position - self.vehicleDistance - vehicle.length
    
    def safetyPositionFromFollowingVehicleOf(self, vehicle):
        return vehicle.position + self.vehicleDistance + vehicle.length

    def removeVehicle(self, vehicle):
        for i in range(len(self.lanes)):
            if self.hasVehicleInLane(vehicle, i):
                self.lanes[i].remove(vehicle)
                return True
        return False

    def vehicleDensity(self):
        vehicles = self.getAllVehicles()
        return len(vehicles) / self.length
    
    def vehiclesAt(self, start, end):
        vehiclesAt = []
        vehicles = self.getAllVehicles()
        for vehicle in vehicles:
            if vehicle.position > start and vehicle.position <= end:
                vehiclesAt.append(vehicle)
        return vehiclesAt
    
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
        endSemaphore = self.getEndSemaphore()
        if endSemaphore is not None:
            return endSemaphore.isGreen(currentTime)
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
    
    def getNumberOfLanes(self):
        return len(self.lanes)
        
    def resetVehiclePosition(self, vehicle):
        vehicle.setPosition(0)

    def hasVehicleInLane(self, vehicle, laneIndex):
        if (vehicles := self.getVehiclesInLane(laneIndex)) is None:
            return False
        return vehicle.getLane() == laneIndex and vehicle in vehicles
    
    def hasVehicle(self, vehicle):
        vehicles = self.getAllVehicles()
        for v in vehicles:
            if v == vehicle:
                return True
        return False
    
    def getVehiclesInLane(self, laneIndex):
        if laneIndex >= len(self.lanes):
            return None
        return self.lanes[laneIndex].getVehicles()#.sort(key=lambda vehicle: vehicle.position, reverse=False)
    
    def getAllVehicles(self):
        allVehicles = []
        for index in range(len(self.lanes)):
            allVehicles += self.lanes[index].getVehicles()
        return allVehicles
    
    def appendVehicle(self, vehicle, laneIndex = 0):
        #self.vehicles.append(vehicle)
        self.lanes[laneIndex].append(vehicle)

    def getLaneWhereVehicleIs(self, vehicle):
        return vehicle.getLane()
    
    def getCoordinatesByPosition(self, position):
        return self.Shape.calculateCoordinatesOnShape(position)
    
class Semaphore:
    STATE_GREEN = "green"
    STATE_YELLOW = "yellow"
    STATE_RED = "red"
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
                return self.STATE_GREEN
            elif timeInCycle < self.greenTime + self.yellowTime:
                return self.STATE_YELLOW
            else:
                return self.STATE_RED
        return self.STATE_RED
    
    def isGreen(self, currentTime):
        return self.getState(currentTime) == self.STATE_GREEN
    
    def isRed(self, currentTime):
        return self.getState(currentTime) == self.STATE_RED
    
    def isYellow(self, currentTime):
        return self.getState(currentTime) == self.STATE_YELLOW
    
    def isAtEnd(self):
        return self.position == -1


class Junction:
    #TODO: handleVehicle virtual function to override. Add other types of junctions, implement the handleVehicle method foreach type of junction
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        pass

class Bifurcation(Junction):
    #Deprecated: NFurcation can be used instead of Bifurcation
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
            print("Vehicle %d is at the bifurcation" % vehicle.id)
            nextRoad = self.outgoingRoad1 if random.uniform(0,1) < self.flux1 else self.outgoingRoad2
            print("Trying to add vehicle %d to road %d at position %f" % (vehicle.id, nextRoad.id, position))
            pos = nextRoad.tryAddVehicle(vehicle, currentTime, position)
            if pos < 0: #if the vehicle cannot be added to the next road
                print("Vehicle %d cannot be added to road %d" % (vehicle.id, nextRoad.id))
                pos += self.incomingRoad.length
                self.incomingRoad.waitForNextRoad(vehicle,pos)
            else:
                print("Removing vehicle %d from road %d" % (vehicle.id, self.incomingRoad.id))
                self.incomingRoad.removeVehicle(vehicle)

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

    def getNextRoad(self):
        randomValue = random.uniform(0,1)
        chosenRoad = 0
        for i in range(len(self.fluxes)):
            if randomValue < self.fluxes[i]:
                chosenRoad = i
                break
            randomValue -= self.fluxes[i]
        nextRoad = self.outgoingRoads[chosenRoad]
        return nextRoad
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if self.incomingRoad.hasVehicle(vehicle):
            print("Vehicle %d is at the n-furcation" % vehicle.id)
            if self.outgoingRoads == None or self.fluxes == None:
                if self.incomingRoad != None:
                    self.incomingRoad.removeVehicle(vehicle)
                print("Error: n-furcation has no outgoing roads")
                return
            #fluxes represent the probability of going to each road, given randomValue I choose the next road
            nextRoad = self.getNextRoad()
            print("NFurcation: Vehicle %d is going from road %d to road %d" % (vehicle.id, self.incomingRoad.id, nextRoad.id))
            pos = nextRoad.tryAddVehicle(vehicle, currentTime, position)
            if pos < 0: #if the vehicle cannot be added to the next road
                pos += self.incomingRoad.length
                self.incomingRoad.waitForNextRoad(vehicle,pos)
            else:
                self.incomingRoad.removeVehicle(vehicle)

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
        if self.incomingRoad1.hasVehicle(vehicle) or self.incomingRoad2.hasVehicle(vehicle):
            fromRoad = self.incomingRoad1 if self.incomingRoad1.hasVehicle(vehicle) else self.incomingRoad2 #I get the road from which the vehicle comes

            if fromRoad == self.priorityRoad or not self.priorityRoad.hasOutgoingVehicles(timeStep): #if the vehicle comes from the priority road or the priority road is free
                pos = self.outgoingRoad.tryAddVehicle(vehicle, currentTime, position)
                if pos < 0: #if the vehicle cannot be added to the next road
                    pos += fromRoad.length
                    fromRoad.waitForNextRoad(vehicle,pos)
                else:
                    print("Merge: Vehicle %d is going from road %d to road %d" % (vehicle.id, fromRoad.id, self.outgoingRoad.id))
                    fromRoad.removeVehicle(vehicle)
            else:
                fromRoad.giveWay(vehicle)

class Intersection(Junction): #n incoming roads, n outgoing roads
    #TODO: handle a list of fluxes for each incoming road
    def __init__(self, id, incomingRoads = [], outgoingRoads = [], outgoingFluxes = []):
        self.id = id
        self.incomingRoads = incomingRoads
        for road in incomingRoads:
            road.addEndJunction(self)
        self.outgoingRoads = outgoingRoads
        for road in outgoingRoads:
            road.addStartJunction(self)
        self.outgoingRoadsFluxes = outgoingFluxes if outgoingFluxes else [1/len(outgoingRoads) for road in outgoingRoads]

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
            if road.hasVehicle(vehicle):
                return road
        return None

    def getPriorityRoad(self): #returns the road with the highest priority that has green light
        if self.incomingRoads == None:
            print("Error: intersection has no incoming roads")
            return None
        priorityRoad = None
        #TODO: order roads by priority in the Junction and extract the first one with green light
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
        randomValue = random.uniform(0,1)
        chosenRoad = 0
        for i in range(len(self.outgoingRoadsFluxes)):
            if randomValue < self.outgoingRoadsFluxes[i]:
                chosenRoad = i
                break
            randomValue -= self.outgoingRoadsFluxes[i]
        nextRoad = self.outgoingRoads[chosenRoad]
        return nextRoad
    
    def canGo(self, road, currentTime, position):
        #I take every road with higher priority (lowest number) that has Green and has outgoing vehicles, if there is no such road I return True
        if self.incomingRoads == None:
            return False
        for r in self.incomingRoads:
            if r.getPriority() < road.getPriority() and r.isGreen(currentTime) and r.hasOutgoingVehicles():
                return False
        #ritorno False anche se nella road dove deve immettersi il veicolo ci sono veicoli all'inizio della strada
        lastVehInNextRoad = road.getLastVehicle()
        safePos = road.safetyPositionFrom(lastVehInNextRoad) - Road.SAFETY_DISTANCE_AFTER_INTERSECTION if lastVehInNextRoad is not None else 1000000
        if position > safePos:
            return False
        return True
    
    def outgoingRoadsOrderedByPriority(self):
        '''#this function is O(n^2), consider using a priority queue
        roads = self.outgoingRoads
        orderedRoads = []
        #i append first the road with the highest priority, then the road with the second highest priority, and so on
        for i in range(len(self.outgoingRoads)):
            maxPriority = roads[0].getPriority()
            maxPriorityRoad = roads[0]
            for road in roads:
                if road.getPriority() < maxPriority:
                    maxPriority = road.getPriority()
                    maxPriorityRoad = road
            orderedRoads.append(maxPriorityRoad)
            roads.remove(maxPriorityRoad)
        return orderedRoads'''
        return sorted(self.outgoingRoads, key=lambda x: x.priority, reverse=False)
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if self.incomingRoads == None:
            print("Error: intersection has no incoming roads")
            return
        incomingRoad = self.incomingRoad(vehicle)
        if incomingRoad != None:
            if self.outgoingRoads == None or self.outgoingRoadsFluxes == None:
                incomingRoad.removeVehicle(vehicle)
                vehicle.setArrivalTime(currentTime)
                print("Error: intersection has no outgoing roads, removing vehicle %d" % vehicle.id)
                return
            #fluxes represent the probability of going to each road, given randomValue I choose the next road
            nextRoad = self.getNextRoad()
            #priorityRoad = self.getPriorityRoad()

            canGo = self.canGo(incomingRoad,currentTime,position)
            if canGo: #if the vehicle can go (i.e there is no vehicle with higher priority that has green light and outgoing vehicles)
                pos = nextRoad.tryAddVehicle(vehicle, currentTime, position) #retuns the new position, <0 if the vehicle cannot be added
                if pos < 0: #if the vehicle cannot be added to the next road
                    pos += incomingRoad.length #I calculate the position where to wait in the incoming road
                    incomingRoad.waitForNextRoad(vehicle, pos) #I make the vehicle wait in the incoming road
                else:
                    incomingRoad.removeVehicle(vehicle)
            else:
                incomingRoad.giveWay(vehicle)

#TODO: add intersection with semaphores, add priority to lanes, add priority to vehicles, add vehicle types, add vehicle types to lanes, add vehicle types to junctions
#TODO: Factory classes with functions to handle initialization of networks

#TODO: implementa strada a doppia carreggiata: Roadway gestisce una strada a 2 carreggiata, Road diventa la carreggiata: Road > Roadway > Lane
#class Roadway:
#TODO: Network class to handle multiple lanes and junctions (maybe all map?), and Simulator class to handle the simulation, and update every Lane etc...
#Simulation class will also handle the history of the entirye Network (or Map), and have a saveHistory function to save the entire history of the map in a json file


