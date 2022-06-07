import pygame
from debug import debug

class Bullet(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites,bullet_direction,speed):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/player/bullet_off.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(32, 32))
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10,-10)

        self.sprite_type = 'bullet'

        self.direction = pygame.math.Vector2()
        self.bullet_direction = bullet_direction
        self.speed = speed
        self.living_time = 0

        self.death = False
        self.death_time = 2

        self.obstacle_sprites = obstacle_sprites
    
    def move(self):
        self.direction.x = self.bullet_direction[0]
        self.direction.y = self.bullet_direction[1]

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * self.speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center
       
    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving left
                        self.hitbox.left = sprite.hitbox.right
                    if sprite.sprite_type == 'mob' and self.death == False: 
                        self.death = True
                    
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    if sprite.sprite_type == 'mob' and self.death == False: 
                        self.death = True
    
    def change_image(self):
        if self.living_time >= 2: 
            self.image = pygame.image.load('../graphics/player/bullet_on.png').convert_alpha()
            self.image = pygame.transform.scale(self.image,(32, 32))
        if self.death == True:
            self.image = pygame.image.load('../graphics/player/bullet_off.png').convert_alpha()
            self.image = pygame.transform.scale(self.image,(32, 32))


    def destroy(self):
        if self.living_time >= 100: self.kill()
        self.living_time += 1
        if self.death == True: self.death_time -= 1
        if self.death_time <= 0: self.kill()

    def update(self):
        self.move()
        self.change_image()
        self.destroy()