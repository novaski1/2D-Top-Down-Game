import chunk
from cmath import pi
import math
import pygame
from settings import *
from tile import Tile
from entity import Entity
from mob import Mob
from player import Player, Hand
from bullet import Bullet
from debug import debug
from support import *
from time import sleep

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.player = Player((10,10),[self.visible_sprites],self.obstacle_sprites)
        self.player_hands = Hand((10,10),[self.visible_sprites],self.obstacle_sprites,self.player)

        self.layouts = {
            'boundary': import_csv_layout('map/out.csv')
        }

        self.mob_group = []

        self.debug_mode = False

        # Cooldowns
        self.cooldown_debug_hitbox = 0

        #self.create_map(self.layouts)
    
    def create_map(self,layouts): 
        for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col in ('-0.1','0.1'):
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')

    def shoot(self):
        left, middle, right = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player_pos = (self.player.rect.centerx,self.player.rect.centery)
        if left and self.player.last_cooldown >= self.player.gun.freq:
            self.player.last_cooldown = 0
            bullet_direction = self.shooting_direction(self.visible_sprites.offset,self.player.rect,mouse_pos)
            Bullet((self.player.rect.centerx,self.player.rect.centery-15),[self.visible_sprites],self.obstacle_sprites,bullet_direction,self.player.gun.speed)
        
    def create_mob(self):
        left, middle, right = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player_pos = (self.player.rect.centerx,self.player.rect.centery)
        if right and self.player.last_cooldown >= self.player.gun.freq:
            self.player.last_cooldown = 0
            bullet_direction = (mouse_pos[0]+self.visible_sprites.offset.x,mouse_pos[1]+self.visible_sprites.offset.y)
            self.mob_group.append(Mob((bullet_direction),[self.visible_sprites,self.obstacle_sprites],self.visible_sprites,self.obstacle_sprites,self.player,len(self.mob_group)))
            if len(self.mob_group) > 10: self.mob_group.pop(0)
            print(len(self.mob_group))
       
    def shooting_direction(self,offset,player_rect,mouse_pos):
        bullet_direction = (-player_rect.centerx+mouse_pos[0]+offset.x,-player_rect.centery+mouse_pos[1]+offset.y)
        return bullet_direction
    
    def debug_hitboxes(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_h] and self.debug_mode == False and self.cooldown_debug_hitbox == 0: 
            print('yes')
            self.debug_mode = True
            self.cooldown_debug_hitbox = 10
        if keys[pygame.K_h] and self.debug_mode == True and self.cooldown_debug_hitbox == 0: 
            print('yes')
            self.debug_mode = False
            self.cooldown_debug_hitbox = 10
    
    def cooldowns(self):
        if self.cooldown_debug_hitbox > 0: self.cooldown_debug_hitbox -= 1

    def run(self,screen):
        self.shoot()
        self.create_mob()
        self.visible_sprites.custom_draw(self.player,self.player_hands,screen,self.debug_mode)
        self.visible_sprites.update()
        self.visible_sprites.sprite_update(self.player)
        #self.visible_sprites.draw_hitbox(screen)
        debug(self.cooldowns)
        self.debug_hitboxes()
        self.cooldowns()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #self.floor_surf = pygame.image.load('../graphics/tilemap/map.png').convert()
        self.floor_chunks = chunk_loading('graphics/tilemap/chunks/')

    def custom_draw(self,player,player_hands,screen,debug_mode):
        self.offset.x = player.rect.centerx - self.half_width + (pygame.mouse.get_pos()[0] - self.half_width)/15
        self.offset.y = player.rect.centery - self.half_height + (pygame.mouse.get_pos()[1] - self.half_height)/15

        # Chunk based terrain display
        for i in [-2,-1,0,1,2]:
            for j in [-1,0,1]:
                try:
                    x = player.chunk_pos[0]+i
                    y = player.chunk_pos[1]+j

                    if (x <= N_CHUNKS and y <= N_CHUNKS) and (x >= 0 and y >= 0):
                        floor_chunks_rect = self.floor_chunks[x][y].get_rect(topleft = ((player.chunk_pos[0]+i)*TILESIZE*CHUNK_SIZE,(player.chunk_pos[1]+j)*TILESIZE*CHUNK_SIZE))
                        floor_offset_pos = floor_chunks_rect.topleft - self.offset
                        self.display_surface.blit(self.floor_chunks[x][y],floor_offset_pos)
                except:
                    pass
        
        player_hands.hand_movement(player, self.half_width,self.half_height)
        # Sprite display sorted by y axis
        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_position)

            # Hitboxes
            if debug_mode == True: self.draw_hitbox(sprite,screen)
        
        #player_hands.hand_movement(player, self.half_width,self.half_height)

    def sprite_update(self,player):
        all_sprites = [sprite for sprite in self.sprites()]
        for sprite in all_sprites:
            if sprite.sprite_type == 'mob': sprite.mob_update(player,self.offset)
    
    def draw_hitbox(self,sprite,screen):
        hitbox_rect = pygame.Rect(sprite.hitbox[0],sprite.hitbox[1],sprite.hitbox[2],sprite.hitbox[3])
        hitbox_rect.topleft -= self.offset
        if sprite.sprite_type == 'mob': pygame.draw.rect(screen,(255,75,75),hitbox_rect,3)
        if sprite.sprite_type == 'player': pygame.draw.rect(screen,(75,255,226),hitbox_rect,3)
        if sprite.sprite_type == 'bullet': pygame.draw.rect(screen,(160,75,255),hitbox_rect,3)
        #if sprite.sprite_type == 'hand': pygame.draw.rect(screen,(75,255,226),hitbox_rect,3)   # TO BE FIXED
