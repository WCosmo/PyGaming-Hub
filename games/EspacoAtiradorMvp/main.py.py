import pygame
import configparser
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_PATH = os.path.join(BASE_DIR, "conf.inf")   

config = configparser.ConfigParser()

if not os.path.exists(CONF_PATH):
    print(f"ERRO: O arquivo conf.inf não foi encontrado em: {CONF_PATH}")
    sys.exit()

config.read(CONF_PATH)


width = config.getint("Display", "width")
height = config.getint("Display", "height")
fullscreen = config.getboolean("Display", "fullscreen")


def key(name):
    if len(name) == 1:  
        return getattr(pygame, f"K_{name.lower()}")
    return getattr(pygame, f"K_{name.upper()}")

key_up = key(config.get("Controls", "up"))
key_down = key(config.get("Controls", "down"))
key_left = key(config.get("Controls", "left"))
key_right = key(config.get("Controls", "right"))
key_action_a = key(config.get("Controls", "action_a"))
key_action_b = key(config.get("Controls", "action_b"))
key_pause = key(config.get("Controls", "pause"))

pygame.init()

if fullscreen:
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Jogo com Config via INF")
clock = pygame.time.Clock()

player = pygame.Rect(width // 2, height // 2, 50, 50)
player_speed = 6

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == key_pause:
                running = False
            if event.key == key_action_a:
                print("Ação A (O)")
            if event.key == key_action_b:
                print("Ação B (P)")

    keys = pygame.key.get_pressed()

    if keys[key_up]:
        player.y -= player_speed
    if keys[key_down]:
        player.y += player_speed
    if keys[key_left]:
        player.x -= player_speed
    if keys[key_right]:
        player.x += player_speed

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), player)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
