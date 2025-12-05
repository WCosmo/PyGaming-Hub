from __future__ import annotations

import configparser
import random
import sys
from pathlib import Path
from typing import Dict, Tuple

import pygame

# Caminhos-base do projeto
GAME_DIR = Path(__file__).resolve().parent
ROOT_DIR = GAME_DIR.parents[1]
CONFIG_PATH = ROOT_DIR / "conf" / "conf.ini"
MUSIC_PATH = GAME_DIR / "musica.mp3"

# Constantes de gameplay
PLAYER_SIZE = 40
PORTAL_RADIUS = 28
BASE_SPEED = 5
ROUND_DURATION = 5  # segundos por rodada
GAME_DURATION = 40  # segundos totais
MAX_ERRORS = 3

COLOR_PALETTE: Dict[str, Tuple[int, int, int]] = {
    "Vermelho": (220, 60, 60),
    "Verde": (60, 200, 80),
    "Azul": (70, 130, 240),
    "Amarelo": (240, 210, 70),
    "Roxo": (150, 70, 200),
}

DEFAULT_KEYS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "action_a": "j",
    "action_b": "k",
    "pause": "escape",
}

KEY_ALIASES = {
    "enter": "return",  # trata Enter principal como Return
    "return": "return",
    "esc": "escape",
    "spacebar": "space",
}


def load_settings(config_file: Path) -> Dict[str, Dict[str, int | str]]:
    """Lê conf.ini e devolve as configurações de tela e os nomes das teclas."""
    parser = configparser.ConfigParser()
    if not config_file.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_file}")

    parser.read(config_file, encoding="utf-8")

    display = {
        "width": parser.getint("Display", "width", fallback=960),
        "height": parser.getint("Display", "height", fallback=540),
        "fullscreen": parser.getboolean("Display", "fullscreen", fallback=False),
    }

    controls_str = {}
    for action, default in DEFAULT_KEYS.items():
        controls_str[action] = parser.get("Controls", action, fallback=default)

    return {"display": display, "controls": controls_str}


def map_control_keys(control_names: Dict[str, str]) -> Dict[str, int]:
    """Converte os nomes das teclas em keycodes do Pygame."""
    mapped = {}
    for action, key_name in control_names.items():
        normalized = key_name.strip().lower()
        canonical = KEY_ALIASES.get(normalized, normalized)
        try:
            mapped[action] = pygame.key.key_code(canonical)
        except ValueError:
            fallback_name = KEY_ALIASES.get(DEFAULT_KEYS[action], DEFAULT_KEYS[action])
            mapped[action] = pygame.key.key_code(fallback_name)
    return mapped


def random_portal_position(width: int, height: int) -> pygame.Vector2:
    """Cria uma posição aleatória ao longo das bordas da tela."""
    edge = random.choice(("top", "bottom", "left", "right"))
    if edge == "top":
        x = random.randint(PORTAL_RADIUS, width - PORTAL_RADIUS)
        y = PORTAL_RADIUS
    elif edge == "bottom":
        x = random.randint(PORTAL_RADIUS, width - PORTAL_RADIUS)
        y = height - PORTAL_RADIUS
    elif edge == "left":
        x = PORTAL_RADIUS
        y = random.randint(PORTAL_RADIUS, height - PORTAL_RADIUS)
    else:  # right
        x = width - PORTAL_RADIUS
        y = random.randint(PORTAL_RADIUS, height - PORTAL_RADIUS)
    return pygame.Vector2(x, y)


def reset_round(portals: Dict[str, pygame.Vector2], width: int, height: int) -> Tuple[str, int]:
    """Reposiciona todos os portais e escolhe uma nova cor-alvo."""
    for color in portals:
        portals[color] = random_portal_position(width, height)
    new_target = random.choice(tuple(COLOR_PALETTE.keys()))
    return new_target, pygame.time.get_ticks()


def circle_rect_collision(center: pygame.Vector2, radius: int, rect: pygame.Rect) -> bool:
    """Detecta colisão entre o círculo (portal) e o quadrado do jogador."""
    closest_x = max(rect.left, min(center.x, rect.right))
    closest_y = max(rect.top, min(center.y, rect.bottom))
    dx = center.x - closest_x
    dy = center.y - closest_y
    return dx * dx + dy * dy <= radius * radius


