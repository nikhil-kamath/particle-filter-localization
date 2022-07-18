from math import cos, pi, sin
from typing import Tuple
from Odometry import Linear, Angular
import numpy as np

class Robot:
    """class which allows for simulating where the robot thinks it is. 
    Also allows for different levels of errors in the measurements
    """
    def __init__(self, linear: Linear, angular: Angular, position: Tuple[int, int]=(0, 0), angle: int=0, v: float=.5, omega: float=.05, bounds: Tuple[int, int]=(540, 694)) -> None:
        self.position = position # location
        self.angle = angle # turn angle, 0 degrees is to the right
        
        self.linear = linear # error distributions
        self.angular = angular
        
        self.v = v # speed
        self.o = omega # angular velocity
        self.bounds = bounds
    
    def drive(self, dt):
        """simulates driving a certain distance based on the object's velocity parameter and angle.
        adds linear error according to the object's linear distribution

        Args:
            dt (_type_): time step
        """
        distance = self.v * dt
        sim_distance = self.linear.move(distance)
        
        dl = (sim_distance * cos(self.angle), sim_distance * sin(self.angle))
        
        new_position = np.add(self.position, dl)
        new_x, new_y = new_position
        if new_x < 0 or new_y < 0 or new_x >= self.bounds[0] or new_y >= self.bounds[1]:
            return
        self.position = new_position
    
    def turn(self, dt, clockwise: bool=False):
        """simulates turning a certain angle based on the object's turn velocity parameter.
        adds angular error according to the object's angular distribution

        Args:
            dt (_type_): time step
            clockwise (bool): direction to turn, False by default 
        """
        turn = self.o * dt
        sim_turn = self.angular.turn(turn)
        multiplier = int(clockwise) * -2 + 1 # clockwise is -1, ccw is 1
        self.angle += sim_turn * multiplier
        self.angle %= 2*pi
        
        
        
        
        