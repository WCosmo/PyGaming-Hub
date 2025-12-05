
import pygame
import sys
import configparser
import random
from pathlib import Path

# ---------- Config / leitura do conf.ini ----------
config = configparser.ConfigParser()
conf_path = Path("conf/conf.ini")
if not conf_path.exists():
    conf_path = Path("../conf/conf.ini")
config.read(conf_path)

def get_display_config():
    try:
        disp = config["Display"]
        w = int(disp.get("width", 640))
        h = int(disp.get("height", 480))
        fs = disp.get("fullscreen", "False").lower() in ("1", "true", "yes")
        return w, h, fs
    except Exception:
        return 640, 480, False

def get_controls():
    defaults = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "action_a": "a",   # revelar
        "action_b": "b",   # bandeira / reiniciar
        "pause": "escape"
    }
    controls = {}
    try:
        sec = config["Controls"]
        for k, d in defaults.items():
            controls[k] = sec.get(k, d)
    except Exception:
        controls = defaults
    return controls

controls_names = get_controls()
W, H, FULLSCREEN = get_display_config()

# ---------- Helper: converter nome -> keycode ----------
def name_to_keycode(name):
    n = str(name).lower()
    try:
        return pygame.key.key_code(n)
    except Exception:
        attr = f"K_{n}"
        return getattr(pygame, attr, None)

# Inicializa pygame e mapeia controles para códigos
pygame.init()
CONTROL_KEYS = {k: name_to_keycode(v) for k, v in controls_names.items()}

# ---------- Janela ----------
flags = pygame.FULLSCREEN if FULLSCREEN else 0
screen = pygame.display.set_mode((W, H), flags)
pygame.display.set_caption("Campo Minado - PyGaming Hub")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 24)
BIGFONT = pygame.font.SysFont(None, 36)

# ---------- Config do jogo ----------
ROWS = 9
COLS = 9
MINES = 10

