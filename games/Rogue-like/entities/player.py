import pygame
from settings import *
from entities.projectile import Projectile

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.speed_normal = PLAYER_SPEED
        self.hp = PLAYER_MAX_HP
        self.size = 40
        self.cooldown = 0  # delay entre tiros
        self.damage_timer = 0

        # --- habilidades ---
        self.ability_active = False
        self.ability_on_cooldown = False
        self.ability_duration = 10000
        self.ability_cooldown_time = 60000
        self.ability_cooldown_start_time = 0
        self.ability_start_time = 0

    def draw(self, win):
        pygame.draw.rect(win, (0, 150, 255), (self.x, self.y, self.size, self.size))

    def move(self, keys):
        if keys[pygame.K_a]: self.x -= self.speed
        if keys[pygame.K_d]: self.x += self.speed
        if keys[pygame.K_w]: self.y -= self.speed
        if keys[pygame.K_s]: self.y += self.speed

        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))

    def auto_shoot(self, projectiles, enemies, boss):
        if self.cooldown > 0:
            return
        targets = []

        if enemies:
            targets.extend(enemies)
        if boss is not None:
            targets.append(boss)
        if len(targets) == 0:
            return

    # Pega o inimigo mais próximo
        closest_enemy = min(
            targets,
            key=lambda e: ((e.x - self.x)**2 + (e.y - self.y)**2)
        )

    # Mira no centro do inimigo
        target_pos = (
            closest_enemy.x + closest_enemy.size // 2,
            closest_enemy.y + closest_enemy.size // 2
        )

    # Atira exatamente como o shoot normal
        proj = Projectile(self.x + self.size // 2, self.y + self.size // 2, target_pos)
        projectiles.append(proj)
        self.cooldown = 15  # recarrega


    def update_cooldown(self):
        if self.cooldown > 0:
            self.cooldown -= 1
    def handly_ability(self, keys):
        now = pygame.time.get_ticks()

        if (keys[pygame.K_o]) and not self.ability_active and not self.ability_on_cooldown:
            self.ability_active = True
            self.speed = self.speed_normal * 2
            self.ability_start_time = now
        
        if self.ability_active:
            if now - self.ability_start_time >= self.ability_duration:
                self.ability_active = False
                self.speed = self.speed_normal
                self.ability_on_cooldown = True
                self.cooldown_start_time = now

        if self.ability_on_cooldown:
            if now - self.cooldown_start_time >= self.ability_cooldown_time:
                self.ability_on_cooldown = False
                
    def update_damage_timer(self):
        if self.damage_timer > 0:
            self.damage_timer -= 1

