import pygame
from ui.button import Button

class GameOverScreen:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 50)
        self.btn_restart = Button(280, 300, 240, 60, "JOGAR NOVAMENTE")
        self.btn_exit = Button(280, 400, 240, 60, "FECHAR")

    def draw(self, win):
        text = self.font.render("GAME OVER", True, (255, 0, 0))
        win.blit(text, (260, 150))
        self.btn_restart.draw(win)
        self.btn_exit.draw(win)
