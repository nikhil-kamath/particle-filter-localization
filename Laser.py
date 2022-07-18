from math import cos, dist, pi, sin
from typing import List, Tuple
import numpy as np
import pygame

from Robot import Robot

def uncertainty_add(distance, sigma):
    return np.random.normal(distance, sigma)

class Laser:
    def __init__(self, range: float, Map: pygame.Surface, uncertainty: float = .5, WALL_COLOR: Tuple[int, int, int] = (0, 0, 0), angles: List[float] = (0, pi/6, -pi/6)) -> None:
        self.range = range
        self.sigma = uncertainty
        
        self.Map = Map
        self.W, self.H = self.Map.get_size()
        
        self.WALL_COLOR = WALL_COLOR
        self.angles = angles
    
    def sense_obstacles(self, robot: Robot) -> List[float]:
        """sense walls in the "angles" directions

        Args:
            robot (Robot): robot from which obstacles are sensed
            angles (List[float], optional): angles to sense at. Defaults to (0, pi/6, -pi/6).
        """
        data = [-1] * len(self.angles)
        x1, y1 = robot.position

        sample_density = 1000
        # for each angle
        for index, angle in enumerate(self.angles):
            # calculate the end of the laser beam using the laser range
            dx, dy = self.range * cos(angle), self.range * sin(angle)


            # for many iterations along this laser
            for i in range(sample_density):
                u = i / sample_density
                x = int(x1 + u * dx)
                y = int(y1 + u * dy)

                # check this point for an obstacle
                if 0 <= x < self.W and 0 <= y < self.H:
                    color = self.Map.get_at((x, y))

                    if color == self.WALL_COLOR:
                        # pygame.draw.circle(self.Map, (0, 255, 0), (x, y), 5)
                        distance = dist(robot.position, (x, y))
                        output = uncertainty_add(distance, self.sigma)
                        data[index] = output
                        break
                
                # if no walls were hit, distance remains -1

        return data
            
            
            
    
    
