"""
@file    data.py
@authors  David Megli

Description:
This file contains the classes to handle the history of the map, saving the state of the roads at different times.
The classes calculate the number of vehicles and density for each sector of a Road, and can save the history of the road in a json file.
"""
from map import Road
import json

class RoadState:
    def __init__(self, time, vehiclesPerSector, densityPerSector, densityPerSectorPerLane, numSectors, minimumDensityToConsiderTrafficQueue = 0.8):
        self.time = time
        self.vehiclesPerSector = vehiclesPerSector
        self.densityPerSector = densityPerSector
        self.densityPerSectorPerLane = densityPerSectorPerLane
        self.longestTrafficQueue = 0
        self.numSectors = numSectors
        self.minDensityToConsiderTrafficQueue = minimumDensityToConsiderTrafficQueue
        self.calculateLongestTrafficQueue()

    def calculateLongestTrafficQueue(self):
        for i in range(self.numSectors):
            if self.densityPerSector[i] > self.minDensityToConsiderTrafficQueue:
                count = 1
                for j in range(i+1, self.numSectors):
                    if self.densityPerSector[j] > self.minDensityToConsiderTrafficQueue:
                        count += 1
                    else:
                        break
                if count > self.longestTrafficQueue:
                    self.longestTrafficQueue = count

class RoadHistory:
    def __init__(self, road: Road, sectorLength = 100): #sectorLength in meters
        self.road = road
        self.numLanes = road.getNumberOfLanes()
        self.sectorLength = sectorLength
        self.states = [] #list of SectorsState objects that represent the state of the road in a given time

    def saveState(self, road, time): #Given the time, I save the state of the road, saving the number of vehicles in each sector
        vehiclesPerSector = []
        densityPerSector = []
        densityPerSectorPerLane = []
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
            sectorDensity = occupiedSpace / self.sectorLength if self.sectorLength > 0 else 0
            densityPerSector.append(sectorDensity)
            densityPerSectorPerLane.append(sectorDensity / self.numLanes)
            if int(road.length) - i < self.sectorLength*3/2:
                break
        self.states.append(RoadState(time, vehiclesPerSector, densityPerSector, densityPerSectorPerLane, len(vehiclesPerSector)))

    def getHistory(self):
        return self.states
    
    def printHistory(self):
        for state in self.states:
            print("Time: %d" % state.time)
            for i in range(state.numSectors):
                print("Sector %d: %d vehicles" % (i, state.vehiclesPerSector[i]))

    def saveHistory(self, filename):
        history_dict = self.getHistoryDict()
        with open(filename, "w+", create_parents=True) as f:
            json.dump(history_dict, f, indent = 4)

    def getHistoryDict(self):
        history_dict = {
            "road": self.road.id,
            "states": []
            }
        for state in self.states:
            state_dict = {
                "time": state.time,
                "numSectors": state.numSectors,
                "sectorLenght": self.sectorLength,
                "DensityPerSector": [],
                "vehiclesPerSector": [],
                "DensityPerSectorPerLane": [],
                "longestTrafficQueue": state.longestTrafficQueue
            }
            for i in range(state.numSectors):
                state_dict["vehiclesPerSector"].append(state.vehiclesPerSector[i])
                state_dict["DensityPerSector"].append(state.densityPerSector[i]) 
                state_dict["DensityPerSectorPerLane"].append(state.densityPerSectorPerLane[i])
            history_dict["states"].append(state_dict)
        return history_dict
    
    def getMetrics(self):
        #calculates average density, average vehicles per sector, average longest traffic queue
        totalDensity = 0
        totalVehicles = 0
        totalLongestTrafficQueue = 0
        for state in self.states:
            totalDensity += sum(state.densityPerSector)
            totalVehicles += sum(state.vehiclesPerSector)
            totalLongestTrafficQueue += state.longestTrafficQueue
        return {
            "road": self.road.id,
            "sectorLength": self.sectorLength,
            "averageDensity": totalDensity / len(self.states) / state.numSectors,
            "averageVehiclesPerSector": totalVehicles / len(self.states) / state.numSectors,
            "averageLongestTrafficQueue": totalLongestTrafficQueue * self.sectorLength / len(self.states)
        }
    
    def saveMetrics(self, filename):
        metrics = self.getMetrics()
        with open(filename, "w+", create_parents=True) as f:
            json.dump(metrics, f, indent = 4)

class MapHistory:
    def __init__(self, roads, sectorLength = 100):
        self.roads = roads
        self.roadHistories = []
        for road in roads:
            self.roadHistories.append(RoadHistory(road, sectorLength))
        
    def saveState(self, time):
        for roadHistory in self.roadHistories:
            roadHistory.saveState(roadHistory.road, time)

    def saveHistory(self, filename):
        history_dict = self.getHistoryDict()
        with open(filename, "w+", create_parents=True) as f:
            json.dump(history_dict, f, indent = 4)

    def getHistoryDict(self):
        history_dict = {
            "roads": []
            }
        for roadHistory in self.roadHistories:
            history_dict["roads"].append(roadHistory.getHistoryDict())
        return history_dict

    def getMetrics(self):
        metrics = {
            "metrics": []
        }
        for roadHistory in self.roadHistories:
            metrics["metrics"].append(roadHistory.getMetrics())
        return metrics

    def saveMetrics(self, filename):
        metrics = self.getMetrics()
        with open(filename, "w+", create_parents=True) as f:
            json.dump(metrics, f, indent = 4)
