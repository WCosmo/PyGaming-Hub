import pygame
import sys
import random
import math

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ataque Aéreo - PyGaming Hub")
clock = pygame.time.Clock()

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 0)
PURPLE = (150, 50, 200)

class JogoAtaqueAereo:
    def __init__(self):
        # Estado do jogo
        self.rodando = True
        self.game_over = False
        self.pontuacao = 0
        self.vidas = 3
        self.nivel = 1
        self.poder_tiro = 1
        
        # Avião do jogador
        self.aviao_x = WIDTH // 2
        self.aviao_y = HEIGHT - 100
        self.tamanho_aviao = 25
        self.velocidade_aviao = 6
        self.cooldown_tiro = 0
        
        # Listas de objetos
        self.tiros = []
        self.misseis = []
        self.alvos = []
        self.explosoes = []
        self.powerups = []
        
        # Criar alvos iniciais
        self.criar_alvos(5)
        
        # Timer para spawn de inimigos
        self.timer_missil = 0
        self.timer_powerup = 0
        
        # Fontes
        self.fonte_grande = pygame.font.Font(None, 36)
        self.fonte_media = pygame.font.Font(None, 24)
        self.fonte_pequena = pygame.font.Font(None, 18)
    
    def criar_alvos(self, quantidade):
        """Cria alvos terrestres na base"""
        for _ in range(quantidade):
            alvo = {
                'x': random.randint(50, WIDTH - 110),
                'y': HEIGHT - 150,
                'largura': 60,
                'altura': 40,
                'vida': random.randint(1, 3),
                'destruido': False
            }
            self.alvos.append(alvo)
    
    def criar_explosao(self, x, y, tamanho=30):
        """Cria efeito visual de explosão"""
        self.explosoes.append({
            'x': x,
            'y': y,
            'tamanho': tamanho,
            'timer': 20
        })
    
    def criar_powerup(self, x, y):
        """Cria power-up no local especificado"""
        tipo = random.choice(['vida', 'poder'])
        self.powerups.append({
            'x': x,
            'y': y,
            'tipo': tipo,
            'velocidade': 2
        })
    
    def processar_eventos(self):
        """Processa eventos do teclado e mouse"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            
            if evento.type == pygame.KEYDOWN:
                # Tecla ESC para sair (equivale à tecla Pause)
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                
                # Reiniciar quando game over
                if self.game_over and evento.key == pygame.K_r:
                    self.__init__()  # Reinicia o jogo
    
    def processar_controles(self):
        """Processa controles contínuos (teclas pressionadas)"""
        if self.game_over:
            return
        
        teclas = pygame.key.get_pressed()
        
        # Movimento do avião
        if teclas[pygame.K_LEFT] and self.aviao_x > self.tamanho_aviao:
            self.aviao_x -= self.velocidade_aviao
        if teclas[pygame.K_RIGHT] and self.aviao_x < WIDTH - self.tamanho_aviao:
            self.aviao_x += self.velocidade_aviao
        if teclas[pygame.K_UP] and self.aviao_y > self.tamanho_aviao:
            self.aviao_y -= self.velocidade_aviao
        if teclas[pygame.K_DOWN] and self.aviao_y < HEIGHT - self.tamanho_aviao:
            self.aviao_y += self.velocidade_aviao
        
        # Disparar tiros
        if teclas[pygame.K_SPACE] and self.cooldown_tiro <= 0:
            self.disparar_tiro()
            self.cooldown_tiro = 8
    
    def disparar_tiro(self):
        """Cria novos tiros baseado no poder atual"""
        for i in range(self.poder_tiro):
            offset = (i - (self.poder_tiro - 1) / 2) * 12
            self.tiros.append({
                'x': self.aviao_x + offset,
                'y': self.aviao_y - self.tamanho_aviao,
                'velocidade': 10
            })
    
    def spawnar_missil(self):
        """Cria míssil inimigo se for hora"""
        if self.timer_missil <= 0 and len(self.misseis) < 3 + self.nivel:
            self.misseis.append({
                'x': random.randint(50, WIDTH - 50),
                'y': -20,
                'vel_x': random.uniform(-1.5, 1.5),
                'vel_y': random.uniform(3, 4)
            })
            self.timer_missil = max(40, 80 - self.nivel * 5)
    
    def spawnar_powerup(self):
        """Cria power-up aleatório"""
        if self.timer_powerup <= 0 and random.random() < 0.005:
            self.criar_powerup(
                random.randint(50, WIDTH - 50),
                -20
            )
            self.timer_powerup = 400
    
    def atualizar_tiros(self):
        """Atualiza posição dos tiros"""
        for tiro in self.tiros[:]:
            tiro['y'] -= tiro['velocidade']
            if tiro['y'] < 0:
                self.tiros.remove(tiro)
    
    def atualizar_misseis(self):
        """Atualiza posição dos mísseis"""
        for missil in self.misseis[:]:
            missil['x'] += missil['vel_x']
            missil['y'] += missil['vel_y']
            
            if (missil['y'] > HEIGHT or 
                missil['x'] < -20 or 
                missil['x'] > WIDTH + 20):
                self.misseis.remove(missil)
    
    def atualizar_powerups(self):
        """Atualiza posição dos power-ups"""
        for powerup in self.powerups[:]:
            powerup['y'] += powerup['velocidade']
            if powerup['y'] > HEIGHT:
                self.powerups.remove(powerup)
    
    def atualizar_explosoes(self):
        """Atualiza animação das explosões"""
        for explosao in self.explosoes[:]:
            explosao['timer'] -= 1
            if explosao['timer'] <= 0:
                self.explosoes.remove(explosao)
    
    def verificar_colisoes(self):
        """Verifica todas as colisões do jogo"""
        self.verificar_colisao_tiros_alvos()
        self.verificar_colisao_misseis_aviao()
        self.verificar_colisao_powerups_aviao()
    
    def verificar_colisao_tiros_alvos(self):
        """Verifica se tiros atingiram alvos"""
        for tiro in self.tiros[:]:
            rect_tiro = pygame.Rect(tiro['x'] - 3, tiro['y'] - 3, 6, 6)
            
            for alvo in self.alvos[:]:
                if not alvo['destruido']:
                    rect_alvo = pygame.Rect(alvo['x'], alvo['y'], 
                                          alvo['largura'], alvo['altura'])
                    
                    if rect_tiro.colliderect(rect_alvo):
                        # Remover tiro
                        if tiro in self.tiros:
                            self.tiros.remove(tiro)
                        
                        # Reduzir vida do alvo
                        alvo['vida'] -= 1
                        
                        if alvo['vida'] <= 0:
                            # Alvo destruído
                            alvo['destruido'] = True
                            self.pontuacao += 100
                            self.criar_explosao(
                                alvo['x'] + alvo['largura'] // 2,
                                alvo['y'] + alvo['altura'] // 2
                            )
                            
                            # Chance de criar power-up
                            if random.random() < 0.15:
                                self.criar_powerup(
                                    alvo['x'] + alvo['largura'] // 2,
                                    alvo['y'] + alvo['altura'] // 2
                                )
                        break
    
    def verificar_colisao_misseis_aviao(self):
        """Verifica se míssil atingiu o avião"""
        rect_aviao = pygame.Rect(self.aviao_x - self.tamanho_aviao,
                               self.aviao_y - self.tamanho_aviao,
                               self.tamanho_aviao * 2, self.tamanho_aviao * 2)
        
        for missil in self.misseis[:]:
            rect_missil = pygame.Rect(missil['x'] - 6, missil['y'] - 6, 12, 12)
            
            if rect_aviao.colliderect(rect_missil):
                self.misseis.remove(missil)
                self.criar_explosao(missil['x'], missil['y'])
                self.vidas -= 1
                
                if self.vidas <= 0:
                    self.game_over = True
    
    def verificar_colisao_powerups_aviao(self):
        """Verifica se avião pegou power-up"""
        rect_aviao = pygame.Rect(self.aviao_x - self.tamanho_aviao,
                               self.aviao_y - self.tamanho_aviao,
                               self.tamanho_aviao * 2, self.tamanho_aviao * 2)
        
        for powerup in self.powerups[:]:
            rect_powerup = pygame.Rect(powerup['x'] - 8, powerup['y'] - 8, 16, 16)
            
            if rect_aviao.colliderect(rect_powerup):
                self.aplicar_powerup(powerup)
                self.powerups.remove(powerup)
                self.criar_explosao(powerup['x'], powerup['y'], tamanho=15)
    
    def aplicar_powerup(self, powerup):
        """Aplica efeito do power-up coletado"""
        if powerup['tipo'] == 'vida':
            self.vidas = min(5, self.vidas + 1)
            self.pontuacao += 150
        elif powerup['tipo'] == 'poder':
            self.poder_tiro = min(3, self.poder_tiro + 1)
            self.pontuacao += 100
    
    def verificar_nivel_completo(self):
        """Verifica se todos alvos foram destruídos para avançar de nível"""
        if all(alvo['destruido'] for alvo in self.alvos):
            self.nivel += 1
            self.pontuacao += 300
            self.alvos = []
            self.criar_alvos(min(5 + self.nivel, 8))
    
    def atualizar(self):
        """Atualiza toda a lógica do jogo"""
        if self.game_over:
            return
        
        # Atualizar cooldowns
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1
        
        # Atualizar timers
        if self.timer_missil > 0:
            self.timer_missil -= 1
        if self.timer_powerup > 0:
            self.timer_powerup -= 1
        
        # Spawn de inimigos e power-ups
        self.spawnar_missil()
        self.spawnar_powerup()
        
        # Atualizar posições
        self.atualizar_tiros()
        self.atualizar_misseis()
        self.atualizar_powerups()
        self.atualizar_explosoes()
        
        # Verificar colisões
        self.verificar_colisoes()
        
        # Verificar nível
        self.verificar_nivel_completo()
    
    def desenhar_fundo(self):
        """Desenha o céu e nuvens"""
        # Céu gradiente
        for y in range(0, HEIGHT, 3):
            azul = 80 + int(120 * (y / HEIGHT))
            cor = (40, 40, azul)
            pygame.draw.line(screen, cor, (0, y), (WIDTH, y), 3)
        
        # Nuvens
        for i in range(3):
            nuvem_x = (pygame.time.get_ticks() // 60 + i * 250) % (WIDTH + 300) - 150
            nuvem_y = 60 + i * 70
            pygame.draw.circle(screen, (230, 230, 250), (nuvem_x, nuvem_y), 20)
            pygame.draw.circle(screen, (230, 230, 250), (nuvem_x + 15, nuvem_y - 8), 25)
            pygame.draw.circle(screen, (230, 230, 250), (nuvem_x + 30, nuvem_y), 20)
    
    def desenhar_chao(self):
        """Desenha o chão com estrada"""
        chao_y = HEIGHT - 60
        
        # Grama
        pygame.draw.rect(screen, (20, 110, 20), 
                        (0, chao_y, WIDTH, 60))
        
        # Estrada
        largura_estrada = 140
        estrada_x = (WIDTH - largura_estrada) // 2
        pygame.draw.rect(screen, (50, 50, 50), 
                        (estrada_x, chao_y, largura_estrada, 60))
        
        # Linhas da estrada
        for y in range(chao_y + 8, chao_y + 60, 18):
            for x in range(estrada_x + 10, estrada_x + largura_estrada - 10, 35):
                pygame.draw.line(screen, YELLOW, 
                               (x, y), (x + 18, y), 2)
    
    def desenhar_aviao(self):
        """Desenha o avião do jogador"""
        # Corpo (triângulo)
        pontos = [
            (self.aviao_x, self.aviao_y - self.tamanho_aviao),
            (self.aviao_x - self.tamanho_aviao, self.aviao_y + self.tamanho_aviao),
            (self.aviao_x + self.tamanho_aviao, self.aviao_y + self.tamanho_aviao)
        ]
        
        pygame.draw.polygon(screen, BLUE, pontos)
        pygame.draw.polygon(screen, (100, 150, 255), pontos, 2)
        
        # Cabine
        pygame.draw.circle(screen, RED, 
                          (self.aviao_x, self.aviao_y - self.tamanho_aviao // 3), 5)
        
        # Asas
        pygame.draw.rect(screen, BLUE,
                        (self.aviao_x - self.tamanho_aviao - 4, self.aviao_y - 4,
                         self.tamanho_aviao * 2 + 8, 8))
    
    def desenhar_tiros(self):
        """Desenha todos os tiros"""
        for tiro in self.tiros:
            pygame.draw.circle(screen, YELLOW, 
                             (int(tiro['x']), int(tiro['y'])), 5)
            pygame.draw.circle(screen, WHITE, 
                             (int(tiro['x']), int(tiro['y'])), 2)
    
    def desenhar_misseis(self):
        """Desenha todos os mísseis"""
        for missil in self.misseis:
            # Corpo do míssil
            pygame.draw.polygon(screen, RED, [
                (missil['x'], missil['y'] - 7),
                (missil['x'] - 3, missil['y'] + 7),
                (missil['x'] + 3, missil['y'] + 7)
            ])
            
            # Ponta
            pygame.draw.circle(screen, ORANGE, 
                             (int(missil['x']), int(missil['y'])), 3)
            
            # Rastro
            for i in range(1, 4):
                rastro_y = missil['y'] + i * 2
                pygame.draw.circle(screen, (255, 100, 50),
                                 (int(missil['x']), int(rastro_y)), 3 - i)
    
    def desenhar_alvos(self):
        """Desenha todos os alvos terrestres"""
        for alvo in self.alvos:
            if not alvo['destruido']:
                # Cor baseada na vida
                if alvo['vida'] == 1:
                    cor = RED
                elif alvo['vida'] == 2:
                    cor = ORANGE
                else:
                    cor = GREEN
                
                # Corpo do alvo
                pygame.draw.rect(screen, cor,
                               (alvo['x'], alvo['y'], 
                                alvo['largura'], alvo['altura']))
                
                # Borda
                pygame.draw.rect(screen, BLACK,
                               (alvo['x'], alvo['y'], 
                                alvo['largura'], alvo['altura']), 2)
                
                # Janelas (detalhes)
                for i in range(2):
                    for j in range(2):
                        janela_x = alvo['x'] + 12 + i * 20
                        janela_y = alvo['y'] + 8 + j * 12
                        pygame.draw.rect(screen, (30, 30, 30),
                                       (janela_x, janela_y, 10, 8))
            else:
                # Escombros do alvo destruído
                centro_x = alvo['x'] + alvo['largura'] // 2
                centro_y = alvo['y'] + alvo['altura'] // 2
                
                for i in range(3):
                    angulo = i * 120
                    x1 = centro_x + 8 * math.cos(math.radians(angulo))
                    y1 = centro_y + 8 * math.sin(math.radians(angulo))
                    x2 = centro_x + 12 * math.cos(math.radians(angulo + 60))
                    y2 = centro_y + 12 * math.sin(math.radians(angulo + 60))
                    
                    pygame.draw.polygon(screen, (90, 90, 90),
                                      [(centro_x, centro_y), (x1, y1), (x2, y2)])
    
    def desenhar_powerups(self):
        """Desenha todos os power-ups"""
        for powerup in self.powerups:
            if powerup['tipo'] == 'vida':
                # Coração (vida extra)
                pontos = []
                for angulo in range(0, 360, 15):
                    rad = math.radians(angulo)
                    rx = 12 * (math.sin(rad) ** 3)
                    ry = 10 * math.cos(rad) - 4 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)
                    pontos.append((powerup['x'] + rx * 0.25, powerup['y'] - ry * 0.25))
                pygame.draw.polygon(screen, RED, pontos)
            else:
                # Estrela (poder do tiro)
                pontos = []
                for i in range(5):
                    angulo = math.radians(72 * i - 90)
                    raio = 8 if i % 2 == 0 else 4
                    pontos.append((
                        powerup['x'] + raio * math.cos(angulo),
                        powerup['y'] + raio * math.sin(angulo)
                    ))
                pygame.draw.polygon(screen, YELLOW, pontos)
    
    def desenhar_explosoes(self):
        """Desenha todas as explosões"""
        for explosao in self.explosoes:
            tamanho = explosao['tamanho'] * (explosao['timer'] / 20)
            pygame.draw.circle(screen, ORANGE,
                             (int(explosao['x']), int(explosao['y'])), 
                             int(tamanho))
            pygame.draw.circle(screen, YELLOW,
                             (int(explosao['x']), int(explosao['y'])), 
                             int(tamanho * 0.6))
    
    def desenhar_hud(self):
        """Desenha a interface do jogador (HUD)"""
        # Fundo semi-transparente para HUD
        superficie_hud = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        superficie_hud.fill((0, 0, 0, 160))
        screen.blit(superficie_hud, (0, 0))
        
        # Pontuação
        texto_pontos = self.fonte_grande.render(f"PONTOS: {self.pontuacao}", True, YELLOW)
        screen.blit(texto_pontos, (15, 15))
        
        # Vidas
        texto_vidas = self.fonte_grande.render(f"VIDAS: {self.vidas}", True, GREEN)
        screen.blit(texto_vidas, (15, 50))
        
        # Nível
        texto_nivel = self.fonte_grande.render(f"NÍVEL: {self.nivel}", True, BLUE)
        screen.blit(texto_nivel, (WIDTH - 140, 15))
        
        # Poder do tiro
        texto_poder = self.fonte_media.render(f"PODER: {self.poder_tiro}", True, ORANGE)
        screen.blit(texto_poder, (WIDTH - 140, 50))
        
        # Controles (parte inferior)
        controles_y = HEIGHT - 90
        controles = [
            "CONTROLES:",
            "SETAS - Mover avião",
            "ESPAÇO - Atirar",
            "ESC - Sair (Tecla Pause)",
            "R - Reiniciar (game over)"
        ]
        
        for i, texto in enumerate(controles):
            cor = WHITE if i == 0 else (180, 180, 180)
            texto_controle = self.fonte_pequena.render(texto, True, cor)
            screen.blit(texto_controle, (15, controles_y + i * 18))
    
    def desenhar_game_over(self):
        """Desenha tela de game over"""
        # Overlay escuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Texto GAME OVER
        texto_gameover = pygame.font.Font(None, 64).render("GAME OVER", True, RED)
        rect_gameover = texto_gameover.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        screen.blit(texto_gameover, rect_gameover)
        
        # Pontuação final
        texto_pontuacao = self.fonte_grande.render(f"Pontuação Final: {self.pontuacao}", True, YELLOW)
        rect_pontuacao = texto_pontuacao.get_rect(center=(WIDTH//2, HEIGHT//2 - 10))
        screen.blit(texto_pontuacao, rect_pontuacao)
        
        # Nível alcançado
        texto_nivel = self.fonte_grande.render(f"Nível Alcançado: {self.nivel}", True, GREEN)
        rect_nivel = texto_nivel.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
        screen.blit(texto_nivel, rect_nivel)
        
        # Instrução para reiniciar
        texto_reiniciar = self.fonte_media.render("Pressione R para reiniciar ou ESC para sair", True, WHITE)
        rect_reiniciar = texto_reiniciar.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
        screen.blit(texto_reiniciar, rect_reiniciar)
    
    def desenhar(self):
        """Desenha todos os elementos na tela"""
        # Limpar tela
        screen.fill(BLACK)
        
        # Fundo
        self.desenhar_fundo()
        self.desenhar_chao()
        
        # Elementos do jogo
        self.desenhar_alvos()
        self.desenhar_powerups()
        self.desenhar_misseis()
        self.desenhar_tiros()
        self.desenhar_explosoes()
        self.desenhar_aviao()
        
        # Interface
        self.desenhar_hud()
        
        # Tela de game over (se necessário)
        if self.game_over:
            self.desenhar_game_over()
    
    def executar(self):
        """Loop principal do jogo"""
        while self.rodando:
            self.processar_eventos()
            self.processar_controles()
            self.atualizar()
            self.desenhar()
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

# Iniciar o jogo
if __name__ == "__main__":
    jogo = JogoAtaqueAereo()
    jogo.executar()