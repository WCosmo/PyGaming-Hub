import pygame
import math
import time
import subprocess

pygame.init()

# -------------------------
# RESOLUÇÃO
# -------------------------
width = 1280
height = 720
fullscreen = False

if fullscreen:
    SCREEN = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
else:
    SCREEN = pygame.display.set_mode((width, height))

CLOCK = pygame.time.Clock()

# -------------------------
# CONFIG
# -------------------------
PLAYER_SPEED = 4
TOWER_COST = 50
TOWER_SELL_VALUE = 30

PLAYER_MAX_HP = 10
player_hp = PLAYER_MAX_HP

# -------------------------
# PATH (LABIRINTO SIMPLES SEM VOLTAS)
# -------------------------
PATH = [
    (-40, 360),     # entrada esquerda

    (150, 360),     # vai reto
    (150, 120),     # sobe
    (600, 120),     # vai para direita
    (600, 450),     # desce
    (1000, 450),    # direita
    (1000, 200),    # sobe um pouco
    (1280 + 40, 200)   # saída direita
]

# -------------------------
# CLASSES
# -------------------------
class Player:
    def __init__(self):
        self.x = 400
        self.y = 300
        self.size = 20

    def draw(self):
        pygame.draw.rect(SCREEN, (0, 150, 255), (self.x, self.y, self.size, self.size))

    def move(self, keys):
        if keys[pygame.K_w]: self.y -= PLAYER_SPEED
        if keys[pygame.K_s]: self.y += PLAYER_SPEED
        if keys[pygame.K_a]: self.x -= PLAYER_SPEED
        if keys[pygame.K_d]: self.x += PLAYER_SPEED


class Enemy:
    def __init__(self, wave):
        self.path_index = 0
        self.x, self.y = PATH[0]

        # Velocidade aumenta por wave
        self.speed = 1.2 + (wave * 0.25)

        self.hp = 40 + (wave * 5)
        self.max_hp = self.hp

    def update(self):
        if self.path_index >= len(PATH) - 1:
            return True

        tx, ty = PATH[self.path_index + 1]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < 2:
            self.path_index += 1
            return False

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        return False

    def draw(self):
        pygame.draw.rect(SCREEN, (255, 50, 50), (self.x, self.y, 20, 20))

        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(SCREEN, (0, 0, 0), (self.x - 2, self.y - 10, 24, 6))
        pygame.draw.rect(SCREEN, (0, 255, 0), (self.x, self.y - 8, 20 * hp_ratio, 4))


class Bullet:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5

    def update(self):
        if not self.target:
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def draw(self):
        pygame.draw.circle(SCREEN, (255, 255, 0), (int(self.x), int(self.y)), 4)


class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.cooldown = 40
        self.cool = 0

    def draw(self):
        pygame.draw.circle(SCREEN, (0, 200, 0), (self.x, self.y), 18)

    def update(self, enemies, bullets):
        if self.cool > 0:
            self.cool -= 1
            return

        target = None
        min_dist = 9999

        for e in enemies:
            dist = math.hypot(e.x - self.x, e.y - self.y)
            if dist < min_dist and dist < self.range:
                min_dist = dist
                target = e

        if target:
            bullets.append(Bullet(self.x, self.y, target))
            target.hp -= 10
            self.cool = self.cooldown


# -------------------------
# INITIAL DATA
# -------------------------
player = Player()
towers = []
enemies = []
bullets = []
spawn_timer = 0
money = 200

font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 80)

# WAVES
wave = 1
enemies_to_spawn = 5 + wave * 2
spawned = 0

# -------------------------
# GAME LOOP
# -------------------------
running = True
while running:
    CLOCK.tick(60)

    # Tecla espaço -> volta ao hub
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        subprocess.Popen(["python", "hub_de_jogos.py"])
        break

    # Game Over
    if player_hp <= 0:
        SCREEN.fill((0, 0, 0))
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        SCREEN.blit(text, (430, 300))
        pygame.display.update()
        time.sleep(5)
        subprocess.Popen(["python", "hub_de_jogos.py"])
        break

    SCREEN.fill((30, 80, 30))

    # Estrada do labirinto
    for i in range(len(PATH)-1):
        pygame.draw.line(SCREEN, (120, 120, 120), PATH[i], PATH[i+1], 50)
        pygame.draw.line(SCREEN, (255, 255, 0), PATH[i], PATH[i+1], 4)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimentação
    player.move(keys)

    # Construir torre
    if keys[pygame.K_o]:
        if money >= TOWER_COST:
            towers.append(Tower(player.x + 10, player.y + 10))
            money -= TOWER_COST
            pygame.time.wait(150)

    # Vender torre
    if keys[pygame.K_p]:
        for t in towers:
            if math.hypot(player.x - t.x, player.y - t.y) < 40:
                towers.remove(t)
                money += TOWER_SELL_VALUE
                break
        pygame.time.wait(150)

    # -------------------------
    # WAVES
    # -------------------------
    spawn_timer += 1

    if spawned < enemies_to_spawn:
        if spawn_timer > 60:
            enemies.append(Enemy(wave))
            spawned += 1
            spawn_timer = 0

    # Próxima wave
    if spawned == enemies_to_spawn and len(enemies) == 0:
        wave += 1
        spawned = 0
        enemies_to_spawn = 5 + wave * 2

    # Inimigos
    for e in enemies[:]:
        reached_end = e.update()
        if e.hp <= 0:
            enemies.remove(e)
            money += 10
        elif reached_end:
            enemies.remove(e)
            player_hp -= 1

    # Torres
    for t in towers:
        t.update(enemies, bullets)

    # Balas
    for b in bullets[:]:
        b.update()
        if b.target not in enemies:
            bullets.remove(b)
            continue
        if math.hypot(b.x - b.target.x, b.target.y - b.y) < 10:
            bullets.remove(b)

    # -------------------------
    # DRAW
    # -------------------------
    player.draw()

    for t in towers:
        t.draw()

    for e in enemies:
        e.draw()

    for b in bullets:
        b.draw()

    SCREEN.blit(font.render(f"Dinheiro: {money}", True, (255, 255, 255)), (10, 10))
    SCREEN.blit(font.render(f"Vida: {player_hp}", True, (255, 100, 100)), (10, 40))

    SCREEN.blit(font.render(f"Wave: {wave}", True, (255,255,255)), (width - 150, 10))

    pygame.display.update()

pygame.quit()