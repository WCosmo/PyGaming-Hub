import random
from config import GRID_SIZE, FOOD_COLOR, DISPLAY_WIDTH, DISPLAY_HEIGHT
from drawing import draw_element

class Food:
    def __init__(self, snake_body):
        self.position = self._random_spawn(snake_body)
    
    def _random_spawn(self, snake_body):
        """Método privado para gerar uma posição aleatória fora da cobra."""
        while True:
            x = random.randrange(0, DISPLAY_WIDTH // GRID_SIZE) * GRID_SIZE
            y = random.randrange(0, DISPLAY_HEIGHT // GRID_SIZE) * GRID_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def spawn(self, snake_body):
        """Gera uma nova posição pública para a comida."""
        self.position = self._random_spawn(snake_body)

    def draw(self, screen):
        """Desenha a comida na tela."""
        draw_element(screen, FOOD_COLOR, self.position)