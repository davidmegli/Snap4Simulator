"""
@file    data.py
@author  David Megli
"""
from map import Road
import json

class RoadState:
    def __init__(self, time, vehiclesPerSector, numSectors):
        self.time = time
        self.vehiclesPerSector = vehiclesPerSector
        self.numSectors = numSectors

class RoadHistory:
    def __init__(self, road, sectorLength = 100): #sectorLength in meters
        self.road = road
        self.sectorLength = sectorLength
        self.states = [] #list of SectorsState objects that represent the state of the road in a given time

    def saveState(self, road, time): #Given the time, I save the state of the road, saving the number of vehicles in each sector
        vehiclesPerSector = []
        for i in range(0, int(road.length), int(self.sectorLength)):
            maxpos = i + self.sectorLength if i + self.sectorLength <= road.length else int(road.length)
            if int(road.length) - i < self.sectorLength*3/2: #in case the last sector is too short
                maxpos = int(road.length)
            vehiclesPerSector.append(len(road.vehiclesAt(i, maxpos)))
            if int(road.length) - i < self.sectorLength*3/2:
                break
        self.states.append(RoadState(time, vehiclesPerSector, len(vehiclesPerSector)))

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
                len = self.sectorLength if i < state.numSectors - 1 else self.road.length - (state.numSectors - 1) * self.sectorLength
                state_dict["DensityPerSector"].append(state.vehiclesPerSector[i] / len if len > 0 else 0) 
            history_dict["states"].append(state_dict)
        with open(filename, "w") as f:
            json.dump(history_dict, f, indent = 4)
        #json.dumps(history_dict)

