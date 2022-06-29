import pygame
from settings import *
from debug import debug 
from support import import_folder
from entity import Entity
from gun import Gun
import math
import random

class Player(Entity):
    def __init__(self,pos,groups,obstacle_sprites):

        super().__init__(pos,groups,obstacle_sprites)

        # Rect setup
        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(64, 64))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-20,-8)
        self.sprite_type = 'player'

        # Graphics setup
        self.import_entity_assets()
        self.status = 'right'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.change_fps = False
        self.cooldown = 400
        self.change_fps_time = None
        self.dashing = 'no'
        self.dashing_time = 100

        # Position
        self.chunk_pos = [None,None]

        # Figthing
        self.gun = Gun(random.choice(range(2,6)),random.choice(range(15,40)))
        self.last_cooldown = 0

        # Other
        self.obstacle_sprites = obstacle_sprites

    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox) and sprite.rect.center != self.rect.center and self.sprite_type not in ('player','bullet'):
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox.left = sprite.hitbox.right
                    
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox) and sprite.rect.center != self.rect.center and self.sprite_type not in ('player','bullet'):
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_z]:
            self.direction.y = -1
            if self.status == 'right_idle': self.status = 'right'
            if self.status == 'left_idle': self.status = 'left'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            if self.status == 'right_idle': self.status = 'right'
            if self.status == 'left_idle': self.status = 'left'
            #self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_q]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0
        
        # Attack input
        if keys[pygame.K_p]:
            if self.change_fps == False: 
                self.change_fps = True
                self.change_fps_time = pygame.time.get_ticks()
                print(FPS)
                if globals()['FPS'] == 30: globals()['FPS'] = 60
                if globals()['FPS'] == 60: globals()['FPS'] = 165
                if globals()['FPS'] == 165: globals()['FPS'] = 30

            
            
    
    def dash(self):
        if self.dashing == 'yes' and 0 < pygame.time.get_ticks() - self.dashing_time <= 500: self.speed = 12
        else: self.speed = 5
    
    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.change_fps:
            if current_time - self.change_fps_time >= self.cooldown:
                self.change_fps = False
        
        if self.dashing:
            if current_time - self.dashing_time >= 2000:
                self.dashing = 'no'
        
        self.last_cooldown += 1

    def update(self):
        self.input()
        self.chunk_update()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.dash()
        self.move(self.speed)
        #debug(self.status)
    
class Hand(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites,player):
        super().__init__(groups)
        self.image = pygame.image.load('graphics/player/hands.png').convert_alpha()
        #self.image = pygame.transform.scale(self.image,(128, 128))
        self.image = pygame.transform.scale(self.image,(128, 128))
        self.image_left = pygame.transform.flip(self.image, False, True)
        self.image_right = self.image

        self.sprite_type = 'hand'

        self.rect = self.image.get_rect(topleft = pos)
        self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery
        self.hitbox = self.rect.inflate(-20,-8)

        self.direction = 'left'

        self.obstacle_sprites = obstacle_sprites
    
    def rotatePivoted(self,im,angle,pivot):
        # rotate the leg image around the pivot
        image = pygame.transform.rotate(im, angle)
        rect = image.get_rect()
        rect.center = pivot
        return image, rect

    def hand_movement(self,player,half_width,half_height):
        dx = pygame.mouse.get_pos()[0] - half_width
        dy = pygame.mouse.get_pos()[1] - half_height
        rads = math.atan2(-dy,dx)
        rads %= 2*math.pi
        degs = math.degrees(rads)

        pivot = (40,40)
        if 90 <= degs < 270:
            #self.image = pygame.transform.rotate(self.image_left, degs)
            self.image, self.rect = self.rotatePivoted(self.image_left,degs,pivot)
        else:
            #self.image = pygame.transform.rotate(self.image_right, degs)
            self.image, self.rect = self.rotatePivoted(self.image_right,degs,pivot)

        self.rect.centerx = player.rect.centerx + math.cos(rads)*80
        self.rect.centery = player.rect.centery - math.sin(rads)*80 + 7




