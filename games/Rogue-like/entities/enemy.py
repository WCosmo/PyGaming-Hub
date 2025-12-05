import pygame
import random
from settings import *
from entities.projectile import Projectile

class Enemy:
    def __init__(self):
        self.x = random.randint(100, WIDTH-100)
        self.y = random.randint(100, HEIGHT-100)
        self.hp = ENEMY_HP
        self.speed = ENEMY_SPEED
        self.size = 35
        self.shoot_cd = 60

    def draw(self, win):
        pygame.draw.rect(win, (255, 50, 50), (self.x, self.y, self.size, self.size))

    def follow(self, player):
        if player.x > self.x: self.x += self.speed
        if player.x < self.x: self.x -= self.speed
        if player.y > self.y: self.y += self.speed
        if player.y < self.y: self.y -= self.speed

    def shoot(self, player, projectiles):
        if self.shoot_cd == 0:
            proj = Projectile(self.x, self.y, (player.x, player.y))
            projectiles.append(proj)
            self.shoot_cd = 90
        else:
            self.shoot_cd -= 1
