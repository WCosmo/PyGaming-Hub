import pygame
import sys
import os
import configparser
import random

# --- Configuração Inicial (Herdada do SimpleMover) ---
CONFIG_FILE = os.path.join('conf', 'conf.ini')
config = configparser.ConfigParser()

# Valores padrão (usados se o conf.ini não for encontrado)
CONTROLS_KEY_CODES = {}
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FULLSCREEN = False

# Mapeamento de teclas padrão (para uso quando o conf.ini não é lido)
DEFAULT_CONTROLS = {
    'up': 'w',
    'down': 's',
    'left': 'a',
    'right': 'd',
    'action_a': 'o',
    'action_b': 'p',
    'pause': 'enter'
}

# Tenta ler o arquivo de configuração
config_loaded = False
if os.path.exists(CONFIG_FILE):
    try:
        config.read(CONFIG_FILE)
        config_loaded = True
    except configparser.Error as e:
        print(f"AVISO: ERRO ao ler o arquivo de configuração ({CONFIG_FILE}): {e}. Usando valores padrão.")

if config_loaded:
    # Carregar Configurações de Display
    display_section = 'Display'
    SCREEN_WIDTH = config.getint(display_section, 'width', fallback=SCREEN_WIDTH)
    SCREEN_HEIGHT = config.getint(display_section, 'height', fallback=SCREEN_HEIGHT)
    FULLSCREEN = config.getboolean(display_section, 'fullscreen', fallback=FULLSCREEN)

    # Carregar Configurações de Controles
    controls_section = 'Controls'
    for action, fallback_key in DEFAULT_CONTROLS.items():
        key_name = config.get(controls_section, action, fallback=fallback_key)
        CONTROLS_KEY_CODES[action.upper()] = pygame.key.key_code(key_name)
else:
    print(f"AVISO: Arquivo de configuração do console não encontrado em {CONFIG_FILE}. Usando configurações padrão.")
    # Usar os valores padrão e mapear as teclas padrão
    for action, key_name in DEFAULT_CONTROLS.items():
        CONTROLS_KEY_CODES[action.upper()] = pygame.key.key_code(key_name)


# --- Inicialização do Pygame ---
pygame.init()

# Configuração da tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN if FULLSCREEN else 0)
pygame.display.set_caption("Simple Pong - PyGaming Hub")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# Fontes
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)

# --- Variáveis do Jogo ---
# Paletas
paddle_width = 10
paddle_height = 100
paddle_speed = 7

# Posições iniciais das paletas
player1_y = SCREEN_HEIGHT // 2 - paddle_height // 2
player2_y = SCREEN_HEIGHT // 2 - paddle_height // 2

# Bola
ball_radius = 8
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
# Velocidade inicial da bola (aleatória)
ball_dx = random.choice([-5, 5])
ball_dy = random.choice([-5, 5])

# Placar
score1 = 0
score2 = 0

# Função para reiniciar a bola
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    ball_dx = random.choice([-5, 5])
    ball_dy = random.choice([-5, 5])

