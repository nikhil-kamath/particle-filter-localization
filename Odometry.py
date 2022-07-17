import numpy as np

class Linear:
    """Class to simulate errors in movement forward
    """
    def __init__(self, mean, sd) -> None:
        self.mean = mean # usually 0
        self.sd = sd # some error
    
    def move(self, true_distance) -> float:
        return true_distance + np.random.normal(self.mean, self.sd)
    
class Angular:
    """Class to simulate errors in angle 
    """
    def __init__(self, mean, sd) -> None:
        self.mean = mean # usually 0 
        self.sd = sd # some error
    
    def turn(self, true_angle) -> float:
        return true_angle + np.random.normal(self.mean, self.sd)