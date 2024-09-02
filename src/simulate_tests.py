"""
@file    simulate.py
@authors  David Megli

Description:
This file simulates the movement of vehicles in a road, receiving a JSON file with the configuration of the simulation.
"""
from simulate import Simulation
from map import Shape, Coordinates, Semaphore
import sys

minVehicleSpeed = 7#40/3.6 #40 km/h in m/s
maxVehicleSpeed = 7#40/3.6
topVehicleSpeed = 150/3.6 #150 km/h in m/s
speedLimit = 100/3.6 #100 km/h in m/s
maxAcceleration = 4.0
vehicleLength = 5 #5m
startingPosition = 0
vehicleCount = 1000000
timeStep = 1 #cycle steps in seconds
injectingRateForRoad = 2 #instantiate one vehicle every x cycles
sectorsPerRoad = 10 #number of sectors in the road
roadLength = 500 #meters
singleRoadLen = 1000
simulationCycles = 600
greenLight = 40 #seconds
redLight = 20 #seconds
reactionTime = 1.0
reactionTimeAtSemaphore = 1.0
dampingFactor = 0.18 # fattore di smorzamento per il calcolo dei tempi di reazione nelle code
sigma = 0.00
vehicleDistance = 1.0

#The following functions are used to simulate the scenarios described in the report without using the JSON configuration file
def single_road():
    simulationName = "1_single_road_sim"
    simulation = Simulation(simulationCycles, timeStep, injectingRateForRoad, roadLength / sectorsPerRoad, simulationName)
    road = simulation.addRoad(singleRoadLen, vehicleDistance, speedLimit, True)
    road.setShape(Shape([Coordinates(0,0), Coordinates(singleRoadLen,0)]))
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

def single_road_semaphore():
    simulationName = "2_single_road_semaphore_sim"
    simulation = Simulation(simulationCycles, timeStep, injectingRateForRoad, roadLength / sectorsPerRoad, simulationName)
    semaphore = Semaphore(greenLight, redLight, 800, 0, 0)
    road = simulation.addRoad(singleRoadLen, vehicleDistance, speedLimit, True)
    road.setShape(Shape([Coordinates(0,0), Coordinates(singleRoadLen,0)]))
    road.addSemaphore(semaphore)
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

def merge_sem():
    green = 30
    red = 30
    delay1 = red
    simulationName = "4_merge_sem_sim"
    n_roads = 2
    injectionRate = 5
    simulationCycles = 10
    simulation = Simulation(simulationCycles, timeStep, injectionRate, roadLength / sectorsPerRoad, simulationName)
    semaphore1 = Semaphore(green, red, roadLength, 0, delay1)
    semaphore2 = Semaphore(green, red, roadLength, 0, 0)
    inRoads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, n_roads, True)
    inRoads[0].setShape(Shape([Coordinates(0,roadLength/(2**0.5)), Coordinates(roadLength/(2**0.5),0)]))
    inRoads[1].setShape(Shape([Coordinates(0,-roadLength/(2**0.5)), Coordinates(roadLength/(2**0.5),0)]))
    inRoads[0].addSemaphore(semaphore1)
    inRoads[1].addSemaphore(semaphore2)
    outRoads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 1)
    outRoads[0].setShape(Shape([Coordinates(roadLength/(2**0.5),0), Coordinates(2*roadLength,0)]))
    print("Road 1) from x: %d, y: %d to x: %d, y: %d" % (0, roadLength/(2**0.5), roadLength, 0))
    print("Road 2) from x: %d, y: %d to x: %d, y: %d" % (0, -roadLength/(2**0.5), roadLength, 0))
    print("Road 3) from x: %d, y: %d to x: %d, y: %d" % (roadLength, 0, 2*roadLength, 0))
    merge = simulation.addIntersection(inRoads, outRoads, [1])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

def bifurcation():
    simulationName = "3_bifurcation_sim"
    injectingRate = 3
    simulation = Simulation(simulationCycles, timeStep, injectingRate, roadLength / sectorsPerRoad, simulationName)
    inroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 1, True)
    inroads[0].setShape(Shape([Coordinates(0,0), Coordinates(roadLength,0)]))
    outroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 2)
    outroads[0].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),roadLength/(2**0.5))]))
    outroads[1].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),-roadLength/(2**0.5))]))
    bifurcation = simulation.addIntersection(inroads, outroads, [0.8, 0.2])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

