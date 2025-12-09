"""
Asteroids Geométrico - Compatível com PyGaming Hub
Regras implementadas:
- Lê conf/conf.ini (Display + Controls)
- Usa tecla de pause para sair
- Nenhuma imagem externa (somente pygame.draw)
"""

import pygame
import math
import random
import configparser
from pathlib import Path

# ------------------------------------------------------
#   MAPEAMENTO DE TECLAS (igual ao SimpleMover)
# ------------------------------------------------------
KEY_NAME_MAP = {
    'space': pygame.K_SPACE,
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'w': pygame.K_w,
    'a': pygame.K_a,
    's': pygame.K_s,
    'd': pygame.K_d,
    'enter': pygame.K_RETURN,
    'return': pygame.K_RETURN,
    'escape': pygame.K_ESCAPE,
    'pause': pygame.K_p,
}

def map_key(name):
    if not name:
        return None
    name = name.strip().lower()

    if name in KEY_NAME_MAP:
        return KEY_NAME_MAP[name]

    if len(name) == 1:
        return getattr(pygame, f"K_{name}", None)

    try:
        return getattr(pygame, f"K_{name.upper()}")
    except:
        return None


# ------------------------------------------------------
#   CARREGAR CONFIGURAÇÃO (Display + Controls)
# ------------------------------------------------------
def load_conf():
    cfg = configparser.ConfigParser()

    # conf.ini fica em PyGaming-Hub/conf/conf.ini
    base = Path(__file__).resolve().parents[2] / "conf" / "conf.ini"

    if not base.exists():  # fallback
        base = Path(__file__).resolve().parents[1] / "conf" / "conf.ini"

    cfg.read(base)

    display = cfg["Display"]
    controls = cfg["Controls"]

    width = int(display.get("width", 800))
    height = int(display.get("height", 600))
    fullscreen = display.get("fullscreen", "no").lower() in ("1", "true", "yes")

    mapped = {
        k: map_key(controls.get(k, "")) for k in
        ("up", "down", "left", "right", "action_a", "action_b", "pause")
    }

    return width, height, fullscreen, mapped


# ------------------------------------------------------
#   CLASSES DO JOGO
# ------------------------------------------------------
class Ship:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.angle = -90
        self.radius = 12

    def update(self, dt, w, h):
        self.pos += self.vel * dt
        self.pos.x %= w
        self.pos.y %= h

    def draw(self, surf):
        rad = math.radians(self.angle)
        direction = pygame.Vector2(math.cos(rad), math.sin(rad))
        right = direction.rotate(120)
        left = direction.rotate(-120)

        p1 = self.pos + direction * 18
        p2 = self.pos + right * 12
        p3 = self.pos + left * 12

        pygame.draw.polygon(surf, (255, 255, 255), [p1, p2, p3], 2)


class Bullet:
    def __init__(self, pos, vel):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.life = 1.5

    def update(self, dt, w, h):
        self.pos += self.vel * dt
        self.pos.x %= w
        self.pos.y %= h
        self.life -= dt

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 200, 0), (int(self.pos.x), int(self.pos.y)), 3)


class Asteroid:
    def __init__(self, pos, vel, size=3):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.size = size
        self.radius = 15 * size

        # forma irregular
        self.points = []
        for i in range(10):
            ang = i * (360/10)
            dist = self.radius * (0.7 + random.random()*0.6)
            self.points.append((ang, dist))

        self.rotation = random.random() * 360

    def update(self, dt, w, h):
        self.pos += self.vel * dt
        self.pos.x %= w
        self.pos.y %= h
        self.rotation += 20 * dt

    def draw(self, surf):
        verts = []
        for ang, dist in self.points:
            rad = math.radians(ang + self.rotation)
            x = self.pos.x + math.cos(rad) * dist
            y = self.pos.y + math.sin(rad) * dist
            verts.append((x, y))

        pygame.draw.polygon(surf, (200, 200, 200), verts, 2)


# ------------------------------------------------------
#   LOOP PRINCIPAL
# ------------------------------------------------------
def main():
    pygame.init()

    width, height, fullscreen, controls = load_conf()

    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((width, height), flags)
    clock = pygame.time.Clock()

    ship = Ship((width/2, height/2))
    bullets = []
    asteroids = []

    for _ in range(5):
        pos = (random.randrange(width), random.randrange(height))
        vel = pygame.Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
        size = random.choice([2, 3])
        asteroids.append(Asteroid(pos, vel, size))

    cooldown = 0
    running = True

    while running:
        dt = clock.tick(60) / 1000

        # EVENTOS
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            if ev.type == pygame.KEYDOWN:
                if controls["pause"] and ev.key == controls["pause"]:
                    running = False

        keys = pygame.key.get_pressed()

        # MOVIMENTO DA NAVE
        if controls["left"] and keys[controls["left"]]:
            ship.angle -= 180 * dt
        if controls["right"] and keys[controls["right"]]:
            ship.angle += 180 * dt
        if controls["up"] and keys[controls["up"]]:
            rad = math.radians(ship.angle)
            force = pygame.Vector2(math.cos(rad), math.sin(rad)) * 120
            ship.vel += force * dt

        # TIRO
        if controls["action_a"] and keys[controls["action_a"]] and cooldown <= 0:
            rad = math.radians(ship.angle)
            vel = pygame.Vector2(math.cos(rad), math.sin(rad)) * 300
            bullets.append(Bullet(ship.pos, vel))
            cooldown = 0.25
        cooldown -= dt

        # UPDATE
        ship.update(dt, width, height)

        for b in bullets[:]:
            b.update(dt, width, height)
            if b.life <= 0:
                bullets.remove(b)

        for a in asteroids:
            a.update(dt, width, height)

        # COLISÕES
        for b in bullets[:]:
            for a in asteroids[:]:
                if (b.pos - a.pos).length() < a.radius:
                    bullets.remove(b)
                    asteroids.remove(a)

                    if a.size > 1:
                        for _ in range(2):
                            vel = pygame.Vector2(
                                random.uniform(-120, 120),
                                random.uniform(-120, 120)
                            )
                            asteroids.append(Asteroid(a.pos, vel, a.size-1))
                    break

        # DRAW
        screen.fill((10, 10, 25))
        ship.draw(screen)
        for b in bullets:
            b.draw(screen)
        for a in asteroids:
            a.draw(screen)

        # HUD
        font = pygame.font.SysFont(None, 22)
        txt = font.render("ASTEROIDS GEO — Pause volta ao menu", True, (180, 180, 180))
        screen.blit(txt, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
