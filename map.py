"""
@file    map.py
@author  David Megli
"""
class Semaphore:
    def __init__(self, greenTime, redTime, yellowTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.yellowTime = yellowTime

class SectorDensity:
    def __init__(self, time, vehicles):
        self.time = time
        self.vehicles = vehicles

class Sector:
    def __init__(self, id, start, end, capacity):
        self.id = id
        self.start = start
        self.end = end
        self.capacity = capacity
        self.vehicles = 0
        self.densities = []

    def add_vehicle(self):
        if not self.is_full():
            self.vehicles += 1
            return True
        return False
    
    def remove_vehicle(self):
        if self.vehicles > 0:
            self.vehicles -= 1
            return True
        return False
    
    def is_full(self):
        return self.vehicles >= self.capacity
    
    def save_sector_density(self, time):
        self.densities.append(SectorDensity(time, self.vehicles))
    
    def get_density(self, time):
        for density in self.densities:
            if density.time >= time:
                return density.vehicles / (self.end - self.start)
        return 0


# A road is composed of multiple sectors
class Road:
    def __init__(self, id, numSectors, length, capacityPerSector, vehicleDistance = 1):
        self.id = id
        self.numSectors = numSectors
        self.length = length
        self.capacity = capacityPerSector
        self.sectors = []
        for i in range(numSectors):
            start = i * length / numSectors
            end = (i+1) * length / numSectors
            self.sectors.append(Sector(i, start, end, capacityPerSector))
        self.vehicles = [] #list of vehicles on the road
        self.vehicleDistance = vehicleDistance #distance between vehicles in meters
        self.startJunction = None #TODO: implement junctions
        self.endJunction = None

    def add_vehicle(self, vehicle, time): #add vehicle to the road
        # I check if there is a vehicle too close
        previousVehicle = self.previous_vehicle(vehicle)
        vehicle.states[-1].time = time #update time
        vehicle.states[-1].position = self.sectors[0].start
        if previousVehicle != None and (previousVehicle.states[-1].position - self.vehicleDistance - previousVehicle.length) <= 0:
            vehicle.states[-1].state = "Waiting"
        else:
            vehicle.states[-1].state = "Traveling"
            self.sectors[0].add_vehicle()
        self.vehicles.append(vehicle)
    
    def get_sector(self, position): #get sector by position
        for sector in self.sectors:
            if position >= sector.start and position < sector.end:
                return sector
        return None

    def move_vehicle(self, vehicle, timeStep = 1):
        # If the vehicle is in the road, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        # in the current sector at the end of the sector
        if vehicle in self.vehicles:
            pastPosition = vehicle.states[-1].position
            futurePosition = vehicle.futurePosition(timeStep)
            previousVehicle = self.previous_vehicle(vehicle)
            safetyPosition = previousVehicle.states[-1].position - self.vehicleDistance - previousVehicle.length if previousVehicle != None else 0
            if previousVehicle != None and futurePosition > safetyPosition:
                vehicle.moveAt(safetyPosition, previousVehicle.states[-1].speed, previousVehicle.states[-1].acceleration, timeStep)
                print("Car %d stopped at %f" % (vehicle.id, safetyPosition))
                self.update_sector(pastPosition, safetyPosition)
                return True
            
            vehicle.move(timeStep)
            if futurePosition >= self.length: #if the vehicle reach the end of the road
                self.remove_vehicle(vehicle)
                print("Car %d reached the end of the road" % vehicle.id)
                self.update_sector(pastPosition, futurePosition)
            return True
        return False
    
    def move_vehicles(self, timeStep = 1):
        tmp = self.vehicles[:] #I iterate over a copy of the list
        for vehicle in tmp:
            self.move_vehicle(vehicle, timeStep)
        
    def previous_vehicle(self, vehicle):
        for i in range(len(self.vehicles)):
            if self.vehicles[i] == vehicle:
                if i > 0:
                    return self.vehicles[i-1]
                return None
        return None

    def remove_vehicle(self, vehicle):
        self.vehicles.remove(vehicle)
        self.update_sector(vehicle.states[-1].position, self.length+1) #I update the sector to remove the vehicle

    def update_sector(self, pastPosition, futurePosition):
        sector = self.get_sector(pastPosition)
        if sector != None:
            print("Car removed from sector %d" % sector.id)
            sector.remove_vehicle()
        sector = self.get_sector(futurePosition)
        if sector != None:
            print("Car added to sector %d" % sector.id)
            sector.add_vehicle()

    def update_sector_densities(self, time):
        for sector in self.sectors:
            sector.save_sector_density(time)
    
#class Junction:

# carreggiata, è composta da n corsie
#class Roadway:



