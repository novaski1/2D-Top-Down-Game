import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self,pos,groups,sprite_type,surface = pygame.Surface((TILESIZE,TILESIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        #if self.sprite_type == '-0.1': self.image = pygame.image.load('../graphics/test/grass_cold.png')
        #elif self.sprite_type == '0.1': self.image = pygame.image.load('../graphics/test/grass_hot.png')
        #else: self.image = pygame.image.load('../graphics/test/grass.png')
        #self.image = pygame.image.load('../graphics/test/grass.png')
        #self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(topleft = pos)          
        self.hitbox = self.rect.inflate(0,-10)
