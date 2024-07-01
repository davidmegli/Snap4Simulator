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

class Lane:
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6, semaphores = None, startJunction = None, endJunction = None, priority = 0):
        self.id = id
        self.length = length
        self.vehicles = [] #list of vehicles on the lane
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.semaphores = semaphores if semaphores else []  # list of semaphores on the lane
        self.startJunction = startJunction
        self.endJunction = endJunction
        self.priority = priority

    def addVehicle(self, vehicle, currentTime, position = 0): #add vehicle to the lane and returns the position of the vehicle
        # I check if there is a vehicle too close
        self.resetVehiclePosition(vehicle) #vehicle's position represents the position on the lane, so I reset it to 0 in case it's coming from another lane
        precedingVehicle = self.precedingVehicle(vehicle)
        firstSem = self.getFirstSemaphore()
        if precedingVehicle != None:
            precedingVehiclePosition = precedingVehicle.getPosition()
            safetyPosition = self.safetyPositionFrom(precedingVehicle)
            if precedingVehiclePosition < 0:
                position = safetyPosition
                print("Vehicle %d has negative position: %f" % (precedingVehicle.id, precedingVehiclePosition)) #non arriva mai qui?? capisci dov'è che decrementa la posizione
            if safetyPosition <= 0:
                position = safetyPosition
                print("Vehicle %d is too close to the previous vehicle, setting position to %f" % (vehicle.id, safetyPosition)) 
                vehicle.stopAtVehicle(0) #solve increasing negative position problem
            else:
                self.limitSpeed(vehicle)
        elif firstSem != None and firstSem.isRed(currentTime) and position >= firstSem.position:
            vehicle.stopAtSemaphore(firstSem.position)
        else:
            self.limitSpeed(vehicle)
        self.vehicles.append(vehicle)
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
        if vehicle in self.vehicles: #if the vehicle is on the lane
            currentPos = vehicle.getPosition()
            nextPos = vehicle.calculatePosition(timeStep) #I get the future position of the vehicle based on current speed and acceleration
            precedingVeh = self.precedingVehicle(vehicle) #I get the previous vehicle
            nextSem = self.getNextSemaphore(vehicle.getPosition()) #I get the next semaphore
            nextSemPos = self.getSemaphorePosition(nextSem) if nextSem != None else -2 #I get the position of the semaphore
            redSemInFront = nextSem != None and nextSem.isRed(currentTime) and nextPos >= nextSemPos
            vehicleInFront = precedingVeh != None and nextPos > self.safetyPositionFrom(precedingVeh)
            freeLane = not redSemInFront and not vehicleInFront

            if not vehicle.isGivingWay(): #if the vehicle is not giving way
                if vehicle.isStopped():
                    if freeLane: #if the lane is free
                        pos = vehicle.restart(timeStep)
                        if precedingVeh != None and pos > self.safetyPositionFrom(precedingVeh):
                            if self.safetyPositionFrom(precedingVeh) >= 0:
                                vehicle.followVehicle(precedingVeh,self.vehicleDistance)
                            else:
                                vehicle.stopAtVehicle(0)
                    elif redSemInFront: #if the next semaphore is red
                        pass
                    elif precedingVeh != None and not precedingVeh.isStopped(): #if there is a vehicle in front and it's moving
                        if self.safetyPositionFrom(precedingVeh) >= 0:
                            pos = vehicle.restart(timeStep)
                            if pos > self.safetyPositionFrom(precedingVeh):
                                vehicle.followVehicle(precedingVeh,self.vehicleDistance)
                else: #if the vehicle is moving
                    if freeLane: #if the lane is free
                        vehicle.move(timeStep)
                        if precedingVeh != None and vehicle.getPosition() > self.safetyPositionFrom(precedingVeh):
                            vehicle.followVehicle(precedingVeh,self.vehicleDistance)
                    elif redSemInFront and vehicleInFront: #if the next semaphore is red and there is a vehicle in front
                        if nextSemPos < self.safetyPositionFrom(precedingVeh): #if the red semaphore is closer
                            vehicle.stopAtSemaphore(nextSemPos) #stop at the semaphore
                        else: #if the vehicle in front is closer
                            vehicle.followVehicle(precedingVeh,self.vehicleDistance) #follow the vehicle in front
                    elif redSemInFront: #if the next semaphore is red but there is no vehicle in front
                        vehicle.stopAtSemaphore(nextSemPos)
                    elif vehicleInFront: #if there is a vehicle in front
                        vehicle.followVehicle(precedingVeh,self.vehicleDistance)
        
                ExceedingDistance = vehicle.getPosition() - self.length
                if ExceedingDistance > 0: #if the vehicle reach the end of the lane
                    self.endOfLaneHandler(vehicle, ExceedingDistance, currentTime, timeStep)

            else: #if the vehicle is giving way
                vehicle.restart(timeStep) #I try to restart the vehicle
                ExceedingDistance = vehicle.getPosition() - self.length #I know the vehicle is at the end of the lane
                self.endOfLaneHandler(vehicle, ExceedingDistance, currentTime, timeStep) #endOfLaneHandler will decide if the vehicle can go or has to keep waiting

            return True
        return False
    
    def endOfLaneHandler(self, vehicle, ExceedingDistance, currentTime, timeStep = 1):
        if ExceedingDistance > 0:
            if self.endJunction != None: #if there is a junction at the end of the lane
                print("Vehicle %d reached the end of lane %d" % (vehicle.id, self.id))
                self.endJunction.handleVehicle(vehicle, ExceedingDistance,currentTime, timeStep)
            else:
                self.removeVehicle(vehicle)
                print("Vehicle %d reached the end of lane %d and was removed" % (vehicle.id, self.id))

    def hasOutgoingVehicles(self, timeStep = 1):
        for vehicle in self.vehicles:
            if vehicle.calculatePosition(timeStep) > self.length:
                return True

    def moveVehicles(self, time, timeStep = 1):
        tmp = self.vehicles[:] #I iterate over a copy of the list
        for vehicle in tmp:
            #print("Moving vehicle %d" % vehicle.id)
            self.moveVehicle(vehicle, time, timeStep)

    def waitForNextLane(self, vehicle, posToWaitAt):
        followingVehicle = self.followingVehicle(vehicle)
        safePos = self.safetyPositionFromFollowingVehicleOf(followingVehicle) if followingVehicle != None else 0
        if posToWaitAt >= safePos:
            vehicle.GiveWay(posToWaitAt)
        elif safePos < self.length:
            vehicle.GiveWay(safePos)
        else:
            vehicle.GiveWay(self.length)

    def giveWay(self, vehicle): #check if the vehicle stops everytime without checking if the lane is free
        vehicle.giveWay(self.length)
    
    def limitSpeed(self, vehicle):
        if vehicle.getSpeed() > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def precedingVehicle(self, vehicle): #I get the preceding vehicle of the current vehicle, Vehicles must be ordered by position
        for i in range(len(self.vehicles)):
            if self.vehicles[i] == vehicle:
                if i > 0:
                    return self.vehicles[i-1]
                return None
        if len(self.vehicles) > 0:
            return self.vehicles[-1] #if the vehicle is not in the list, I return the last vehicle
        return None
    
    def followingVehicle(self, vehicle): #I get the following vehicle of the current vehicle, Vehicles must be ordered by position
        for i in range(len(self.vehicles)):
            if self.vehicles[i] == vehicle:
                if i < len(self.vehicles) - 1:
                    return self.vehicles[i+1]
                return None
        return None
    
    def safetyPositionFrom(self, vehicle):
        return vehicle.position - self.vehicleDistance - vehicle.length
    
    def safetyPositionFromFollowingVehicleOf(self, vehicle):
        return vehicle.position + self.vehicleDistance + vehicle.length

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
            return semaphore.position if semaphore.position != -1 else self.length #if the semaphore is at the end of the lane, I return the length of the lane
    
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

    def hasVehicle(self, vehicle):
        for v in self.vehicles:
            if v == vehicle:
                return True
        return False

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
            print("Removing vehicle %d from lane %d" % (vehicle.id, self.incomingLane.id))
            print("Adding vehicle %d to lane %d" % (vehicle.id, nextLane.id))
            pos = nextLane.tryAddVehicle(vehicle, currentTime, position)
            if pos < 0: #if the vehicle cannot be added to the next lane
                pos += self.incomingLane.length
                self.incomingLane.waitForNextLane(vehicle,pos)
            else:
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
                    self.incomingLane.waitForNextLane(vehicle,pos)
                else:
                    print("Merge: Vehicle %d is going from lane %d to lane %d" % (vehicle.id, fromLane.id, self.outgoingLane.id))
                    fromLane.removeVehicle(vehicle)
            else:
                fromLane.giveWay(vehicle)

