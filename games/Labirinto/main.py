import pygame
import sys
import os
import configparser

LEVELS = {
    1: [
        "1111111111111",
        "1S00000000001",
        "1011110111111",
        "1000010100001",
        "1111010110111",
        "1000010000101",
        "1011110110101",
        "1000000010101",
        "1110111010101",
        "10G0100000001",
        "1111111111111",
    ],

    2: [
        "1111111111111",
        "1S00000100001",
        "1011101010111",
        "1000101000001",
        "1110101110101",
        "1000001000101",
        "1011101110101",
        "1010000010101",
        "1010111010101",
        "10G0100010G01",
        "1111111111111",
    ],
}


CONF_DIR = 'conf'
CONFIG_FILE = os.path.join(CONF_DIR, 'conf.ini')


def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config['Display'] = {'width': '800',
                             'height': '600', 'fullscreen': 'False'}
        config['Controls'] = {
            'up': 'w', 'down': 's', 'left': 'a', 'right': 'd',
            'action_a': 'o', 'action_b': 'p', 'pause': 'enter'
        }
        config['Info'] = {'authors': 'Equipe Labirinto'}
        os.makedirs(CONF_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
    else:
        config.read(CONFIG_FILE, encoding='utf-8')
    return config


config = load_config()

SCREEN_WIDTH = config.getint('Display', 'width')
SCREEN_HEIGHT = config.getint('Display', 'height')
FULLSCREEN = config.getboolean('Display', 'fullscreen')

controls_section = 'Controls'
CONTROLS = {
    'UP': config.get(controls_section, 'up', fallback='w'),
    'DOWN': config.get(controls_section, 'down', fallback='s'),
    'LEFT': config.get(controls_section, 'left', fallback='a'),
    'RIGHT': config.get(controls_section, 'right', fallback='d'),
    'A': config.get(controls_section, 'action_a', fallback='o'),
    'B': config.get(controls_section, 'action_b', fallback='p'),
    'PAUSE': config.get(controls_section, 'pause', fallback='enter')
}

AUTHORS = config.get('Info', 'authors', fallback='Autor Desconhecido')

MAZE = [
    "1111111111111",
    "1S00000000001",
    "1011110111111",
    "1000010100001",
    "1111010110111",
    "1000010000101",
    "1011110110101",
    "1000000010101",
    "1110111010101",
    "10G0100000001",
    "1111111111111",
]


ROWS = len(MAZE)
COLS = len(MAZE[0])


TILE_W = SCREEN_WIDTH // COLS
TILE_H = SCREEN_HEIGHT // ROWS
TILE = min(TILE_W, TILE_H)

# Centraliza mapa na tela
MAP_WIDTH_PX = TILE * COLS
MAP_HEIGHT_PX = TILE * ROWS
OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH_PX) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT_PX) // 2


def maze_get(r, c):
    if r < 0 or r >= ROWS or c < 0 or c >= COLS:
        return '1'
    return MAZE[r][c]


def find_tile(tile_char):
    for r in range(ROWS):
        for c in range(COLS):
            if MAZE[r][c] == tile_char:
                return r, c
    return None


def draw_text(surface, text, size, x, y, color=(255, 255, 255), anchor="topleft"):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if anchor == "center":
        text_rect.center = (x, y)
    elif anchor == "topleft":
        text_rect.topleft = (x, y)
    elif anchor == "midtop":
        text_rect.midtop = (x, y)

    surface.blit(text_surface, text_rect)
    return text_rect


def main():
    pygame.init()
    pygame.font.init()

    display_flags = 0
    if FULLSCREEN:
        display_flags = pygame.FULLSCREEN | pygame.SCALED

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), display_flags)
    pygame.display.set_caption("Labirinto")
    clock = pygame.time.Clock()
    start = find_tile('S')
    goal = find_tile('G')
    if not start:
        start = (1, 1)
    player_r, player_c = start

    won = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                if key_name == CONTROLS['PAUSE']:
                    pygame.quit()
                    sys.exit()

                if not won:
                    # movimentos por tile (colisão simples)
                    new_r, new_c = player_r, player_c
                    if key_name == CONTROLS['UP']:
                        new_r -= 1
                    elif key_name == CONTROLS['DOWN']:
                        new_r += 1
                    elif key_name == CONTROLS['LEFT']:
                        new_c -= 1
                    elif key_name == CONTROLS['RIGHT']:
                        new_c += 1

                    if maze_get(new_r, new_c) != '1':
                        player_r, player_c = new_r, new_c

                    if (player_r, player_c) == goal:
                        won = True

        # ----- Draw -----
        screen.fill((10, 10, 30))

        # desenha o labirinto
        for r in range(ROWS):
            for c in range(COLS):
                ch = MAZE[r][c]
                x = OFFSET_X + c * TILE
                y = OFFSET_Y + r * TILE
                rect = pygame.Rect(x, y, TILE, TILE)

                if ch == '1':
                    # parede
                    pygame.draw.rect(screen, (180, 30, 30), rect)
                elif ch == '0' or ch == 'S':
                    # caminho
                    pygame.draw.rect(screen, (30, 30, 80), rect)
                    # desenha linhas de grade suaves
                    pygame.draw.rect(screen, (20, 20, 50), rect, 1)
                elif ch == 'G':
                    pygame.draw.rect(screen, (30, 80, 30), rect)
                    # desenha um círculo no centro para marcar a meta
                    cx = x + TILE // 2
                    cy = y + TILE // 2
                    pygame.draw.circle(
                        screen, (200, 255, 200), (cx, cy), TILE // 4)

        # desenha jogador
        px = OFFSET_X + player_c * TILE
        py = OFFSET_Y + player_r * TILE
        player_rect = pygame.Rect(
            px + TILE * 0.15, py + TILE * 0.15, TILE * 0.7, TILE * 0.7)
        pygame.draw.rect(screen, (240, 220, 60), player_rect)

        # HUD do game
        draw_text(screen, f"Autores: {AUTHORS}", 20, 10, 10, anchor="topleft")
        draw_text(screen, "Labirinto", 36,
                  SCREEN_WIDTH // 2, 10, anchor="midtop")
        draw_text(screen, f"Use {CONTROLS['UP'].upper()}/{CONTROLS['DOWN'].upper()}/{CONTROLS['LEFT'].upper()}/{CONTROLS['RIGHT'].upper()} para mover",
                  20, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, anchor="midtop")

        if won:
            draw_text(screen, "VOCÊ VENCEU! Pressione 'Pause' para sair.", 40,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, color=(255, 255, 255), anchor="center")

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
