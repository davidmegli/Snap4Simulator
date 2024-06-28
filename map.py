"""
@file    map.py
@author  David Megli
"""

class Road:
    def __init__(self, id, length, vehicleDistance = 1, speedLimit = 50/3.6):
        self.id = id
        self.length = length
        self.vehicles = [] #list of vehicles on the road
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.speedLimit = speedLimit #speed limit in m/s
        self.startJunction = None #TODO: implement junctions
        self.endJunction = None

    def addVehicle(self, vehicle, time, position = 0): #add vehicle to the road
        # I check if there is a vehicle too close
        previousVehicle = self.previousVehicle(vehicle)
        if previousVehicle != None and (previousVehicle.position - self.vehicleDistance - previousVehicle.length) <= 0:
            vehicle.moving = False
            vehicle.setSpeed(0)
        else:
            vehicle.moving = True
            self.limitSpeed(vehicle)
        self.vehicles.append(vehicle)

    def moveVehicle(self, vehicle, timeStep = 1):
        # If the vehicle is in the road, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        # in the current sector at the end of the sector
        if vehicle in self.vehicles:
            pastPosition = vehicle.position
            nextPosition = vehicle.nextPosition(timeStep)
            previousVehicle = self.previousVehicle(vehicle)
            if previousVehicle != None: #if there is a vehicle in front of the current vehicle I check if the distance is enough to move the vehicle
                safetyPosition = previousVehicle.position - self.vehicleDistance - previousVehicle.length
                if nextPosition > safetyPosition: #if the distance is not enough
                    vehicle.moveTo(safetyPosition, timeStep) #I move the vehicle to the safety position
                    vehicle.setSpeed(previousVehicle.speed) #and set the speed to the speed of the previous vehicle
                    vehicle.acceleration = 0
                    return True
            
            vehicle.move(timeStep)
            if nextPosition >= self.length: #if the vehicle reach the end of the road TODO: implement junctions, call the junction method to handle the vehicle
                self.removeVehicle(vehicle)
                print("Car %d reached the end of the road" % vehicle.id)
            return True
        return False
    
    def moveVehicles(self, timeStep = 1):
        tmp = self.vehicles[:] #I iterate over a copy of the list
        for vehicle in tmp:
            self.moveVehicle(vehicle, timeStep)
    
    def limitSpeed(self, vehicle):
        if vehicle.speed > self.speedLimit:
            vehicle.setSpeed(self.speedLimit)

    def previousVehicle(self, vehicle):
        for i in range(len(self.vehicles)):
            if self.vehicles[i] == vehicle:
                if i > 0:
                    return self.vehicles[i-1]
                return None
        return None

    def removeVehicle(self, vehicle):
        self.vehicles.remove(vehicle)

    def vehicleDensity(self):
        return len(self.vehicles) / self.length
    
    def vehiclesAt(self, start, end):
        vehicles = []
        for vehicle in self.vehicles:
            if vehicle.position >= start and vehicle.position <= end:
                vehicles.append(vehicle)
        return vehicles

class Semaphore:
    def __init__(self, greenTime, redTime, yellowTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.yellowTime = yellowTime


#class Junction:

# carreggiata, è composta da n corsie
#class Roadway:



