
import pygame, random
import time
import sys
from configparser import ConfigParser 
import os 
from math import cos, sin, pi 

# =========================================================================
# 1. FUNÇÕES DE SUPORTE PARA LEITURA DO CONF.INI
# =========================================================================

TECLA_MAP = {
    'w': pygame.K_w, 'a': pygame.K_a, 's': pygame.K_s, 'd': pygame.K_d, 
    'p': pygame.K_p, 'o': pygame.K_o, 'enter': pygame.K_RETURN, 
    'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT
}

def get_key_code(key_str):
    key_str = key_str.lower()
    return TECLA_MAP.get(key_str, None)

def load_settings():
    parser = ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, '..', '..', 'conf', 'conf.ini')
    parser.read(path) 
    
    if not parser.has_section('Display'):
        return {
            'WIDTH': 600, 'HEIGHT': 400, 'TECLA_LEFT': pygame.K_LEFT, 
            'TECLA_RIGHT': pygame.K_RIGHT, 'TECLA_PAUSE': pygame.K_p
        }

    width = parser.getint('Display', 'width')
    height = parser.getint('Display', 'height')
    controls = parser['Controls']
    
    return {
        'WIDTH': width, 'HEIGHT': height,
        'TECLA_LEFT': get_key_code(controls.get('left', 'left')),
        'TECLA_RIGHT': get_key_code(controls.get('right', 'right')),
        'TECLA_PAUSE': get_key_code(controls.get('pause', 'p'))
    }

# --- Carregando as configurações reais ---
SETTINGS = load_settings() 
LARGURA = SETTINGS['WIDTH']
ALTURA = SETTINGS['HEIGHT']
TECLA_LEFT = SETTINGS['TECLA_LEFT']
TECLA_RIGHT = SETTINGS['TECLA_RIGHT']
TECLA_PAUSE = SETTINGS['TECLA_PAUSE']


# 2. Inicialização e Configurações
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo do Atirador Espacial")
clock = pygame.time.Clock()

# Cores 
FUNDO_HUB_AZUL_ESCURO = (20, 20, 40)   
ROXO_JOGADOR = (120, 40, 160)          
AMARELO_BALA = (255, 255, 100)         
BRANCO = (255, 255, 255)
AZUL_BOTAO = (0, 100, 255)             
VERMELHO_BOTAO = (255, 50, 50)         
OURO_VITORIA = (255, 215, 0) 

VERMELHO_TERRA = (180, 50, 50)         
VERDE_MUSGO = (80, 120, 80)            
LARANJA_SUAVE = (200, 100, 40)         
AZUL_GELO = (50, 150, 200) 
VERMELHO_DIAMANTE = (220, 0, 0) 
FOGO_MOTOR_VERM = (255, 100, 0) # NOVO: Cor para a chama

INIMIGO_CORES = [VERMELHO_TERRA, VERDE_MUSGO, LARANJA_SUAVE] 
OURO_ESTRELA = (255, 215, 0) 

