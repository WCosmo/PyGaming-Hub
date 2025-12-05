import pygame, os, configparser, random

C_BG, C_GRID = (5, 10, 5), (0, 40, 0)
C_GOOD, C_BAD = (0, 80, 0), (200, 0, 0)
C_WORM, C_NUKE = (180, 0, 255), (0, 255, 255)
C_LOCK, C_SHIELD = (100, 100, 100), (0, 0, 200)
C_CUR, C_TXT, C_BSOD, C_WHT = (0, 255, 0), (255, 255, 0), (0, 0, 170), (255, 255, 255)
COLS, ROWS = 8, 6
LOG_FILE = "system.log"

class FloatingText:
    def __init__(self, x, y, txt, col):
        self.x, self.y, self.txt, self.col, self.life = x, y, txt, col, 45
        self.font = pygame.font.SysFont('consolas', 20, bold=True)
    def update(self): self.y -= 1.5; self.life -= 1
    def draw(self, s):
        if self.life > 0: s.blit(self.font.render(self.txt, True, self.col), (self.x, self.y))

class Particle:
    def __init__(self, x, y, col):
        self.x, self.y, self.col, self.life = x, y, col, 25
        self.vx, self.vy, self.sz = random.uniform(-6,6), random.uniform(-6,6), random.randint(3,7)
    def update(self): self.x += self.vx; self.y += self.vy; self.life -= 1
    def draw(self, s, ox, oy):
        if self.life > 0: pygame.draw.rect(s, self.col, (self.x+ox, self.y+oy, self.sz, self.sz))

class Sector:
    def __init__(self, c, r, t='BAD'):
        self.c, self.r, self.type, self.tm = c, r, t, 0
    def update(self, all_s):
        if self.type == 'WORM':
            self.tm += 1
            if self.tm >= 150:
                self.tm = 0; burst = []
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:
                        if dx==0 and dy==0: continue
                        nc, nr = self.c+dx, self.r+dy
                        if 0<=nc<COLS and 0<=nr<ROWS and (nc,nr) not in all_s: burst.append((nc,nr))
                return burst
        return None

def get_highscores():
    try:
        if not os.path.exists(LOG_FILE): return [0]*5
        with open(LOG_FILE, 'r') as f: sc = [int(l.strip()) for l in f.readlines()]
        return sorted(sc, reverse=True)[:5]
    except: return [0]*5

def save_score(score):
    sc = get_highscores()
    sc.append(score)
    sc = sorted(sc, reverse=True)[:5]
    try:
        with open(LOG_FILE, 'w') as f:
            for s in sc: f.write(f"{s}\n")
        return score == sc[0]
    except: return False

