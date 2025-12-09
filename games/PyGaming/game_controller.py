import pygame
from snake import Snake
from food import Food
from config import *
from drawing import draw_button

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Snake - PyGaming Hub (POO)")
        self.clock = pygame.time.Clock()
        self.current_state = MENU
        
        self.snake = Snake()
        self.food = Food(self.snake.body)
        
        self._setup_fonts()
        self.global_high_score = 0 # Variável interna para High Score
        
    def _setup_fonts(self):
        fonte_path = 'Early GameBoy.ttf' 
        tamanho_titulo = 32
        tamanho_menu = 20
        tamanho_score = 18

        try:
            self.font_title = pygame.font.Font(fonte_path, tamanho_titulo)
            self.font_menu = pygame.font.Font(fonte_path, tamanho_menu)
            self.font_score = pygame.font.Font(fonte_path, tamanho_score)
        except pygame.error:
            self.font_title = pygame.font.Font(None, 80)
            self.font_menu = pygame.font.Font(None, 40)
            self.font_score = pygame.font.Font(None, 36)

    def _draw_grid(self):
        self.screen.fill(BG_COLOR)
        for x in range(0, DISPLAY_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, DISPLAY_HEIGHT))
        for y in range(0, DISPLAY_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (DISPLAY_WIDTH, y))

    def run(self):
        running = True
        while running:
            
            if self.current_state == MENU:
                self._handle_menu()
            
            elif self.current_state == GAME:
                self._handle_game()
                
            elif self.current_state == GAME_OVER:
                if self.snake.score > self.global_high_score:
                    self.global_high_score = self.snake.score
                self._handle_game_over()
            
            elif self.current_state == -1:
                running = False

        pygame.quit()
        
    # --- MÉTODOS DE ESTADO (Detalhes omitidos para concisão, são iguais à versão anterior) ---

    def _handle_menu(self):
        BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
        center_x = DISPLAY_WIDTH // 2
        start_button_rect = pygame.Rect(center_x - BUTTON_WIDTH // 2, DISPLAY_HEIGHT * 0.55, BUTTON_WIDTH, BUTTON_HEIGHT)
        exit_button_rect = pygame.Rect(center_x - BUTTON_WIDTH // 2, DISPLAY_HEIGHT * 0.70, BUTTON_WIDTH, BUTTON_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.current_state = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button_rect.collidepoint(mouse_pos):
                    self.snake.reset()
                    self.food.spawn(self.snake.body)
                    self.current_state = GAME
                if exit_button_rect.collidepoint(mouse_pos): self.current_state = -1
            if event.type == pygame.KEYDOWN and event.key == CONTROLS_MAP['pause']: self.current_state = -1

        self.screen.fill(BG_COLOR)
        title_text = self.font_title.render("COBRINHA PYGAME", True, SNAKE_HEAD_COLOR)
        title_rect = title_text.get_rect(center=(center_x, DISPLAY_HEIGHT * 0.20))
        self.screen.blit(title_text, title_rect)
        
        score_text = self.font_menu.render(f"MELHOR SCORE: {self.global_high_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(center_x, DISPLAY_HEIGHT * 0.40))
        self.screen.blit(score_text, score_rect)
        
        draw_button(self.screen, start_button_rect, "START", self.font_menu)
        draw_button(self.screen, exit_button_rect, "SAIR", self.font_menu)
        pygame.display.flip()
        self.clock.tick(15)

    def _handle_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.current_state = -1
            if event.type == pygame.KEYDOWN:
                if event.key == CONTROLS_MAP['pause']:
                    self.current_state = GAME_OVER
                self.snake.handle_input(event.key)
        
        self.snake.move()
        
        if self.snake.check_collision():
            self.current_state = GAME_OVER
            return

        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.spawn(self.snake.body)
        else:
            self.snake.body.pop()

        self._draw_grid()
        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        score_text = self.font_score.render(f"Score: {self.snake.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()
        self.clock.tick(FPS + (self.snake.score // 50))

    def _handle_game_over(self):
        BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50
        center_x = DISPLAY_WIDTH // 2
        restart_button_rect = pygame.Rect(center_x - BUTTON_WIDTH // 2, DISPLAY_HEIGHT * 0.55, BUTTON_WIDTH, BUTTON_HEIGHT)
        menu_button_rect = pygame.Rect(center_x - BUTTON_WIDTH // 2, DISPLAY_HEIGHT * 0.70, BUTTON_WIDTH, BUTTON_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.current_state = -1
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if restart_button_rect.collidepoint(mouse_pos):
                    self.snake.reset()
                    self.food.spawn(self.snake.body)
                    self.current_state = GAME
                if menu_button_rect.collidepoint(mouse_pos): self.current_state = MENU
            if event.type == pygame.KEYDOWN and event.key == CONTROLS_MAP['pause']: self.current_state = MENU

        self.screen.fill(BG_COLOR)
        game_over_text = self.font_title.render("GAME OVER", True, RED)
        go_rect = game_over_text.get_rect(center=(center_x, DISPLAY_HEIGHT * 0.20))
        self.screen.blit(game_over_text, go_rect)
        
        score_text = self.font_menu.render(f"SCORE FINAL: {self.snake.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(center_x, DISPLAY_HEIGHT * 0.40))
        self.screen.blit(score_text, score_rect)
        
        draw_button(self.screen, restart_button_rect, "RESTART", self.font_menu)
        draw_button(self.screen, menu_button_rect, "MENU INICIAL", self.font_menu)
        pygame.display.flip()
        self.clock.tick(15)