# Função para desenhar o menu de pausa
def draw_pause_menu(screen, screen_width, screen_height, selection):
    # Overlay semi-transparente
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Preto com 70% de opacidade
    screen.blit(overlay, (0, 0))

    # Título
    text_pause = font_large.render("PAUSADO", True, WHITE)
    rect_pause = text_pause.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
    screen.blit(text_pause, rect_pause)

    # Pergunta
    text_question = font_medium.render("Deseja sair do jogo?", True, WHITE)
    rect_question = text_question.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text_question, rect_question)

    # Opções
    options = ["Sim", "Não"]
    y_offset = screen_height // 2 + 50
    
    for i, option in enumerate(options):
        color = YELLOW if i == selection else WHITE
        text_option = font_medium.render(option, True, color)
        rect_option = text_option.get_rect(center=(screen_width // 2, y_offset + i * 50))
        screen.blit(text_option, rect_option)

# Loop principal do jogo
running = True
paused = False # NOVO: Estado de pausa
menu_selection = 0 # NOVO: 0 para "Sim", 1 para "Não"
clock = pygame.time.Clock()

while running:
    # --- Processamento de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == CONTROLS_KEY_CODES['PAUSE']:
                # Alterna o estado de pausa
                paused = not paused
                if paused:
                    menu_selection = 0 # Reseta a seleção ao pausar
            
            if paused:
                # Lógica de input do menu de pausa
                if event.key == CONTROLS_KEY_CODES['UP']:
                    menu_selection = (menu_selection - 1) % 2
                elif event.key == CONTROLS_KEY_CODES['DOWN']:
                    menu_selection = (menu_selection + 1) % 2
                elif event.key == CONTROLS_KEY_CODES['ACTION_A']:
                    if menu_selection == 0: # Sim
                        running = False # Sai do loop principal
                    elif menu_selection == 1: # Não
                        paused = False # Retorna ao jogo
            
            # Lógica de input de movimento (só se não estiver pausado)
            elif not paused:
                # Ações de movimento (Simple Mover)
                if event.key == CONTROLS_KEY_CODES['UP']:
                    pass # Movimento contínuo é melhor com get_pressed()
                if event.key == CONTROLS_KEY_CODES['DOWN']:
                    pass # Movimento contínuo é melhor com get_pressed()
                if event.key == CONTROLS_KEY_CODES['LEFT']:
                    pass
                if event.key == CONTROLS_KEY_CODES['RIGHT']:
                    pass
                
                # Ações A e B (exemplo de uso)
                if event.key == CONTROLS_KEY_CODES['ACTION_B']:
                    pass # Exemplo de uso de ACTION_B

    if not paused:
        # --- Lógica de Movimento (Input) ---
        keys = pygame.key.get_pressed()

        # Jogador 1 (Paleta Esquerda) - Usa UP e DOWN
        if keys[CONTROLS_KEY_CODES['UP']]:
            player1_y -= paddle_speed
        if keys[CONTROLS_KEY_CODES['DOWN']]:
            player1_y += paddle_speed

        # Jogador 2 (Paleta Direita) - Usa ACTION_A e ACTION_B
        if keys[CONTROLS_KEY_CODES['ACTION_A']]: # Mover para cima
            player2_y -= paddle_speed
        if keys[CONTROLS_KEY_CODES['ACTION_B']]: # Mover para baixo
            player2_y += paddle_speed

        # Limitar movimento das paletas
        player1_y = max(0, min(player1_y, SCREEN_HEIGHT - paddle_height))
        player2_y = max(0, min(player2_y, SCREEN_HEIGHT - paddle_height))

        # --- Lógica da Bola ---
        ball_x += ball_dx
        ball_y += ball_dy

        # Colisão com o topo e a base
        if ball_y <= ball_radius or ball_y >= SCREEN_HEIGHT - ball_radius:
            ball_dy *= -1

        # Colisão com as paletas
        # Paleta 1 (Esquerda)
        paddle1_rect = pygame.Rect(20, player1_y, paddle_width, paddle_height)
        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
        
        if ball_rect.colliderect(paddle1_rect) and ball_dx < 0:
            ball_dx *= -1
            # Adiciona um pouco de aleatoriedade no ângulo
            ball_dy += random.uniform(-1, 1)

        # Paleta 2 (Direita)
        paddle2_rect = pygame.Rect(SCREEN_WIDTH - 20 - paddle_width, player2_y, paddle_width, paddle_height)
        if ball_rect.colliderect(paddle2_rect) and ball_dx > 0:
            ball_dx *= -1
            # Adiciona um pouco de aleatoriedade no ângulo
            ball_dy += random.uniform(-1, 1)

        # Ponto (Saiu da tela)
        if ball_x < 0:
            score2 += 1
            reset_ball()
        elif ball_x > SCREEN_WIDTH:
            score1 += 1
            reset_ball()

    # --- Desenho (Draw) ---
    screen.fill(BLACK) # Limpa a tela

    # Desenha as paletas (retângulos)
    paddle1_rect = pygame.Rect(20, player1_y, paddle_width, paddle_height)
    paddle2_rect = pygame.Rect(SCREEN_WIDTH - 20 - paddle_width, player2_y, paddle_width, paddle_height)
    pygame.draw.rect(screen, WHITE, paddle1_rect)
    pygame.draw.rect(screen, WHITE, paddle2_rect)

    # Desenha a bola (círculo)
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)

    # Desenha a linha central (opcional)
    pygame.draw.aaline(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    # Desenha o placar
    text1 = font_large.render(str(score1), True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 4, 20))
    text2 = font_large.render(str(score2), True, WHITE)
    screen.blit(text2, (SCREEN_WIDTH * 3 // 4 - text2.get_width(), 20))

    # Desenha o menu de pausa se estiver pausado
    if paused:
        draw_pause_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, menu_selection)

    # Atualiza a tela
    pygame.display.flip()

    # Limita o FPS
    clock.tick(60)

# --- Finalização ---
pygame.quit()
sys.exit()
