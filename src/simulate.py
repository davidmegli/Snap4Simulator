"""
@file    simulate.py
@author  David Megli

Description:
This file simulates the movement of vehicles in a road
"""
from vehicle import Vehicle
from map import Road, Semaphore, Junction, Intersection
from data import RoadHistory, MapHistory
import random
import time as t

class Simulation:
    def __init__(self, simulationCycles: int = 600, timeStep: int = 1, vehicleInjectionRate: int = 1, sectorLength: int = 100, simulationName: str = "simulation"):
        self.roadCount = 0
        self.intersectionCount = 0
        self.vehicleTypeCount = 0
        self.vehicleTypes: list[Vehicle] = []
        self.vehicleCount = 0
        self.vehicles: list[Vehicle] = []
        self.roads: list[Road] = []
        self.startingRoads: list[Road] = []
        self.intersections: list[Intersection] = []
        self.timeStep = timeStep
        self.simulationCycles = simulationCycles
        self.sectorLength = sectorLength
        self.history: MapHistory = None
        self.simulationName = simulationName
        self.vehicleInjectionRate = vehicleInjectionRate
   
    def addVehicleType(self,length: int = 5, initialPos: int = 0, initialSpeed: int = 7, initialAcceleration: int = 0, maxSpeed: int = 7, maxAcceleration: int = 0.8, creationTime: int = 0, sigma: float = 0.0, reactionTime: int = 0.8):
        self.vehicleTypes.append(Vehicle(self.vehicleTypeCount, length, initialPos, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime, sigma, reactionTime))
        self.vehicleTypeCount += 1
        return self.vehicleTypes[-1]

    def addRoad(self, roadLenght: int = 1000, vehicleDistance: int = 1, speedLimit: int = 50/3.6, isStartingRoad: bool = False):
        road = Road(self.roadCount, roadLenght, vehicleDistance, speedLimit)
        print("Adding road %d with length %d, vehicle distance %d, speed limit %d" % (road.id, road.length, road.vehicleDistance, road.speedLimit))
        self.roads.append(road)
        self.roadCount += 1
        if isStartingRoad:
            self.startingRoads.append(road)
        return self.roads[-1]
    
    def addRoads(self, roadLenght: int = 1000, vehicleDistance: int = 1, speedLimit: int = 50/3.6, roadCount: int = 1, isStartingRoad: bool = False):
        for i in range(roadCount):
            self.addRoad(roadLenght, vehicleDistance, speedLimit, isStartingRoad)
        return self.roads[-roadCount:]
    
    def addSemaphore(self, road, greenLight: int = 60, redLight: int = 30, position: int = 500, yellowLight: int = 0, delay: int = 0):
        road.addSemaphore(Semaphore(greenLight, redLight, position, 0, 0))

    def addIntersection(self, incomingRoads: list[Road], outgoingRoads: list[Road], outProbabilities: list[int]):
        self.intersections.append(Intersection(self.intersectionCount, incomingRoads, outgoingRoads, outProbabilities))
        print("Adding intersection %d with incoming roads %s and outgoing roads %s with probabilities %s" % (self.intersections[-1].id, [road.id for road in incomingRoads], [road.id for road in outgoingRoads], outProbabilities))
        self.intersectionCount += 1
        return self.intersections[-1]
    
    def injectVehicles(self, time, cycle):
        for vehicle in self.vehicleTypes:
            if cycle % self.vehicleInjectionRate == 0:        
                for road in self.startingRoads:
                    veh = Vehicle(self.vehicleCount, vehicle.length, 0, vehicle.initialSpeed, vehicle.initialAcceleration, vehicle.maxSpeed, vehicle.maxAcceleration, time, vehicle.sigma, vehicle.reactionTime)
                    road.addVehicle(veh,time)
                    self.vehicles.append(veh)
                    self.vehicleCount += 1

    def moveVehicles(self, time):
        roads = sorted(self.roads, key=lambda road: road.id, reverse=True)
        for road in roads:
            road.moveVehicles(time, self.timeStep)

    def simulate(self):
        output = "../output/%s_simulation_output_%i.txt" % (self.simulationName, self.simulationCycles)
        vehHistoryMetricsFile = "../output/%s_vehicles_metrics_%i.json" % (self.simulationName, self.simulationCycles)
        vehMetricsFile = "../output/%s_vehicles_metrics_%i.txt" % (self.simulationName, self.simulationCycles)
        roadsMetricsJsonFile = "../output/%s_road_metrics_%i.json" % (self.simulationName, self.simulationCycles)
        f = open(vehMetricsFile, "w")
        f2 = open(output, "w")
        f3 = open(vehHistoryMetricsFile, "w")
        self.history = MapHistory(self.roads, self.sectorLength)
        for i in range(self.simulationCycles):
            time = i * self.timeStep
            print("Time: %ds" % time, file=f2)
            self.injectVehicles(time, i)
            self.moveVehicles(time)
            self.history.saveState(time)
            print("Cycle %d/%d" % (i,self.simulationCycles), end="\r")
            for vehicle in self.vehicles:
                for road in self.roads:
                    if road.hasVehicle(vehicle):
                        print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d (%s)" % (vehicle.id, vehicle.position, road.length, vehicle.speed, vehicle.speed*3.6, vehicle.acceleration, road.id, road), file=f2)

        print("VEHICLES METRICS:", file=f)
        for vehicle in self.vehicles:
            if vehicle.isArrived():
                print("Vehicle %d: " % vehicle.id, end="", file=f)
                print(vehicle.getMetricsAsString(), file=f)
                #print(Vehicle.getVehicleStateHistoryMetricsAsJSON(vehicle), file=f3, end=",\n")
        print()
        print("Simulation duration: %ds" % (self.simulationCycles * self.timeStep), file=f)
        print(Vehicle.getVehiclesMetricsAsString(self.vehicles), file=f)
        self.history.saveMetrics(roadsMetricsJsonFile)


minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
maxVehicleSpeed = 7#40/3.6
topVehicleSpeed = 150/3.6 #150 km/h in m/s
#topAcceleration = 0#.8 #0.8 m/s^2
speedLimit = 100/3.6 #100 km/h in m/s
maxAcceleration = 4
vehicleLength = 5 #5m
startingPosition = 0
vehicleCount = 1000000
timeStep = 1 #cycle steps in seconds
spawningRate = 1 #instantiate one vehicle every x cycles
sectorsPerRoad = 10 #number of sectors in the road
roadLength = 500 #meters
singleRoadLen = 1000
simulationCycles = 600
greenLight = 40 #seconds
redLight = 20 #seconds
reactionTime = 0.3
sigma = 0.0

def single_road():
    simulationName = "single_road_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    road = simulation.addRoad(singleRoadLen, 1, speedLimit, True)
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

def single_road_semaphore():
    simulationName = "single_road_semaphore_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road = simulation.addRoad(singleRoadLen, 1, speedLimit, True)
    road.addSemaphore(semaphore)
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

def merge():
    simulationName = "merge_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    #semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    inRoads = simulation.addRoads(roadLength, 1, speedLimit, 2, True)
    outRoads = simulation.addRoads(roadLength, 1, speedLimit, 1)
    #road1.addSemaphore(semaphore)
    merge = simulation.addIntersection(inRoads, outRoads, [1])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

def merge_sem():
    green = 40
    red = 40
    delay1 = red
    simulationName = "merge_sem_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    semaphore1 = Semaphore(green, red, roadLength, 0, delay1)
    semaphore2 = Semaphore(green, red, roadLength, 0, 0)
    inRoads = simulation.addRoads(roadLength, 1, speedLimit, 2, True)
    inRoads[0].addSemaphore(semaphore1)
    inRoads[1].addSemaphore(semaphore2)
    outRoads = simulation.addRoads(roadLength, 1, speedLimit, 1)
    merge = simulation.addIntersection(inRoads, outRoads, [1])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

def bifurcation():
    simulationName = "bifurcation_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    inroads = simulation.addRoads(roadLength, 1, speedLimit, 1, True)
    outroads = simulation.addRoads(roadLength, 1, speedLimit, 2)
    bifurcation = simulation.addIntersection(inroads, outroads, [0.8, 0.2])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

def bifurcation_sem():
    simulationName = "bifurcation_sem_sim"
    simulation = Simulation(simulationCycles, timeStep, spawningRate, roadLength / sectorsPerRoad, simulationName)
    semaphore = Semaphore(greenLight, redLight, 500, 0, 0)
    inroads = simulation.addRoads(roadLength, 1, speedLimit, 1, True)
    inroads[0].addSemaphore(semaphore)
    outroads = simulation.addRoads(roadLength, 1, speedLimit, 2)
    bifurcation = simulation.addIntersection(inroads, outroads, [0.8, 0.2])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime)
    simulation.simulate()

if __name__ == "__main__":
    single_road()
    single_road_semaphore()
    #merge()
    bifurcation()
    bifurcation_sem()
    merge_sem()