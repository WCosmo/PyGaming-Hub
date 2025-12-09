# CONFIGURAÇÕES GLOBAIS
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
GRID_SIZE = 20
FPS = 10 

# ESTADOS DO JOGO
MENU = 0
GAME = 1
GAME_OVER = 2

# CORES (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)   
BG_COLOR = (15, 15, 30) 
GRID_COLOR = (25, 25, 50)
SNAKE_COLOR = (0, 200, 0)   
SNAKE_HEAD_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)   
BUTTON_COLOR = (40, 40, 70)
BUTTON_BORDER_COLOR = (80, 80, 150)

# CONTROLES (pygame.K_*)
import pygame
CONTROLS_MAP = {
    'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 
    'right': pygame.K_RIGHT, 'pause': pygame.K_ESCAPE
}