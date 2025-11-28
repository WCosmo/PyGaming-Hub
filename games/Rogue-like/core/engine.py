import pygame
from settings import *

class Engine:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("rouge-like")
        self.clock = pygame.time.Clock()

    def update(self):
        pygame.display.update()
        self.clock.tick(FPS)
