# Snap4Simulator

## Introduction

Snap4Simulator is a traffic simulation tool developed in Python. Given an input of a road network and the desired traffic flow (in terms of vehicles per unit of time), the simulator outputs statistical data on traffic density, queue lengths, and the current state of each vehicle in the network. This output can be used as input for a visual simulator.

## Features

- **Input/Output**: The simulator accepts data in JSON format to configure the road network and vehicles, and produces output in JSON format containing traffic statistics and vehicle states.
- **Key Classes**:
  - **Vehicle**: Represents a vehicle and manages its characteristics and state.
  - **Road**: Models a road, contains a list of vehicles, and manages their movement.
  - **Junction**: Models a road intersection and manages vehicle direction.
  - **Semaphore**: Represents a traffic light and manages its phases (green, yellow, red).

## How It Works

The simulator iterates every second of the simulation, updating each vehicle's state based on the desired traffic flow. It handles vehicle behavior in relation to their position on the road, distance from other vehicles, traffic lights, and intersections.

### Simulation

The simulation is configurable via a JSON file that specifies roads, vehicles, traffic lights, and intersections. You can configure:
- **Roads**: Length, speed limit, vehicle safety distance, etc.
- **Vehicles**: Maximum speed, acceleration, reaction time, etc.
- **Traffic Lights**: Green, yellow, red times, position on the road.
- **Intersections**: Incoming and outgoing roads, turning probabilities.

## Simulation Examples

Example simulation configurations are provided for various scenarios, such as road segments with or without traffic lights, bifurcations, and intersections with high traffic flow. The simulation results can be compared with those obtained using the SUMO simulator, showing good agreement.

## Requirements
Python and jsonschema library are mandatory to execute the simulation
Note: python scripts and "simulation_schema.json" must be in the same folder.

matplotlib and numpy libraries are optional. They are only used to plot the output using the plot.py script

## Usage

To run a simulation, execute the `simulate.py` script and pass the JSON configuration file as an argument. e.g.:

```bash
python simulate.py simulation.json
```

The JSON file must follow the JSON schema "simulation_schema.json".

Complete instructions are provided in the pdf file inside the "Documents" folder.

You can run the 6 test cases described in the report by running simulate_tests.py in one of the following 2 ways:
1. Pass the test number as a parameter (integer between 1 and 6):
```bash
python simulate_tests.py <test_number>
```
2. Run the script without passing parameters, and choose the test to run by following the command line instructions:
```bash
python simulate_tests.py
```

The output files are saved by the program in the "/Snap4Simulator/output" folder

## Output
The simulator produces three types of JSON output files:

1. Road Statistics: Vehicle density per sector and queue lengths.
2. Vehicle Metrics: Travel time, number of stops, etc.
3. Vehicle State History: Position, speed, acceleration for each second of the simulation.
## Expansion and Scalability
Snap4Simulator is designed to be extensible, allowing for the simulation of complex and large-scale traffic scenarios. It supports the addition of new vehicle and road types and can be adapted to include elements such as pedestrian crossings, bike lanes, and more.