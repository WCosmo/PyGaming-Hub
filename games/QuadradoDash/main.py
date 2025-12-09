import pygame
import configparser
import os
import sys
import random

# Caminho raiz do console
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Carregar Configurações Globais ===
config = configparser.ConfigParser()
config.read(os.path.join(ROOT_DIR, "conf", "conf.ini"))

# Resolução e fullscreen
WIDTH  = config.getint("Display", "width")
HEIGHT = config.getint("Display", "height")
FULLSCREEN = config.getboolean("Display", "fullscreen")

# Controles
controls = dict(config.items("Controls"))

# Mapear string para códigos do pygame
def map_key(key_name):
    return pygame.key.key_code(key_name)

KEY_UP       = map_key(controls["up"])
KEY_DOWN     = map_key(controls["down"])
KEY_LEFT     = map_key(controls["left"])
KEY_RIGHT    = map_key(controls["right"])
KEY_ACTION_A = map_key(controls["action_a"])
KEY_PAUSE    = map_key(controls["pause"])

# === Inicialização ===
pygame.init()
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.FULLSCREEN if FULLSCREEN else 0
)
pygame.display.set_caption("QuadradoDash")
clock = pygame.time.Clock()

# === Objetos do Jogo ===
player_size = 40
player_x = WIDTH // 2
player_y = HEIGHT - 80
player_speed = 6

obstacles = []
SPAWN_TIME = 800
last_spawn = pygame.time.get_ticks()

def spawn_obstacle():
    size = random.randint(20, 60)
    x = random.randint(0, WIDTH - size)
    speed = random.randint(3, 8)
    obstacles.append([x, -size, size, speed])

def draw_player():
    pygame.draw.rect(screen, (50, 200, 255), (player_x, player_y, player_size, player_size))

def draw_obstacles():
    for o in obstacles:
        pygame.draw.rect(screen, (255, 80, 80), (o[0], o[1], o[2], o[2]))

def move_obstacles():
    for o in obstacles:
        o[1] += o[3]

def check_collision():
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for o in obstacles:
        if player_rect.colliderect(pygame.Rect(o[0], o[1], o[2], o[2])):
            return True
    return False

# === Loop Principal ===
running = True
game_over = False

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == KEY_PAUSE:
                running = False

    if not game_over:

        # Movimento do jogador
        keys = pygame.key.get_pressed()

        if keys[KEY_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[KEY_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[KEY_UP] and player_y > 0:
            player_y -= player_speed
        if keys[KEY_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed

        # Spawning de obstáculos
        if pygame.time.get_ticks() - last_spawn > SPAWN_TIME:
            spawn_obstacle()
            last_spawn = pygame.time.get_ticks()

        move_obstacles()

        if check_collision():
            game_over = True

    # === Desenho ===
    screen.fill((15, 15, 20))

    if not game_over:
        draw_player()
        draw_obstacles()
    else:
        font = pygame.font.SysFont(None, 80)
        txt = font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))

        font2 = pygame.font.SysFont(None, 40)
        txt2 = font2.render("Pressione Pause para sair", True, (200, 200, 200))
        screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
