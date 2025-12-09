import pygame

class Renderer:
    def __init__(self, screen, board, cell_size, ox, oy):
        self.screen = screen
        self.board = board
        self.cs = cell_size
        self.ox = ox
        self.oy = oy
        self.font = pygame.font.SysFont(None, int(cell_size*0.65))
        self.status_font = pygame.font.SysFont(None, 24)

    def draw(self, cursor):
        self.screen.fill((30,30,30))
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                self.draw_cell(r,c)
        self.draw_cursor(cursor)
        self.draw_status()
        pygame.display.flip()

    def draw_cell(self, r, c):
        cell = self.board.grid[r][c]
        x = self.ox + c*self.cs
        y = self.oy + r*self.cs
        rect = pygame.Rect(x,y,self.cs,self.cs)
        if cell.revealed:
            pygame.draw.rect(self.screen,(200,200,200),rect)
            if cell.mine:
                pygame.draw.circle(self.screen,(0,0,0),(x+self.cs//2,y+self.cs//2),self.cs//3)
            elif cell.adj>0:
                t=self.font.render(str(cell.adj),True,(20,20,180))
                self.screen.blit(t,t.get_rect(center=rect.center))
        else:
            pygame.draw.rect(self.screen,(100,100,100),rect)
            if cell.flagged:
                pygame.draw.polygon(self.screen,(200,40,40),[
                    (x+self.cs*0.25,y+self.cs*0.2),
                    (x+self.cs*0.6, y+self.cs*0.3),
                    (x+self.cs*0.25,y+self.cs*0.5)
                ])
        pygame.draw.rect(self.screen,(50,50,50),rect,1)

    def draw_cursor(self,cursor):
        r,c=cursor
        x=self.ox+c*self.cs
        y=self.oy+r*self.cs
        pygame.draw.rect(self.screen,(255,255,0),(x,y,self.cs,self.cs),max(2,self.cs//12))

    def draw_status(self):
        if self.board.game_over: msg="Game Over — Pause para sair"
        elif self.board.victory: msg="Vitória — Pause para sair"
        else: msg=f"Restantes: {self.board.remaining} | Minas: {self.board.mines}"
        st=self.status_font.render(msg,True,(230,230,230))
        self.screen.blit(st,(10,10))