# Variáveis de Jogo
jogador_rect = pygame.Rect(LARGURA // 2 - 20, ALTURA - 50, 40, 40)
velocidade_jogador_base = 8 
velocidade_jogador = velocidade_jogador_base 

velocidade_inimigo_base = 3.0 # NOVO: Começa em 3.0 para permitir incrementos decimais
velocidade_inimigo = velocidade_inimigo_base

balas = []
inimigos = [] 

pontuacao = 0
erros = 0
VIDAS_MAX = 3
Y_VIDAS = 60 

game_running = True
game_over_screen = False
game_won_screen = False 
game_paused = False

# Variáveis de Fase
FASE_ATUAL = 1
MAX_FASES = 5
TEMPO_FASE = 50000 
tempo_inicial_fase = 0 
INTERVALO_SPAWN_BASE = 1500 

# Controles de Tempo
ultimo_spawn = 0
ultimo_disparo = 0
INTERVALO_DISPARO = 250
FPS = 60

# --- VARIÁVEIS DE POWER-UP COM TIMERS INDEPENDENTES ---
TEMPO_POWER_UP = 10000 
TEMPO_BONUS_VELOCIDADE = 7000 

# Timers
timer_tiro_triplo = 0 
timer_slow = 0
timer_velocidade = 0 

# Estados
tiro_triplo_ativo = False
slow_ativo = False
velocidade_bonus_ativa = False

# Mensagens na Tela
msg_avanco_ativa = False
timer_msg_avanco = 0
TEMPO_MSG_AVANCO = 3000 

# Fundo Estrelado
NUM_ESTRELAS = 50
estrelas = [(random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(1, 2)) for _ in range(NUM_ESTRELAS)]

# Configurações de Texto
fonte_placar = pygame.font.Font(None, 30)
fonte_game_over = pygame.font.Font(None, 74)
fonte_botoes = pygame.font.Font(None, 40)
fonte_mensagem = pygame.font.Font(None, 24)
fonte_fase = pygame.font.Font(None, 50)

# --- Funções do Jogo ---

def reset_game():
    global jogador_rect, balas, inimigos, pontuacao, erros, game_running, game_over_screen, game_paused, game_won_screen
    global velocidade_jogador, velocidade_inimigo, FASE_ATUAL, tiro_triplo_ativo, slow_ativo, velocidade_bonus_ativa, timer_tiro_triplo, timer_slow, timer_velocidade
    global velocidade_inimigo_base
    
    jogador_rect = pygame.Rect(LARGURA // 2 - 20, ALTURA - 50, 40, 40)
    balas.clear()
    inimigos.clear()
    pontuacao = 0
    erros = 0
    
    game_running = True
    game_over_screen = False
    game_paused = False
    game_won_screen = False
    
    velocidade_jogador = velocidade_jogador_base 
    velocidade_inimigo_base = 3.0
    velocidade_inimigo = velocidade_inimigo_base
    
    tiro_triplo_ativo = False
    slow_ativo = False
    velocidade_bonus_ativa = False
    
    timer_tiro_triplo = 0
    timer_slow = 0
    timer_velocidade = 0
    
    FASE_ATUAL = 1
    iniciar_fase() 

def iniciar_fase():
    global tempo_inicial_fase, ultimo_spawn
    tempo_inicial_fase = pygame.time.get_ticks()
    ultimo_spawn = tempo_inicial_fase 

def avancar_fase():
    global FASE_ATUAL, erros, inimigos, msg_avanco_ativa, timer_msg_avanco, game_running, game_won_screen
    global velocidade_inimigo_base
    
    FASE_ATUAL += 1
    erros = 0
    inimigos.clear()
    
    velocidade_inimigo_base += 0.5 
    
    if FASE_ATUAL <= MAX_FASES:
        msg_avanco_ativa = True
        timer_msg_avanco = pygame.time.get_ticks()
        iniciar_fase()
    else:
        game_running = False
        game_won_screen = True

def desenhar_botao(surf, text, x, y, width, height, cor_fundo, cor_texto):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surf, cor_fundo, rect, border_radius=5)
    
    text_surface = fonte_botoes.render(text, True, cor_texto)
    text_rect = text_surface.get_rect(center=rect.center)
    surf.blit(text_surface, text_rect)
    return rect

def desenhar_pause():
    s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    
    texto = fonte_game_over.render("PAUSE", True, BRANCO)
    tela.blit(s, (0, 0))
    tela.blit(texto, texto.get_rect(center=(LARGURA / 2, ALTURA / 2)))

def desenhar_estrela(surface, center, outer_radius, inner_radius, color):
    points = []
    for i in range(5):
        angle = 90 + i * 72 
        x = center[0] + outer_radius * pygame.math.Vector2(0, -1).rotate(angle).x
        y = center[1] + outer_radius * pygame.math.Vector2(0, -1).rotate(angle).y
        points.append((x, y))

        angle += 36 
        x = center[0] + inner_radius * pygame.math.Vector2(0, -1).rotate(angle).x
        y = center[1] + inner_radius * pygame.math.Vector2(0, -1).rotate(angle).y
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)

def desenhar_hexagono(surface, center, size, color):
    points = []
    for i in range(6):
        angle_deg = 60 * i + 30 
        angle_rad = pi / 180 * angle_deg
        x = center[0] + size * cos(angle_rad)
        y = center[1] + size * sin(angle_rad)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points)

def desenhar_retangulo_arredondado(surface, rect, radius, color):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def desenhar_diamante(surface, center, size, color):
    half_size = size / 2
    points = [
        (center[0], center[1] - half_size),
        (center[0] + half_size, center[1]),
        (center[0], center[1] + half_size),
        (center[0] - half_size, center[1]), 
    ]
    pygame.draw.polygon(surface, color, points)


# --- Loop Principal ---
reset_game()
running = True
while running:
    
    # 3. Gerenciamento de Eventos (Global)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN and event.key == TECLA_PAUSE and not game_over_screen and not game_won_screen:
            game_paused = not game_paused

        if (game_over_screen or game_won_screen) and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if 'jogar_novamente_rect' in locals() and jogar_novamente_rect.collidepoint(mouse_pos):
                reset_game()
            
            if 'sair_rect' in locals() and sair_rect.collidepoint(mouse_pos):
                running = False


    if game_running and not game_paused:
        clock.tick(FPS)
        agora = pygame.time.get_ticks()

        # --------------------------------------------------------------------
        # LÓGICA DE POWER-UPS E TEMPORIZADORES
        # --------------------------------------------------------------------
        
        # Desativa Tiro Triplo
        if tiro_triplo_ativo and agora - timer_tiro_triplo > TEMPO_POWER_UP:
            tiro_triplo_ativo = False
            
        # Desativa Slow-Motion
        if slow_ativo and agora - timer_slow > TEMPO_POWER_UP:
            slow_ativo = False
            velocidade_inimigo = velocidade_inimigo_base # Usa o valor de fase atualizado
        
        # Desativa Velocidade do Jogador
        if velocidade_bonus_ativa and agora - timer_velocidade > TEMPO_BONUS_VELOCIDADE:
            velocidade_bonus_ativa = False
            velocidade_jogador = velocidade_jogador_base
            
        # 4. Movimento do Jogador
        teclas = pygame.key.get_pressed()
        if teclas[TECLA_LEFT]: jogador_rect.x -= velocidade_jogador
        if teclas[TECLA_RIGHT]: jogador_rect.x += velocidade_jogador
        jogador_rect.clamp_ip(tela.get_rect())

        # 5. Disparo Automático (Triplo se ativo)
        if agora - ultimo_disparo > INTERVALO_DISPARO:
            balas.append(pygame.Rect(jogador_rect.centerx - 2, jogador_rect.top, 4, 10))
            
            if tiro_triplo_ativo: 
                 balas.append(pygame.Rect(jogador_rect.centerx - 10, jogador_rect.top, 4, 10))
                 balas.append(pygame.Rect(jogador_rect.centerx + 6, jogador_rect.top, 4, 10))
                 
            ultimo_disparo = agora
            
        # 6. Geração de Inimigos (A dificuldade do spawn diminui, a velocidade aumenta na função avancar_fase)
        fator_dificuldade = 1 - (FASE_ATUAL - 1) * 0.10 
        intervalo_spawn_atual = INTERVALO_SPAWN_BASE * fator_dificuldade

        if agora - ultimo_spawn > intervalo_spawn_atual: 
            x_aleatorio = random.randint(0, LARGURA - 60)
            chance = random.random()
            
            # Tipos de spawn
            if chance < 0.6: 
                cor_inimigo = random.choice(INIMIGO_CORES)
                if random.random() < 0.5:
                    inimigos.append((pygame.Rect(x_aleatorio, 0, 40, 40), 'square', cor_inimigo, 10))
                else:
                    inimigos.append((pygame.Rect(x_aleatorio, 0, 40, 40), 'circle', cor_inimigo, 10))
            
            elif chance < 0.75: 
                inimigos.append((pygame.Rect(x_aleatorio, 0, 45, 45), 'hexagon', VERDE_MUSGO, 25, 2)) 
            
            elif chance < 0.9: 
                if random.random() < 0.5:
                    inimigos.append((pygame.Rect(x_aleatorio, 0, 40, 40), 'power_slow', AZUL_GELO, 0))
                else:
                    inimigos.append((pygame.Rect(x_aleatorio, 0, 40, 40), 'power_triple', VERMELHO_DIAMANTE, 0))
                    
            else: 
                inimigos.append((pygame.Rect(x_aleatorio, 0, 50, 50), 'star', OURO_ESTRELA, 50))
                
            ultimo_spawn = agora
            
        # 7. Atualização de Posições e Verificação de ERROS
        for bala in balas: bala.y -= 7
        balas = [b for b in balas if b.bottom > 0]

        inimigos_mantidos = []
        for inimigo_tuple in inimigos:
            inimigo_rect, inimigo_type, _, inimigo_points = inimigo_tuple[:4]
            
            velocidade_atual = velocidade_inimigo
            if inimigo_type == 'hexagon':
                 velocidade_atual = inimigo_tuple[4]
            
            inimigo_rect.y += velocidade_atual
            
            if inimigo_rect.top > ALTURA:
                # Apenas inimigos de pontuação (square, circle, hexagon) causam erro.
                if inimigo_type in ('square', 'circle', 'hexagon'):
                    erros += 1
            else:
                inimigos_mantidos.append(inimigo_tuple)
                
        inimigos = inimigos_mantidos

        # 8. Detecção de Colisão
        balas_a_remover = []
        inimigos_a_remover = []
        
        for bala in balas:
            for inimigo_tuple in inimigos:
                inimigo_rect, inimigo_type, _, inimigo_points = inimigo_tuple[:4]
                
                if bala.colliderect(inimigo_rect):
                    balas_a_remover.append(bala)
                    inimigos_a_remover.append(inimigo_tuple)
                    
                    # Aplica power-ups
                    if inimigo_type == 'star': 
                        velocidade_jogador = velocidade_jogador_base * 1.5 
                        velocidade_bonus_ativa = True
                        timer_velocidade = agora 
                    elif inimigo_type == 'power_triple': 
                        tiro_triplo_ativo = True
                        timer_tiro_triplo = agora
                    elif inimigo_type == 'power_slow':
                        slow_ativo = True
                        velocidade_inimigo = velocidade_inimigo_base * 0.5
                        timer_slow = agora
                        
                    pontuacao += inimigo_points 
                    
        balas = [b for b in balas if b not in balas_a_remover]
        inimigos = [e for e in inimigos if e not in inimigos_a_remover]

        # 9. Verificação de Game Over e Avanço de Fase
        if erros >= VIDAS_MAX:
            game_running = False
            game_over_screen = True
            
        # Verifica o avanço de fase após a correção do erro de nome
        if FASE_ATUAL <= MAX_FASES and agora - tempo_inicial_fase >= TEMPO_FASE:
            avancar_fase()
            
        # 10. Desenho (Renderização do Jogo)
        tela.fill(FUNDO_HUB_AZUL_ESCURO)
        
        # Desenha Fundo Estrelado
        for x, y, size in estrelas:
            pygame.draw.circle(tela, BRANCO, (x, y), size)
        
        # Desenha o FOGO do Motor (NOVO)
        motor_offset = random.randint(-2, 2) # Oscilação
        chama_points = [
            (jogador_rect.centerx + motor_offset, jogador_rect.bottom + 1),
            (jogador_rect.centerx - 5 + motor_offset, jogador_rect.bottom + 15),
            (jogador_rect.centerx + 5 + motor_offset, jogador_rect.bottom + 15)
        ]
        pygame.draw.polygon(tela, FOGO_MOTOR_VERM, chama_points)
        
        # Desenha o jogador (Triângulo Roxo)
        ponto_a = (jogador_rect.centerx, jogador_rect.top)
        ponto_b = jogador_rect.bottomleft
        ponto_c = jogador_rect.bottomright
        pygame.draw.polygon(tela, ROXO_JOGADOR, [ponto_a, ponto_b, ponto_c])
        
        # Desenha Balas e Inimigos
        for bala in balas: pygame.draw.rect(tela, AMARELO_BALA, bala)
        for inimigo_tuple in inimigos:
            inimigo_rect, inimigo_type, inimigo_color, _ = inimigo_tuple[:4]
            
            if inimigo_type == 'square': 
                pygame.draw.rect(tela, inimigo_color, inimigo_rect)
            elif inimigo_type == 'circle':
                radius = inimigo_rect.width // 2 
                pygame.draw.circle(tela, inimigo_color, inimigo_rect.center, radius)
            elif inimigo_type == 'star': 
                desenhar_estrela(tela, inimigo_rect.center, inimigo_rect.width // 2, inimigo_rect.width // 4, inimigo_color)
            elif inimigo_type == 'hexagon': 
                desenhar_hexagono(tela, inimigo_rect.center, inimigo_rect.width // 2, inimigo_color)
            elif inimigo_type == 'power_slow': 
                desenhar_retangulo_arredondado(tela, inimigo_rect, 10, inimigo_color)
            elif inimigo_type == 'power_triple': 
                desenhar_diamante(tela, inimigo_rect.center, inimigo_rect.width, inimigo_color)

        # --- Placar, Erros e Fase ---
        tempo_decorrido_fase = (agora - tempo_inicial_fase) // 1000
        tempo_restante_fase = max(0, 50 - tempo_decorrido_fase)
        
        # 1. Desenho da Vida (Corações)
        for i in range(VIDAS_MAX):
             if i < (VIDAS_MAX - erros):
                 heart_center_x = LARGURA - 25 - i * 30
                 heart_center_y = Y_VIDAS
                 heart_points = [(heart_center_x, heart_center_y - 10), 
                                 (heart_center_x - 10, heart_center_y + 5), 
                                 (heart_center_x + 10, heart_center_y + 5)]
                 pygame.draw.polygon(tela, VERMELHO_BOTAO, heart_points)
        
        # 2. Desenho de Textos de Placar
        texto_fase = fonte_placar.render(f"Fase: {FASE_ATUAL}/{MAX_FASES}", True, BRANCO)
        texto_tempo = fonte_placar.render(f"Tempo: {tempo_restante_fase}s", True, BRANCO)
        texto_pontos = fonte_placar.render(f"Pontos: {pontuacao}", True, BRANCO)

        tela.blit(texto_fase, (10, 10))
        tela.blit(texto_tempo, (10, 35))
        tela.blit(texto_pontos, (LARGURA - texto_pontos.get_width() - 10, 10))
        

        # 3. Mensagens de Power-Up (Canto Esquerdo)
        power_up_list = []
        if velocidade_bonus_ativa:
            tempo_restante_pu = (TEMPO_BONUS_VELOCIDADE - (agora - timer_velocidade)) // 1000 + 1
            power_up_list.append(("Velocidade", tempo_restante_pu, OURO_ESTRELA))
        if tiro_triplo_ativo:
            tempo_restante_pu = (TEMPO_POWER_UP - (agora - timer_tiro_triplo)) // 1000 + 1
            power_up_list.append(("Tiro Triplo", tempo_restante_pu, VERMELHO_DIAMANTE))
        if slow_ativo:
            tempo_restante_pu = (TEMPO_POWER_UP - (agora - timer_slow)) // 1000 + 1
            power_up_list.append(("Slow", tempo_restante_pu, AZUL_GELO))
            
        y_pu_pos = 65 
        for msg_txt, tempo_restante, cor in power_up_list:
             msg_pu = fonte_mensagem.render(f"{msg_txt} ({tempo_restante}s)", True, cor) 
             tela.blit(msg_pu, (10, y_pu_pos))
             y_pu_pos += 25 
        
        # Mensagem de Avanço de Fase
        if msg_avanco_ativa and FASE_ATUAL <= MAX_FASES:
            msg_texto = f"PARABÉNS! PRÓXIMA FASE: {FASE_ATUAL}"
            cor_msg = BRANCO

            msg_avanco = fonte_fase.render(msg_texto, True, cor_msg)
            tela.blit(msg_avanco, msg_avanco.get_rect(center=(LARGURA // 2, ALTURA // 2)))


    # 11. Lógica de PAUSE
    elif game_paused:
        desenhar_pause()

    # 12. Telas Finais (Game Over OU Game Won)
    
    if game_over_screen:
        titulo_texto = "GAME OVER"
        titulo_cor = VERMELHO_BOTAO
    elif game_won_screen:
        titulo_texto = "VITÓRIA! JOGO COMPLETO"
        titulo_cor = OURO_VITORIA
    else:
        pygame.display.flip()
        continue

    tela.fill(FUNDO_HUB_AZUL_ESCURO) 
    
    texto_final = fonte_game_over.render(titulo_texto, True, titulo_cor)
    tela.blit(texto_final, texto_final.get_rect(center=(LARGURA / 2, ALTURA / 4)))
    
    texto_score_final = fonte_placar.render(f"Pontuação Final: {pontuacao}", True, BRANCO)
    tela.blit(texto_score_final, texto_score_final.get_rect(center=(LARGURA / 2, ALTURA / 4 + 70)))

    botao_w = 200
    botao_h = 50
    
    jogar_novamente_rect = desenhar_botao(tela, "Jogar Novamente", 
                                          (LARGURA / 2) - (botao_w / 2), ALTURA / 2 + 30, 
                                          botao_w, botao_h, AZUL_BOTAO, BRANCO)
    
    sair_rect = desenhar_botao(tela, "Sair", 
                               (LARGURA / 2) - (botao_w / 2), ALTURA / 2 + 100, 
                               botao_w, botao_h, VERMELHO_BOTAO, BRANCO)
    
    pygame.display.flip()

# Encerramento
pygame.quit()
sys.exit()