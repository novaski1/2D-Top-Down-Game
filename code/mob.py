import pygame
from regex import R
from settings import *
from debug import debug 
from support import import_folder
from entity import Entity
import math
import random

class Mob(Entity):
    def __init__(self,pos,groups,visible_sprites,obstacle_sprites,player,group_size):

        super().__init__(pos,groups,obstacle_sprites)

        # If more than group_size mobs on screen -> kill
        if group_size >= 100: self.kill()

        # Rect setup
        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(64, 64))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-20,-8)
        self.sprite_type = 'mob'

        # Graphics setup
        self.import_entity_assets()
        self.status = 'right'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Movement
        self.direction = pygame.math.Vector2()
        self.speed_original = random.uniform(1.5,6)
        self.speed = self.speed_original

        # Bump mechanic
        self.bumped = False
        self.bump = 0
        self.bump_direction_x = 0
        self.bump_direction_y = 0

        # Stats
        self.got_hit = False
        self.hit_cooldown = 0
        self.health = 1000

        # Player position
        self.player_x = player.rect.centerx
        self.player_y = player.rect.centery
        self.offset_x = 0
        self.offset_y = 0

        # Position
        self.chunk_pos = [None,None]

        # Other
        self.mob_group_avgposition_x = 0
        self.mob_group_avgposition_y = 0
        self.visible_sprites = visible_sprites
        self.obstacle_sprites = obstacle_sprites


    def collision(self,direction):
        mob_group_position_x = []
        mob_group_position_y = []
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.hitbox) and sprite.rect.center != self.rect.center:

                ### Collisions between sprites ###
                if direction == 'horizontal':
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox.left = sprite.hitbox.right
                if direction == 'vertical':
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox.top = sprite.hitbox.bottom
                
        ### Bump mechanic ###
        for sprite in self.visible_sprites:
            if sprite.hitbox.inflate(2,2).colliderect(self.hitbox) and sprite.rect.center != self.rect.center:
                if self.bumped == False and sprite.sprite_type == 'bullet': # Self get bumped by bullet
                        if self.hit_cooldown == 0 or self.got_hit == False: # If possible, inflict damage
                            self.got_hit = True
                            self.hit_cooldown = 10
                        self.bumped = True # In all cases, get bumped
                        self.bump = 2
                        self.bump_direction_x = sprite.direction.x
                        self.bump_direction_y = sprite.direction.y

                if sprite.sprite_type == 'mob': # Bump other mobs
                    mob_group_position_x.append(sprite.rect.centerx)
                    mob_group_position_y.append(sprite.rect.centery)
                    if self.bumped == True and sprite.bumped == False: # Self is bumped and gives the bump effect to a colliding mob
                        sprite.bumped = True
                        sprite.bump = self.bump*0.4
                        sprite.bump_direction_x = self.direction.x
                        sprite.bump_direction_y = self.direction.y

        if mob_group_position_x != [] and mob_group_position_y != []:
            self.mob_group_avgposition_x = sum(mob_group_position_x)/len(mob_group_position_x)
            self.mob_group_avgposition_y = sum(mob_group_position_y)/len(mob_group_position_y)

    def pathfinding(self):
        if self.bumped == False:
            direction = (self.player_x-self.rect.centerx,self.player_y-self.rect.centery)
            direction_offset = (self.mob_group_avgposition_x-self.rect.centerx,self.mob_group_avgposition_y-self.rect.centery)
            direction_final = ((self.player_x+self.mob_group_avgposition_x)/2-self.rect.centerx,(self.player_y+self.mob_group_avgposition_y)/2-self.rect.centery)
            self.direction.x = direction[0]
            self.direction.y = direction[1]
        
    def bump_mechanic(self):
        if self.bumped == True:
            self.direction.x = self.bump_direction_x*self.bump
            self.direction.y = self.bump_direction_y*self.bump
            self.bump -= 0.1
        if self.bump < 0: 
            self.bump = 0
            self.bumped = False
    
    def stats_update(self):
        if self.got_hit == True:
            self.health -= 20
            self.hot_hit = False
        if self.hit_cooldown > 0: self.hit_cooldown -= 1

        
        if self.health <= 0: self.kill()

    def mob_update(self,player,offset):
        self.player_x = player.rect.centerx
        self.player_y = player.rect.centery
        self.offset_x = offset.x
        self.offset_y = offset.y
    
    def update(self):
        self.pathfinding()
        self.bump_mechanic()
        self.move(self.speed)
        self.animate()
        self.stats_update()

        debug(self.bumped)