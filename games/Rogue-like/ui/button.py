import pygame

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("arial", 32)
        self.color = (200, 200, 200)

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        label = self.font.render(self.text, True, (0,0,0))
        win.blit(label, (self.rect.x + 10, self.rect.y + 10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
