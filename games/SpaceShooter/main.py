import os
import configparser
import pygame
import random

def load_config(path):
    config = configparser.ConfigParser()
    if os.path.exists(path):
        config.read(path)
    return config

def key_name_to_keycode(name):
    if not name:
        return None
    name = name.strip()
    if name.isdigit():
        return int(name)
    if name.upper().startswith("K_"):
        name = name[2:]
    try:
        return pygame.key.key_code(name)
    except Exception:
        pass
    fallback = {
        "SPACE": pygame.K_SPACE,
        "ENTER": pygame.K_RETURN,
        "RETURN": pygame.K_RETURN,
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        "PAUSE": pygame.K_PAUSE,
        "ESC": pygame.K_ESCAPE,
        "A": pygame.K_a,
        "D": pygame.K_d,
        "W": pygame.K_w,
        "S": pygame.K_s,
    }
    if name.upper() in fallback:
        return fallback[name.upper()]
    attr = "K_" + name.upper()
    return getattr(pygame, attr, None)

def main():
    pygame.init()
    clock = pygame.time.Clock()

    base_dir = os.path.dirname(__file__)
    conf_path = os.path.join(base_dir, "..", "conf", "conf.ini")
    config = load_config(conf_path)

    width, height = 800, 600
    fullscreen = False

    default_controls = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "action_a": "space",
        "pause": "escape"
    }

    if config and "Display" in config:
        width = config.getint("Display", "width", fallback=width)
        height = config.getint("Display", "height", fallback=height)
        fullscreen = config.getboolean("Display", "fullscreen", fallback=fullscreen)

    controls = default_controls.copy()
    if config and "Controls" in config:
        for k in controls:
            if config.has_option("Controls", k):
                controls[k] = config.get("Controls", k)

    keycodes = {k: key_name_to_keycode(v) for k, v in controls.items()}

    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Space Shooter Deluxe")

    player_w, player_h = 45, 28

    def new_pos():
        return width // 2 - player_w // 2, height - player_h - 10

    player_x, player_y = new_pos()
    player_speed = 7

    bullets = []
    enemies = []
    hearts = []

    enemy_spawn_timer = 0
    enemy_spawn_delay = 1300

    heart_spawn_timer = 0
    heart_spawn_delay = 5000

    score = 0
    vidas = 3

    font = pygame.font.SysFont(None, 24)
    btn_exit = pygame.Rect(10, height - 70, 120, 50)

    running = True
    game_over = False
    shooting = False

    shot_delay = 220
    shot_timer = 0

    stars = [{"x": random.randint(0, width),
              "y": random.randint(0, height),
              "speed": random.randint(1, 3)} for _ in range(100)]

    def reset_game():
        nonlocal bullets, enemies, hearts, enemy_spawn_timer, score, vidas, player_x, player_y, game_over
        bullets = []
        enemies = []
        hearts = []
        enemy_spawn_timer = 0
        score = 0
        vidas = 3
        player_x, player_y = new_pos()
        game_over = False

    def shoot():
        bx = player_x + player_w // 2 - 3
        by = player_y - 6
        bullets.append({"rect": pygame.Rect(bx, by, 6, 14), "dy": -9})

    while running:
        dt = clock.tick(60)
        shot_timer += dt

        if shooting and shot_timer >= shot_delay and not game_over:
            shoot()
            shot_timer = 0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if keycodes.get("pause") and event.key == keycodes["pause"]:
                    running = False
                if game_over and event.key == pygame.K_r:
                    reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_exit.collidepoint(event.pos):
                    running = False
                if event.button == 1 and not game_over:
                    shooting = True
                    shot_timer = shot_delay

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    shooting = False

        if game_over:
            screen.fill((10, 10, 25))

            big = pygame.font.SysFont(None, 70)
            score_big = big.render(f"SCORE: {score}", True, (255, 255, 120))
            screen.blit(score_big, score_big.get_rect(center=(width//2, height//2 + 30)))

            go_big = pygame.font.SysFont(None, 90)
            go = go_big.render("GAME OVER", True, (255, 80, 80))
            screen.blit(go, go.get_rect(center=(width//2, height//2 - 40)))

            sub = font.render("Pressione R para reiniciar", True, (200, 200, 200))
            screen.blit(sub, sub.get_rect(center=(width//2, height//2 + 80)))

            pygame.draw.rect(screen, (180, 60, 60), btn_exit, border_radius=10)
            screen.blit(font.render("SAIR", True, (255, 255, 255)),
                        (btn_exit.x + 35, btn_exit.y + 15))

            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += player_speed

        player_x = max(0, min(player_x, width - player_w))
        player_y = max(0, min(player_y, height - player_h))

        screen.fill((5, 5, 15))
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), (star["x"], star["y"]), 2)
            star["y"] += star["speed"]
            if star["y"] > height:
                star["y"] = 0
                star["x"] = random.randint(0, width)

        for b in bullets[:]:
            b["rect"].y += b["dy"]
            if b["rect"].bottom < 0:
                bullets.remove(b)

        enemy_spawn_timer += dt
        if enemy_spawn_timer >= enemy_spawn_delay:
            enemy_spawn_timer = 0
            ex = random.randint(10, width - 40)
            ew = 45
            eh = 35
            dy = random.randint(3, 5)
            enemies.append({"rect": pygame.Rect(ex, -eh, ew, eh), "dy": dy})

        for e in enemies[:]:
            e["rect"].y += e["dy"]
            if e["rect"].top > height:
                enemies.remove(e)
                vidas -= 1
                if vidas <= 0:
                    game_over = True

        for b in bullets[:]:
            for e in enemies[:]:
                if b["rect"].colliderect(e["rect"]):
                    bullets.remove(b)
                    enemies.remove(e)
                    score += 10
                    break

        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

        for e in enemies[:]:
            if player_rect.colliderect(e["rect"]):
                enemies.remove(e)
                vidas -= 1
                if vidas <= 0:
                    game_over = True

        heart_spawn_timer += dt
        if heart_spawn_timer >= heart_spawn_delay:
            heart_spawn_timer = 0
            hx = random.randint(20, width - 20)
            hearts.append({"x": hx, "y": -20, "dy": 2})

        for h in hearts[:]:
            h["y"] += h["dy"]
            hr = pygame.Rect(h["x"], h["y"], 22, 22)
            if player_rect.colliderect(hr):
                hearts.remove(h)
                vidas += 1
            if h["y"] > height:
                hearts.remove(h)

        ship_points = [
            (player_x + player_w//2, player_y),
            (player_x, player_y + player_h),
            (player_x + player_w, player_y + player_h),
        ]
        pygame.draw.polygon(screen, (80, 180, 255), ship_points)
        pygame.draw.rect(screen, (30, 120, 200),
                         (player_x + player_w//2 - 6, player_y + 8, 12, 8))

        for e in enemies:
            ex, ey, ew, eh = e["rect"]
            enemy_points = [
                (ex + ew//2, ey),
                (ex, ey + eh),
                (ex + ew, ey + eh),
            ]
            pygame.draw.polygon(screen, (255, 50, 50), enemy_points)
            pygame.draw.circle(screen, (0, 0, 0), (ex + ew//2, ey + eh//2), 5)

        for b in bullets:
            pygame.draw.rect(screen, (255, 240, 100), b["rect"])

        for h in hearts:
            x, y = h["x"], h["y"]
            pygame.draw.circle(screen, (0, 200, 0), (x, y), 8)
            pygame.draw.circle(screen, (0, 200, 0), (x+12, y), 8)
            pygame.draw.polygon(screen, (0, 200, 0),
                                [(x-5, y+5), (x+17, y+5), (x+6, y+17)])

        hud = font.render(f"Score: {score}   Vidas: {vidas}", True, (220, 220, 220))
        screen.blit(hud, (10, 10))

        pygame.draw.rect(screen, (180, 60, 60), btn_exit, border_radius=10)
        screen.blit(font.render("SAIR", True, (255, 255, 255)),
                    (btn_exit.x + 35, btn_exit.y + 15))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
