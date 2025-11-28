import pygame
from settings import *
from entities.projectile import bossProjectile
import math

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - 50
        self.y = 100
        self.size = 100
        self.hp = BOSS_HP

        # Controle de tiros
        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = 1000  # 1 segundo entre ataques

    def draw(self, win):
        pygame.draw.rect(win, (200, 0, 200), (self.x, self.y, self.size, self.size))

    def shoot(self, boss_projectiles):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shot_delay:
            self.last_shot = now
            speed = 2

            # Bullet-hell: cria projéteis em círculo
            num_bullets = 8
            for i in range(num_bullets):
                angle = i * (2 * math.pi / num_bullets)
                dir_x = math.cos(angle)
                dir_y = math.sin(angle)

                proj = bossProjectile(
                    self.x + self.size // 2,
                    self.y + self.size // 2,
                    dir_x=dir_x,
                    dir_y=dir_y,
                    speed=speed
                )
                boss_projectiles.append(proj)

    def take_damage(self, amount):
        self.hp -= amount
