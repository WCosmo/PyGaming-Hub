import pygame 
import random
import configparser
import os

pygame.init

def carregar_config():
    config = configparser.ConfigParser()
    config.read(os.path.join("conf", "conf.ini"))

    # Display
    width = int(config["Display"]["width"])
    height = int(config["Display"]["height"])
    fullscreen = config["Display"].getboolean("fullscreen")

    # Controles
    keys = {}
    for nome, valor in config["Controls"].items():
        keys[nome] = getattr(pygame, f"K_{valor}")

    return width, height, fullscreen, keys


class Carta:
    def __init__(self, x, y, tamanho, cor):
        self.x = x
        self.y = y
        self.tamanho = tamanho
        self.cor = cor
        self.revelada = False
        self.combinada = False

    def desenhar(self, tela):
        if self.revelada or self.combinada:
            pygame.draw.rect(tela, self.cor, (self.x, self.y, self.tamanho, self.tamanho), border_radius=8)
        else:
            pygame.draw.rect(tela, (180, 180, 180), (self.x, self.y, self.tamanho, self.tamanho), border_radius=8)
            pygame.draw.rect(tela, (100, 100, 100), (self.x, self.y, self.tamanho, self.tamanho), 3, border_radius=8)

    def contem(self, px, py):
        return (self.x <= px <= self.x + self.tamanho) and (self.y <= py <= self.y + self.tamanho)


def main():
    pygame.init()

    width, height, fullscreen, keys = carregar_config()
    flags = pygame.FULLSCREEN if fullscreen else 0
    tela = pygame.display.set_mode((width, height), flags)
    pygame.display.set_caption("Jogo da Memória")

    clock = pygame.time.Clock()

    # Layout da grade
    linhas, colunas = 4, 4
    total = linhas * colunas
    tamanho = min(width // (colunas + 2), height // (linhas + 2))

    margem_x = (width - (colunas * tamanho)) // 2
    margem_y = (height - (linhas * tamanho)) // 2

    # Criar cores dos pares
    cores = []
    for _ in range(total // 2):
        cores.append((random.randint(30, 255), random.randint(30, 255), random.randint(30, 255)))
    cores = cores * 2
    random.shuffle(cores)

    # Criar cartas
    cartas = []
    idx = 0
    for i in range(linhas):
        for j in range(colunas):
            x = margem_x + j * tamanho
            y = margem_y + i * tamanho
            cartas.append(Carta(x, y, tamanho, cores[idx]))
            idx += 1

    primeira = None
    segunda = None
    intervalo = 0

    rodando = True
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN:
                if event.key == keys["pause"]:
                    rodando = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for carta in cartas:
                    if carta.contem(mx, my) and not carta.combinada:
                        if not carta.revelada:
                            carta.revelada = True
                            if primeira is None:
                                primeira = carta
                            elif segunda is None:
                                segunda = carta
                                intervalo = pygame.time.get_ticks()

        # Lógica de comparação
        if primeira and segunda:
            if pygame.time.get_ticks() - intervalo > 800:
                if primeira.cor == segunda.cor:
                    primeira.combinada = True
                    segunda.combinada = True
                else:
                    primeira.revelada = False
                    segunda.revelada = False
                primeira, segunda = None, None

        # Desenha
        tela.fill((40, 40, 40))

        for carta in cartas:
            carta.desenhar(tela)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
