"""
@file    simulation.py
@author  David Megli
"""

from vehicle import Vehicle
from map import Road

#class TrafficSimulator:
    




def simulate():

    road = Road(0, 3, 300, 300/6) #id, numSectors, length, capacity, each sector is 100m long and can hold 50 vehicles (5m lenght + 1 ms gap between vehicles)
    car = Vehicle(0, 5, 10, 0, 13.89, 0.8) #id, length, initialSpeed, initialPosition, maxSpeed, maxAcceleration
    # in this example the car is 5m long, starts at position 0m, with an initial speed of 10m/s (36 km/h), max speed of 50 km/h and max acceleration of 0.8 m/s^2
    # the road is 300m long and has 3 sectors, each sector is 100m long and can hold 50 vehicles (5m lenght + 1 ms gap between vehicles)
    #road.add_vehicle(car)
    for i in range(35):
        car.move()
        #printing car position and speed
        print ("%.2f\t%.2f" % (car.states[-1].position, car.states[-1].speed))
        


if __name__ == "__main__":
    simulate()