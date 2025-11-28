import pygame
import math
from settings import PROJECTILE_SPEED

class Projectile:
    def __init__(self, x, y, target_pos):
        self.x = x
        self.y = y
        self.radius = 6
        
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        dist = math.hypot(dx, dy)

        if dist == 0:
            dist = 1

        self.dx = (dx / dist) * PROJECTILE_SPEED
        self.dy = (dy / dist) * PROJECTILE_SPEED

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, win):
        pygame.draw.circle(win, (255, 255, 0), (int(self.x), int(self.y)), self.radius)

class bossProjectile:
    def __init__(self, x, y, amplitude=20, frequency=0.1, dir_x=0, dir_y=5 , speed=1.5):
        self.x = x
        self.y = y
        self.size = 8
        self.dir_x = dir_x
        self.dir_y = dir_y
        

        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.base_y = y
        self.time = 0

    def move(self):
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed + self.amplitude * math.sin(self.frequency * self.time)
        self.time += 0.5

    def draw(self, win):
        pygame.draw.circle(win, (255, 50, 50), (int(self.x), int(self.y)), self.size)
