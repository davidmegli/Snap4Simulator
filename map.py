"""
@file    map.py
@author  David Megli
"""

class Semaphore:
    def __init__(self, greenTime, redTime, yellowTime = 0):
        self.greenTime = greenTime
        self.redTime = redTime
        self.yellowTime = yellowTime

    
class Sector:
    def __init__(self, id, start, end, capacity):
        self.id = id
        self.start = start
        self.end = end
        self.capacity = capacity
        self.vehicles = 0

    def add_vehicle(self):
        if self.vehicles < self.capacity:
            self.vehicles += 1
            return True
        return False

# A road is composed of multiple segments
class Road:
    def __init__(self, id, numSectors, length, capacityPerSector):
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
        self.startJunction = None #TODO: implement junctions
        self.endJunction = None

    def add_vehicle(self, vehicle, time): #add vehicle to the road
        if self.sectors[0].add_vehicle():
            vehicle.states[-1].time = time #update time
            vehicle.states[-1].position = self.sectors[0].start
            vehicle.states[-1].state = "Traveling"
            self.vehicles.append(vehicle)
            return True
        vehicle.stop()
        return False
    
    def get_sector(self, position): #get sector by position
        for sector in self.sectors:
            if position >= sector.start and position < sector.end:
                return sector
        return None
    
    def move_vehicle(self, vehicle, time):
        # If the vehicle is in the road, I get its future position, if the position is in the next sector I check if it is not full, if it's not full
        # I move the vehicle to the next sector and call the move method of the vehicle, otherwise I call the stopAt method of the vehicle to stop it
        # in the current sector at the end of the sector
        if vehicle in self.vehicles:
            futurePosition = vehicle.futurePosition()
            sector = self.get_sector(futurePosition)
            if sector.add_vehicle():
                vehicle.move()
                return True
            vehicle.stopAt(sector.end)
            return False
        
    def remove_vehicle(self, vehicle):
        for sector in self.sectors:
            if vehicle.states[-1].position >= sector.start and vehicle.states[-1].position < sector.end:
                sector.vehicles -= 1
                self.vehicles.remove(vehicle)
                return True
        return False
    
#class Junction:

# carreggiata, è composta da n corsie
#class Roadway:



