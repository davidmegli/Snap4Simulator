"""
@file    map.py
@author  David Megli

Description:
This file contains the classes that represent the map of the simulation.
The map is composed of lanes, semaphores and junctions.
Lanes have length and speed limit properties. They handle all the vehicles that are on them, stored in a list, throught the moveVehicle method.
A Lane can contain a Semaphore, in the moveVehicles is checked the presence of red semaphores and vehicles in front of the current vehicle.
A Lane can also contain a Junction, that can be a Bifurcation, NFurcation, Merge or Intersection, and handle the vehicles that reach it and the subsequent lanes.
Bifurcation = 1 incoming lane, 2 outgoing lanes
NFurcation = 1 incoming lane, n outgoing lanes
Merge = 2 incoming lanes, 1 outgoing lane
Intersection = n incoming lanes, n outgoing lanes
Junctions have a handleVehicle method that is called when a vehicle reaches the junction.
"""
import random

class Road:
    def __init__(self, id, numLanes, laneLength, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0):
        self.id = id
        self.num_lanes = numLanes
        self.length = laneLength
        self.vehicle_distance = vehicleDistance
        self.speed_limit = speedLimit
        self.semaphores = semaphores if semaphores else []
        self.lanes = [Lane(self, i) for i in range(numLanes)]

    def addVehicle(self, vehicle, lane_index, current_time, position=0):
        if lane_index < 0 or lane_index >= self.num_lanes:
            raise ValueError("Invalid lane index")
        return self.lanes[lane_index].add_vehicle(vehicle, current_time, position)

    def moveVehicles(self, time, time_step=1):
        for lane in self.lanes:
            lane.move_vehicles(time, time_step)

    def getNextSemaphore(self, position):
        for semaphore in self.semaphores:
            if semaphore.position >= position:
                return semaphore
        return None

    def isGreen(self, current_time):
        last_semaphore = self.getNextSemaphore(self.length)
        if last_semaphore:
            return last_semaphore.is_green(current_time)
        return True


class Line: #TODO: use this class to handle the lines of a multilane
    #Step 1: replace vehicles list with a list of Line objects without changing the Lane methods (DONE)
    #Step 2: add multiple lines feature to Lane (altready added Lane attribute to Vehicle, use it to get and set the line of the vehicle, then use
    #the line as Line list index in Lane)
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
#the junction must handle all the lines of a multilane as different lanes
class Lane:
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0):
        self.id = id
        self.length = length
        self.line = [Line()] #TODO: add lane reference to vehicle, lane corresponds to the lane the vehicle is in, vehicles in lane x are in list x (list of lists?)
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.semaphores = semaphores if semaphores else []  # list of semaphores on the lane
        self.startJunction = startJunction
        self.endJunction = endJunction
        self.priority = priority
        #FIXME: priority should not be assigned to the lane, but to the lane reference in the junction, because the lane can be used in multiple junctions and have different priorities
#FIXME: vehicles are added through addVehicle, then moveVehicles is called, so the vehicles instead of spawning at position 0 spawn at speed * timeStep position
#one possible solution is to not call moveVehicles in the first cycle
    def addVehicle(self, vehicle, currentTime, position = 0): #add vehicle to the lane and returns the position of the vehicle
        # I check if there is a vehicle too close
        self.resetVehiclePosition(vehicle) #vehicle's position represents the position on the lane, so I reset it to 0 in case it's coming from another lane
        for i in range(len(self.line)):
            pos = self.addVehicleToLane(vehicle, currentTime, position, i)
            if pos >= 0:
                return pos
        return pos
    
    def addVehicleToLane(self, vehicle, currentTime, position, laneIndex):
        precedingVehicle = self.precedingVehicle(vehicle, laneIndex)
        firstSem = self.getFirstSemaphore()
        if precedingVehicle is not None:
            precedingVehiclePosition = precedingVehicle.getPosition()
            safetyPosition = self.safetyPositionFrom(precedingVehicle)
            if precedingVehiclePosition < 0:
                position = safetyPosition
            if safetyPosition <= 0:
                position = safetyPosition
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
        self.appendVehicle(vehicle)
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
        # If the vehicle is in the lane, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        if vehicle.lastUpdate == currentTime:
            return False
        if not self.hasVehicle(vehicle): #no vehicle no party
            return False
        laneIndex = self.getLaneWhereVehicleIs(vehicle)
        vehicles = self.getVehiclesInLane(laneIndex)
        nextPos = vehicle.calculatePosition(timeStep) #I get the future position of the vehicle based on current speed and acceleration
        precedingVehicle = self.precedingVehicle(vehicle) #I get the previous vehicle
        hasPrecedingVehicle = precedingVehicle is not None
        nextSemaphore = self.getNextSemaphore(vehicle.getPosition()) #I get the next semaphore
        nextSemPos = self.getSemaphorePosition(nextSemaphore) if nextSemaphore != None else -2 #I get the position of the semaphore
        redSemInFront = nextSemaphore is not None and nextSemaphore.isRed(currentTime) and nextPos >= nextSemPos
        safetyPositionFromPrecedingVehicle = self.safetyPositionFrom(precedingVehicle) if hasPrecedingVehicle else 0
        vehicleInFront = precedingVehicle is not None and nextPos > safetyPositionFromPrecedingVehicle
        noCloseVehiclesOrSemaphores = not redSemInFront and not vehicleInFront
        if not vehicle.isGivingWay(): #if the vehicle is not giving way
            if vehicle.isStopped():
                if noCloseVehiclesOrSemaphores: #if the lane is free
                    if safetyPositionFromPrecedingVehicle < 0:
                        vehicle.stopAtVehicle(0)
                    elif precedingVehicle is not None:
                        self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=False)
                elif redSemInFront: #if the next semaphore is red
                    pass #wait
                elif precedingVehicle is not None and not precedingVehicle.isStopped(): #if there is a vehicle in front and it's moving
                    if safetyPositionFromPrecedingVehicle >= 0:
                        self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=False)
            else: #if the vehicle is moving
                if noCloseVehiclesOrSemaphores: #if the lane is free
                    self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=True)
                elif redSemInFront and vehicleInFront: #if the next semaphore is red and there is a vehicle in front
                    if nextSemPos < safetyPositionFromPrecedingVehicle: #if the red semaphore is closer
                        vehicle.stopAtSemaphore(nextSemPos) #stop at the semaphore
                    else: #if the vehicle in front is closer. Note: I don't make the vehicle surpasse the other one, since there's a close red semaphore
                        vehicle.followVehicle(precedingVehicle,self.vehicleDistance) #follow the vehicle in front
                elif redSemInFront: #if the next semaphore is red but there is no vehicle in front
                    vehicle.stopAtSemaphore(nextSemPos)
                elif vehicleInFront: #if there is a vehicle in front but the semaphore is green
                    self.moveAndOvertakeIfPossible(vehicle, precedingVehicle, laneIndex, currentTime, timeStep, wasMoving=True)
    
            ExceedingDistance = vehicle.getPosition() - self.length
            if ExceedingDistance > 0: #if the vehicle reach the end of the lane
                self.endOfLaneHandler(vehicle, ExceedingDistance, currentTime, timeStep)

        else: #if the vehicle is giving way
            oldPosition = vehicle.getPosition()
            vehicle.restart(self.speedLimit, timeStep) #I try to restart the vehicle
            ExceedingDistance = vehicle.getPosition() - self.length #I know the vehicle is at the end of the lane
            self.endOfLaneHandler(vehicle, ExceedingDistance, currentTime, timeStep) #endOfLaneHandler will decide if the vehicle can go or has to keep waiting
            vehicles = self.getAllVehicles()
            if vehicle in vehicles and vehicle.isGivingWay():
                vehicle.setPosition(oldPosition) #if the vehicle has to keep waiting, I reset its position to the previous one

        vehicle.update(currentTime)
        return True
    
    def endOfLaneHandler(self, vehicle, ExceedingDistance, currentTime, timeStep = 1):
        if ExceedingDistance > 0:
            if self.endJunction != None: #if there is a junction at the end of the lane
                self.endJunction.handleVehicle(vehicle, ExceedingDistance,currentTime, timeStep)
            else:
                self.removeVehicle(vehicle)
                vehicle.setArrivalTime(currentTime)

    def moveAndOvertakeIfPossible(self, vehicle, precedingVehicle, laneIndex, currentTime, timeStep = 1, wasMoving = True):
        hasPrecedingVehicle = precedingVehicle is not None
        safetyPositionFromPrecedingVehicle = self.safetyPositionFrom(precedingVehicle) if hasPrecedingVehicle else 0
        if wasMoving:
            newPosition = vehicle.move(self.speedLimit, timeStep)
        else:
            newPosition = vehicle.restart(self.speedLimit, timeStep)
        if hasPrecedingVehicle and newPosition > safetyPositionFromPrecedingVehicle:
            nextLaneIndex = laneIndex + 1
            nextLaneIsFree = self.isLaneFreeAtPosition(newPosition, nextLaneIndex)
            if nextLaneIsFree:
                vehicle.setLane(nextLaneIndex)
            else:
                vehicle.followVehicle(precedingVehicle,self.vehicleDistance)
        self.limitSpeed(vehicle)

    def isLaneFreeAtPosition(self, position, laneIndex):
        if len(self.line) <= 0 or laneIndex >= len(self.line):
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

    def hasOutgoingVehicles(self, timeStep = 1):
        vehicles = self.getAllVehicles()
        for vehicle in vehicles:
            if vehicle.calculatePosition(timeStep) > self.length:
                return True
    
    def moveVehicles(self, time, timeStep = 1):
        tmp = self.getAllVehicles().copy()
        for vehicle in tmp:
            #print("Moving vehicle %d" % vehicle.id)
            self.moveVehicle(vehicle, time, timeStep)

    def waitForNextLane(self, vehicle, posToWaitAt):
        followingVehicle = self.followingVehicle(vehicle)
        safePos = self.safetyPositionFromFollowingVehicleOf(followingVehicle) if followingVehicle != None else 0
        if posToWaitAt >= safePos:
            vehicle.giveWay(posToWaitAt)
        elif safePos < self.length:
            vehicle.giveWay(safePos)
        else:
            vehicle.giveWay(self.length)

    def giveWay(self, vehicle): #check if the vehicle stops everytime without checking if the lane is free
        vehicle.giveWay(self.length)
    
    def limitSpeed(self, vehicle):
        if vehicle.getSpeed() > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def precedingVehicle(self, vehicle, laneIndex = 0): #I get the preceding vehicle of the current vehicle, Vehicles must be ordered by position
        vehicles = self.getVehiclesInLane(laneIndex)
        if len(vehicles) <= 1:
            return None
        for i in range(len(vehicles)):
            if vehicles[i] == vehicle:
                if i > 0:
                    return vehicles[i-1]
                return None
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
        for i in range(len(self.line)):
            if self.hasVehicleInLane(vehicle, i):
                self.line[i].remove(vehicle)
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
            return semaphore.position if semaphore.position != -1 else self.length #if the semaphore is at the end of the lane, I return the length of the lane
    
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
        return self.line[laneIndex].getVehicles() if laneIndex < len(self.line) else None
    
    def getAllVehicles(self):
        allVehicles = []
        for index in range(len(self.line)):
            allVehicles += self.line[index].getVehicles()
        return allVehicles
    
    def appendVehicle(self, vehicle):
        index = 0
        #self.vehicles.append(vehicle)
        self.line[index].append(vehicle)

    def getLaneWhereVehicleIs(self, vehicle):
        return vehicle.getLane()

'''class RoadWay(Lane):
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0):
        super().__init__(id, length, vehicleDistance, speedLimit, semaphores, startJunction, endJunction, priority)
        self.lanes = []
        
    def __init__(self, id, lanes = []):
        self.id = id
        self.lanes = lanes

    def addLane(self, lane):
        self.lanes.append(lane)

    def removeLane(self, lane):
        self.lanes.remove(lane)

    def getLane(self, id):
        for lane in self.lanes:
            if lane.id == id:
                return lane
            
    def getLaneWithVehicle(self, vehicle):
        for lane in self.lanes:
            if lane.hasVehicle(vehicle):
                return lane

    def tryAddVehicle(self, vehicle, currentTime, position = 0):
        for lane in self.lanes:
            pos = lane.tryAddVehicle(vehicle, currentTime, position)
            if pos >= 0:
                return pos
        return -1

    def addVehicleToLane(self, vehicle, laneId, currentTime, position = 0):
        lane = self.getLane(laneId)
        self.addVehicleToLane(vehicle, lane, currentTime, position)

    def addVehicleToLane(self, vehicle, lane, currentTime, position = 0):
        if lane != None:
            lane.addVehicle(vehicle, currentTime, position)

    def tryAddVehicleToLane(self, vehicle, laneId, currentTime, position = 0):
        lane = self.getLane(laneId)
        return self.tryAddVehicleToLane(vehicle, lane, currentTime, position)
    
    def tryAddVehicleToLane(self, vehicle, lane, currentTime, position = 0):
        if lane != None:
            return lane.tryAddVehicle(vehicle, currentTime, position)

    def addStartJunction(self, junction):
        for lane in self.lanes:
            lane.addStartJunction(junction)

    def addEndJunction(self, junction):
        for lane in self.lanes:
            lane.addEndJunction(junction)

    def moveVehicles(self, time, timeStep = 1):
        for lane in self.lanes:
            lane.moveVehicles(time, timeStep)

    def hasOutgoingVehicles(self, timeStep = 1):
        for lane in self.lanes:
            if lane.hasOutgoingVehicles(timeStep):
                return True
            
    def getPriority(self):
        return self.lanes[0].getPriority()
    
    def addSemaphoreAtEnd(self, semaphore):
        for lane in self.lanes:
            lane.addSemaphoreAtEnd(semaphore)

    def isGreen(self, currentTime):
        return self.lanes[0].isGreen(currentTime)
    
    def isRed(self, currentTime):
        return self.lanes[0].isRed(currentTime)
    
    def getPriority(self):
        return self.lanes[0].getPriority()
    
    def removeVehicle(self, vehicle):
        for lane in self.lanes:
            lane.removeVehicle(vehicle)

    def waitForNextLane(self, vehicle, posToWaitAt):
        for lane in self.lanes:
            if lane.hasVehicle(vehicle):
                lane.waitForNextLane(vehicle, posToWaitAt)

    def giveWay(self, vehicle):
        for lane in self.lanes:
            if lane.hasVehicle(vehicle):
                lane.giveWay(vehicle)'''

class Semaphore:
    def __init__(self, greenTime, redTime, position = -1, yellowTime = 0, startTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.position = position #position of the semaphore on the lane, -1 = end of the lane, 0 = start of the lane
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

class Bifurcation(Junction): #I can use NFurcation instead of Bifurcation with 2 outgoing lanes
    def __init__(self, id, incomingLane, outgoingLane1, outgoingLane2, flux1):
        self.id = id
        self.incomingLane = incomingLane
        self.outgoingLane1 = outgoingLane1
        self.outgoingLane2 = outgoingLane2
        self.flux1 = flux1
        if incomingLane != None:
            incomingLane.addEndJunction(self)
        if outgoingLane1 != None:
            outgoingLane1.addStartJunction(self)
        if outgoingLane2 != None:
            outgoingLane2.addStartJunction(self)

    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingLane.vehicles:
            print("Vehicle %d is at the bifurcation" % vehicle.id)
            nextLane = self.outgoingLane1 if random.uniform(0,1) < self.flux1 else self.outgoingLane2
            print("Trying to add vehicle %d to lane %d at position %f" % (vehicle.id, nextLane.id, position))
            pos = nextLane.tryAddVehicle(vehicle, currentTime, position)
            if pos < 0: #if the vehicle cannot be added to the next lane
                print("Vehicle %d cannot be added to lane %d" % (vehicle.id, nextLane.id))
                pos += self.incomingLane.length
                self.incomingLane.waitForNextLane(vehicle,pos)
            else:
                print("Removing vehicle %d from lane %d" % (vehicle.id, self.incomingLane.id))
                self.incomingLane.removeVehicle(vehicle)

class NFurcation(Junction): #1 incoming lane, n outgoing lanes
    def __init__(self, id, incomingLane = None, outgoingLanes = [], fluxes = []):
        self.id = id
        self.incomingLane = incomingLane
        if incomingLane != None:
            incomingLane.addEndJunction(self)
        self.outgoingLanes = outgoingLanes
        if outgoingLanes != None:
            for lane in outgoingLanes:
                lane.addStartJunction(self)
        self.fluxes = fluxes

    def addOutgoingLane(self, lane, flux):
        self.outgoingLanes.append(lane)
        self.fluxes.append(flux)
        lane.addStartJunction(self)
    
    def addIncomingLane(self, lane):
        self.incomingLane = lane
        lane.addEndJunction(self)

    def getNextLane(self):
        randomValue = random.uniform(0,1)
        chosenLane = 0
        for i in range(len(self.fluxes)):
            if randomValue < self.fluxes[i]:
                chosenLane = i
                break
            randomValue -= self.fluxes[i]
        nextLane = self.outgoingLanes[chosenLane]
        return nextLane
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingLane.vehicles:
            print("Vehicle %d is at the n-furcation" % vehicle.id)
            if self.outgoingLanes == None or self.fluxes == None:
                if self.incomingLane != None:
                    self.incomingLane.removeVehicle(vehicle)
                print("Error: n-furcation has no outgoing lanes")
                return
            #fluxes represent the probability of going to each lane, given randomValue I choose the next lane
            nextLane = self.getNextLane()
            print("NFurcation: Vehicle %d is going from lane %d to lane %d" % (vehicle.id, self.incomingLane.id, nextLane.id))
            pos = nextLane.tryAddVehicle(vehicle, currentTime, position)
            if pos < 0: #if the vehicle cannot be added to the next lane
                pos += self.incomingLane.length
                self.incomingLane.waitForNextLane(vehicle,pos)
            else:
                self.incomingLane.removeVehicle(vehicle)

class Merge(Junction): #2 incoming lanes, 1 outgoing lane
    def __init__(self, id, incomingLane1, incomingLane2, outgoingLane):
        self.id = id
        self.incomingLane1 = incomingLane1
        self.incomingLane2 = incomingLane2
        self.outgoingLane = outgoingLane
        self.priorityLane = self.priorityLane()
        if incomingLane1 != None:
            incomingLane1.addEndJunction(self)
        if incomingLane2 != None:
            incomingLane2.addEndJunction(self)
        if outgoingLane != None:
            outgoingLane.addStartJunction(self)
        
    def priorityLane(self):
        if self.incomingLane1.getPriority() <= self.incomingLane2.getPriority():
            return self.incomingLane1
        return self.incomingLane2

    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if vehicle in self.incomingLane1.vehicles or vehicle in self.incomingLane2.vehicles:
            fromLane = self.incomingLane1 if vehicle in self.incomingLane1.vehicles else self.incomingLane2 #I get the lane from which the vehicle comes

            if fromLane == self.priorityLane or not self.priorityLane.hasOutgoingVehicles(timeStep): #if the vehicle comes from the priority lane or the priority lane is free
                pos = self.outgoingLane.tryAddVehicle(vehicle, currentTime, position)
                if pos < 0: #if the vehicle cannot be added to the next lane
                    pos += fromLane.length
                    fromLane.waitForNextLane(vehicle,pos)
                else:
                    print("Merge: Vehicle %d is going from lane %d to lane %d" % (vehicle.id, fromLane.id, self.outgoingLane.id))
                    fromLane.removeVehicle(vehicle)
            else:
                fromLane.giveWay(vehicle)

class Intersection(Junction): #n incoming lanes, n outgoing lanes
    #TODO: handle a list of fluxes for each incoming lane
    def __init__(self, id, incomingLanes = [], outgoingLanes = [], outgoingFluxes = []):
        self.id = id
        self.incomingLanes = incomingLanes
        for lane in incomingLanes:
            lane.addEndJunction(self)
        self.outgoingLanes = outgoingLanes
        for lane in outgoingLanes:
            lane.addStartJunction(self)
        self.outgoingLanesFluxes = outgoingFluxes

    def addIncomingLane(self, lane, semaphore = None): #semaphores must be synchronized setting same start time and opposite green and red times
        self.incomingLanes.append(lane)
        lane.addEndJunction(self)
        if semaphore != None:
            lane.addSemaphoreAtEnd(semaphore)
    
    def addOutgoingLane(self, lane, flux):
        self.outgoingLanes.append(lane)
        self.outgoingLanesFluxes.append(flux)
        lane.addStartJunction(self)

    def incomingLane(self, vehicle):
        for lane in self.incomingLanes:
            if vehicle in lane.getVehicles():
                return lane
        return None

    def getPriorityLane(self): #returns the lane with the highest priority that has green light
        if self.incomingLanes == None:
            print("Error: intersection has no incoming lanes")
            return None
        priorityLane = None
        for lane in self.incomingLanes: #get the first lane that is not red
            if lane.isGreen():
                priorityLane = lane
                break
        if priorityLane == None:
            return None
        for lane in self.incomingLanes:
            if lane.getPriority() < priorityLane.getPriority() and lane.isGreen():
                priorityLane = lane
        return priorityLane

    def getNextLane(self):
        randomValue = random.uniform(0,1)
        chosenLane = 0
        for i in range(len(self.outgoingLanesFluxes)):
            if randomValue < self.outgoingLanesFluxes[i]:
                chosenLane = i
                break
            randomValue -= self.outgoingLanesFluxes[i]
        nextLane = self.outgoingLanes[chosenLane]
        return nextLane
    
    def canGo(self, lane, currentTime):
        #I take every lane with higher priority (lowest number) that has Green and has outgoing vehicles, if there is no such lane I return True
        if self.incomingLanes == None:
            return False
        for r in self.incomingLanes:
            if r.getPriority() < lane.getPriority() and r.isGreen(currentTime) and r.hasOutgoingVehicles():
                return False
        return True
    
    def outgoingLanesOrderedByPriority(self):
        '''#this function is O(n^2), consider using a priority queue
        lanes = self.outgoingLanes
        orderedLanes = []
        #i append first the lane with the highest priority, then the lane with the second highest priority, and so on
        for i in range(len(self.outgoingLanes)):
            maxPriority = lanes[0].getPriority()
            maxPriorityLane = lanes[0]
            for lane in lanes:
                if lane.getPriority() < maxPriority:
                    maxPriority = lane.getPriority()
                    maxPriorityLane = lane
            orderedLanes.append(maxPriorityLane)
            lanes.remove(maxPriorityLane)
        return orderedLanes'''
        return sorted(self.outgoingLanes, key=lambda x: x.priority, reverse=False)
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if self.incomingLanes == None:
            print("Error: intersection has no incoming lanes")
            return
        incomingLane = self.incomingLane(vehicle)
        if incomingLane != None:
            if self.outgoingLanes == None or self.outgoingLanesFluxes == None:
                incomingLane.removeVehicle(vehicle)
                vehicle.setArrivalTime(currentTime)
                print("Error: intersection has no outgoing lanes")
                return
            #fluxes represent the probability of going to each lane, given randomValue I choose the next lane
            nextLane = self.getNextLane()
            #priorityLane = self.getPriorityLane()

            canGo = self.canGo(incomingLane,currentTime)
            if canGo: #if the vehicle can go (i.e there is no vehicle with higher priority that has green light and outgoing vehicles)
                pos = nextLane.tryAddVehicle(vehicle, currentTime, position) #retuns the new position, <0 if the vehicle cannot be added
                if pos < 0: #if the vehicle cannot be added to the next lane
                    pos += incomingLane.length #I calculate the position where to wait in the incoming lane
                    incomingLane.waitForNextLane(vehicle, pos) #I make the vehicle wait in the incoming lane
                else:
                    incomingLane.removeVehicle(vehicle)
            else:
                incomingLane.giveWay(vehicle)

#FIXME: Solve: Changing speed when changing lane.
#TODO: add intersection with semaphores, add priority to lanes, add priority to vehicles, add vehicle types, add vehicle types to lanes, add vehicle types to junctions
#TODO: implementa strade a doppia corsia: Lane gestisce una corsia come l'attuale Road, Road gestisce una strada a n Lane
#TODO: Factory classes with functions to handle initialization of networks

#TODO: implementa strada a doppia carreggiata: Roadway gestisce una strada a 2 carreggiata, Road diventa la carreggiata: Road > Roadway > Lane
#class Roadway:
#TODO: Network class to handle multiple lanes and junctions (maybe all map?), and Simulator class to handle the simulation, and update every Lane etc...
#Simulation class will also handle the history of the entirye Network (or Map), and have a saveHistory function to save the entire history of the map in a json file


