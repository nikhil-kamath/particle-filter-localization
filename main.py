import pygame
from Maps import draw_on_surface, end_loop

def main():
    pygame.init()
    
    # initializing constants
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    WIDTH, HEIGHT = 1080, 720
    HEADER_HEIGHT = 25
    pygame.font.init()
    font = pygame.font.SysFont("Monaco", HEADER_HEIGHT-5)
    
    # initializing base map
    pygame.display.set_caption("Particle Filter Localization")
    Map = pygame.display.set_mode((WIDTH, HEIGHT))
    Map.fill(WHITE)
    # halfway line
    pygame.draw.line(Map, BLACK, (WIDTH/2, 0), (WIDTH/2, HEIGHT),)
    pygame.draw.line(Map, BLACK, (0, HEADER_HEIGHT), (WIDTH, HEADER_HEIGHT),)
    left_header = font.render("True Scene", True, BLACK)
    right_header = font.render("Localization", True, BLACK)
    Map.blit(left_header, (WIDTH/4-left_header.get_width()/2, 10))
    Map.blit(right_header, (3*WIDTH/4-right_header.get_width()/2, 10))

    
    # allowing user to create map
    left = pygame.Surface((WIDTH/2, HEIGHT-HEADER_HEIGHT-1))
    location = (0, HEADER_HEIGHT+1)
    hint = pygame.font.SysFont('Monaco', 100)
    hint_box = hint.render('draw here', True, (150, 150, 150))
    Map.blit(hint_box, (WIDTH/4-hint_box.get_width()/2, (HEIGHT-HEADER_HEIGHT-hint_box.get_height())/2))
    points = draw_on_surface(Map, left, location)
    
    # putting another copy of the map on the right side
    Map.blit(left, (WIDTH/2+1, location[1]))
    
    end_loop()
    
    
if __name__ == "__main__":
    main()
    
    