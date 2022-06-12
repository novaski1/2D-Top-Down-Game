import pygame
from settings import *
from debug import debug 
from support import import_folder
from gun import Gun
import math
import random

class Entity(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites):

        super().__init__(groups)

        # Rect setup
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(64, 64))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-8,-26)

        # Graphics setup
        self.import_entity_assets()
        self.status = 'right'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 5

        # Position
        self.chunk_pos = [None,None]

        # Other
        self.obstacle_sprites = obstacle_sprites

    def import_entity_assets(self):
        character_path = 'graphics/player/'
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_status(self):

        # Idle
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
        
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle','_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack','')

    def move(self,speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            if self.speed <= 6 and self.sprite_type != 'mob':
                self.speed *= 1.08
            if self.speed >= 6: self.speed = 6

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def animate(self):
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

    def chunk_update(self):
        self.chunk_pos[0] = int((int((self.rect.topleft[0])/TILESIZE) - int((self.rect.topleft[0])/TILESIZE)%CHUNK_SIZE)/CHUNK_SIZE)
        self.chunk_pos[1] = int((int((self.rect.topleft[1])/TILESIZE) - int((self.rect.topleft[1])/TILESIZE)%CHUNK_SIZE)/CHUNK_SIZE)