def bifurcation_sem():
    simulationName = "5_bifurcation_sem_sim"
    injectionRate = 5
    simulation = Simulation(simulationCycles, timeStep, injectionRate, roadLength / sectorsPerRoad, simulationName)
    semaphore = Semaphore(greenLight, redLight, 500, 0, 0)
    inroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 1, True)
    inroads[0].setShape(Shape([Coordinates(0,0), Coordinates(roadLength,0)]))
    inroads[0].addSemaphore(semaphore)
    outroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 2)
    outroads[0].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),roadLength/(2**0.5))]))
    outroads[1].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),-roadLength/(2**0.5))]))
    bifurcation = simulation.addIntersection(inroads, outroads, [0.5, 0.5])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

def bifurcation_sem_high_flow():
    simulationName = "6_bifurcation_sem_high_flow_sim"
    injectionRate = 2
    simulation = Simulation(simulationCycles, timeStep, injectionRate, roadLength / sectorsPerRoad, simulationName)
    semaphore = Semaphore(greenLight, redLight, 500, 0, 0)
    inroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 1, True)
    inroads[0].setShape(Shape([Coordinates(0,0), Coordinates(roadLength,0)]))
    inroads[0].addSemaphore(semaphore)
    outroads = simulation.addRoads(roadLength, vehicleDistance, speedLimit, 2)
    outroads[0].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),roadLength/(2**0.5))]))
    outroads[1].setShape(Shape([Coordinates(roadLength,0), Coordinates(roadLength+roadLength/(2**0.5),-roadLength/(2**0.5))]))
    bifurcation = simulation.addIntersection(inroads, outroads, [0.5, 0.5])
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()

'''def road_different_speeds():
    simulationName = "7_road_different_speeds_sim"
    injectionRate = 2
    simulation = Simulation(simulationCycles, timeStep, injectionRate, roadLength / sectorsPerRoad, simulationName)
    road1 = simulation.addRoad(roadLength, vehicleDistance, speedLimit, True)
    road2 = simulation.addRoad(roadLength, vehicleDistance, topVehicleSpeed, False)
    simulation.addVehicleType(vehicleLength, startingPosition, minVehicleSpeed, 0, maxVehicleSpeed, maxAcceleration, 0, sigma, reactionTime, reactionTimeAtSemaphore, dampingFactor)
    simulation.simulate()'''

#This is the main function that reads the JSON configuration file and runs the simulation
def main(argv):
    if len(argv) < 1:
        while True:
            # Asking to the user which of the 6 test cases to run
            print("Test Cases:")
            print("1) Single road (Segmento Stradale)")
            print("2) Single road with semaphore (Segmento Stradale con semaforo)")
            print("3) Bifurcation (Biforcazione stradale)")
            print("4) Merge with semaphore (Congiunzione strade con semaforo)")
            print("5) Bifurcation with semaphore (Biforcazione con semaforo)")
            print("6) Bifurcation with semaphore, high flow (Biforcazione con semaforo, flusso elevato)")
            print("")
            choice = input("Enter the number of the test case to run: ")
            if choice == "1":
                single_road()
                break
            elif choice == "2":
                single_road_semaphore()
                break
            elif choice == "3":
                bifurcation()
                break
            elif choice == "4":
                merge_sem()
                break
            elif choice == "5":
                bifurcation_sem()
                break
            elif choice == "6":
                bifurcation_sem_high_flow()
                break
            else:
                print("Invalid choice")
    else:
        if argv[0] == "1":
            single_road()
        elif argv[0] == "2":
            single_road_semaphore()
        elif argv[0] == "3":
            bifurcation()
        elif argv[0] == "4":
            merge_sem()
        elif argv[0] == "5":
            bifurcation_sem()
        elif argv[0] == "6":
            bifurcation_sem_high_flow()
        else:
            print("Invalid choice")

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)