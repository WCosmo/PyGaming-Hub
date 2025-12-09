
import pygame
import sys
import os
import configparser
import random

class JogoCobrinha:
    def __init__(self):
        pygame.init()
        self.arquivo_config = os.path.join('conf', 'conf.ini')
        self.config = configparser.ConfigParser()
        self.controles = {}
        self.largura_tela = 800
        self.altura_tela = 600
        self.tela_cheia = False
        self.tamanho_bloco = 20
        self.fps = 15
        self.cor_fundo = (10, 10, 10)
        self.cor_cobra = (0, 255, 0)
        self.cor_comida = (255, 0, 0)
        self.fonte = pygame.font.SysFont("Arial", 36)
        self.carregar_configuracoes()
        self.flags_tela = pygame.FULLSCREEN | pygame.SCALED if self.tela_cheia else 0
        self.tela = pygame.display.set_mode((self.largura_tela, self.altura_tela), self.flags_tela)
        pygame.display.set_caption("Jogo da Cobrinha")
        self.relogio = pygame.time.Clock()
        self.reiniciar_jogo()

    def carregar_configuracoes(self):
        try:
            if not os.path.exists(self.arquivo_config):
                raise FileNotFoundError(f"Arquivo de configuração não encontrado em {self.arquivo_config}")
            self.config.read(self.arquivo_config)
            secao_display = 'Display'
            self.largura_tela = self.config.getint(secao_display, 'width', fallback=1280)
            self.altura_tela = self.config.getint(secao_display, 'height', fallback=720)
            self.tela_cheia = self.config.getboolean(secao_display, 'fullscreen', fallback=False)
            secao_controles = 'Controls'
            self.controles['CIMA'] = pygame.key.key_code(self.config.get(secao_controles, 'up', fallback='w'))
            self.controles['BAIXO'] = pygame.key.key_code(self.config.get(secao_controles, 'down', fallback='s'))
            self.controles['ESQUERDA'] = pygame.key.key_code(self.config.get(secao_controles, 'left', fallback='a'))
            self.controles['DIREITA'] = pygame.key.key_code(self.config.get(secao_controles, 'right', fallback='d'))
            self.controles['PAUSAR'] = pygame.key.key_code(self.config.get(secao_controles, 'pause', fallback='enter'))
            self.controles['SAIR'] = pygame.key.key_code(self.config.get(secao_controles, 'action_b', fallback='p'))
        except Exception as e:
            print(f"ERRO: {e}. Usando padrão.")
            self.controles = {
                'CIMA': pygame.K_w, 'BAIXO': pygame.K_s, 'ESQUERDA': pygame.K_a, 'DIREITA': pygame.K_d,
                'PAUSAR': pygame.K_RETURN, 'SAIR': pygame.K_p
            }

    def reiniciar_jogo(self):
        self.cobra = [(self.largura_tela // 2, self.altura_tela // 2)]
        self.direcao = 'DIREITA'
        self.comida = self.posicao_aleatoria()
        self.pontuacao = 0
        self.rodando = True

    def posicao_aleatoria(self):
        x = random.randint(0, (self.largura_tela - self.tamanho_bloco) // self.tamanho_bloco) * self.tamanho_bloco
        y = random.randint(0, (self.altura_tela - self.tamanho_bloco) // self.tamanho_bloco) * self.tamanho_bloco
        return x, y

    def desenhar_texto(self, texto, tamanho, cor, x, y, centralizado=True):
        fonte_obj = pygame.font.SysFont("Arial", tamanho)
        superficie = fonte_obj.render(texto, True, cor)
        retangulo = superficie.get_rect()
        if centralizado:
            retangulo.center = (x, y)
        else:
            retangulo.topleft = (x, y)
        self.tela.blit(superficie, retangulo)

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == self.controles['PAUSAR']:
                    pygame.quit()
                    sys.exit()
                elif evento.key == self.controles['CIMA'] and self.direcao != 'BAIXO':
                    self.direcao = 'CIMA'
                elif evento.key == self.controles['BAIXO'] and self.direcao != 'CIMA':
                    self.direcao = 'BAIXO'
                elif evento.key == self.controles['ESQUERDA'] and self.direcao != 'DIREITA':
                    self.direcao = 'ESQUERDA'
                elif evento.key == self.controles['DIREITA'] and self.direcao != 'ESQUERDA':
                    self.direcao = 'DIREITA'

    def atualizar(self):
        cabeca_x, cabeca_y = self.cobra[0]
        if self.direcao == 'CIMA':
            cabeca_y -= self.tamanho_bloco
        elif self.direcao == 'BAIXO':
            cabeca_y += self.tamanho_bloco
        elif self.direcao == 'ESQUERDA':
            cabeca_x -= self.tamanho_bloco
        elif self.direcao == 'DIREITA':
            cabeca_x += self.tamanho_bloco

        nova_cabeca = (cabeca_x, cabeca_y)

        if (cabeca_x < 0 or cabeca_x >= self.largura_tela or cabeca_y < 0 or cabeca_y >= self.altura_tela or nova_cabeca in self.cobra):
            self.rodando = False
            return

        self.cobra.insert(0, nova_cabeca)

        if nova_cabeca == self.comida:
            self.pontuacao += 10
            self.comida = self.posicao_aleatoria()
        else:
            self.cobra.pop()

    def desenhar(self):
        self.tela.fill(self.cor_fundo)
        for segmento in self.cobra:
            pygame.draw.rect(self.tela, self.cor_cobra, (*segmento, self.tamanho_bloco, self.tamanho_bloco))
        pygame.draw.rect(self.tela, self.cor_comida, (*self.comida, self.tamanho_bloco, self.tamanho_bloco))
        self.desenhar_texto(f"Pontuação: {self.pontuacao}", 28, (255, 255, 255), 10, 10, centralizado=False)
        pygame.display.flip()

    def tela_game_over(self):
        self.tela.fill((0, 0, 0))
        self.desenhar_texto("FIM DE JOGO", 64, (255, 0, 0), self.largura_tela // 2, self.altura_tela // 2 - 50)
        self.desenhar_texto(f"Pontuação: {self.pontuacao}", 48, (255, 255, 255), self.largura_tela // 2, self.altura_tela // 2 + 10)
        self.desenhar_texto("ENTER para reiniciar | 'P' para sair", 28, (200, 200, 200), self.largura_tela // 2, self.altura_tela // 2 + 80)
        pygame.display.flip()

        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        esperando = False
                        self.reiniciar_jogo()
                    elif evento.key == self.controles['SAIR']:
                        pygame.quit()
                        sys.exit()

    def executar(self):
        while True:
            while self.rodando:
                self.tratar_eventos()
                self.atualizar()
                self.desenhar()
                self.relogio.tick(self.fps)
            self.tela_game_over()

if __name__ == "__main__":
    JogoCobrinha().executar()
