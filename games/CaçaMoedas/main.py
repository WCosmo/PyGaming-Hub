import pygame
from collections import deque

# -------------------------------
# CONFIGURAÇÕES BÁSICAS DO JOGO
# -------------------------------
WIDTH, HEIGHT = 800, 600   # resolução da janela (no PyGaming-Hub virá do conf.ini)
FPS = 60                   # quadros por segundo
TILE = 40                  # tamanho de cada célula do grid em pixels

# -------------------------------
# MAPA EM GRID
# '#' = parede
# 'P' = posição inicial do player
# 'G' = posição inicial do inimigo
# qualquer outra coisa é caminho
# -------------------------------
LEVEL = [
    "####################",
    "#P.......#.........#",
    "#.#####..#..###....#",
    "#.....#.....#......#",
    "###.#.###.###.###..#",
    "#...#.....#....#...#",
    "#.#######.#.###.#..#",
    "#.......#.#.....#..#",
    "#.###.#.#.#####.#..#",
    "#...#.#.#.....#.#..#",
    "#.#.#.#.###.#.#.#..#",
    "#.#...#.....#...#..#",
    "#.#####.#####.###..#",
    "#........G.........#",
    "####################",
]

ROWS = len(LEVEL)
COLS = len(LEVEL[0])

def grid_to_px(c, r):
    """
    Converte coordenadas de grid (coluna, linha)
    para coordenadas em pixels (centro do tile).
    """
    return c * TILE + TILE // 2, r * TILE + TILE // 2

def neighbors(c, r):
    """
    Retorna os vizinhos caminháveis (não parede) de (c, r)
    nas 4 direções (cima, baixo, esquerda, direita).
    """
    for dc, dr in ((1,0),(-1,0),(0,1),(0,-1)):
        nc, nr = c + dc, r + dr
        # dentro dos limites do mapa e não é parede
        if 0 <= nc < COLS and 0 <= nr < ROWS and LEVEL[nr][nc] != '#':
            yield nc, nr

def bfs_step(start, goal):
    """
    Usa Busca em Largura (BFS) para encontrar um caminho
    de 'start' até 'goal' no grid.
    Retorna APENAS o PRÓXIMO passo a partir de 'start'.

    start e goal são tuplas (coluna, linha).
    """
    if start == goal:
        return start

    q = deque([start])   # fila da BFS
    parent = {start: None}  # guarda de onde cada célula foi alcançada

    # BFS padrão
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nb in neighbors(*cur):
            if nb not in parent:
                parent[nb] = cur
                q.append(nb)

    # se goal não foi alcançado, não há caminho
    if goal not in parent:
        return start

    # reconstrói o caminho goal -> start usando 'parent'
    cur = goal
    path = []
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()

    # path[0] = start, path[1] = primeiro passo em direção ao goal
    if len(path) >= 2:
        return path[1]
    return start

def main():
    # inicialização do Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Foge-Foge (Pac-Man simples)")

    # ---------------------------
    # CRIAÇÃO DAS ESTRUTURAS
    # ---------------------------
    walls = []          # lista de retângulos para desenhar paredes
    dots = set()        # conjunto de coordenadas (c, r) das moedas
    player_pos = None   # posição do jogador no grid
    enemy_pos = None    # posição do inimigo no grid

    # varre o LEVEL e preenche as estruturas
    for r, line in enumerate(LEVEL):
        for c, ch in enumerate(line):
            x, y = grid_to_px(c, r)

            if ch == '#':
                # cria um retângulo para a parede (para desenhar)
                walls.append(pygame.Rect(c * TILE, r * TILE, TILE, TILE))
            else:
                # define posições iniciais de player e inimigo
                if ch == 'P':
                    player_pos = [c, r]
                elif ch == 'G':
                    enemy_pos = [c, r]
                # qualquer célula que não seja parede ganha uma moeda,
                # exceto a posição inicial do player
                if ch != 'P':
                    dots.add((c, r))

    font = pygame.font.SysFont("consolas", 24)

    running = True
    move_cooldown = 0.0    # tempo até o próximo movimento do player
    enemy_cooldown = 0.0   # tempo até o próximo movimento do inimigo
    score = 0
    game_over = False
    win = False

    # ---------------------------
    # LOOP PRINCIPAL
    # ---------------------------
    while running:
        dt = clock.tick(FPS) / 1000.0  # tempo entre frames em segundos

        # 1) trata eventos do Pygame (fechar janela)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # no PyGaming-Hub, aqui entraria a tecla PAUSE do conf.ini
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False

        # 2) atualização da lógica do jogo, se não houve game over
        if not game_over:
            move_cooldown -= dt
            enemy_cooldown -= dt

            # 2.1) movimento do player (um tile por vez)
            dc = dr = 0
            if move_cooldown <= 0:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dc = -1
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dc = 1
                elif keys[pygame.K_UP] or keys[pygame.K_w]:
                    dr = -1
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dr = 1

                if dc != 0 or dr != 0:
                    nc = player_pos[0] + dc
                    nr = player_pos[1] + dr
                    # só anda se não for parede
                    if LEVEL[nr][nc] != '#':
                        player_pos = [nc, nr]
                        move_cooldown = 0.12  # controla velocidade de movimento

                        # se havia moeda nessa célula, remove do conjunto
                        if (nc, nr) in dots:
                            dots.remove((nc, nr))
                            score += 10

                            # se não há mais moedas, o jogador venceu
                            if not dots:
                                game_over = True
                                win = True

            # 2.2) movimento do inimigo usando BFS
            if enemy_cooldown <= 0:
                enemy_cooldown = 0.18
                # calcula próximo passo em direção ao player
                enemy_pos = list(bfs_step(tuple(enemy_pos), tuple(player_pos)))

            # 2.3) checa se o inimigo pegou o player
            if tuple(enemy_pos) == tuple(player_pos):
                game_over = True
                win = False

        # 3) desenho
        screen.fill((0, 0, 0))

        # paredes
        for w in walls:
            pygame.draw.rect(screen, (40, 40, 200), w)

        # moedas
        for (c, r) in dots:
            x, y = grid_to_px(c, r)
            pygame.draw.circle(screen, (255, 255, 0), (x, y), 6)

        # player (verde)
        px, py = grid_to_px(*player_pos)
        pygame.draw.circle(screen, (50, 255, 50), (px, py), TILE // 2 - 4)

        # inimigo (vermelho)
        ex, ey = grid_to_px(*enemy_pos)
        pygame.draw.circle(screen, (255, 50, 50), (ex, ey), TILE // 2 - 4)

        # HUD (pontuação)
        hud = font.render(f"Pontos: {score}", True, (255, 255, 255))
        screen.blit(hud, (10, 10))

        # mensagem de game over
        if game_over:
            txt = "VOCÊ VENCEU!" if win else "PEGARAM VOCÊ!"
            msg = font.render(txt + "  (R = reiniciar, ESC = sair)", True, (255, 255, 255))
            rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(msg, rect)

            # opção de reiniciar rapidamente (fora do PyGaming-Hub)
            if keys[pygame.K_r]:
                return  # volta para main(); no Hub, o console controla isso

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
