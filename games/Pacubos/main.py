import os
import os, sys, random, time, json, math, configparser
import pygame

def find_config_file():
    candidates = [
        os.path.join(os.getcwd(), 'conf', 'conf.ini'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'conf', 'conf.ini'),
        os.path.join(os.path.dirname(__file__), '..', 'conf', 'conf.ini'),
    ]
    for p in candidates:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            return p
    return None

def key_from_name(name):
    name = (name or '').strip()
    if not name:
        return None
    try:
        return pygame.key.key_code(name)
    except Exception:
        lname = name.lower()
        aliases = {'enter': pygame.K_RETURN, 'return': pygame.K_RETURN, 'space': pygame.K_SPACE, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN}
        if lname in aliases:
            return aliases[lname]
        attr = 'K_' + lname.upper()
        return getattr(pygame, attr, None)

CONFIG_FILE = find_config_file()
config = configparser.ConfigParser()
if CONFIG_FILE:
    config.read(CONFIG_FILE)
else:
    config['Controls'] = {'up': 'w', 'down': 's', 'left': 'a', 'right': 'd', 'action_a': 'o', 'action_b': 'p', 'pause': 'return'}
    config['Display'] = {'width': '800', 'height': '600', 'fullscreen': 'False'}

controls_names = {}
for key in ('up', 'down', 'left', 'right', 'action_a', 'action_b', 'pause'):
    controls_names[key] = config.get('Controls', key, fallback='')

SCREEN_WIDTH = int(config.get('Display', 'width', fallback='800'))
SCREEN_HEIGHT = int(config.get('Display', 'height', fallback='600'))
FULLSCREEN = config.getboolean('Display', 'fullscreen', fallback=False)

PLAYER_SIZE = 28
PLAYER_SPEED = 3.5
GHOST_SIZE = 28
GHOST_SPEED = 4.8
PELLET_RADIUS = 4
PELLET_SPACING = 36
MARGIN = 20
BG_COLOR = (10, 10, 10)
PLAYER_COLOR = (255, 200, 0)
GHOST_COLOR = (200, 30, 30)
PELLET_COLOR = (200, 200, 200)

SPECIAL_SPAWN_INTERVAL = 7.0
WALL_SPAWN_INTERVAL = 4.0
GHOST_SPAWN_INTERVAL = 12.0
GHOST_MAX = 20

POWER_DURATION = 8.0
SPEED_DURATION = 5.0
GIANT_DURATION = 6.0

CLEAR_LEADERBOARD_ON_SAVE = False

def build_controls():
    return {
        'UP': key_from_name(controls_names.get('up')) or pygame.K_w,
        'DOWN': key_from_name(controls_names.get('down')) or pygame.K_s,
        'LEFT': key_from_name(controls_names.get('left')) or pygame.K_a,
        'RIGHT': key_from_name(controls_names.get('right')) or pygame.K_d,
        'ACTION_A': key_from_name(controls_names.get('action_a')) or pygame.K_o,
        'ACTION_B': key_from_name(controls_names.get('action_b')) or pygame.K_p,
        'PAUSE': key_from_name(controls_names.get('pause')) or pygame.K_RETURN,
        'RESTART': pygame.K_r,
    }

CONTROLS = build_controls()

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), 'leaderboard.json')

