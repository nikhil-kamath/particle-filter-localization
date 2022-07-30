from math import dist, pi
import random
from time import sleep
import numpy as np
import pygame
from typing import List, Tuple
from Laser import Laser
from Maps import check_continue, check_movements, draw_robot, scatter_robots
from Robot import Robot
from Odometry import Linear, Angular


def simulation(Map: pygame.Surface, TrueSurface: pygame.Surface, SimSurface: pygame.Surface,
               true_surface_location: Tuple[int, int], sim_surface_location: Tuple[int, int],
               true_robot: Robot, WALL_COLOR: Tuple[int, int, int] = (0, 0, 0), exit_key=pygame.K_RETURN, N=100,
               sim_odometry: Tuple[Linear, Angular] = None, sim_laser: Laser = None, true_laser: Laser = None):
    """runs the main simulation on the 2 screens

    Args:
        Map (pygame.Surface): main pygame surface, where everything else is overlayed
        TrueSurface (pygame.Surface): surface where only the true robot's locations are displayed. must have walls
        SimSurface (pygame.Surface): surface where simulation robots are displayed. should have the same walls as TrueSurface
        true_surface_location (Tuple[int, int]): location where TrueSurface is Blit'd 
        sim_surface_location (Tuple[int, int]): location where SimSurface is blit'd
        true_robot (Robot): true robot object
        WALL_COLOR (Tuple[int, int, int], optional): color of walls in TrueSurface. Defaults to (0, 0, 0).
        exit_key (_type_, optional): key to continue. Defaults to pygame.K_RETURN.
        N (int, optional): number of simulation robots. Defaults to 100.
        sim_odometry (Tuple[Linear, Angular], optional): odometry for error in simulation robots. Defaults to None.
        sim_laser (Laser, optional): laser sensor for simulation robots. Defaults to None.
        true_laser (Laser, optional): laser sensor for true robot. Defaults to None.
    """

    redistribute_frequency, RF = 1000, 1000
    
    hint = pygame.font.SysFont("Monaco", 25)
    hint_box = hint.render(
        "move with W, A, D. estimate location with SPACE.", True, (200, 200, 200))

    Map.blit(TrueSurface, true_surface_location)
    Map.blit(SimSurface, sim_surface_location)
    true_surface_blank = TrueSurface.copy()
    sim_surface_blank = SimSurface.copy()

    if sim_odometry is None:
        sim_odometry = (Linear(0, .01), Angular(0, .005))
    if sim_laser is None:
        sim_laser = Laser(500, true_surface_blank, WALL_COLOR=WALL_COLOR, angles=(
            0, pi/12, pi/6, pi/4, -pi/12, -pi/6, -pi/4))
    if true_laser is None:
        true_laser = sim_laser

    sim_robots = [Robot(*sim_odometry) for _ in range(N)]
    scatter_robots(sim_robots, TrueSurface.get_size())

    running = True
    while running:
        pygame.time.wait(int(1/30*100))
        running = check_continue(key=exit_key)

        # redistribution key
        if pygame.key.get_pressed()[pygame.K_SPACE] or redistribute_frequency < 0:
            redistribute_frequency = RF
            
            # calculate the readings at the true robot's location and each of the simulated ones
            true_reading = true_laser.sense_obstacles(true_robot)
            sim_readings = [sim_laser.sense_obstacles(sim) for sim in sim_robots]

            # calculate the similarities between the readings
            similarity_list = similarities(true_reading, sim_readings, sim_laser.sigma)

            # draw permanent green circles around the most similar poses
            for sim_robot, s, reading in zip(sim_robots, similarity_list, sim_readings):
                if s > np.percentile(similarity_list, 90):
                    if s > np.percentile(similarity_list, 95):
                        pygame.draw.circle(
                            sim_surface_blank, (100, 255, 100), sim_robot.position, 15)
                    else:
                        pygame.draw.circle(
                            sim_surface_blank, (200, 255, 200), sim_robot.position, 15)

            pygame.display.update()
            redistribute(sim_robots, similarity_list, SimSurface.get_size())
            sleep(1/30)

        # apply movements 
        new_true_surface = true_surface_blank.copy() # create copies of the blank maps
        new_sim_surface = sim_surface_blank.copy()
        apply_movements(Map, new_true_surface, new_sim_surface,
                        true_surface_location, sim_surface_location,
                        true_robot, sim_robots)

        # put instructions at bottom of the screen
        Map.blit(hint_box, (Map.get_width()/4-hint_box.get_width() /
                 2, Map.get_height() - 1.5 * hint_box.get_height()))

        pygame.display.update()


def apply_movements(Map: pygame.Surface, left_blank: pygame.Surface, right_blank: pygame.Surface, left_coords: Tuple[int, int], 
                    right_coords: Tuple[int, int], true_robot: Robot, sim_robots: List[Robot]) -> None:
    """applies movements using controls each frame. 

    Args:
        Map (pygame.Surface): main map
        left_blank (pygame.Surface): a copy of the left, true side of the screen, with walls and without any robots
        right_blank (pygame.Surface): same as left_blank
        left_coords (Tuple[int, int]): location where left is blit'd onto map
        right_coords (Tuple[int, int]): location where right is blit'd onto map
        true_robot (Robot): true robot object
        sim_robots (List[Robot]): list of simulated robots
    """
    forward, ccw, cw = check_movements()

    if forward:
        for robot in (true_robot, *sim_robots):
            robot.drive(.5)
    if cw != ccw:
        for robot in (true_robot, *sim_robots):
            robot.turn(.5, cw)

    draw_robot(left_blank, true_robot, true_robot=True)
    for sim in sim_robots:
        draw_robot(right_blank, sim, true_robot=False)

    Map.blit(left_blank, left_coords)
    Map.blit(right_blank, right_coords)

def similarity(ideal, sim, sigma):
    product = 1
    for ideal_measurement, sim_measurement in zip(ideal, sim):
        if ideal_measurement == -1 == sim_measurement:
            product *= .5
        # if the simulated one didn't see the wall at all itll basically make it 0
        elif ideal_measurement != -1 and sim_measurement == -1:
            product *= .05
        elif ideal_measurement == -1 and sim_measurement != -1:
            product *= .01
        else:
            # product *= gaussian(sim_measurement, ideal_measurement, sigma * 10) + .1
            product *= 1/(dist(ideal, sim) / 35)
    return product * 10 ** len(sim)


def similarities(ideal, sims, sigma):
    return [similarity(ideal, sim, sigma) for sim in sims]


def redistribute(sim_robots: List[Robot], s_list: List[float], dims: Tuple[int, int], scatter_factor: float = .1, abandon_factor: float = 100, distance_spread: float = 25, angle_spread: float = pi/24) -> None:
    if max(s_list) < abandon_factor:
        scatter_robots(sim_robots, dims)
        return

    similarity_sum = sum(s_list)

    coords = [r.position for r in sim_robots]
    angles = [r.angle for r in sim_robots]

    for r in sim_robots:
        if random.random() < scatter_factor:
            r.position = (random.randrange(
                0, dims[0]), random.randrange(0, dims[1]))

        else:
            ran = random.random() * similarity_sum
            current_sum = s_list[0]
            current_index = 0
            while current_sum < ran:
                current_index += 1
                current_sum += s_list[current_index]

            r.position = np.add(coords[current_index], (random.uniform(
                -distance_spread/2, distance_spread/2), random.uniform(-distance_spread/2, distance_spread/2)))
            
            r.angle = angles[current_index] + random.uniform(-angle_spread/2, angle_spread/2)
