import pygame
from config import ConfigLoader
from board import Board
from renderer import Renderer

class Game:
    def __init__(self, config):
        pygame.init()
        width=config.getint('Display','width'); height=config.getint('Display','height')
        fullscreen=config.getboolean('Display','fullscreen')
        flags=pygame.FULLSCREEN if fullscreen else 0
        self.screen=pygame.display.set_mode((width,height),flags)

        self.controls={k:ConfigLoader.map_key(config['Controls'][k]) for k in config['Controls']}
        self.rows,self.cols,self.mines=10,12,15
        margin=20
        self.cs=min((width-margin*2)//self.cols,(height-margin*2)//self.rows)
        self.grid_w=self.cs*self.cols; self.grid_h=self.cs*self.rows
        self.ox=(width-self.grid_w)//2; self.oy=(height-self.grid_h)//2

        self.board=Board(self.rows,self.cols,self.mines)
        self.renderer=Renderer(self.screen,self.board,self.cs,self.ox,self.oy)

        self.cr=0; self.cc=0

    def run(self):
        clock=pygame.time.Clock(); running=True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                elif e.type==pygame.KEYDOWN: running=self.handle_key(e.key)
                elif e.type==pygame.MOUSEBUTTONDOWN: self.handle_mouse(e)
            self.renderer.draw((self.cr,self.cc))
            clock.tick(60)
        pygame.quit()

    def handle_key(self,key):
        if key==self.controls.get('pause'): return False
        if key==self.controls.get('up'): self.cr=(self.cr-1)%self.rows
        elif key==self.controls.get('down'): self.cr=(self.cr+1)%self.rows
        elif key==self.controls.get('left'): self.cc=(self.cc-1)%self.cols
        elif key==self.controls.get('right'): self.cc=(self.cc+1)%self.cols
        elif key==self.controls.get('action_a'): self.board.reveal(self.cr,self.cc)
        elif key==self.controls.get('action_b'): self.board.toggle_flag(self.cr,self.cc)
        return True

    def handle_mouse(self,e):
        mx,my=e.pos
        if not(self.ox<=mx<self.ox+self.grid_w): return
        if not(self.oy<=my<self.oy+self.grid_h): return
        c=(mx-self.ox)//self.cs; r=(my-self.oy)//self.cs
        self.cr,self.cc=r,c
        if e.button==1: self.board.reveal(r,c)
        elif e.button==3: self.board.toggle_flag(r,c)
