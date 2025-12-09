import pygame
import sys
import os
import configparser
import random

CONFIG_FILE = os.path.join('conf', 'conf.ini')
config = configparser.ConfigParser()

CONTROLS_KEY_CODES = {}
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FULLSCREEN = False

try:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Arquivo de configuration do console não encontrado em {CONFIG_FILE}")

    config.read(CONFIG_FILE)

    display_section = 'Display'
    SCREEN_WIDTH = config.getint(display_section, 'width', fallback=1280)
    SCREEN_HEIGHT = config.getint(display_section, 'height', fallback=720)
    FULLSCREEN = config.getboolean(display_section, 'fullscreen', fallback=False)

    controls_section = 'Controls'
    CONTROLS_KEY_CODES['LEFT'] = pygame.key.key_code(config.get(controls_section, 'left', fallback='a'))
    CONTROLS_KEY_CODES['RIGHT'] = pygame.key.key_code(config.get(controls_section, 'right', fallback='d'))
    CONTROLS_KEY_CODES['PAUSE'] = pygame.key.key_code(config.get(controls_section, 'pause', fallback='enter'))


except Exception as e:
    print(f"ERRO: Não foi possível carregar a configuração do console: {e}")
    print("Usando controles e resolução padrão (800x600, WASD, O, P, Enter).")
    CONTROLS_KEY_CODES = {
        'LEFT': pygame.K_a, 'RIGHT': pygame.K_d,
        'PAUSE': pygame.K_RETURN
    }

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

pygame.init()

TELA = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Vertical")

FUNDO = (20, 20, 30)
RAQUETE_JOGADOR_COR = (0, 200, 255)
RAQUETE_IA_COR = (255, 80, 80)
BOLA_COR = (255, 255, 255)
LINHA_COR = (100, 100, 100)
FONTE_COR = (240, 240, 240)

raquete_largura, raquete_altura = 100, 15

raquete_jogador = pygame.Rect(
    (SCREEN_WIDTH // 2) - (raquete_largura // 2),
    SCREEN_HEIGHT - 40,
    raquete_largura,
    raquete_altura
)

raquete_ia = pygame.Rect(
    (SCREEN_WIDTH // 2) - (raquete_largura // 2),
    25,
    raquete_largura,
    raquete_altura
)

bola = pygame.Rect(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - 10, 20, 20)

vel_raquete = 7
vel_bola_x = 5 * random.choice([-1, 1])
vel_bola_y = 5 * random.choice([-1, 1])
vel_raquete_ia = 4

pontos_ia = 0
pontos_jogador = 0
fonte = pygame.font.SysFont('Consolas', 60)

clock = pygame.time.Clock()
rodando = True

def resetar_bola():
    global vel_bola_x, vel_bola_y
    bola.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    vel_bola_x = 5 * random.choice([-1, 1])
    vel_bola_y = 5 * random.choice([-1, 1])

while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == CONTROLS_KEY_CODES['PAUSE']:
                rodando = False

    teclas = pygame.key.get_pressed()
    if teclas[CONTROLS_KEY_CODES['LEFT']] and raquete_jogador.left > 0:
        raquete_jogador.x -= vel_raquete
    if teclas[CONTROLS_KEY_CODES['RIGHT']] and raquete_jogador.right < SCREEN_WIDTH:
        raquete_jogador.x += vel_raquete
    if teclas[pygame.K_ESCAPE]:
        rodando = False

    if raquete_ia.centerx < bola.centerx and raquete_ia.right < SCREEN_WIDTH:
        raquete_ia.x += vel_raquete_ia
    elif raquete_ia.centerx > bola.centerx and raquete_ia.left > 0:
        raquete_ia.x -= vel_raquete_ia

    bola.x += vel_bola_x
    bola.y += vel_bola_y

    if bola.left <= 0 or bola.right >= SCREEN_WIDTH:
        vel_bola_x *= -1

    if bola.colliderect(raquete_jogador) and vel_bola_y > 0:
        vel_bola_y *= -1
    if bola.colliderect(raquete_ia) and vel_bola_y < 0:
        vel_bola_y *= -1

    if bola.top <= 0:
        pontos_jogador += 1
        resetar_bola()

    if bola.bottom >= SCREEN_HEIGHT:
        pontos_ia += 1
        resetar_bola()

    TELA.fill(FUNDO)
    pygame.draw.line(TELA, LINHA_COR, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 3)
    pygame.draw.rect(TELA, RAQUETE_JOGADOR_COR, raquete_jogador, border_radius=8)
    pygame.draw.rect(TELA, RAQUETE_IA_COR, raquete_ia, border_radius=8)
    pygame.draw.ellipse(TELA, BOLA_COR, bola)

    pontos_txt_jogador = fonte.render(f"{pontos_jogador}", True, FONTE_COR)
    pontos_txt_ia = fonte.render(f"{pontos_ia}", True, FONTE_COR)
    TELA.blit(pontos_txt_jogador, (SCREEN_WIDTH - 60, SCREEN_HEIGHT // 2 + 20))
    TELA.blit(pontos_txt_ia, (SCREEN_WIDTH - 60, SCREEN_HEIGHT // 2 - 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