def draw_c(surf, txt, font, col, y_off=0, ox=0, oy=0):
    t = font.render(txt, True, col)
    surf.blit(t, t.get_rect(center=(surf.get_width()//2+ox, surf.get_height()//2+y_off+oy)))

def main():
    pygame.init(); pygame.font.init()
    f_mono = pygame.font.SysFont('consolas', 20)
    f_big = pygame.font.SysFont('consolas', 50, bold=True)
    
    cfg = configparser.ConfigParser()
    path = os.path.join('conf', 'conf.ini')
    if not os.path.exists(path): return
    cfg.read(path)

    try:
        sw, sh = int(cfg['Display']['width']), int(cfg['Display']['height'])
        full = cfg.getboolean('Display', 'fullscreen')
        ctrls = cfg['Controls']
        k_map = {k: pygame.key.key_code(ctrls[k].replace('enter','return')) 
                 for k in ['up','down','left','right','action_a','action_b','pause']}
    except: return

    sc = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN if full else 0)
    pygame.display.set_caption("Disk Defrag")
    clock = pygame.time.Clock()

    state, mx, my = "MENU", 50, 80
    cw, ch = (sw - mx*2)//COLS, (sh - my*2)//ROWS
    pc, pr, score, frag, combo, c_tm, shake = 0, 0, 0, 0.0, 0, 0, 0
    spawn_t, freeze_tm = 0, 0
    has_shield = False
    act, parts, txts = {}, [], []
    is_rec, top_sc = False, get_highscores()[0]
    run = True

    while run:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False
            if e.type == pygame.KEYDOWN:
                if e.key == k_map['pause']: run = False
                
                if e.key == k_map['action_b']:
                    if state == "GAME": state = "PAUSED"
                    elif state == "PAUSED": state = "GAME"

                if state == "MENU" and e.key == k_map['action_a']:
                    state, act, score, frag, combo, c_tm = "GAME", {}, 0, 0, 0, 0
                    has_shield, freeze_tm, is_rec = False, 0, False

                elif state == "BSOD" and e.key == k_map['action_a']: 
                    state, top_sc = "MENU", get_highscores()[0]

                elif state == "GAME" and freeze_tm == 0:
                    moved = False
                    if e.key == k_map['up'] and pr > 0: pr -= 1; moved=True
                    elif e.key == k_map['down'] and pr < ROWS-1: pr += 1; moved=True
                    elif e.key == k_map['left'] and pc > 0: pc -= 1; moved=True
                    elif e.key == k_map['right'] and pc < COLS-1: pc += 1; moved=True
                    
                    if e.key == k_map['action_a']:
                        pos = (pc, pr)
                        vx, vy = mx + pc*cw + cw//2, my + pr*ch + ch//2
                        if pos in act:
                            tgt = act[pos]
                            if tgt.type == 'NUKE':
                                score += 1000 + len(act)*100
                                frag, shake = 0, 25
                                txts.append(FloatingText(vx, vy-40, "SYSTEM PURGED!", C_NUKE))
                                for ac in act:
                                    for _ in range(5): parts.append(Particle(mx+ac[0]*cw+cw//2, my+ac[1]*ch+ch//2, C_NUKE))
                                act.clear()
                            
                            elif tgt.type == 'LOCK':
                                freeze_tm = 120
                                shake = 10
                                txts.append(FloatingText(vx, vy-20, "LOCKED!", (200,200,200)))
                                del act[pos]

                            elif tgt.type == 'SHIELD':
                                has_shield = True
                                score += 200
                                txts.append(FloatingText(vx, vy-20, "SHIELD UP!", C_SHIELD))
                                del act[pos]
                            
                            else:
                                pts = 100
                                old_c = combo
                                c_add = 10 if tgt.type == 'WORM' else 1
                                combo = (combo + c_add) if c_tm > 0 else c_add
                                c_tm = 120 
                                
                                if (combo // 50) > (old_c // 50):
                                    free = [(c,r) for c in range(COLS) for r in range(ROWS) if (c,r) not in act]
                                    if free:
                                        ntc, ntr = random.choice(free)
                                        act[(ntc, ntr)] = Sector(ntc, ntr, 'NUKE')
                                        txts.append(FloatingText(mx+ntc*cw, my+ntr*ch, "NUKE!", C_NUKE))

                                mult = min(combo, 10)
                                score += pts * mult
                                frag = max(0, frag - 2)
                                txts.append(FloatingText(vx, vy-20, f"+{pts} x{mult}", C_TXT))
                                
                                col_p = C_WORM if tgt.type=='WORM' else C_BAD
                                for _ in range(8): parts.append(Particle(vx, vy, col_p))
                                del act[pos]
                        else:
                            if has_shield:
                                has_shield = False
                                txts.append(FloatingText(vx, vy-20, "SHIELD BROKEN!", C_SHIELD))
                            else:
                                frag += 8; shake = 8; combo = 0
                                txts.append(FloatingText(vx, vy-20, "MISS!", (255,100,100)))

        if state == "GAME":
            if freeze_tm > 0: freeze_tm -= 1
            c_tm -= 1 if c_tm > 0 else 0
            if c_tm == 0: combo = 0
            
            if act: frag += 0.12 

            spawn_t += 1
            if spawn_t > max(8, 30 - (score//800)):
                tc, tr = random.randint(0, COLS-1), random.randint(0, ROWS-1)
                if (tc, tr) not in act:
                    rnd = random.random()
                    st = 'BAD'
                    if rnd < 0.05: st = 'LOCK'
                    elif rnd < 0.08: st = 'SHIELD'
                    elif rnd < 0.25: st = 'WORM'
                    act[(tc, tr)] = Sector(tc, tr, st)
                    if st in ['BAD', 'WORM']: frag += 0.5
                spawn_t = 0
            
            new_i, rem = [], []
            for c, s in act.items():
                res = s.update(act)
                if res:
                    new_i.extend(res); rem.append(c); shake = 15
                    txts.append(FloatingText(mx+c[0]*cw, my+c[1]*ch, "BURST!", C_WORM))
            for c in rem: act[c] = Sector(c[0], c[1], 'BAD')
            for c in new_i: 
                act[c] = Sector(c[0], c[1], 'BAD')
                if not has_shield: frag += 3

            shake -= 1 if shake > 0 else 0
            parts = [p for p in parts if (p.update() or p.life > 0)]
            txts = [t for t in txts if (t.update() or t.life > 0)]
            
            if len(act) > (COLS*ROWS)*0.9 or frag >= 100: 
                state = "BSOD"
                is_rec = save_score(score)

        ox, oy = random.randint(-shake, shake), random.randint(-shake, shake)
        sc.fill(C_BG)

        if state == "MENU":
            go = (pygame.time.get_ticks()//10)%50
            for i in range(0, sh, 50): pygame.draw.line(sc, (0,20,0), (0, i+go), (sw, i+go))
            pygame.draw.rect(sc, C_CUR, (40,40,sw-80,sh-80), 4)
            draw_c(sc, "DISK DEFRAG", f_big, C_CUR, -60)
            draw_c(sc, f"TOP SCORE: {top_sc}", f_mono, C_WHT, -10)
            draw_c(sc, "CINZA=LOCK | AZUL=ESCUDO | ROXO=+10", f_mono, C_WORM, 40)
            draw_c(sc, "[O] JOGAR", f_mono, C_CUR, 120)

        elif state == "PAUSED":
            draw_c(sc, "SYSTEM PAUSED", f_big, C_WHT, -20)
            draw_c(sc, "[ACAO B] RESUME", f_mono, C_WHT, 40)

        elif state == "GAME":
            if c_tm > 0:
                bl = int((c_tm/120)*200)
                pygame.draw.rect(sc, C_TXT, (sw//2-100, 10, bl, 10))
                sc.blit(f_mono.render(f"COMBO x{combo}", True, C_TXT), (sw//2-40, 25))
            
            pygame.draw.rect(sc, (50,0,0), (mx, sh-40, sw-mx*2, 20))
            safew = int((sw-mx*2)*((100-frag)/100))
            if safew > 0: pygame.draw.rect(sc, C_SHIELD if has_shield else (C_CUR if frag<50 else (255,0,0)), (mx, sh-40, safew, 20))
            sc.blit(f_mono.render(f"SCORE: {score}", True, C_WHT), (mx, 15))

            for r in range(ROWS):
                for c in range(COLS):
                    rx, ry = mx+c*cw+ox, my+r*ch+oy
                    col, bord = C_GRID, 1
                    if (c,r) in act:
                        s = act[(c,r)]
                        if s.type == 'NUKE': col = C_WHT if (pygame.time.get_ticks()//50)%2==0 else C_NUKE
                        elif s.type == 'LOCK': col = (150,150,150) if (pygame.time.get_ticks()//100)%2==0 else C_LOCK
                        elif s.type == 'SHIELD': col = C_SHIELD
                        elif s.type == 'WORM':
                            col = C_WORM
                            if (pygame.time.get_ticks()//(200 if s.tm<100 else 50))%2==0: bord=4
                        else: col = C_BAD
                    else: col = C_GOOD
                    pygame.draw.rect(sc, col, (rx+2, ry+2, cw-4, ch-4))
                    if c==pc and r==pr: 
                        ccol = (255,0,0) if freeze_tm > 0 else C_CUR
                        pygame.draw.rect(sc, ccol, (rx, ry, cw, ch), 3)

            for p in parts: p.draw(sc, ox, oy)
            for t in txts: t.draw(sc)

        elif state == "BSOD":
            sc.fill(C_BSOD)
            draw_c(sc, ":(", f_big, C_WHT, -80, ox, oy)
            msg = "NEW RECORD!" if is_rec else "SYSTEM FAILURE"
            draw_c(sc, msg, f_mono, C_TXT if is_rec else C_WHT, -20, ox, oy)
            draw_c(sc, f"FINAL: {score}", f_big, C_WHT, 40, ox, oy)
            draw_c(sc, "[ACAO A] REBOOT", f_mono, C_WHT, 100, ox, oy)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__": main()