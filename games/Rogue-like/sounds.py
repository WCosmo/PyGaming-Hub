import pygame

pygame.mixer.init()


pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.load('games/Rogue-like/assets/sounds/heavy_battle_1_bpm190.mp3') 
pygame.mixer.music.play(-1)

