from math import cos, sin
from typing import Tuple
from Odometry import Linear, Angular
import numpy as np

class Robot:
    """class which allows for simulating where the robot thinks it is. 
    Also allows for different levels of errors in the measurements
    """
    def __init__(self, linear: Linear, angular: Angular, position: Tuple[int, int]=(0, 0), angle: int=0, v: float=.5, omega: float=.05) -> None:
        self.position = position # location
        self.angle = angle # turn angle, 0 degrees is to the right
        
        self.linear = linear # error distributions
        self.angular = angular
        
        self.v = v # speed
        self.o = omega # angular velocity
    
    def drive(self, dt):
        """simulates driving a certain distance based on the object's velocity parameter and angle.
        adds linear error according to the object's linear distribution

        Args:
            dt (_type_): time step
        """
        distance = self.v * dt
        sim_distance = self.linear.move(distance)
        
        dl = (sim_distance * cos(self.angle), sim_distance * sin(self.angle))
        
        self.position = np.add(self.position, dl)
    
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
        
        
        
        
        