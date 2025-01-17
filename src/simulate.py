"""
@file    simulate.py
@authors  David Megli

Description:
This file simulates the movement of vehicles in a road, receiving a JSON file with the configuration of the simulation.
"""
import json
import jsonschema
import sys
from vehicle import Vehicle
from map import Coordinates, Road, Semaphore, Junction, Intersection, Shape
from data import RoadHistory, MapHistory
import random
import time as t
from pathlib import Path
import os

class Simulation:
    # JSON keys:
    SIMULATION_INFO_STRING = "simulation"
    SIMULATION_NAME_STRING = "name"
    SIMULATION_CYCLES_STRING = "cycles"
    TIME_STEP_STRING = "timeStep"
    VEHICLE_INJECTION_RATE_STRING = "vehicleInjectionRate"
    SECTOR_LENGTH_STRING = "sectorLength"
    LOG_STRING = "log"
    VEHICLES_STRING = "vehicles"
    VEHICLE_LENGTH_STRING = "length"
    VEHICLE_INITIAL_POS_STRING = "initialPosition"
    VEHICLE_INITIAL_SPEED_STRING = "initialSpeed"
    VEHICLE_INITIAL_ACCELERATION_STRING = "initialAcceleration"
    VEHICLE_MAX_SPEED_STRING = "maxSpeed"
    VEHICLE_MAX_ACCELERATION_STRING = "maxAcceleration"
    VEHICLE_CREATION_TIME_STRING = "creationTime"
    VEHICLE_SIGMA_STRING = "sigma"
    VEHICLE_REACTION_TIME_STRING = "reactionTime"
    VEHICLE_REACTION_TIME_AT_SEMAPHORE_STRING = "reactionTimeAtSemaphore"
    VEHICLE_DAMPING_FACTOR_STRING = "dampingFactor"
    ROADS_STRING = "roads"
    ROAD_LENGTH_STRING = "length"
    ROAD_VEHICLE_DISTANCE_STRING = "vehicleDistance"
    ROAD_SPEED_LIMIT_STRING = "speedLimit"
    ROAD_IS_STARTING_ROAD_STRING = "isStartingRoad"
    SEMAPHORES_STRING = "semaphores"
    SEMAPHORE_POSITION_STRING = "position"
    SEMAPHORE_GREEN_LIGHT_STRING = "greenLight"
    SEMAPHORE_RED_LIGHT_STRING = "redLight"
    SEMAPHORE_YELLOW_LIGHT_STRING = "yellowLight"
    SEMAPHORE_START_TIME_STRING = "startTime"
    SEMAPHORE_ROAD_ID_STRING = "road"
    INTERSECTIONS_STRING = "intersections"
    INTERSECTION_POSITION_STRING = "position"
    INTERSECTION_INCOMING_ROADS_STRING = "inRoads"
    INTERSECTION_OUTGOING_ROADS_STRING = "outRoads"
    INTERSECTION_OUT_FLUXES_STRING = "outFluxes"
    
    def __init__(self, simulationCycles: int = 600, timeStep: int = 1, vehicleInjectionRate: int = 1, sectorLength: int = 100, simulationName: str = "simulation", log: bool = False):
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
        self.log = log
   
    def addVehicleType(self,length: int = 5, initialPos: int = 0, initialSpeed: int = 7, initialAcceleration: int = 0, maxSpeed: int = 7, maxAcceleration: float = 4, creationTime: int = 0, sigma: float = 0.0, reactionTime: float = 1.0, reactionTimeAtSemaphore: float = 1.0, dampingFactor: float = 0.18):
        self.vehicleTypes.append(Vehicle(self.vehicleTypeCount, length, initialPos, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime, sigma, reactionTime,reactionTimeAtSemaphore, dampingFactor))
        self.vehicleTypeCount += 1
        return self.vehicleTypes[-1]

    def addRoad(self, roadLenght: int = 1000, vehicleDistance: int = 1, speedLimit: int = 50/3.6, isStartingRoad: bool = False, shape: Shape = None):
        road = Road(self.roadCount, roadLenght, vehicleDistance, speedLimit, None, None, None, 0, shape)
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
                    veh = Vehicle(self.vehicleCount, vehicle.length, 0, vehicle.initialSpeed, vehicle.initialAcceleration, vehicle.maxSpeed, vehicle.maxAcceleration, time, vehicle.sigma, vehicle.reactionTime, vehicle.reactionTimeAtSemaphore, vehicle.dampingFactor)
                    road.addVehicle(veh,time)
                    self.vehicles.append(veh)
                    self.vehicleCount += 1

    def moveVehicles(self, time):
        roads = sorted(self.roads, key=lambda road: road.id, reverse=True)
        for road in roads:
            road.moveVehicles(time, self.timeStep)

    def simulate(self):
        os.makedirs("../output", exist_ok=True)
        output = "../output/%s_simulation_output_%i.txt" % (self.simulationName, self.simulationCycles)
        vehHistoryMetricsFile = "../output/%s_vehicles_metrics_%i.json" % (self.simulationName, self.simulationCycles)
        vehMetricsFile = "../output/%s_vehicles_metrics_%i.txt" % (self.simulationName, self.simulationCycles)
        roadsMetricsJsonFile = "../output/%s_road_metrics_%i.json" % (self.simulationName, self.simulationCycles)
        mapHistoryFile = "../output/%s_map_history_%i.json" % (self.simulationName, self.simulationCycles)
        if self.log:
            f = open(vehMetricsFile, "w+")
            f2 = open(output, "w+")
            #f3 = open(vehHistoryMetricsFile, "w+")
        self.history = MapHistory(self.roads, self.sectorLength)
        for i in range(self.simulationCycles):
            time = i * self.timeStep
            if self.log:
                print("Time: %ds" % time, file=f2)
            self.injectVehicles(time, i)
            self.moveVehicles(time)
            self.history.saveState(time)
            print("Cycle %d/%d" % (i,self.simulationCycles), end="\r")
            if self.log:
                roads = None
                if self.roads is not None:
                    roads = sorted(self.roads, key=lambda road: road.id, reverse=True)
                for road in roads:
                    for s in road.semaphores:
                        print("Semaphore in road %d at %dm: %s" % (road.id, s.position, s.getState(time)), file=f2)
                for road in roads:
                    for vehicle in self.vehicles:
                        if road.hasVehicle(vehicle):
                            print("Vehicle %d: pos: %d/%dm, speed: %dm/s (%dkm/h), acc: %dm/s^2, in road %d, State: %s, Arrived: %s, currentDelay: %s, cumulativeDelay: %s" % (vehicle.id, vehicle.position, road.length, vehicle.speed, vehicle.speed*3.6, vehicle.acceleration, road.id, vehicle.state, vehicle.isArrived(), vehicle.currentDelay, vehicle.cumulativeDelay), file=f2)
                print("Arrived Vehicles: %d" % len([vehicle for vehicle in self.vehicles if vehicle.isArrived()]), file=f2)
                arrivedVehs = [vehicle for vehicle in self.vehicles if vehicle.isArrived()]
                if arrivedVehs:
                    arrivedVehs.sort(key=lambda vehicle: vehicle.arrivalTime)
                for vehicle in arrivedVehs:
                    print("%d:%d, " % (vehicle.id, vehicle.arrivalTime), end="", file=f2)
                if arrivedVehs:
                    print("", file=f2)
        print("Simulation finished")
        print("Saving data...")
        if self.log:
            print("VEHICLES METRICS:", file=f)
            for vehicle in self.vehicles:
                if vehicle.isArrived():
                    print("Vehicle %d: " % vehicle.id, end="", file=f)
                    print(vehicle.getMetricsAsString(), file=f)
                    #print(Vehicle.getVehicleStateHistoryMetricsAsJSON(vehicle), file=f3, end=",\n")
            print()
            print("Simulation duration: %ds" % (self.simulationCycles * self.timeStep), file=f)
            print(Vehicle.getVehiclesMetricsAsString(self.vehicles), file=f)
        self.history.saveHistory(mapHistoryFile)
        self.history.saveMetrics(roadsMetricsJsonFile)
        Vehicle.saveVehiclesStateHistoryGroupedByTime(self.vehicles, vehHistoryMetricsFile)
        abspath = os.path.abspath(vehHistoryMetricsFile)
        print("Data saved to %s" % abspath)
        if self.log:
            f.close()
            f2.close()
            #f3.close()

    def getSimulationFromJSON(filename):
        if not Path(filename).is_file():
            print("File %s does not exist" % filename)
            return
        # check JSON schema here
        try:
            jsonschema.validate(instance=json.load(open(filename, "r")), schema=json.load(open("simulation_schema.json", "r")))
        except jsonschema.exceptions.ValidationError as e:
            print("well-formed but invalid JSON:", e)
            return
        except json.decoder.JSONDecodeError as e:
            print("poorly-formed text, not JSON:", e)
            return
        with open(filename, "r") as f:
            data = json.load(f)
            simInfo = data[Simulation.SIMULATION_INFO_STRING]
            simName = simInfo[Simulation.SIMULATION_NAME_STRING]
            simCycles = simInfo[Simulation.SIMULATION_CYCLES_STRING]
            timeStep = simInfo[Simulation.TIME_STEP_STRING] if Simulation.TIME_STEP_STRING in simInfo else 1
            vehicleInjectionRate = simInfo[Simulation.VEHICLE_INJECTION_RATE_STRING] if Simulation.VEHICLE_INJECTION_RATE_STRING in simInfo else 1
            sectorLength = simInfo[Simulation.SECTOR_LENGTH_STRING]
            simulation = Simulation(simCycles, timeStep, vehicleInjectionRate, sectorLength, simName)

            for vehicle in data[Simulation.VEHICLES_STRING]:
                len = vehicle[Simulation.VEHICLE_LENGTH_STRING]
                initialPos = vehicle[Simulation.VEHICLE_INITIAL_POS_STRING] if Simulation.VEHICLE_INITIAL_POS_STRING in vehicle else 0
                initialSpeed = vehicle[Simulation.VEHICLE_INITIAL_SPEED_STRING]
                initialAcceleration = vehicle[Simulation.VEHICLE_INITIAL_ACCELERATION_STRING]
                maxSpeed = vehicle[Simulation.VEHICLE_MAX_SPEED_STRING]
                maxAcceleration = vehicle[Simulation.VEHICLE_MAX_ACCELERATION_STRING]
                creationTime = vehicle[Simulation.VEHICLE_CREATION_TIME_STRING] if Simulation.VEHICLE_CREATION_TIME_STRING in vehicle else 0
                sigma = vehicle[Simulation.VEHICLE_SIGMA_STRING] if Simulation.VEHICLE_SIGMA_STRING in vehicle else 0.0
                reactionTime = vehicle[Simulation.VEHICLE_REACTION_TIME_STRING] if Simulation.VEHICLE_REACTION_TIME_STRING in vehicle else 1.0
                reactionTimeAtSemaphore = vehicle[Simulation.VEHICLE_REACTION_TIME_AT_SEMAPHORE_STRING] if Simulation.VEHICLE_REACTION_TIME_AT_SEMAPHORE_STRING in vehicle else 1.0
                dampingFactor = vehicle[Simulation.VEHICLE_DAMPING_FACTOR_STRING] if Simulation.VEHICLE_DAMPING_FACTOR_STRING in vehicle else 0.18
                simulation.addVehicleType(len, initialPos, initialSpeed, initialAcceleration, maxSpeed, maxAcceleration, creationTime, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)

            for road in data[Simulation.ROADS_STRING]:
                length = road[Simulation.ROAD_LENGTH_STRING]
                vehicleDistance = road[Simulation.ROAD_VEHICLE_DISTANCE_STRING]
                speedLimit = road[Simulation.ROAD_SPEED_LIMIT_STRING]
                isStartingRoad = road[Simulation.ROAD_IS_STARTING_ROAD_STRING] if Simulation.ROAD_IS_STARTING_ROAD_STRING in road else False
                simulation.addRoad(length, vehicleDistance, speedLimit, isStartingRoad)
            
            for semaphore in data[Simulation.SEMAPHORES_STRING]:
                position = semaphore[Simulation.SEMAPHORE_POSITION_STRING]
                greenLight = semaphore[Simulation.SEMAPHORE_GREEN_LIGHT_STRING]
                redLight = semaphore[Simulation.SEMAPHORE_RED_LIGHT_STRING]
                yellowLight = semaphore[Simulation.SEMAPHORE_YELLOW_LIGHT_STRING] if Simulation.SEMAPHORE_YELLOW_LIGHT_STRING in semaphore else 0
                startTime = semaphore[Simulation.SEMAPHORE_START_TIME_STRING]
                roadId = semaphore[Simulation.SEMAPHORE_ROAD_ID_STRING]
                road = next((road for road in simulation.roads if road.id == roadId), None)
                simulation.addSemaphore(road, greenLight, redLight, position, yellowLight, startTime)

            for intersection in data[Simulation.INTERSECTIONS_STRING]:
                inRoads = intersection[Simulation.INTERSECTION_INCOMING_ROADS_STRING]
                outRoads = intersection[Simulation.INTERSECTION_OUTGOING_ROADS_STRING]
                outFluxes = intersection[Simulation.INTERSECTION_OUT_FLUXES_STRING]
                inRoads = []
                for r in inRoads:
                    inRoads.append(next((road for road in simulation.roads if road.id == r), None))
                outRoads = []
                for r in outRoads:
                    outRoads.append(next((road for road in simulation.roads if road.id == r), None))
                simulation.addIntersection(inRoads, outRoads, outFluxes)

            return simulation

#This is the main function that reads the JSON configuration file and runs the simulation
def main(argv):
    if len(argv) < 1:
        print("Please provide the filename of a JSON file with the simulation configuration")
        return
    try:
        simulation = Simulation.getSimulationFromJSON(argv[0])
        simulation.simulate()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)