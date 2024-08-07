
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import json

#filename = "../output/4_merge_sem_sim_vehicles_metrics_600.json"
def parse_coords(filename):
    # I parse the file simulation.json to get the points to plot
    # In the json, for each time there is a number of vehicles, each with its coordinates
    # I have a dictionary indexed by time, and each value is a list of tuples (x, y) with the coordinates of the vehicles
    with open(filename, 'r') as f:
        data = json.load(f)
    coords = {}
    for v in data["vehiclesHistory"]:
        time = v["Time"]
        if time not in coords:
            coords[time] = []
        for veh in v["VehiclesStates"]:
            coords[time].append((veh["CoordX"], veh["CoordY"]))
    return coords

def get_min_max_coords(coords):
    minX = 100
    minY = 100
    maxX = -100
    maxY = -100
    for time in coords:
        for coord in coords[time]:
            if coord[0] < minX:
                minX = coord[0]
            if coord[1] < minY:
                minY = coord[1]
            if coord[0] > maxX:
                maxX = coord[0]
            if coord[1] > maxY:
                maxY = coord[1]
    return minX, minY, maxX, maxY

def main(args):
    coords = parse_coords(args[0])
    fig, ax = plt.subplots()
    #I change the size of the figure
    fig.set_size_inches(10, 10)
    x = []
    y = []
    minX, minY, maxX, maxY = get_min_max_coords(coords)
    def update(frame):
        ax.clear()
        ax.set_xlim(minX, maxX)
        ax.set_ylim(minY, maxY)
        for coord in coords[frame]:
            x.append(coord[0])
            y.append(coord[1])
        ax.scatter(x, y)
    ani = FuncAnimation(fig, update, frames=range(0, 600), repeat=True)
    plt.show()

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)