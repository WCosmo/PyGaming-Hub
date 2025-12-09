import os
import sys
import random
import math
import configparser
import pygame
from pygame.math import Vector2
import os

CONF_PATH = os.path.join(os.path.expanduser("~"), ".meu_jogo", "config.ini")


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CONF_PATH = os.path.join(BASE_DIR, 'conf', 'conf.ini')
DATA_INF_PATH = os.path.join(BASE_DIR, 'data.inf')

DEFAULT_CONF = {
    'controls': {
        
        'up': 'w',
        'down': 's',
        'left': 'a',
        'right': 'd',
        'action': 'space',
        'pause': 'p'
    }
}

def ensure_conf_and_data():
    conf_dir = os.path.dirname(CONF_PATH)
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)
    if not os.path.isfile(CONF_PATH):
        config = configparser.ConfigParser()
        config.read_dict(DEFAULT_CONF)
        with open(CONF_PATH, 'w', encoding='utf-8') as f:
            config.write(f)
        print(f'Arquivo de configuração criado em: {CONF_PATH} (edite para mudar controles)')

def key_from_name(name):
    name = str(name).strip()
    if name.isdigit():
        return int(name)
    try:
        return pygame.key.key_code(name)
    except Exception:
        pass
    keyname = name.upper()
    candidate = getattr(pygame, 'K_' + keyname, None)
    if isinstance(candidate, int):
        return candidate
    if len(name) == 1:
        return ord(name.lower())
    raise ValueError(f'Não foi possível mapear tecla: {name}')

def load_controls():
    config = configparser.ConfigParser()
    config.read(CONF_PATH)
    if 'controls' not in config:
        config.read_dict(DEFAULT_CONF)
    mapping = {}
    for k, v in config['controls'].items():
        try:
            mapping[k] = key_from_name(v)
        except Exception as e:
            print('Erro ao mapear tecla', k, v, e)
            raise
    return mapping

SCREEN_SIZE = (800, 600)
FPS = 60
PLAYER_RADIUS = 12
CHEESE_RADIUS = 8
ENEMY_SIZE = 22
TRAP_SIZE = (28, 12)
BULLET_RADIUS = 5
BUFF_SIZE = 10

class Entity:
    def __init__(self, pos):
        self.pos = Vector2(pos)
class Cheese(Entity):
    def __init__(self, pos):
        super().__init__(pos)
        self.collected = False
class Trap(Entity):
    def __init__(self, pos):
        super().__init__(pos)
class Buff(Entity):
    def __init__(self, pos, kind):
        super().__init__(pos)
        self.kind = kind
class Bullet(Entity):
    def __init__(self, pos, vel, owner):
        super().__init__(pos)
        self.vel = Vector2(vel)
        self.owner = owner

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos)
        self.vel = Vector2(0, 0)
        self.speed = 160.0
        self.lives = 3
        self.score = 0
        self.has_knife = False
        self.knife_timer = 0.0
        self.speed_timer = 0.0

    def update(self, dt):
        if self.knife_timer > 0:
            self.knife_timer -= dt
            if self.knife_timer <= 0:
                self.has_knife = False
        if self.speed_timer > 0:
            self.speed_timer -= dt
            if self.speed_timer <= 0:
                self.speed = 160.0

class Enemy(Entity):
    def __init__(self, pos, speed=80, shooter=False):
        super().__init__(pos)
        self.speed = speed
        self.shooter = shooter
        self.cooldown = random.uniform(1.0, 2.5)
        self.direction = Vector2(0, 0)
        self.alive = True
        self.size = ENEMY_SIZE

    def update(self, dt, player):
        
        dirv = (player.pos - self.pos)
        if dirv.length() > 0:
            dirv = dirv.normalize()
            self.pos += dirv * self.speed * dt
        
        if self.shooter:
            self.cooldown -= dt
            if self.cooldown <= 0:
                self.cooldown = random.uniform(0.8, 2.0)
                return self.shoot_at(player)
        return None

    def shoot_at(self, player):
        
        dirv = (player.pos - self.pos)
        if dirv.length() == 0:
            dirv = Vector2(1, 0)
        vel = dirv.normalize() * 260
        bpos = Vector2(self.pos)
        return Bullet(bpos, vel, self)