def draw_portals(surface: pygame.Surface, portals: Dict[str, pygame.Vector2]) -> None:
    """Desenha todos os portais coloridos."""
    for name, position in portals.items():
        pygame.draw.circle(surface, COLOR_PALETTE[name], position, PORTAL_RADIUS, width=6)


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    total_time_left: float,
    round_time_left: float,
    target_color: str,
) -> None:
    """Renderiza pontuação, tempo e cor-alvo na parte superior."""
    hud_text = (
        f"Pontos: {score}  |  Tempo total: {total_time_left:04.1f}s  "
        f"|  Rodada: {round_time_left:04.1f}s"
    )
    text_surface = font.render(hud_text, True, (255, 255, 255))
    surface.blit(text_surface, (20, 10))

    color_label = font.render(f"Cor-alvo: {target_color}", True, (255, 255, 255))
    surface.blit(color_label, (20, 40))
    pygame.draw.rect(surface, COLOR_PALETTE[target_color], pygame.Rect(240, 45, 60, 20))


def show_game_over(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    restart_key: int,
    pause_key: int,
) -> str:
    """Tela final: 'o' (action_a) reinicia, 'Pause/Enter' volta ao hub."""
    clock = pygame.time.Clock()
    title = font.render("Fim de Jogo", True, (255, 255, 255))
    info = font.render(f"Pontuação Final: {score}", True, (255, 255, 255))
    prompt_restart = font.render("o: Jogar novamente", True, (255, 255, 255))
    prompt_exit = font.render("Enter/Pause: Sair do jogo", True, (255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == restart_key:
                    return "restart"
                if event.key == pause_key:
                    return "exit"

        screen.fill((0, 0, 0))
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen.blit(title, title.get_rect(center=(center_x, center_y - 60)))
        screen.blit(info, info.get_rect(center=(center_x, center_y - 20)))
        screen.blit(prompt_restart, prompt_restart.get_rect(center=(center_x, center_y + 20)))
        screen.blit(prompt_exit, prompt_exit.get_rect(center=(center_x, center_y + 50)))

        pygame.display.flip()
        clock.tick(60)


def show_start_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    start_key: int,
    back_key: int,
    pause_key: int,
) -> str:
    """Tela inicial com instruções: 'o' inicia, 'p' volta ao hub, Pause pausa/sai."""
    clock = pygame.time.Clock()
    title = font.render("Reflexo Quântico", True, (255, 255, 255))
    subtitle = font.render("Colida com o portal da cor-alvo antes do tempo acabar", True, (255, 255, 255))
    instructions = [
        "Movimento: (w/s/a/d) teclas configuradas para cima/baixo/esquerda/direita",
        "Boost (o): Acelera | Foco (p): Movimento mais preciso | Enter/Pause: Pausa, no segundo toque sai do jogo",
        "o: Iniciar o jogo | p: Sair do jogo",
    ]
    rendered = [font.render(text, True, (255, 255, 255)) for text in instructions]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == start_key:
                    return "start"
                if event.key == back_key:
                    pygame.quit()
                    sys.exit(0)

        screen.fill((0, 0, 0))
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        screen.blit(title, title.get_rect(center=(center_x, center_y - 80)))
        screen.blit(subtitle, subtitle.get_rect(center=(center_x, center_y - 40)))
        offset = 10
        for idx, line in enumerate(rendered):
            screen.blit(line, line.get_rect(center=(center_x, center_y + offset + idx * 30)))

        pygame.display.flip()
        clock.tick(60)


def run_game() -> None:
    """Função principal do jogo Reflexo Quântico."""
    settings = load_settings(CONFIG_PATH)

    pygame.init()
    pygame.display.set_caption("Reflexo Quântico - PyGaming Hub")

    controls = map_control_keys(settings["controls"])
    width = settings["display"]["width"]
    height = settings["display"]["height"]
    fullscreen = settings["display"].get("fullscreen", False)
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((width, height), flags)

    music_loaded = False
    try:
        pygame.mixer.init()
        if MUSIC_PATH.exists():
            pygame.mixer.music.load(str(MUSIC_PATH))
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
            music_loaded = True
    except pygame.error:
        music_loaded = False
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    show_intro = True
    while True:
        if show_intro:
            start_choice = show_start_screen(
                screen,
                font,
                controls["action_a"],
                controls["action_b"],
                controls["pause"],
            )
            if start_choice == "exit":
                pygame.quit()
                return

        player_rect = pygame.Rect(
            width // 2 - PLAYER_SIZE // 2, height // 2 - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE
        )
        portals = {name: random_portal_position(width, height) for name in COLOR_PALETTE}
        target_color, round_start = reset_round(portals, width, height)

        score = 0
        errors = 0
        game_start = pygame.time.get_ticks()
        pause_accum_game = 0
        pause_accum_round = 0
        paused = False
        pause_start = None
        paused_total_left = GAME_DURATION
        paused_round_left = ROUND_DURATION

        running = True
        exit_to_hub = False
        while running:
            dt = clock.tick(60)
            now = pygame.time.get_ticks()
            if paused:
                total_time_left = paused_total_left
                round_time_left = paused_round_left
            else:
                total_elapsed = (now - game_start - pause_accum_game) / 1000
                total_time_left = max(0.0, GAME_DURATION - total_elapsed)
                round_time_left = max(0.0, ROUND_DURATION - (now - round_start - pause_accum_round) / 1000)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    exit_to_hub = True
                elif event.type == pygame.KEYDOWN and event.key == controls["pause"]:
                    if not paused:
                        paused = True
                        pause_start = now
                        paused_total_left = total_time_left
                        paused_round_left = round_time_left
                    else:
                        running = False
                        exit_to_hub = True
                elif event.type == pygame.KEYDOWN and paused and event.key == controls["action_a"]:
                    paused = False
                    if pause_start is not None:
                        pause_delta = pygame.time.get_ticks() - pause_start
                        pause_accum_game += pause_delta
                        pause_accum_round += pause_delta
                    pause_start = None

            if paused:
                screen.fill((0, 0, 0))
                draw_portals(screen, portals)
                pygame.draw.rect(screen, (255, 255, 255), player_rect)
                draw_hud(screen, font, score, total_time_left, round_time_left, target_color)
                pause_text = font.render("PAUSADO - Enter: Sair do jogo | o: Continua", True, (255, 200, 50))
                screen.blit(pause_text, pause_text.get_rect(center=(width // 2, height // 2)))
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            speed = BASE_SPEED
            if keys[controls["action_a"]]:
                speed += 10
            if keys[controls["action_b"]]:
                speed = max(3, speed - 2)

            if keys[controls["left"]]:
                player_rect.x -= speed
            if keys[controls["right"]]:
                player_rect.x += speed
            if keys[controls["up"]]:
                player_rect.y -= speed
            if keys[controls["down"]]:
                player_rect.y += speed

            player_rect.clamp_ip(screen.get_rect())

            # Verifica colisões com portais
            collided_color = None
            for name, position in portals.items():
                if circle_rect_collision(position, PORTAL_RADIUS, player_rect):
                    collided_color = name
                    break

            if collided_color:
                if collided_color == target_color:
                    score += 1
                    target_color, round_start = reset_round(portals, width, height)
                    pause_accum_round = 0
                else:
                    score -= 1
                    errors += 1
                    target_color, round_start = reset_round(portals, width, height)
                    pause_accum_round = 0

            if round_time_left <= 0:
                score -= 1
                errors += 1
                target_color, round_start = reset_round(portals, width, height)
                pause_accum_round = 0
                round_time_left = ROUND_DURATION

            if total_time_left <= 0 or errors >= MAX_ERRORS:
                break

            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), player_rect)
            draw_portals(screen, portals)
            draw_hud(screen, font, score, total_time_left, round_time_left, target_color)

            pygame.display.flip()

        if exit_to_hub:
            break

        if total_time_left <= 0 or errors >= MAX_ERRORS:
            choice = show_game_over(
                screen,
                font,
                score,
                controls["action_a"],
                controls["pause"],
            )
            if choice == "restart":
                show_intro = False
                continue
            else:
                break

        break

    if music_loaded:
        pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    run_game()
