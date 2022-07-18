from math import atan2, dist, exp, inf, pi
from typing import List, Tuple
from scipy.stats import norm
import numpy as np
from Odometry import Angular, Linear

from Robot import Robot


class Sensor:
    """Class to create noisy measures of angle and distance to each landmark
    """
    def __init__(self, mean_d=0, sd_d=0, mean_a=0, sd_a=0, range=inf) -> None:
        self.mean_d = mean_d
        self.sd_d = sd_d
        self.mean_a = mean_a
        self.sd_a = sd_a
        # self.range = range # range not implemented yet
    
    def measure_landmarks(self, landmarks: List[Tuple[int, int]], robot: Robot) -> List[Tuple[float, float]]:
        measurements = []
        for l in landmarks:
            true_distance = dist(l, robot.position)
            true_angle = atan2((l[1]-robot.position[1]),
                               (l[0]-robot.position[0]))
            
            measured_distance = true_distance + np.random.normal(self.mean_d, self.sd_d)
            measured_angle = true_angle + np.random.normal(self.mean_a, self.sd_a)
            measurements.append((measured_distance, measured_angle))
        
        return measurements

def gaussian(measured, ideal, sd):
    standard = ((measured-ideal)/sd)
    return 2*CNDF(-abs(standard))

def CNDF(x):
    neg = 0 if x >= 0 else 1
    if neg:
        x *= -1
        
    k = (1. / (1. + 0.2316419 * x))
    y = ((((1.330274429 * k - 1.821255978) * k + 1.781477937) * k - 0.356563782) * k + 0.319381530) * k
    y = 1.0 - 0.398942280401 * exp(-0.5 * x * x) * y

    return (1. - neg) * y + neg * (1. - y)

def probability(sensor: Sensor, measured_dist: float, measured_angle: float, true_dist, true_angle) -> float:
    return gaussian(measured_dist, true_dist, sensor.sd_d) * gaussian(measured_angle, true_angle, sensor.sd_a)



# t = Sensor(0, 30, 0, .1)
# r = Robot(Linear(), Angular())
# print(probability(t, *(238.72568204477818, -0.8657324954920482),
#       *(274.73636653242716, -0.008318086185669954)))

# print(gaussian(238.72568204477818, 274.73636653242716, 30))