MARGIN = 20
BOARD_W = min(W, H) - 2 * MARGIN
CELL = BOARD_W // max(COLS, ROWS)
BOARD_W = CELL * max(COLS, ROWS)
BOARD_ORIGIN = ((W - BOARD_W)//2, (H - BOARD_W)//2 + 10)
LINE_W = max(2, CELL // 20)

# cores
BG = (230, 230, 230)
BOARD_BG = (180, 200, 230)
CELL_BG = (200, 220, 240)
REVEALED_BG = (240, 240, 240)
GRID_COLOR = (60, 60, 60)
CURSOR_COLOR = (255, 100, 100)
MINE_COLOR = (20, 20, 20)
FLAG_COLOR = (200, 30, 30)
TEXT_COLOR = (10, 10, 10)

# estado do tabuleiro
def new_board(rows=ROWS, cols=COLS, mines=MINES):
    # create empty
    b = [[0 for _ in range(cols)] for _ in range(rows)]
    # place mines
    positions = [(r, c) for r in range(rows) for c in range(cols)]
    mines_pos = random.sample(positions, mines)
    for (r, c) in mines_pos:
        b[r][c] = -1
    # fill numbers
    for r in range(rows):
        for c in range(cols):
            if b[r][c] == -1:
                continue
            cnt = 0
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < rows and 0 <= cc < cols and b[rr][cc] == -1:
                        cnt += 1
            b[r][c] = cnt
    return b, [[False]*cols for _ in range(rows)], [[False]*cols for _ in range(rows)]  # board, revealed, flagged

board, revealed, flagged = new_board()
cursor = [0, 0]  # col, row
game_over = False
won = False

def reset_game():
    global board, revealed, flagged, cursor, game_over, won
    board, revealed, flagged = new_board()
    cursor = [0, 0]
    game_over = False
    won = False

# reveal flood-fill
def reveal_cell(r, c):
    global game_over
    if revealed[r][c] or flagged[r][c]:
        return
    revealed[r][c] = True
    if board[r][c] == -1:
        game_over = True
        # reveal all mines
        for i in range(ROWS):
            for j in range(COLS):
                if board[i][j] == -1:
                    revealed[i][j] = True
        return
    # if zero, flood
    if board[r][c] == 0:
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                rr, cc = r+dr, c+dc
                if 0 <= rr < ROWS and 0 <= cc < COLS and not revealed[rr][cc]:
                    reveal_cell(rr, cc)

def check_win():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != -1 and not revealed[r][c]:
                return False
    return True

# ---------- Desenho ----------
def cell_rect(col, row):
    ox, oy = BOARD_ORIGIN
    return pygame.Rect(ox + col*CELL, oy + row*CELL, CELL, CELL)

def draw_board():
    screen.fill(BG)
    # quadro de fundo
    ox, oy = BOARD_ORIGIN
    pygame.draw.rect(screen, BOARD_BG, (ox-4, oy-4, COLS*CELL+8, ROWS*CELL+8))
    # células
    for r in range(ROWS):
        for c in range(COLS):
            rect = cell_rect(c, r)
            # fundo
            if revealed[r][c]:
                pygame.draw.rect(screen, REVEALED_BG, rect)
            else:
                pygame.draw.rect(screen, CELL_BG, rect)
            # borda
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)
            # conteúdo
            if revealed[r][c]:
                val = board[r][c]
                if val == -1:
                    # mine: desenha círculo preto
                    cx, cy = rect.center
                    radius = max(3, CELL//4)
                    pygame.draw.circle(screen, MINE_COLOR, (cx, cy), radius)
                elif val > 0:
                    txt = FONT.render(str(val), True, TEXT_COLOR)
                    screen.blit(txt, txt.get_rect(center=rect.center))
            else:
                if flagged[r][c]:
                    # bandeira = pequeno triângulo/retângulo
                    px = rect.left + CELL//4
                    py = rect.top + CELL//4
                    # triângulo simples
                    points = [
                        (px, rect.centery),
                        (px + CELL//2, rect.top + CELL//3),
                        (px + CELL//2, rect.bottom - CELL//3)
                    ]
                    pygame.draw.polygon(screen, FLAG_COLOR, points)
                    # mastro
                    pygame.draw.line(screen, GRID_COLOR, (px, rect.top + 3), (px, rect.bottom - 3), 2)
    # cursor
    crect = cell_rect(cursor[0], cursor[1])
    pygame.draw.rect(screen, CURSOR_COLOR, crect, max(2, CELL//12))

def draw_status():
    # top-left status texts
    flags_left = sum(1 for r in range(ROWS) for c in range(COLS) if flagged[r][c])
    mines_text = f"Mines: {MINES}  Flags: {flags_left}"
    surf = FONT.render(mines_text, True, TEXT_COLOR)
    screen.blit(surf, (10, 6))
    if game_over:
        txt = "Perdeu! B: Reiniciar  Pause: Sair"
        surf2 = BIGFONT.render(txt, True, (180,20,20))
        screen.blit(surf2, (10, H - 50))
    elif won:
        txt = "Você Venceu! B: Reiniciar  Pause: Sair"
        surf2 = BIGFONT.render(txt, True, (20,120,20))
        screen.blit(surf2, (10, H - 50))
    else:
        hint = "A: Revelar  B: Bandeira  Pause: Sair"
        surf2 = FONT.render(hint, True, TEXT_COLOR)
        screen.blit(surf2, (10, H - 30))

# ---------- Loop principal ----------
def main():
    global cursor, game_over, won
    running = True
    redraw = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if CONTROL_KEYS.get("pause") is not None and event.key == CONTROL_KEYS["pause"]:
                    running = False
                    break

                if game_over or won:
                    # durante fim de jogo só aceita reiniciar (action_b) e pause
                    if CONTROL_KEYS.get("action_b") is not None and event.key == CONTROL_KEYS["action_b"]:
                        reset_game()
                        redraw = True
                    continue

                # movs
                if CONTROL_KEYS.get("up") is not None and event.key == CONTROL_KEYS["up"]:
                    cursor[1] = max(0, cursor[1] - 1); redraw = True
                elif CONTROL_KEYS.get("down") is not None and event.key == CONTROL_KEYS["down"]:
                    cursor[1] = min(ROWS-1, cursor[1] + 1); redraw = True
                elif CONTROL_KEYS.get("left") is not None and event.key == CONTROL_KEYS["left"]:
                    cursor[0] = max(0, cursor[0] - 1); redraw = True
                elif CONTROL_KEYS.get("right") is not None and event.key == CONTROL_KEYS["right"]:
                    cursor[0] = min(COLS-1, cursor[0] + 1); redraw = True

                # action_a -> revelar
                if CONTROL_KEYS.get("action_a") is not None and event.key == CONTROL_KEYS["action_a"]:
                    r, c = cursor[1], cursor[0]
                    if not revealed[r][c] and not flagged[r][c]:
                        reveal_cell(r, c)
                        redraw = True
                        if not game_over and check_win():
                            won = True
                            redraw = True

                # action_b -> bandeira
                if CONTROL_KEYS.get("action_b") is not None and event.key == CONTROL_KEYS["action_b"]:
                    r, c = cursor[1], cursor[0]
                    if not revealed[r][c]:
                        flagged[r][c] = not flagged[r][c]
                        redraw = True

        if redraw:
            draw_board()
            draw_status()
            pygame.display.flip()
            redraw = False

    pygame.quit()

if __name__ == "__main__":
    main()