def distance(a, b):
    return (a - b).length()

class Game:
    def __init__(self, controls):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Mouse Seeker')
        self.clock = pygame.time.Clock()
        self.controls = controls
        self.font = pygame.font.SysFont(None, 20)

        self.reset()

    def reset(self):
        self.level = 1
        self.player = Player(Vector2(SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2))
        self.cheeses = []
        self.enemies = []
        self.traps = []
        self.bullets = []
        self.buffs = []
        self.spawn_level(self.level)
        self.game_over = False
        self.victory = False

    def spawn_level(self, level):
        
        self.cheeses.clear(); self.enemies.clear(); self.traps.clear(); self.bullets.clear(); self.buffs.clear()
        
        cheese_count = min(3 + level, 8)
        for _ in range(cheese_count):
            pos = Vector2(random.randint(40, SCREEN_SIZE[0]-40), random.randint(40, SCREEN_SIZE[1]-40))
            self.cheeses.append(Cheese(pos))
        
        enemy_count = min(1 + level//1, 10)
        for i in range(enemy_count):
            pos = Vector2(random.choice([20, SCREEN_SIZE[0]-20]), random.randint(20, SCREEN_SIZE[1]-20))
            shooter = (level >= 3 and random.random() < 0.3)
            e = Enemy(pos, speed=70 + level*5 + random.uniform(-10, 10), shooter=shooter)
            self.enemies.append(e)
        
        trap_count = max(0, level - 2)
        for _ in range(trap_count):
            pos = Vector2(random.randint(40, SCREEN_SIZE[0]-40), random.randint(40, SCREEN_SIZE[1]-40))
            self.traps.append(Trap(pos))
        
        if random.random() < 0.5:
            kind = random.choice(['knife', 'coffee', 'shield'])
            pos = Vector2(random.randint(40, SCREEN_SIZE[0]-40), random.randint(40, SCREEN_SIZE[1]-40))
            self.buffs.append(Buff(pos, kind))
        
        if level >= 5:
            
            boss = Enemy(Vector2(SCREEN_SIZE[0]/2, 80), speed=40, shooter=True)
            boss.hp = 8 + level * 2
            boss.size = 48
            boss.is_boss = True
            self.enemies = [boss]

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move = Vector2(0, 0)
        if keys[self.controls['up']]:
            move.y -= 1
        if keys[self.controls['down']]:
            move.y += 1
        if keys[self.controls['left']]:
            move.x -= 1
        if keys[self.controls['right']]:
            move.x += 1
        if move.length_squared() > 0:
            move = move.normalize()
        self.player.vel = move * self.player.speed

    def update(self, dt):
        
        self.player.pos += self.player.vel * dt
        self.player.pos.x = max(10, min(SCREEN_SIZE[0]-10, self.player.pos.x))
        self.player.pos.y = max(10, min(SCREEN_SIZE[1]-10, self.player.pos.y))
        self.player.update(dt)

        
        for e in list(self.enemies):
            b = e.update(dt, self.player)
            if b:
                self.bullets.append(b)
            if distance(e.pos, self.player.pos) < (e.size/2 + PLAYER_RADIUS):
                if getattr(e, 'is_boss', False):
                    self.player.lives -= 1
                else:
                    if self.player.has_knife:
                        try: self.enemies.remove(e)
                        except: pass
                    else:
                        self.player.lives -= 1
                self.player.pos += (self.player.pos - e.pos).normalize() * 20

        for b in list(self.bullets):
            b.pos += b.vel * dt
            if b.pos.x < -20 or b.pos.x > SCREEN_SIZE[0]+20 or b.pos.y < -20 or b.pos.y > SCREEN_SIZE[1]+20:
                try: self.bullets.remove(b)
                except: pass
                continue
            if b.owner is not None and isinstance(b.owner, Enemy):
                if distance(b.pos, self.player.pos) < PLAYER_RADIUS + BULLET_RADIUS:
                    self.player.lives -= 1
                    try: self.bullets.remove(b)
                    except: pass

        for t in list(self.traps):
            if distance(t.pos, self.player.pos) < max(TRAP_SIZE)/2 + PLAYER_RADIUS:
                self.player.lives -= 1
                try: self.traps.remove(t)
                except: pass

        for c in self.cheeses:
            if not c.collected and distance(c.pos, self.player.pos) < PLAYER_RADIUS + CHEESE_RADIUS:
                c.collected = True
                self.player.score += 1

        for bf in list(self.buffs):
            if distance(bf.pos, self.player.pos) < PLAYER_RADIUS + BUFF_SIZE:
                if bf.kind == 'knife':
                    self.player.has_knife = True
                    self.player.knife_timer = 8.0
                elif bf.kind == 'coffee':
                    self.player.speed = 260.0
                    self.player.speed_timer = 6.0
                elif bf.kind == 'shield':
                    self.player.lives = min(5, self.player.lives + 1)
                try: self.buffs.remove(bf)
                except: pass

        for e in list(self.enemies):
            if getattr(e, 'is_boss', False) and distance(e.pos, self.player.pos) < (e.size/2 + PLAYER_RADIUS):
                if self.player.has_knife:
                    e.hp -= 1
                    self.player.pos += Vector2(0, -30)
                    if e.hp <= 0:
                        self.enemies.remove(e)
                        big_cheese = Cheese(Vector2(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))
                        big_cheese.is_big = True
                        self.cheeses.append(big_cheese)

        all_collected = all(c.collected for c in self.cheeses)
        if all_collected:
            if getattr(self, 'level', 0) >= 5 and any(getattr(c, 'is_big', False) for c in self.cheeses):
                self.victory = True
            else:
                self.level += 1
                self.spawn_level(self.level)

        if self.player.lives <= 0:
            self.game_over = True

    def draw_ui(self):
        txt = self.font.render(f'Vidas: {self.player.lives}   Pontos: {self.player.score}   Fase: {self.level}', True, (0,0,0))
        self.screen.blit(txt, (8, 8))
        buffs = []
        if self.player.has_knife: buffs.append('Faca')
        if self.player.speed_timer > 0: buffs.append('Cafe')
        if buffs:
            txt2 = self.font.render('Buffs: ' + ','.join(buffs), True, (0,0,0))
            self.screen.blit(txt2, (8, 28))

    def draw(self):
        self.screen.fill((235, 235, 240))
        for c in self.cheeses:
            if getattr(c, 'is_big', False):
                pygame.draw.circle(self.screen, (230, 180, 0), (int(c.pos.x), int(c.pos.y)), 36)
            else:
                color = (240, 210, 0) if not c.collected else (180, 180, 180)
                pygame.draw.circle(self.screen, color, (int(c.pos.x), int(c.pos.y)), CHEESE_RADIUS)
                pygame.draw.circle(self.screen, (200,160,0), (int(c.pos.x+3), int(c.pos.y-3)), 3)

        for t in self.traps:
            rect = pygame.Rect(t.pos.x - TRAP_SIZE[0]/2, t.pos.y - TRAP_SIZE[1]/2, TRAP_SIZE[0], TRAP_SIZE[1])
            pygame.draw.rect(self.screen, (120,70,30), rect)
            for i in range(3):
                x = rect.x + 6 + i*8
                pygame.draw.polygon(self.screen, (80,40,20), [(x, rect.y+rect.h), (x+4, rect.y+rect.h), (x+2, rect.y)])

        for bf in self.buffs:
            if bf.kind == 'knife':
                pygame.draw.circle(self.screen, (150,150,150), (int(bf.pos.x), int(bf.pos.y)), BUFF_SIZE)
                pygame.draw.rect(self.screen, (200,200,200), (bf.pos.x-6, bf.pos.y-2, 12, 4))
            elif bf.kind == 'coffee':
                pygame.draw.circle(self.screen, (100,60,10), (int(bf.pos.x), int(bf.pos.y)), BUFF_SIZE)
                pygame.draw.rect(self.screen, (60,40,20), (bf.pos.x-5, bf.pos.y-5, 10, 10), 2)
            else:
                pygame.draw.circle(self.screen, (100,180,240), (int(bf.pos.x), int(bf.pos.y)), BUFF_SIZE)

        for e in self.enemies:
            ex, ey = int(e.pos.x), int(e.pos.y)
            if getattr(e, 'is_boss', False):
                pygame.draw.rect(self.screen, (180,40,40), (ex - e.size/2, ey - e.size/2, e.size, e.size))
                hp = getattr(e, 'hp', 1)
                maxhp = 12
                barw = int((e.size) * (hp / maxhp))
                pygame.draw.rect(self.screen, (0,0,0), (ex - e.size/2, ey - e.size/2 - 8, e.size, 6), 1)
                pygame.draw.rect(self.screen, (0,200,0), (ex - e.size/2+1, ey - e.size/2 -7, barw, 4))
            else:
                pygame.draw.rect(self.screen, (200,40,40), (ex - e.size/2, ey - e.size/2, e.size, e.size))

        for b in self.bullets:
            pygame.draw.circle(self.screen, (40,40,80), (int(b.pos.x), int(b.pos.y)), BULLET_RADIUS)

        px, py = int(self.player.pos.x), int(self.player.pos.y)
        pygame.draw.ellipse(self.screen, (200,170,150), (px-PLAYER_RADIUS-8, py-6, PLAYER_RADIUS, 10))
        pygame.draw.circle(self.screen, (150,150,150), (px, py), PLAYER_RADIUS)
        pygame.draw.circle(self.screen, (230,180,180), (px-6, py-12), 6)
        pygame.draw.circle(self.screen, (0,0,0), (px+5, py-4), 2)
        if self.player.has_knife:
            pygame.draw.polygon(self.screen, (180,180,180), [(px+10, py+2), (px+22, py-4), (px+14, py-10)])

        self.draw_ui()

        if self.game_over:
            self.draw_centered_text('GAME OVER — reiniciando...', 36)
        if self.victory:
            self.draw_centered_text('VOCÊ VENCEU! Pegue o queijo gigante para encerrar.', 28)

        pygame.display.flip()

    def draw_centered_text(self, text, size=24):
        f = pygame.font.SysFont(None, size)
        s = f.render(text, True, (10,10,10))
        r = s.get_rect(center=(SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))
        self.screen.blit(s, r)

    def run(self):
        running = True
        accumulator = 0.0
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == self.controls.get('p'):
                        print('Tecla PAUSE recebida — encerrando o jogo.')
                        running = False
                    if event.key == self.controls.get('action'):
                        for e in list(self.enemies):
                            if distance(e.pos, self.player.pos) < PLAYER_RADIUS + e.size/2 + 6:
                                if self.player.has_knife:
                                    try: self.enemies.remove(e)
                                    except: pass
                                else:
                                    pass
            self.handle_input(dt)

            if not self.game_over and not self.victory:
                self.update(dt)
            else:
                pygame.time.wait(800)
                self.reset()
            self.draw()
        pygame.quit()

def main():
    ensure_conf_and_data()
    try:
        controls = load_controls()
    except Exception as e:
        print('Erro ao carregar controles:', e)
        return
    for k in ['up','down','left','right','action','pause']:
        if k not in controls:
            print(f'Controle faltando: {k} — usando padrão')
            controls[k] = key_from_name(DEFAULT_CONF['controls'][k])
    game = Game(controls)
    game.run()

if __name__ == '__main__':
    main()