class Intersection(Junction): #n incoming lanes, n outgoing lanes
    def __init__(self, id, incomingLanes = [], outgoingLanes = [], incomingFluxes = [], outgoingFluxes = []):
        self.id = id
        self.incomingLanes = incomingLanes
        self.outgoingLanes = outgoingLanes
        self.incomingLanesFluxes = incomingFluxes
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
            if vehicle in lane.vehicles:
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
    
    def canGo(self, lane):
        #I take every lane with higher priority (lowest number) that has Green and has outgoing vehicles, if there is no such lane I return True
        if self.incomingLanes == None:
            return False
        for r in self.incomingLanes:
            if r.getPriority() < lane.getPriority() and r.isGreen() and r.hasOutgoingVehicles():
                return False
        return True
    
    def handleVehicle(self, vehicle, position, currentTime, timeStep = 1):
        if self.incomingLanes == None:
            print("Error: intersection has no incoming lanes")
            return
        incomingLane = self.incomingLane(vehicle)
        if incomingLane != None:
            if self.outgoingLanes == None or self.outgoingLanesFluxes == None:
                if incomingLane != None:
                    incomingLane.removeVehicle(vehicle)
                print("Error: intersection has no outgoing lanes")
                return
            #fluxes represent the probability of going to each lane, given randomValue I choose the next lane
            nextLane = self.getNextLane()
            priorityLane = self.getPriorityLane()

            canGo = self.canGo(incomingLane)
            if canGo:
                pos = nextLane.tryAddVehicle(vehicle, currentTime, position)
                if pos < 0: #if the vehicle cannot be added to the next lane
                    pos += incomingLane.length
                    self.incomingLane.waitForNextLane(vehicle, pos)
                else:
                    incomingLane.removeVehicle(vehicle)
            else:
                incomingLane.giveWay(vehicle)

#TODO: Solve: Changing speed when changing lane.
#TODO: add intersection with semaphores, add priority to lanes, add priority to vehicles, add vehicle types, add vehicle types to lanes, add vehicle types to junctions
#TODO: implementa strade a doppia corsia: Lane gestisce una corsia come l'attuale Road, Road gestisce una strada a n Lane
#TODO: Factory classes with functions to handle initialization of networks

#TODO: implementa strada a doppia carreggiata: Roadway gestisce una strada a 2 carreggiata, Road diventa la carreggiata: Roadway > Road > Lane
#class Roadway:



