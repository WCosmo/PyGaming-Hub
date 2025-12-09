from cell import Cell
import random

class Board:
    def __init__(self, rows, cols, mines):
        self.rows, self.cols, self.mines = rows, cols, mines
        self.grid = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.first_move = True
        self.remaining = rows * cols - mines
        self.game_over = False
        self.victory = False

    def place_mines(self, safe_r, safe_c):
        positions = [(r,c) for r in range(self.rows) for c in range(self.cols)]
        forbidden = {(safe_r+dr, safe_c+dc) for dr in (-1,0,1) for dc in (-1,0,1)
                      if 0 <= safe_r+dr < self.rows and 0 <= safe_c+dc < self.cols}
        eligible = [p for p in positions if p not in forbidden]
        random.shuffle(eligible)
        for i in range(self.mines):
            r,c = eligible[i]
            self.grid[r][c].mine = True
        self.calculate_adj()

    def calculate_adj(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.mine:
                    cell.adj = -1
                    continue
                total = 0
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr==0 and dc==0: continue
                        rr,cc = r+dr, c+dc
                        if 0<=rr<self.rows and 0<=cc<self.cols and self.grid[rr][cc].mine:
                            total+=1
                cell.adj = total

    def reveal(self, r, c):
        if self.game_over or self.victory: return
        cell = self.grid[r][c]
        if cell.revealed or cell.flagged: return
        if self.first_move:
            self.place_mines(r, c)
            self.first_move = False
        cell.revealed = True
        if cell.mine:
            self.trigger_game_over(); return
        self.remaining -= 1
        if cell.adj == 0:
            self.flood_fill(r, c)
        if self.remaining == 0:
            self.trigger_victory()

    def flood_fill(self, r, c):
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                rr,cc=r+dr,c+dc
                if 0<=rr<self.rows and 0<=cc<self.cols:
                    if not self.grid[rr][cc].revealed and not self.grid[rr][cc].mine:
                        self.reveal(rr,cc)

    def toggle_flag(self, r, c):
        if not self.grid[r][c].revealed:
            self.grid[r][c].flagged = not self.grid[r][c].flagged

    def trigger_game_over(self):
        self.game_over = True
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].mine:
                    self.grid[r][c].revealed = True

    def trigger_victory(self):
        self.victory = True
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].revealed = True
