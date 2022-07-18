from math import cos, sin
from random import randrange
from typing import List, Tuple

import numpy as np
from Odometry import Angular, Linear
from Robot import Robot
import pygame

from Sensors import Sensor, probability


def draw_points(Map: pygame.Surface, points, color=(255, 0, 0), radius=3):
    for p in points: pygame.draw.circle(Map, color, p, radius)

def draw_on_surface(Map: pygame.Surface, Target: pygame.Surface, target_location: Tuple[int, int], exit_key=pygame.K_RETURN, BG=(255, 255, 255)) -> List[Tuple[int, int]]:
    """Allows user to draw points on a surface which is displayed on the main map

    Args:
        Map (pygame.Surface): The main map which is displayed on pygame.display.update()
        Target (pygame.Surface): The subsurface which the user can draw on
        target_location (tuple[int, int]): the location where Target is blit'd onto the main map
        exit_key (_type_, optional): key to exit this loop. Defaults to pygame.K_RETURN.
        BG (tuple, optional): background to add on target surface every frame. Defaults to (255, 255, 255).

    Returns:
        List[Tuple[int, int]]: list of points drawn
    """
    
    Target.fill(BG)
    running = True
    points = []
    while running:
        running = check_continue(key=exit_key)
        
        focused = pygame.mouse.get_focused()
        clicked = pygame.mouse.get_pressed()[0]
        
        if focused and clicked:
            position = pygame.mouse.get_pos()
            
            # if the click was on the subsurface
            if target_location[0] <= position[0] < target_location[0] + Target.get_width() and target_location[1] <= position[1] < target_location[1] + Target.get_height():
                target_point = (position[0] - target_location[0], position[1] - target_location[1])
                pygame.draw.circle(Target, (255, 0, 0), target_point, 3)
                if position not in points:
                    points.append(position)
                
                Map.blit(Target, target_location)
        
        pygame.display.update()
    
    return points

def end_loop(key=pygame.K_RETURN) -> None:
    """Loop which shows map until exit key is pressed

    Args:
        key (_type_, optional): _description_. Defaults to pygame.K_RETURN.
    """
    
    running = True
    while running:
        running = check_continue(key=key)
        pygame.display.update()
        
def check_continue(key=pygame.K_RETURN) -> bool:
    """checks if key was pressed

    Args:
        key (_type_, optional): key which exits. Defaults to pygame.K_RETURN.

    Returns:
        bool: returns whether the process should continue running (if the key was NOT pressed)
    """
    
    return not any(event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == key) for event in pygame.event.get())
        
def check_movements() -> Tuple[bool, bool, bool]:
    """Checks for pressing of the 3 movement keys

    Returns:
        List[bool, bool, bool]: first key represents moving forwards, second is turning ccw, third is turning cw
        NOTE: ccw and cw are backwards in this entire program. though the controls seem normal, the logic is based on this flip
    """
    keys = pygame.key.get_pressed()
    return (keys[pygame.K_w], keys[pygame.K_d], keys[pygame.K_a]) # NOTE: these are flipped since the origin is at the TOP. Ensures sin/cos still work properly

def place_robot(Map: pygame.Surface, Target: pygame.Surface, target_location: Tuple[int, int], exit_key=pygame.K_RETURN) -> List[Tuple[int, int]]:
    """Allows user to place robot in a location

    Args:
        Map (pygame.Surface): The main map which is displayed on pygame.display.update()
        Target (pygame.Surface): The subsurface which the user can draw on
        target_location (tuple[int, int]): the location where Target is blit'd onto the main map
        exit_key (_type_, optional): key to exit this loop. Defaults to pygame.K_RETURN.
        BG (tuple, optional): background to add on target surface every frame. Defaults to (255, 255, 255).

    Returns:
        List[Tuple[int, int]]: list of points drawn
    """
    blank = Target.copy()
    running = True
    loc = (0, 0)
    while running:
        running = check_continue(key=exit_key)

        focused = pygame.mouse.get_focused()
        clicked = pygame.mouse.get_pressed()[0]

        if focused and clicked:
            position = pygame.mouse.get_pos()

            # if the click was on the subsurface
            if target_location[0] <= position[0] < target_location[0] + Target.get_width() and target_location[1] <= position[1] < target_location[1] + Target.get_height():
                target_point = (
                    position[0] - target_location[0], position[1] - target_location[1])
                
                new_map = blank.copy()
                pygame.draw.circle(new_map, (0, 255, 0), target_point, 5)
                Map.blit(new_map, target_location)

                loc = target_point

        pygame.display.update()

    return loc, blank

def draw_robot(Target: pygame.Surface, r: Robot, true_robot=True):
    robot_color = (200, 200, 255) if true_robot else (255, 200, 200)
    
    pygame.draw.circle(Target, robot_color, r.position, 10)
    x, y = r.position
    length = 8
    x2 = x + length * cos(r.angle)
    y2 = y + length * sin(r.angle)
    pygame.draw.line(Target, (0, 0, 0), r.position, (x2, y2), width=3)    

def draw_walls(Map: pygame.Surface, Target: pygame.Surface, target_location: Tuple[int, int], exit_key=pygame.K_RETURN, hint_color=(0, 255, 0), wall_color=(0, 0, 0), width=3) -> List[Tuple[Tuple[int, int]]]:
    walls = []

    running = True
    drawing = None
    while running:
        pygame.time.delay(5)
        running = check_continue(exit_key)

        focused = pygame.mouse.get_focused()
        left_click = pygame.mouse.get_pressed()[0]
        right_click = pygame.mouse.get_pressed()[2]
        position = (pygame.mouse.get_pos()[0] - target_location[0], pygame.mouse.get_pos()[1] - target_location[1])
        
        if focused:
            # on the initial left click, save the first point as drawing
            if drawing:
                Target.blit(before_line, (0, 0))

                # we can use right click to cancel this line
                if right_click:
                    drawing = None
                    Map.blit(before_line, target_location)

                # drawing dotted lines while user is still dragging mouse
                elif left_click:
                    pygame.draw.line(Target, hint_color,
                                     drawing, position, width=width)
                    Map.blit(Target, target_location)

                # when user lets go of left click, draw our actual line
                else:
                    pygame.draw.line(Target, wall_color,
                                     drawing, position, width=width)
                    Map.blit(Target, target_location)
                    walls.append((drawing, position))
                    drawing = None

            elif left_click:
                drawing = position
                before_line = Target.copy()

        pygame.display.update()

    return walls

def move_loop(Map: pygame.Surface, Target: pygame.Surface, target_location: Tuple[int, int], robots: List[Robot], exit_key=pygame.K_RETURN):
    blank = Target.copy()
    
    running = True
    while running:        
        running = check_continue(exit_key)
        
        forward, ccw, cw = check_movements()
        
        new = blank.copy()
        if forward:
            for robot in robots:
                robot.drive(.1)
        if ccw != cw:
            for robot in robots:
                robot.turn(.1, cw)
        
        for index, robot in enumerate(robots):        
            draw_robot(new, robot, true_robot = not bool(index))
            
        Map.blit(new, target_location)
        
        pygame.display.update()


def scatter_robots(robots: List[Robot], dims: Tuple[int, int]) -> None:
    """randomize location of robots

    Args:
        robots (List[Robot]): robots
    """
    
    for r in robots:
        x, y = randrange(0, dims[0]), randrange(0, dims[1])
        r.position = (x, y)

    
