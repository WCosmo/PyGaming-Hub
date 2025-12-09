import pygame
import configparser
import os

def load_config():
    config = configparser.ConfigParser()
    config.read(os.path.join("..", "..", "conf", "conf.ini"))

    width = config.getint("Display", "width", fallback=800)
    height = config.getint("Display", "height", fallback=600)

    controls_raw = dict(config.items("Controls"))
    controls = {}
    for name, key_name in controls_raw.items():
        try:
            controls[name] = getattr(pygame, f"K_{key_name}")
        except AttributeError:
            print(f"Tecla inválida em conf.ini: {key_name}")
    return width, height, controls

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 5

    def move(self, keys, controls):
        if keys[controls.get("up", pygame.K_w)]:
            self.y -= self.speed
        if keys[controls.get("down", pygame.K_s)]:
            self.y += self.speed
        if keys[controls.get("left", pygame.K_a)]:
            self.x -= self.speed
        if keys[controls.get("right", pygame.K_d)]:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size))

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = speed

    def update(self, screen_width):
        self.x -= self.speed
        if self.x < -self.size:
            self.x = screen_width + self.size

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.size, self.size))

def main():
    pygame.init()

    width, height, controls = load_config()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Quadrado que Desvia")
    clock = pygame.time.Clock()

    player = Player(width // 4, height // 2)
    enemies = [
        Enemy(width, height // 3, 4),
        Enemy(width + 200, height // 1.5, 6)
    ]

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == controls.get("pause", pygame.K_ESCAPE):
                    running = False

        keys = pygame.key.get_pressed()
        player.move(keys, controls)

        player.draw(screen)

        for enemy in enemies:
            enemy.update(width)
            enemy.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
