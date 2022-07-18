from math import dist, pi
from time import sleep
import numpy as np
import pygame
from typing import List, Tuple
from Laser import Laser
from Maps import check_continue, check_movements, draw_robot, scatter_robots
from Sensors import Sensor, gaussian
from Robot import Robot
from Odometry import Linear, Angular

def simulation(Map: pygame.Surface, TrueSurface: pygame.Surface, SimSurface: pygame.Surface,
                    true_surface_location: Tuple[int, int], sim_surface_location: Tuple[int, int],
                    true_robot: Robot, WALL_COLOR: Tuple[int, int, int]=(0, 0, 0), exit_key=pygame.K_RETURN, N=1000,
                    sim_odometry: Tuple[Linear, Angular] = None, sim_laser: Laser=None, true_laser: Laser=None):

    true_surface_copy = TrueSurface.copy()
    sim_surface_copy = SimSurface.copy()
    
    if sim_odometry is None:
        sim_odometry = (Linear(0, .01), Angular(0, .01))
    if sim_laser is None:
        sim_laser = Laser(500, true_surface_copy, WALL_COLOR=WALL_COLOR, angles=(0, pi/12, pi/6, pi/4, -pi/12, -pi/6, -pi/4))
    if true_laser is None:
        true_laser = sim_laser
        
    sim_robots = [Robot(*sim_odometry) for _ in range(N)]
    scatter_robots(sim_robots, TrueSurface.get_size())
    # sim_robots[0].position = np.add(true_robot.position, (50, 0))
    
    running = True
    while running:
        running = check_continue(key=exit_key)
        
        new_true_surface = true_surface_copy.copy()
        new_sim_surface = sim_surface_copy.copy()
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            true_reading = true_laser.sense_obstacles(true_robot)
            sim_readings = [sim_laser.sense_obstacles(sim) for sim in sim_robots]
            print("true reading:", true_reading)
            # print("sim readings:", sim_readings)
            similarity_list = similarities(true_reading, sim_readings, sim_laser.sigma)
            
            # print("similarities:", similarity_list)
            

            for sim_robot, s, reading in zip(sim_robots, similarity_list, sim_readings):
                if s > np.percentile(similarity_list, 90):
                    print("sim reading:", reading, end=" ")
                    print("similarity", s)
                    if s > np.percentile(similarity_list, 95):
                        pygame.draw.circle(sim_surface_copy, (100, 255, 100), sim_robot.position, 15)
                    else:
                        pygame.draw.circle(sim_surface_copy, (200, 255, 200), sim_robot.position, 15)
            
            pygame.display.update()
            sleep(1)
            

        forward, ccw, cw = check_movements()

        if forward:
            for robot in (true_robot, *sim_robots):
                robot.drive(.1)
        if cw != ccw:
            for robot in (true_robot, *sim_robots):
                robot.turn(.1, cw)

        draw_robot(new_true_surface, true_robot, true_robot=True)
        for sim in sim_robots:
            draw_robot(new_sim_surface, sim, true_robot=False)

        Map.blit(new_true_surface, true_surface_location)
        Map.blit(new_sim_surface, sim_surface_location)

        pygame.display.update()
            
def similarity(ideal, sim, sigma):
    product = 1
    for ideal_measurement, sim_measurement in zip(ideal, sim):
        if ideal_measurement == -1 == sim_measurement:
            product *= .5
        elif ideal_measurement != -1 and sim_measurement == -1: # if the simulated one didn't see the wall at all itll basically make it 0
            product *= .05
        elif ideal_measurement == -1 and sim_measurement != -1:
            product *= .01
        else:
            # product *= gaussian(sim_measurement, ideal_measurement, sigma * 10) + .1
            product *= 1/(dist(ideal, sim) / 35)
    return product * 10 ** len(sim)
        

            
def similarities(ideal, sims, sigma):
    return [similarity(ideal, sim, sigma) for sim in sims]
