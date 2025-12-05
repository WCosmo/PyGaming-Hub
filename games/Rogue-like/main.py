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
    CONTROLS_KEY_CODES['UP'] = pygame.key.key_code(config.get(controls_section, 'up', fallback='w'))
    CONTROLS_KEY_CODES['DOWN'] = pygame.key.key_code(config.get(controls_section, 'down', fallback='s'))
    CONTROLS_KEY_CODES['LEFT'] = pygame.key.key_code(config.get(controls_section, 'left', fallback='a'))
    CONTROLS_KEY_CODES['RIGHT'] = pygame.key.key_code(config.get(controls_section, 'right', fallback='d'))
    CONTROLS_KEY_CODES['A'] = pygame.key.key_code(config.get(controls_section, 'action_a', fallback='o'))
    CONTROLS_KEY_CODES['PAUSE'] = pygame.key.key_code(config.get(controls_section, 'pause', fallback='enter'))


except Exception as e:
    print(f"ERRO: Não foi possível carregar a configuração do console: {e}")
    print("Usando controles e resolução padrão (800x600, WASD, O, P, Enter).")
    CONTROLS_KEY_CODES = {
        'UP': pygame.K_w, 'DOWN': pygame.K_s, 'LEFT': pygame.K_a, 'RIGHT': pygame.K_d,
        'A': pygame.K_o, 'B': pygame.K_p, 'PAUSE': pygame.K_RETURN
    }


import pygame
from settings import *
from core.engine import Engine
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from ui.game_over import GameOverScreen
from sounds import *
global_score = 0
def main():
    game = Engine()
    player = Player(400, 500)
    enemies = [Enemy() for _ in range(10)]
    projectiles = []
    enemy_projectiles = []
    boss_projectiles = []
    boss = None
    game_over = False
    go_screen = GameOverScreen()
    global global_score
    pygame.mixer.music.play(-1)



    while True:
        game.window.fill((20, 20, 20))
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key ==pygame.K_RETURN and game_over:
                    return
            if ev.type == pygame.QUIT:
                return
            if game_over and ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if go_screen.btn_restart.is_clicked((mx, my)):
                    return main()
                if go_screen.btn_exit.is_clicked((mx, my)):
                    return

        if not game_over:
            # MOVE PLAYER
            keys = pygame.key.get_pressed()
            player.handly_ability(keys)
            player.auto_shoot(projectiles, enemies, boss)
            player.move(keys)
            player.update_damage_timer()
            player.update_cooldown()
            player.draw(game.window)


            # ENEMIES
            for e in enemies:
                e.follow(player)
                e.shoot(player, enemy_projectiles)
                e.draw(game.window)

                if not hasattr(player, 'damager_timer'):
                    player.damage_timer = 0

                if player.damage_timer == 0 and pygame.Rect(e.x,e.y,35, 35).colliderect(pygame.Rect(player.x,player.y,40,40)):
                    if player.damage_timer == 0:
                        player.hp -= 1
                        player.damage_timer = 100 # invencibilidade por 1 segundo


                # Player bullets x enemy
                for p in projectiles:
                    if pygame.Rect(p.x,p.y,6,6).colliderect(
                            pygame.Rect(e.x,e.y,35,35)):
                        e.hp -= 1
                        projectiles.remove(p)
                        if e.hp <= 0:
                            enemies.remove(e)
                            global_score += 1

            # SPAWN BOSS
            if len(enemies) == 0 and boss is None:
                boss = Boss()

            # BOSS
            if boss:
                boss.draw(game.window)
                boss.shoot(boss_projectiles)

                
                PLAYER_PROJECTILE_RADIUS = 6  # igual ao p.radius

                for p in projectiles[:]:
                    proj_rect = pygame.Rect(
                        p.x - p.radius,
                        p.y - p.radius,
                        p.radius * 2,
                        p.radius * 2
                    )

                    boss_rect = pygame.Rect(boss.x, boss.y, boss.size, boss.size)

                    if boss_rect.colliderect(proj_rect):
                        boss.take_damage(1)
                        projectiles.remove(p)




                if boss.hp <= 0:
                    global_score += 10
                    return main()

            # Player projectiles
            for p in projectiles:
                p.move()
                p.draw(game.window)

            # Enemy projectiles
            for ep in enemy_projectiles:
                ep.move()
                ep.draw(game.window)

                if pygame.Rect(ep.x,ep.y,6,6).colliderect(
                        pygame.Rect(player.x,player.y,40,40)):
                    player.hp -= 1
                    enemy_projectiles.remove(ep)
            # Boss projectiles
            font = pygame.font.SysFont('arial', 24)
            life_text = font.render(f'vida : {player.hp}', True, (255, 0, 0))
            text = font.render(f'pontos : {global_score}', True, (255, 255, 0))
            game.window.blit(life_text, (10, 10))
            game.window.blit(text, (10, 40))
            for bp in boss_projectiles:
                bp.move()
                bp.draw(game.window)

                proj_rect = pygame.Rect(
                    bp.x - bp.size,
                    bp.y - bp.size,
                    bp.size * 2,
                    bp.size * 2
                )

                player_rect = pygame.Rect(player.x, player.y, 40, 40)

                if proj_rect.colliderect(player_rect):
                    player.hp -= 1
                    boss_projectiles.remove(bp)


            # CHECK GAME OVER
            if player.hp <= 0:
                global_score = 0
                pygame.mixer.music.stop()
                game_over = True

        else:
            go_screen.draw(game.window)

        game.update()

if __name__ == "__main__":
    main()
