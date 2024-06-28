"""
@file    data.py
@author  David Megli
"""
from map import Road
import json

class RoadState:
    def __init__(self, time, vehiclesPerSector, densityPerSector, numSectors):
        self.time = time
        self.vehiclesPerSector = vehiclesPerSector
        self.densityPerSector = densityPerSector
        self.numSectors = numSectors

class RoadHistory:
    def __init__(self, road, sectorLength = 100): #sectorLength in meters
        self.road = road
        self.sectorLength = sectorLength
        self.states = [] #list of SectorsState objects that represent the state of the road in a given time

    def saveState(self, road, time): #Given the time, I save the state of the road, saving the number of vehicles in each sector
        vehiclesPerSector = []
        densityPerSector = []
        for i in range(0, int(road.length), int(self.sectorLength)):
            maxpos = i + self.sectorLength if i + self.sectorLength <= road.length else int(road.length)
            if int(road.length) - i < self.sectorLength*3/2: #in case the last sector is too short
                maxpos = int(road.length)
            vehicles = self.road.vehiclesAt(i, maxpos)
            occupiedSpace = 0
            for v in vehicles:
                occupiedSpace += v.length
                occupiedSpace += self.road.vehicleDistance
            vehiclesPerSector.append(len(road.vehiclesAt(i, maxpos)))
            densityPerSector.append(occupiedSpace / self.sectorLength if self.sectorLength > 0 else 0)
            if int(road.length) - i < self.sectorLength*3/2:
                break
        self.states.append(RoadState(time, vehiclesPerSector, densityPerSector, len(vehiclesPerSector)))

    def getHistory(self):
        return self.states
    
    def printHistory(self):
        for state in self.states:
            print("Time: %d" % state.time)
            for i in range(state.numSectors):
                print("Sector %d: %d vehicles" % (i, state.vehiclesPerSector[i]))

    def saveHistory(self, filename):
        history_dict = {
            "road": self.road.id,
            "states": []
            }
        for state in self.states:
            state_dict = {
                "time": state.time,
                "DensityPerSector": [],
                "numSectors": state.numSectors
            }
            for i in range(state.numSectors):
                state_dict["DensityPerSector"].append(state.densityPerSector[i]) 
            history_dict["states"].append(state_dict)
        with open(filename, "w") as f:
            json.dump(history_dict, f, indent = 4)
        #json.dumps(history_dict)

