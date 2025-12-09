import pygame
from config import GRID_SIZE, BLACK, BUTTON_COLOR, BUTTON_BORDER_COLOR

def draw_element(surface, color, position):
    """Desenho base para blocos (usado por Snake e Food)."""
    # 1. Desenho da Sombra (Simulação 3D)
    shadow_rect = pygame.Rect(position[0] + 2, position[1] + 2, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, BLACK, shadow_rect)
    
    # 2. Desenho Principal
    rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, color, rect)
    
    # 3. Efeito de brilho interno
    r = min(color[0] + 50, 255)
    g = min(color[1] + 50, 255)
    b = min(color[2] + 50, 255)
    inner_color = (r, g, b)
    inner_rect = pygame.Rect(position[0] + 1, position[1] + 1, GRID_SIZE - 2, GRID_SIZE - 2)
    pygame.draw.rect(surface, inner_color, inner_rect)
    
def draw_button(screen, rect, text, font):
    """Desenha um botão com efeito 3D simples e texto centralizado."""
    shadow_rect = pygame.Rect(rect.left + 3, rect.top + 3, rect.width, rect.height)
    pygame.draw.rect(screen, BLACK, shadow_rect)
    
    pygame.draw.rect(screen, BUTTON_COLOR, rect)
    pygame.draw.rect(screen, BUTTON_BORDER_COLOR, rect, 3) 
    
    # Renderiza o texto (cor branca)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)