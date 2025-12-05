import pygame
import random
import math
import sys
import time
import configparser
import os

pygame.init()



CONFIG_FILE = os.path.join("conf", "conf.ini")
config = configparser.ConfigParser()


try:
    config.read(CONFIG_FILE)
except Exception as e:
    print(f"Aviso ao ler {CONFIG_FILE}: {e}")


MUSICA_BOSS = None
AUDIO_DISPONIVEL = False

try:
    pygame.mixer.init()
    AUDIO_DISPONIVEL = True
    
    try:
        pygame.mixer.music.load('sons/musica2.mp3')
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        print("✓ Música principal carregada com sucesso")
    except:
        print("Aviso: Música principal não encontrada em 'sons/musica2.mp3'")
    
    
    try:
        MUSICA_BOSS = pygame.mixer.Sound('sons/musica2.mp3')
        MUSICA_BOSS.set_volume(0.6)
        print("✓ Música de boss carregada com sucesso")
    except:
        print("Aviso: Música de boss não encontrada")
        MUSICA_BOSS = None
        
except pygame.error as e:
    print(f"Aviso: Sistema de áudio não disponível: {e}")
    print("O jogo continuará sem música.")
    AUDIO_DISPONIVEL = False
    MUSICA_BOSS = None

_default_width = 1280
_default_height = 720
_default_fullscreen = False

try:
    W = int(config["Display"].get("width", _default_width)) if "Display" in config else _default_width
    H = int(config["Display"].get("height", _default_height)) if "Display" in config else _default_height
    FULLSCREEN = config["Display"].getboolean("fullscreen", fallback=_default_fullscreen) if "Display" in config else _default_fullscreen
except Exception as e:
    print(f"Aviso ao carregar Display do conf.ini: {e}")
    W, H = _default_width, _default_height
    FULLSCREEN = _default_fullscreen

flags = pygame.FULLSCREEN if FULLSCREEN else 0
SCREEN = pygame.display.set_mode((W, H), flags)
pygame.display.set_caption("Survival: Geometric Bosses - BALANCED")
CLOCK = pygame.time.Clock()
FPS = 60


BG = (14, 16, 22)
PLAYER_COL = (100, 200, 255)
BULLET_COL = (255, 180, 90)
ENEMY_COL = (240, 100, 120)
BOSS_COL = (180, 90, 255)
SHIELD_COL = (120, 220, 160)
HUD_COL = (200, 200, 210)
UP_COL = (180, 220, 120)
SPECIAL_COL = (255, 220, 80)
LASER_COL = (255, 60, 60)

FONT = pygame.font.SysFont("Arial", 18)
BIG = pygame.font.SysFont("Arial", 36)

MAX_ENEMIES = 60
MAX_MINIONS_PER_BOSS = 20
MAX_BULLETS = 300

DEFAULT_TIME_TO_BOSS = 40.0

SPECIAL_KILLS = 700
SPECIAL_COST  = 120
SPECIAL_SHOT_COUNT = 36
SPECIAL_BULLET_SPEED = 520
SPECIAL_BULLET_DAMAGE = 22


def length(v):
    return math.hypot(v[0], v[1])

def normalize(v):
    l = length(v)
    if l == 0:
        return (0, 0)
    return (v[0]/l, v[1]/l)

def clamp(x, a, b):
    return max(a, min(b, x))

def point_line_distance(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    c1 = vx*wx + vy*wy
    if c1 <= 0:
        return math.hypot(px-x1, py-y1), 0
    c2 = vx*vx + vy*vy
    if c2 <= c1:
        return math.hypot(px-x2, py-y2), 1
    b = c1 / c2
    bx = x1 + b*vx
    by = y1 + b*vy
    return math.hypot(px-bx, py-by), b


KEY_MAP = {
    "a": pygame.K_a,
    "b": pygame.K_b,
    "c": pygame.K_c,
    "d": pygame.K_d,
    "e": pygame.K_e,
    "f": pygame.K_f,
    "g": pygame.K_g,
    "h": pygame.K_h,
    "i": pygame.K_i,
    "j": pygame.K_j,
    "k": pygame.K_k,
    "l": pygame.K_l,
    "m": pygame.K_m,
    "n": pygame.K_n,
    "o": pygame.K_o,
    "p": pygame.K_p,
    "q": pygame.K_q,
    "r": pygame.K_r,
    "s": pygame.K_s,
    "t": pygame.K_t,
    "u": pygame.K_u,
    "v": pygame.K_v,
    "w": pygame.K_w,
    "x": pygame.K_x,
    "y": pygame.K_y,
    "z": pygame.K_z,

    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,

    "space": pygame.K_SPACE,
    "enter": pygame.K_RETURN,
    "return": pygame.K_RETURN,
    "tab": pygame.K_TAB,
    "escape": pygame.K_ESCAPE,
    "esc": pygame.K_ESCAPE,
    "shift": pygame.K_LSHIFT,
    "ctrl": pygame.K_LCTRL,
    "control": pygame.K_LCTRL,
}

def keyname_to_keycode(name, fallback=None):
    if not name:
        return fallback
    try:
        s = str(name).strip().lower()
        if s == "":
            return fallback
        
        if s in KEY_MAP:
            return KEY_MAP[s]
        
        if len(s) == 1:
            ch = s.lower()
            if ch.isalpha():
                return KEY_MAP.get(ch, fallback)
        
        if s.startswith("k_"):
            key = s[2:]
            return KEY_MAP.get(key, fallback)
        
        return KEY_MAP.get(s, fallback)
    except Exception:
        return fallback


fallback_up = pygame.K_w
fallback_down = pygame.K_s
fallback_left = pygame.K_a
fallback_right = pygame.K_d
fallback_action_a = pygame.K_SPACE  
fallback_action_b = pygame.K_p
fallback_pause = pygame.K_TAB

try:
    if "Controls" in config:
        c = config["Controls"]
        CTRL_UP = keyname_to_keycode(c.get("up", "w"), fallback_up)
        CTRL_DOWN = keyname_to_keycode(c.get("down", "s"), fallback_down)
        CTRL_LEFT = keyname_to_keycode(c.get("left", "a"), fallback_left)
        CTRL_RIGHT = keyname_to_keycode(c.get("right", "d"), fallback_right)
        CTRL_A = keyname_to_keycode(c.get("action_a", "o"), fallback_action_a)
        CTRL_B = keyname_to_keycode(c.get("action_b", "p"), fallback_action_b)
        CTRL_PAUSE = keyname_to_keycode(c.get("pause", "tab"), fallback_pause)
        CTRL_A_NAME = c.get("action_a", "space")
    else:
        CTRL_UP = fallback_up
        CTRL_DOWN = fallback_down
        CTRL_LEFT = fallback_left
        CTRL_RIGHT = fallback_right
        CTRL_A = fallback_action_a
        CTRL_B = fallback_action_b
        CTRL_PAUSE = fallback_pause
        CTRL_A_NAME = "space"
except Exception as e:
    print(f"Aviso ao carregar Controls do conf.ini: {e}")
    CTRL_UP = fallback_up
    CTRL_DOWN = fallback_down
    CTRL_LEFT = fallback_left
    CTRL_RIGHT = fallback_right
    CTRL_A = fallback_action_a
    CTRL_B = fallback_action_b
    CTRL_PAUSE = fallback_pause
    CTRL_A_NAME = "space"


try:
    CTRL_A_LABEL = config["Controls"].get("action_a", "space") if "Controls" in config else "space"
except:
    CTRL_A_LABEL = "space"



class Player:
    def __init__(self):
        self.x = W*0.12
        self.y = H/2
        self.r = 14
        self.speed = 280
        self.hp = 140
        self.max_hp = 140
        self.kills = 0
        self.weapon_level = 1
        self.reload_time = 0.15
        self.reload = 0
        self.bullets_per_shot = 1
        self.piercing = False
        self.damage_mult = 1.0
        self.auto_burst = False
        self.storm_on_shoot = False
        self._burst_shots_left = 0
        self._burst_rate = 0.06
        self._burst_timer = 0.0
        self.special_ready = False
        self.update_weapon()

    def update_weapon(self):
        thresholds = [0, 40, 80, 120, 200, 300, 500]
        new_lvl = 1
        for idx, th in enumerate(thresholds, start=1):
            if self.kills >= th:
                new_lvl = idx
        if new_lvl != self.weapon_level:
            self.weapon_level = new_lvl
        self.reload_time = 0.30
        self.bullets_per_shot = 1
        self.piercing = False
        self.damage_mult = 1.0
        self.auto_burst = False
        self.storm_on_shoot = False
        if self.weapon_level >= 2:
            self.reload_time = 0.25
        if self.weapon_level >= 3:
            self.reload_time = 0.20
        if self.weapon_level >= 4:
            self.reload_time = 0.16
        if self.weapon_level >= 5:
            self.reload_time = 0.12
        if self.weapon_level >= 6:
            self.reload_time = 0.08
        if self.weapon_level >= 7:
            self.bullets_per_shot = 2

    
    def update(self, dt, keys):
        try:
            dx = keys[CTRL_RIGHT] - keys[CTRL_LEFT]
            dy = keys[CTRL_DOWN] - keys[CTRL_UP]
        except Exception:
            
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

        if dx != 0 or dy != 0:
            v = normalize((dx, dy))
            self.x += v[0]*self.speed*dt
            self.y += v[1]*self.speed*dt
        self.x = clamp(self.x, 16, W-16)
        self.y = clamp(self.y, 16, H-16)
        if self.reload > 0:
            self.reload -= dt
        if self._burst_shots_left > 0:
            self._burst_timer -= dt
            if self._burst_timer <= 0:
                self._burst_timer = self._burst_rate
                self._burst_shots_left -= 1
                self.reload = 0.0
        self.update_weapon()
        self.special_ready = (self.kills >= SPECIAL_KILLS)

    def draw(self, surf):
        pygame.draw.circle(surf, PLAYER_COL, (int(self.x), int(self.y)), self.r)
        ratio = clamp(self.hp / self.max_hp, 0.0, 1.0)
        pygame.draw.arc(surf, (0,200,120), (self.x-22, self.y-22, 44, 44), -math.pi/2, -math.pi/2 + 2*math.pi*ratio, 3)

    def can_shoot(self):
        return self.reload <= 0

    def start_burst(self, shots=3):
        self._burst_shots_left = shots
        self._burst_timer = 0.0

    def shoot(self, target_pos):
        if not self.can_shoot():
            return []
        self.reload = self.reload_time
        bullets = []
        dirv_center = normalize((target_pos[0]-self.x, target_pos[1]-self.y))
        base_speed = 640
        base_damage = 16 * self.damage_mult
        if self.storm_on_shoot:
            for i in range(12):
                ang = i * (math.tau / 12) + random.uniform(-0.1, 0.1)
                d = (math.cos(ang), math.sin(ang))
                b = Bullet(self.x + d[0]*(self.r+6), self.y + d[1]*(self.r+6), d, speed=420, life=1.6, friendly=True)
                b.damage = int(base_damage * 0.6)
                b.piercing = True
                bullets.append(b)
        n = max(1, self.bullets_per_shot)
        if n == 1:
            b = Bullet(self.x + dirv_center[0]*self.r, self.y + dirv_center[1]*self.r, dirv_center, speed=base_speed, life=2.0, friendly=True)
            b.damage = int(base_damage)
            b.piercing = self.piercing
            bullets.append(b)
        else:
            spread_total = 0.28
            for i in range(n):
                t = (i - (n-1)/2) / ((n-1)/2) if n>1 else 0
                ang_offset = t * (spread_total/2)
                base_ang = math.atan2(dirv_center[1], dirv_center[0])
                ang = base_ang + ang_offset
                d = (math.cos(ang), math.sin(ang))
                b = Bullet(self.x + d[0]*self.r, self.y + d[1]*self.r, d, speed=base_speed, life=2.0, friendly=True)
                b.damage = int(base_damage)
                b.piercing = self.piercing
                bullets.append(b)
        if self.auto_burst:
            self.start_burst(shots=2)
        return bullets

    def use_special(self):
        if not self.special_ready or self.kills < SPECIAL_COST:
            return []
        bullets = []
        mx, my = pygame.mouse.get_pos()
        dirv = normalize((mx - self.x, my - self.y))
        if dirv == (0,0):
            dirv = (1,0)
        laser = Bullet(self.x, self.y, dirv, speed=0, life=0.40, friendly=True)
        laser.laser = True
        laser.damage = 120
        laser.beam_length = max(W, H) * 1.5
        laser.hit_done = False
        bullets.append(laser)
        self.kills = max(0, self.kills - SPECIAL_COST)
        self.special_ready = (self.kills >= SPECIAL_KILLS)
        return bullets

class Bullet:
    def __init__(self, x, y, dirv, speed=640, life=2.0, friendly=True):
        self.x = x
        self.y = y
        self.dirv = dirv
        self.speed = speed
        self.life = life
        self.radius = 5
        self.friendly = friendly
        self.piercing = False
        self.damage = 14
        self.laser = getattr(self, "laser", False)
        self.beam_length = getattr(self, "beam_length", 0)
        self.hit_done = getattr(self, "hit_done", False)

    def update(self, dt):
        if not getattr(self, "laser", False):
            self.x += self.dirv[0]*self.speed*dt
            self.y += self.dirv[1]*self.speed*dt
        self.life -= dt

    def draw(self, surf):
        if getattr(self, "laser", False):
            x2 = self.x + self.dirv[0] * self.beam_length
            y2 = self.y + self.dirv[1] * self.beam_length
            pygame.draw.line(surf, LASER_COL, (int(self.x), int(self.y)), (int(x2), int(y2)), 6)
            pygame.draw.circle(surf, LASER_COL, (int(self.x), int(self.y)), 6)
            return
        color = (200, 220, 100) if self.friendly else (220, 120, 140)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

    def alive(self):
        return self.life > 0 and (-40 <= self.x <= W+40 and -40 <= self.y <= H+40)

class Minion:
    def __init__(self, x, y, phase=1):
        self.x = x
        self.y = y
        self.size = 14 + int(phase*0.8)
        self.speed = random.uniform(70 + phase*4, 140 + phase*6)
        self.hp = 18 + phase*4
        self.phase = phase

    def update(self, dt, player):
        dirv = normalize((player.x - self.x, player.y - self.y))
        self.x += dirv[0]*self.speed*dt
        self.y += dirv[1]*self.speed*dt

    def draw(self, surf):
        pts = [(self.x, self.y - self.size), (self.x - self.size, self.y + self.size), (self.x + self.size, self.y + self.size)]
        pygame.draw.polygon(surf, ENEMY_COL, pts)
        maxhp = 18 + self.phase*4
        if self.hp < maxhp:
            ratio = clamp(self.hp / maxhp, 0, 1)
            pygame.draw.rect(surf, (50,50,50), (self.x - self.size, self.y + self.size + 4, self.size*2, 4))
            pygame.draw.rect(surf, (200,70,70), (self.x - self.size, self.y + self.size + 4, int(self.size*2*ratio), 4))

class Boss:
    POWERS = ['FLASHEE', 'REI DOS MINIONS', 'CASCUDO', 'laser', 'TP TP', 'meio a meio']

    def __init__(self, phase):
        self.x = W - 120
        self.y = H/2
        self.phase = phase
        self.size = 48 + phase*8
        self.base_hp = (120 + phase*80) * 4
        self.hp = self.base_hp
        self.max_hp = self.base_hp
        self.regen_rate = 0.5 + 0.15 * phase
        self.speed = 80 + phase*10
        self.power = random.choice(Boss.POWERS)
        self.power_cd = 0
        self.minions = []
        self.shield = False
        self.shield_timer = 0
        self.laser_timer = 0
        self.teleport_cd = 0
        self.split_done = False
        if self.power == 'FLASHEE':
            self.speed *= 1.9
        elif self.power == 'CASCUDO':
            self.shield = True
            self.shield_timer = 6.0

    def update(self, dt, player, bullets, entities):
        if self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.regen_rate * dt)
        ang = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(ang)*self.speed*dt*0.7
        self.y += math.sin(ang)*self.speed*dt*0.7
        self.x = clamp(self.x, W*0.5, W-40)
        self.y = clamp(self.y, 40, H-40)
        if self.power == 'REI DOS MINIONS':
            self.power_cd -= dt
            if self.power_cd <= 0:
                self.power_cd = max(1.2, 3.0 - 0.20*self.phase)
                spawn_count = random.randint(1, 2 + self.phase//2)
                for _ in range(spawn_count):
                    if len(self.minions) < MAX_MINIONS_PER_BOSS:
                        m = Minion(self.x + random.randint(-50,50), self.y + random.randint(-40,40), phase=self.phase)
                        self.minions.append(m)
        elif self.power == 'CASCUDO':
            if self.shield_timer > 0:
                self.shield_timer -= dt
                self.shield = True
            else:
                self.shield = False
                self.power_cd -= dt
                if self.power_cd <= 0:
                    self.shield_timer = max(3.0, 4.0 - 0.2*self.phase)
                    self.power_cd = max(3.5, 6.0 - 0.5*self.phase)
        elif self.power == 'laser':
            self.laser_timer -= dt
            if self.laser_timer <= 0:
                self.laser_timer = max(1.1, 2.5 - 0.1*self.phase)
                dirv = normalize((player.x - self.x, player.y - self.y))
                burst = 1 + self.phase//2
                for i in range(burst):
                    jitter = random.uniform(-0.06, 0.06)
                    d = normalize((dirv[0] + jitter, dirv[1] + jitter))
                    b = Bullet(self.x + d[0]*(self.size+8), self.y + d[1]*(self.size+8), d, speed=0, life=0.6, friendly=False)
                    b.damage = 10 + self.phase*2
                    b.laser = True
                    b.beam_length = max(W, H) * 1.2
                    b.hit_done = False
                    if len(bullets) < MAX_BULLETS:
                        bullets.append(b)
        elif self.power == 'TP TP':
            self.teleport_cd -= dt
            if self.teleport_cd <= 0:
                self.teleport_cd = max(1.6, 3.0 - 0.18*self.phase)
                self.x = random.uniform(W*0.55, W-60)
                self.y = random.uniform(60, H-60)
                for i in range(5):
                    ang = random.uniform(0, math.tau)
                    d = (math.cos(ang), math.sin(ang))
                    b = Bullet(self.x + d[0]*(self.size+6), self.y + d[1]*(self.size+6), d, speed=300 + self.phase*10, life=2.0, friendly=False)
                    if len(bullets) < MAX_BULLETS:
                        bullets.append(b)
        elif self.power == 'meio a meio':
            if self.hp < self.base_hp * 0.5 and not self.split_done:
                self.split_done = True
                for i in range(2):
                    nb = Boss(self.phase)
                    nb.size = int(self.size*0.6)
                    nb.base_hp = int(self.base_hp * 0.45)
                    nb.hp = nb.base_hp
                    nb.x = self.x + (i*40 - 20)
                    nb.y = self.y + random.randint(-40,40)
                    entities['bosses'].append(nb)
                self.hp = 0
        for m in list(self.minions):
            m.update(dt, player)
            if random.random() < 0.02 + 0.01*self.phase:
                dirv = normalize((player.x - m.x, player.y - m.y))
                b = Bullet(m.x + dirv[0]*10, m.y + dirv[1]*10, dirv, speed=300 + self.phase*10, life=2.0, friendly=False)
                if len(bullets) < MAX_BULLETS:
                    bullets.append(b)
            if m.x < -40 or m.x > W+40 or m.y < -40 or m.y > H+40:
                try:
                    self.minions.remove(m)
                except:
                    pass
        if len(self.minions) > MAX_MINIONS_PER_BOSS:
            self.minions = self.minions[:MAX_MINIONS_PER_BOSS]
        
        
       

    def draw(self, surf):
        rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size*2, self.size*2)
        pygame.draw.rect(surf, BOSS_COL, rect, border_radius=12)
        ptxt = FONT.render(self.power.upper(), True, HUD_COL)
        surf.blit(ptxt, (self.x - ptxt.get_width()/2, self.y - 10))
        hpw = int((self.hp / self.base_hp) * (self.size*2))
        pygame.draw.rect(surf, (60,60,60), (self.x-self.size, self.y - self.size - 10, self.size*2, 6))
        pygame.draw.rect(surf, (200,60,60), (self.x-self.size, self.y - self.size - 10, max(0, hpw), 6))
        if self.shield:
            pygame.draw.circle(surf, SHIELD_COL, (int(self.x), int(self.y)), int(self.size*1.2), 3)
        for m in self.minions:
            m.draw(surf)

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.entities = {'bosses': []}
        self.phase = 1
        self.spawn_timer = 0.6
        self.time_to_boss = DEFAULT_TIME_TO_BOSS
        self.in_boss_phase = False
        self.level_boss = None
        self.score = 0
        self.game_over = False
        self.spawn_wave_active = True

    def next_boss(self):
        self.bullets.clear()
        self.enemies.clear()
        self.entities['bosses'].clear()
        boss = Boss(self.phase)
        boss.x = W - 140
        boss.y = H/2
        self.entities['bosses'].append(boss)
        self.level_boss = boss
        self.in_boss_phase = True
        
        
        

    def reset(self):
        self.__init__()

    def spawn_enemy(self):
        if len(self.enemies) >= MAX_ENEMIES:
            return
        x = random.uniform(W*0.6, W-30)
        y = random.uniform(30, H-30)
        e = Minion(x, y, phase=self.phase)
        self.enemies.append(e)

    def update(self, dt, keys, mouse, mouse_pressed):
        if self.game_over:
            return
        self.player.update(dt, keys)
        mx, my = mouse
        want_shoot = mouse_pressed[0]
        if want_shoot:
            if self.player.can_shoot() or self.player._burst_shots_left > 0:
                new_bullets = self.player.shoot((mx, my))
                for nb in new_bullets:
                    if len(self.bullets) < MAX_BULLETS:
                        self.bullets.append(nb)
        for b in list(self.bullets):
            b.update(dt)
            if not b.alive():
                try: self.bullets.remove(b)
                except: pass
        for b in list(self.bullets):
            if getattr(b, "laser", False) and b.friendly and (not getattr(b, "hit_done", False)):
                ex = b.x + b.dirv[0] * b.beam_length
                ey = b.y + b.dirv[1] * b.beam_length
                for e in list(self.enemies):
                    dist, t = point_line_distance(e.x, e.y, b.x, b.y, ex, ey)
                    if dist <= e.size + 6 and 0.0 <= t <= 1.0:
                        e.hp -= int(b.damage)
                for boss in list(self.entities['bosses']):
                    for m in list(boss.minions):
                        dist, t = point_line_distance(m.x, m.y, b.x, b.y, ex, ey)
                        if dist <= m.size + 6 and 0.0 <= t <= 1.0:
                            m.hp -= int(b.damage)
                for boss in list(self.entities['bosses']):
                    dist, t = point_line_distance(boss.x, boss.y, b.x, b.y, ex, ey)
                    if dist <= boss.size + 6 and 0.0 <= t <= 1.0:
                        boss.hp -= int(b.damage)
                b.hit_done = True
        if not self.in_boss_phase:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = max(0.4 - 0.02*self.phase, 0.16)
                if random.random() < 0.75:
                    count = random.randint(1, 2 + self.phase//2)
                    for _ in range(count):
                        self.spawn_enemy()
            self.time_to_boss -= dt
            if self.time_to_boss <= 0:
                self.next_boss()
        else:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = max(0.6 - 0.02*self.phase, 0.2)
                if random.random() < 0.45:
                    self.spawn_enemy()
        for e in list(self.enemies):
            e.update(dt, self.player)
            if math.hypot(e.x - self.player.x, e.y - self.player.y) < e.size + self.player.r:
                self.player.hp -= 8
                try: self.enemies.remove(e)
                except: pass
        for boss in list(self.entities['bosses']):
            boss.update(dt, self.player, self.bullets, self.entities)
            for m in list(boss.minions):
                if math.hypot(m.x - self.player.x, m.y - self.player.y) < m.size + self.player.r:
                    self.player.hp -= 6
                    m.hp = 0
            for b in list(self.bullets):
                if b.friendly and (not getattr(b, "laser", False)) and math.hypot(b.x - boss.x, b.y - boss.y) < boss.size + b.radius:
                    if boss.shield:
                        boss.hp -= max(1, int(b.damage * 0.3))
                    else:
                        boss.hp -= int(b.damage)
                    if not b.piercing:
                        try: self.bullets.remove(b)
                        except: pass
            for m in list(boss.minions):
                for b in list(self.bullets):
                    if (not getattr(b, "laser", False)) and b.friendly and math.hypot(b.x - m.x, b.y - m.y) < m.size + b.radius:
                        m.hp -= int(b.damage)
                        if not b.piercing:
                            try: self.bullets.remove(b)
                            except: pass
                if m.hp <= 0:
                    try: boss.minions.remove(m)
                    except: pass
                    self.player.kills += 1
                    self.score += 6
                    if self.player.kills >= SPECIAL_KILLS:
                        self.player.special_ready = True
            if boss.hp <= 0:
                try: self.entities['bosses'].remove(boss)
                except: pass
                gained = 12 + boss.phase * 6
                self.player.kills += gained
                self.score += 120 * self.phase
                if self.player.kills >= SPECIAL_KILLS:
                    self.player.special_ready = True
                self.phase += 1
                self.in_boss_phase = False
                self.time_to_boss = DEFAULT_TIME_TO_BOSS + 10 * (self.phase-1)
                self.player.hp = min(self.player.max_hp, self.player.hp + 30)
        for b in list(self.bullets):
            if not b.friendly and math.hypot(b.x - self.player.x, b.y - self.player.y) < b.radius + self.player.r:
                self.player.hp -= 10
                try: self.bullets.remove(b)
                except: pass
        for e in list(self.enemies):
            for b in list(self.bullets):
                if (not getattr(b, "laser", False)) and b.friendly and math.hypot(b.x - e.x, b.y - e.y) < e.size + b.radius:
                    e.hp -= int(b.damage)
                    if not b.piercing:
                        try: self.bullets.remove(b)
                        except: pass
            if e.hp <= 0:
                try: self.enemies.remove(e)
                except: pass
                self.player.kills += 1
                self.score += 6
                if self.player.kills >= SPECIAL_KILLS:
                    self.player.special_ready = True
        if len(self.bullets) > MAX_BULLETS:
            self.bullets = self.bullets[-MAX_BULLETS:]
        self.player.update_weapon()
        if self.player.hp <= 0:
            self.game_over = True

    def draw(self, surf):
        hptext = FONT.render(f"HP: {int(self.player.hp)}", True, HUD_COL)
        surf.blit(hptext, (16, 12))
        sc = FONT.render(f"Phase: {self.phase}  Score: {self.score}  Enemies: {len(self.enemies)}  BossMinions: {sum(len(b.minions) for b in self.entities['bosses'])}", True, HUD_COL)
        surf.blit(sc, (16, 36))
        wl = FONT.render(f"Kills: {self.player.kills}  Weapon Lv: {self.player.weapon_level}", True, UP_COL)
        surf.blit(wl, (16, 60))
        thresholds = [0,40,80,120,200,300,500]
        lvl = self.player.weapon_level
        if lvl < 7:
            next_th = f"Next Lv at {thresholds[lvl]} kills"
            nxt = FONT.render(next_th, True, HUD_COL)
            surf.blit(nxt, (16, 82))
        else:
            nxt = FONT.render("Weapon: MAX", True, HUD_COL)
            surf.blit(nxt, (16, 82))
        if self.player.special_ready:
            
            spec_label = CTRL_A_LABEL.upper() if CTRL_A_LABEL else "SPACE"
            spec = FONT.render(f"SPECIAL READY! (Press {spec_label}) [{SPECIAL_KILLS} kills] - Cost: {SPECIAL_COST}", True, SPECIAL_COL)
            surf.blit(spec, (16, 104))
        if not self.in_boss_phase:
            wave_text = FONT.render(f"Boss in: {int(self.time_to_boss)}s (waves)", True, HUD_COL)
            surf.blit(wave_text, (W//2 - wave_text.get_width()//2, 12))
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(surf, (180,180,180), (self.player.x, self.player.y), (mx, my), 1)
        for b in self.bullets:
            b.draw(surf)
        for e in self.enemies:
            e.draw(surf)
        for boss in self.entities['bosses']:
            boss.draw(surf)
        self.player.draw(surf)
        if self.game_over:
            if self.phase > 6:
                txt = BIG.render("You Survived!", True, (180,220,150))
                surf.blit(txt, (W//2 - txt.get_width()//2, H//2 - 40))
            else:
                txt = BIG.render("Game Over", True, (240,120,120))
                surf.blit(txt, (W//2 - txt.get_width()//2, H//2 - 40))
            info = FONT.render("Press R to restart", True, HUD_COL)
            surf.blit(info, (W//2 - info.get_width()//2, H//2 + 20))

def main():
    game = Game()
    running = True
    while running:
        dt = CLOCK.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                elif event.key == CTRL_PAUSE:
                    print("Saindo do jogo...")
                    running = False
        
        if keys[CTRL_A] and game.player.special_ready and not game.game_over:
            special_bullets = game.player.use_special()
            for sb in special_bullets:
                if len(game.bullets) < MAX_BULLETS:
                    game.bullets.append(sb)
        game.update(dt, keys, mouse, mouse_pressed)
        SCREEN.fill(BG)
        game.draw(SCREEN)
        if game.level_boss:
            pinfo = FONT.render(f"Boss Power: {game.level_boss.power}", True, HUD_COL)
            SCREEN.blit(pinfo, (W - pinfo.get_width() - 16, 12))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
