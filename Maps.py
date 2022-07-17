from typing import List, Tuple
import pygame


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

    return loc
