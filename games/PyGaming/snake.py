import pygame
from config import GRID_SIZE, CONTROLS_MAP, SNAKE_COLOR, SNAKE_HEAD_COLOR, DISPLAY_WIDTH, DISPLAY_HEIGHT
from drawing import draw_element

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.body = [(10 * GRID_SIZE, 10 * GRID_SIZE)]
        self.direction = (GRID_SIZE, 0)
        self.score = 0

    def handle_input(self, key):
        current_dir = self.direction
        
        if key == CONTROLS_MAP['up'] and current_dir != (0, GRID_SIZE):
            self.direction = (0, -GRID_SIZE)
        elif key == CONTROLS_MAP['down'] and current_dir != (0, -GRID_SIZE):
            self.direction = (0, GRID_SIZE)
        elif key == CONTROLS_MAP['left'] and current_dir != (GRID_SIZE, 0):
            self.direction = (-GRID_SIZE, 0)
        elif key == CONTROLS_MAP['right'] and current_dir != (-GRID_SIZE, 0):
            self.direction = (GRID_SIZE, 0)
    
    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)
    
    def grow(self):
        self.score += 10

    def check_collision(self):
        head = self.body[0]
        
        # Colisão com parede
        if not (0 <= head[0] < DISPLAY_WIDTH and 0 <= head[1] < DISPLAY_HEIGHT):
            return True
        
        # Colisão com o corpo
        if head in self.body[1:]:
            return True
            
        return False

    def draw(self, screen):
        for index, segment in enumerate(self.body):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_COLOR
            draw_element(screen, color, segment)