def load_leaderboard():
    try:
        if os.path.isfile(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_leaderboard(b):
    try:
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(b, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_score(name, score, elapsed):
    board = load_leaderboard()
    board.append({'name': name, 'score': int(score), 'time': int(elapsed)})
    board = sorted(board, key=lambda x: x['score'], reverse=True)[:10]
    save_leaderboard(board)
    return board

class Ghost:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        self.vx = math.cos(angle) * GHOST_SPEED
        self.vy = math.sin(angle) * GHOST_SPEED
        self.color = color or GHOST_COLOR
        self.change_timer = random.randint(60, 180)
        self.vulnerable = False
        self.vul_timer = 0.0
        self.respawn_timer = 0.0

    def update(self):
        if self.respawn_timer > 0:
            return
        self.change_timer -= 1
        if self.change_timer <= 0:
            ang = random.uniform(0, math.tau)
            self.vx = math.cos(ang) * GHOST_SPEED
            self.vy = math.sin(ang) * GHOST_SPEED
            self.change_timer = random.randint(60, 180)
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = 0
            self.vx *= -1
        if self.x > SCREEN_WIDTH - GHOST_SIZE:
            self.x = SCREEN_WIDTH - GHOST_SIZE
            self.vx *= -1
        if self.y < 0:
            self.y = 0
            self.vy *= -1
        if self.y > SCREEN_HEIGHT - GHOST_SIZE:
            self.y = SCREEN_HEIGHT - GHOST_SIZE
            self.vy *= -1

    def draw(self, surf):
        if self.respawn_timer > 0:
            if int(self.respawn_timer * 10) % 2 == 0:
                col = (255, 255, 255)
            else:
                col = self.color
            pygame.draw.rect(surf, col, (int(self.x), int(self.y), GHOST_SIZE, GHOST_SIZE))
            return
        if self.vulnerable:
            pygame.draw.rect(surf, (80, 160, 255), (int(self.x), int(self.y), GHOST_SIZE, GHOST_SIZE))
        else:
            pygame.draw.rect(surf, self.color, (int(self.x), int(self.y), GHOST_SIZE, GHOST_SIZE))

    def make_vulnerable(self, duration):
        self.vulnerable = True
        self.vul_timer = duration

    def kill_and_respawn(self):
        self.x = random.randint(MARGIN, SCREEN_WIDTH - MARGIN - GHOST_SIZE)
        self.y = random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - GHOST_SIZE)
        self.respawn_timer = 3.0
        self.vulnerable = False

class PacubosGame:
    def __init__(self):
        pygame.init()
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption('Pacubos')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.bigfont = pygame.font.SysFont(None, 48)
        self.player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.player_y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
        self.player_color = PLAYER_COLOR
        self.player_speed = PLAYER_SPEED
        self.player_size = PLAYER_SIZE
        self.flash_timer = 0.0
        self.score = 0
        self.lives = 3
        self.pellets = []
        for x in range(MARGIN, SCREEN_WIDTH - MARGIN, PELLET_SPACING):
            for y in range(MARGIN, SCREEN_HEIGHT - MARGIN, PELLET_SPACING):
                dx = x - SCREEN_WIDTH // 2
                dy = y - SCREEN_HEIGHT // 2
                if abs(dx) < 40 and abs(dy) < 40:
                    continue
                self.pellets.append((x, y))
        self.specials = []
        self.walls = []
        self.ghosts = []
        for _ in range(4):
            self.ghosts.append(Ghost(random.randint(MARGIN, SCREEN_WIDTH - MARGIN - GHOST_SIZE), random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - GHOST_SIZE), GHOST_COLOR))
        self._last_special = time.time() - (SPECIAL_SPAWN_INTERVAL / 2)
        self._last_wall = time.time() - (WALL_SPAWN_INTERVAL / 2)
        self._last_ghost = time.time() - (GHOST_SPAWN_INTERVAL / 2)
        self.start_time = 0.0
        self.entering_initials = False
        self.initials = ['A', 'A', 'A']
        self.initial_index = 0
        self.game_state = 'menu'

    def start_game(self):
        self.score = 0
        self.lives = 3
        self.reset_positions()
        self.pellets.clear()
        for x in range(MARGIN, SCREEN_WIDTH - MARGIN, PELLET_SPACING):
            for y in range(MARGIN, SCREEN_HEIGHT - MARGIN, PELLET_SPACING):
                dx = x - SCREEN_WIDTH // 2
                dy = y - SCREEN_HEIGHT // 2
                if abs(dx) < 40 and abs(dy) < 40:
                    continue
                self.pellets.append((x, y))
        self.specials.clear()
        self.walls.clear()
        self.start_time = time.time()
        self._last_special = time.time() - (SPECIAL_SPAWN_INTERVAL / 2)
        self._last_wall = time.time() - (WALL_SPAWN_INTERVAL / 2)
        self._last_ghost = time.time() - (GHOST_SPAWN_INTERVAL / 2)
        self.spawn_special()
        self.spawn_wall()

    def reset_positions(self):
        self.player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.player_y = SCREEN_HEIGHT // 2 - PLAYER_SIZE // 2
        for g in self.ghosts:
            g.x = random.randint(MARGIN, SCREEN_WIDTH - MARGIN - GHOST_SIZE)
            g.y = random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - GHOST_SIZE)
            g.vulnerable = False
            g.vul_timer = 0.0
            g.respawn_timer = 0.0
        self.player_speed = PLAYER_SPEED
        self.player_size = PLAYER_SIZE
        self.flash_timer = 0.0

    def spawn_special(self):
        self._last_special = time.time()
        ptype = random.choice(['power', 'speed', 'giant'])
        self.specials.append({'x': random.randint(MARGIN, SCREEN_WIDTH - MARGIN), 'y': random.randint(MARGIN, SCREEN_HEIGHT - MARGIN), 'type': ptype})

    def spawn_wall(self):
        self._last_wall = time.time()
        wtype = random.choices(['down', 'fast_down', 'side_left', 'side_right'], weights=[50, 20, 15, 15])[0]
        w = {'w': 60, 'h': 20, 'type': wtype}
        if wtype in ('down', 'fast_down'):
            w['x'] = random.randint(MARGIN, SCREEN_WIDTH - MARGIN - w['w'])
            w['y'] = -40
            w['vy'] = (random.uniform(2.5, 5.5) if wtype == 'down' else random.uniform(6.5, 11.0)) * 4.0
            w['vx'] = 0.0
        else:
            w['y'] = random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - w['h'])
            if wtype == 'side_left':
                w['x'] = -w['w'] - 10
                w['vx'] = random.uniform(3.0, 7.0) * 4.0
            else:
                w['x'] = SCREEN_WIDTH + 10
                w['vx'] = -random.uniform(3.0, 7.0) * 4.0
            w['vy'] = 0.0
        self.walls.append(w)

    def spawn_ghost_if_needed(self):
        if time.time() - self._last_ghost > GHOST_SPAWN_INTERVAL and len(self.ghosts) < GHOST_MAX:
            self._last_ghost = time.time()
            self.ghosts.append(Ghost(random.randint(MARGIN, SCREEN_WIDTH - MARGIN - GHOST_SIZE), random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - GHOST_SIZE), GHOST_COLOR))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == CONTROLS.get('PAUSE'):
                return False
            if self.game_state == 'menu' and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_state = 'playing'
                self.start_game()
            elif self.game_state == 'playing' and not self.entering_initials:
                if event.type == pygame.KEYDOWN and event.key == CONTROLS.get('RESTART'):
                    self.start_game()
            if self.entering_initials and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    elapsed = time.time() - self.start_time if self.start_time else 0.0
                    total = self.score + int(elapsed)
                    add_score(''.join(self.initials), total, elapsed)
                    self.entering_initials = False
                    self.game_state = 'playing'
                    self.start_game()
                elif event.key == pygame.K_BACKSPACE:
                    if self.initial_index > 0:
                        self.initial_index -= 1
                        self.initials[self.initial_index] = 'A'
                elif event.key == pygame.K_LEFT:
                    self.initial_index = max(0, self.initial_index - 1)
                elif event.key == pygame.K_RIGHT:
                    self.initial_index = min(2, self.initial_index + 1)
                else:
                    c = event.unicode.upper()
                    if c.isalpha() and len(c) == 1:
                        self.initials[self.initial_index] = c
                        self.initial_index = min(2, self.initial_index + 1)
        return True

    def update(self, dt):
        if self.game_state != 'playing' or self.entering_initials:
            return
        keys = pygame.key.get_pressed()
        vx = vy = 0
        if keys[CONTROLS.get('UP')]: vy = -self.player_speed
        if keys[CONTROLS.get('DOWN')]: vy = self.player_speed
        if keys[CONTROLS.get('LEFT')]: vx = -self.player_speed
        if keys[CONTROLS.get('RIGHT')]: vx = self.player_speed
        self.player_x += vx
        self.player_y += vy
        self.player_x = max(0, min(self.player_x, SCREEN_WIDTH - self.player_size))
        self.player_y = max(0, min(self.player_y, SCREEN_HEIGHT - self.player_size))
        to_remove = []
        px1 = self.player_x + self.player_size / 2
        py1 = self.player_y + self.player_size / 2
        for p in self.pellets:
            dx = px1 - p[0]
            dy = py1 - p[1]
            if dx*dx + dy*dy < (self.player_size/2 + PELLET_RADIUS)**2:
                to_remove.append(p)
                self.score += 10
        for r in to_remove:
            if r in self.pellets:
                self.pellets.remove(r)
        for s in list(self.specials):
            sx, sy = s['x'], s['y']
            if (px1 - sx)**2 + (py1 - sy)**2 < (self.player_size/2 + 12)**2:
                st = s['type']
                if st == 'power':
                    for g in self.ghosts:
                        g.make_vulnerable(POWER_DURATION)
                elif st == 'speed':
                    self.player_speed = PLAYER_SPEED * 1.8
                    self._speed_until = time.time() + SPEED_DURATION
                elif st == 'giant':
                    self.player_size = PLAYER_SIZE * 2
                    self._giant_until = time.time() + GIANT_DURATION
                try:
                    self.specials.remove(s)
                except Exception:
                    pass
        if hasattr(self, '_speed_until') and time.time() > self._speed_until:
            self.player_speed = PLAYER_SPEED
            try:
                del self._speed_until
            except Exception:
                pass
        if hasattr(self, '_giant_until') and time.time() > self._giant_until:
            self.player_size = PLAYER_SIZE
            try:
                del self._giant_until
            except Exception:
                pass
        for w in list(self.walls):
            w['x'] += w.get('vx', 0) * dt
            w['y'] += w.get('vy', 0) * dt
            if w['y'] > SCREEN_HEIGHT + 200 or w['x'] < -400 or w['x'] > SCREEN_WIDTH + 400:
                try:
                    self.walls.remove(w)
                except Exception:
                    pass
            else:
                pr = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
                wr = pygame.Rect(int(w['x']), int(w['y']), w['w'], w['h'])
                if pr.colliderect(wr):
                    if w['type'] in ('down', 'fast_down'):
                        self.player_y = wr.y + wr.h + 2
                    elif w['type'] == 'side_left':
                        self.player_x = wr.x + wr.w + 2
                    else:
                        self.player_x = wr.x - self.player_size - 2
        for g in self.ghosts:
            if g.respawn_timer > 0:
                g.respawn_timer -= dt
                if g.respawn_timer <= 0:
                    g.x = random.randint(MARGIN, SCREEN_WIDTH - MARGIN - GHOST_SIZE)
                    g.y = random.randint(MARGIN, SCREEN_HEIGHT - MARGIN - GHOST_SIZE)
                continue
            g.update()
            if g.vulnerable:
                g.vul_timer -= dt
                if g.vul_timer <= 0:
                    g.vulnerable = False
            pr = pygame.Rect(self.player_x, self.player_y, self.player_size, self.player_size)
            gr = pygame.Rect(int(g.x), int(g.y), GHOST_SIZE, GHOST_SIZE)
            if pr.colliderect(gr):
                if g.vulnerable:
                    g.kill_and_respawn()
                    self.score += 200
                else:
                    self.lives -= 1
                    self.reset_positions()
                    if self.lives <= 0:
                        self.entering_initials = True
                        self.initials = ['A', 'A', 'A']
                        self.initial_index = 0
        if time.time() - self._last_special > SPECIAL_SPAWN_INTERVAL:
            self.spawn_special()
        if time.time() - self._last_wall > WALL_SPAWN_INTERVAL:
            self.spawn_wall()
        self.spawn_ghost_if_needed()

    def draw(self):
        self.screen.fill(BG_COLOR)
        for p in self.pellets:
            pygame.draw.circle(self.screen, PELLET_COLOR, (int(p[0]), int(p[1])), PELLET_RADIUS)
        for s in self.specials:
            col = (255, 255, 255)
            if s['type'] == 'power': col = (255, 180, 180)
            if s['type'] == 'speed': col = (180, 255, 180)
            if s['type'] == 'giant': col = (255, 220, 120)
            pygame.draw.rect(self.screen, col, (int(s['x']) - 8, int(s['y']) - 8, 16, 16))
        for w in self.walls:
            pygame.draw.rect(self.screen, (100, 100, 120), (int(w['x']), int(w['y']), w['w'], w['h']))
        for g in self.ghosts:
            g.draw(self.screen)
        col = self.player_color
        if self.flash_timer > 0:
            if int(self.flash_timer * 10) % 2 == 0:
                col = (255, 255, 255)
            self.flash_timer -= 1/60
        pygame.draw.rect(self.screen, col, (int(self.player_x), int(self.player_y), int(self.player_size), int(self.player_size)))
        score_surf = self.font.render(f'Pontos: {self.score}', True, (220, 220, 220))
        lives_surf = self.font.render(f'Vidas: {self.lives}', True, (220, 220, 220))
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(lives_surf, (10, 36))
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
        else:
            elapsed = 0
        mins = elapsed // 60
        secs = elapsed % 60
        t_surf = self.font.render(f'Tempo: {mins:02d}:{secs:02d}', True, (220, 220, 220))
        self.screen.blit(t_surf, (SCREEN_WIDTH - 160, 10))
        if self.game_state == 'menu':
            title = self.bigfont.render('PACUBOS', True, (240, 200, 30))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))
            info = self.font.render('Pressione ENTER para começar', True, (200, 200, 200))
            self.screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2))
        if self.entering_initials:
            box = pygame.Surface((400, 140))
            box.fill((20, 20, 40))
            rect = box.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(box, rect.topleft)
            msg = self.font.render('Digite suas iniciais e pressione ENTER', True, (220, 220, 220))
            self.screen.blit(msg, (rect.x + 20, rect.y + 10))
            for i, ch in enumerate(self.initials):
                col = (255, 255, 255) if i == self.initial_index else (180, 180, 180)
                c_s = self.bigfont.render(ch, True, col)
                self.screen.blit(c_s, (rect.x + 60 + i * 100, rect.y + 50))
        board = load_leaderboard()
        x = SCREEN_WIDTH - 220
        y = 80
        head = self.font.render('Top 10', True, (220, 220, 220))
        self.screen.blit(head, (x, y))
        y += 30
        for i, e in enumerate(board):
            line = self.font.render(f"{i+1}. {e['name']} {e['score']} ({e['time']}s)", True, (200, 200, 200))
            self.screen.blit(line, (x, y))
            y += 22
        pygame.display.flip()

def main():
    g = PacubosGame()
    running = True
    while running:
        dt = g.clock.tick(60) / 1000.0
        running = g.handle_events()
        if g.game_state == 'playing' and not g.entering_initials and g.start_time == 0:
            g.start_time = time.time()
        g.update(dt)
        g.draw()
    pygame.quit()

if __name__ == '__main__':
    main()
