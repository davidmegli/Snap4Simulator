"""
@file    data.py
@author  David Megli

Description:
This file contains the classes to handle the history of the map, saving the state of the lanes at different times.
The classes calculate the number of vehicles and density for each sector of a Lane, and can save the history of the lane in a json file.
"""
from map import Lane
import json

#TODO: MapState and MapHistory to keep track of the entire map, with saveHistory function to save the entire history of the map in a json file

class LaneState:
    def __init__(self, time, vehiclesPerSector, densityPerSector, numSectors):
        self.time = time
        self.vehiclesPerSector = vehiclesPerSector
        self.densityPerSector = densityPerSector
        self.numSectors = numSectors

class LaneHistory:
    def __init__(self, lane, sectorLength = 100): #sectorLength in meters
        self.lane = lane
        self.sectorLength = sectorLength
        self.states = [] #list of SectorsState objects that represent the state of the lane in a given time

    def saveState(self, lane, time): #Given the time, I save the state of the lane, saving the number of vehicles in each sector
        vehiclesPerSector = []
        densityPerSector = []
        for i in range(0, int(lane.length), int(self.sectorLength)):
            maxpos = i + self.sectorLength if i + self.sectorLength <= lane.length else int(lane.length)
            if int(lane.length) - i < self.sectorLength*3/2: #in case the last sector is too short
                maxpos = int(lane.length)
            vehicles = self.lane.vehiclesAt(i, maxpos)
            occupiedSpace = 0
            for v in vehicles:
                occupiedSpace += v.length
                occupiedSpace += self.lane.vehicleDistance
            vehiclesPerSector.append(len(lane.vehiclesAt(i, maxpos)))
            densityPerSector.append(occupiedSpace / self.sectorLength if self.sectorLength > 0 else 0)
            if int(lane.length) - i < self.sectorLength*3/2:
                break
        self.states.append(LaneState(time, vehiclesPerSector, densityPerSector, len(vehiclesPerSector)))

    def getHistory(self):
        return self.states
    
    def printHistory(self):
        for state in self.states:
            print("Time: %d" % state.time)
            for i in range(state.numSectors):
                print("Sector %d: %d vehicles" % (i, state.vehiclesPerSector[i]))

    def saveHistory(self, filename):
        history_dict = {
            "lane": self.lane.id,
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

