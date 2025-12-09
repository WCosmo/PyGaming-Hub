import pygame
import random
import sys
import configparser

# --------------------------
# 1. INICIALIZAÇÃO DO PYGAME
# --------------------------
pygame.init()

# --------------------------
# 2. CARREGAR CONF.INI
# --------------------------
config = configparser.ConfigParser()

try:
    config.read('conf/conf.ini')
except Exception:
    print("Aviso: conf/conf.ini não encontrado. Usando padrões.")

# --- RESOLUÇÃO ---
WIDTH = config.getint('Display', 'width', fallback=600)
HEIGHT = config.getint('Display', 'height', fallback=400)
FULLSCREEN = config.getboolean('Display', 'fullscreen', fallback=False)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
pygame.display.set_caption("Dodge - Joguinho")

clock = pygame.time.Clock()

# --------------------------
# 3. CONTROLES
# --------------------------
def map_key(name, fallback):
    """Converte o nome da tecla para pygame.K_*"""
    try:
        return getattr(pygame, f"K_{name.upper()}")
    except:
        return fallback

try:
    KEY_LEFT = map_key(config.get('Controls', 'left'), pygame.K_LEFT)
    KEY_RIGHT = map_key(config.get('Controls', 'right'), pygame.K_RIGHT)
    KEY_PAUSE = map_key(config.get('Controls', 'pause'), pygame.K_ESCAPE)
except:
    KEY_LEFT = pygame.K_LEFT
    KEY_RIGHT = pygame.K_RIGHT
    KEY_PAUSE = pygame.K_ESCAPE
    print("Erro no conf.ini. Usando teclas padrão.")

# --------------------------
# 4. PLAYER
# --------------------------
player_size = 40
player = pygame.Rect(WIDTH//2 - player_size//2, HEIGHT - player_size*1.5, player_size, player_size)
player_speed = 5

# --------------------------
# 5. INIMIGOS
# --------------------------
enemies = []
spawn_timer = 0
score = 0

font = pygame.font.SysFont(None, 32)

def spawn_enemy():
    enemy_size = 20
    x = random.randint(0, WIDTH - enemy_size)
    y = -enemy_size
    speed = random.randint(3, 6)
    return [x, y, speed]

# --------------------------
# 6. LOOP PRINCIPAL DO JOGO
# --------------------------
running = True
while running:
    dt = clock.tick(60)

    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tecla PAUSE → Fecha o jogo
        if event.type == pygame.KEYDOWN and event.key == KEY_PAUSE:
            running = False  # FECHAR SEM ERRO

    # --- MOVIMENTAÇÃO ---
    keys = pygame.key.get_pressed()

    if keys[KEY_LEFT] and player.left > 0:
        player.x -= player_speed

    if keys[KEY_RIGHT] and player.right < WIDTH:
        player.x += player_speed

    # --- GERAR INIMIGOS ---
    spawn_timer += 1
    if spawn_timer > 40:
        enemies.append(spawn_enemy())
        spawn_timer = 0

    screen.fill((20, 20, 30))

    # --- ATUALIZAR INIMIGOS ---
    for e in enemies[:]:
        e[1] += e[2]

        if e[1] > HEIGHT:
            enemies.remove(e)
            score += 1

        enemy_rect = pygame.Rect(e[0], e[1], 20, 20)
        if player.colliderect(enemy_rect):
            print("GAME OVER! Pontuação:", score)
            running = False
            break

        pygame.draw.circle(screen, (255, 80, 80), (int(e[0] + 10), int(e[1] + 10)), 10)

    # --- DESENHAR PLAYER ---
    pygame.draw.rect(screen, (80, 200, 255), player)

    # --- HUD ---
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

# Encerrar corretamente
pygame.quit()
sys.exit()
