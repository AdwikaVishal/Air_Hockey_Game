import pygame
from random import randint, choice

BLACK = (0, 0, 0)

class Ball(pygame.sprite.Sprite):
    
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
 
        pygame.draw.rect(self.image, color, [0, 0, width, height], border_radius=20)
        
        self.velocity = [randint(4, 8) * choice([-1, 1]), randint(-8, 8)]
        while self.velocity[1] == 0:
            self.velocity[1] = randint(-8, 8)
        
        self.rect = self.image.get_rect()
        
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
          
    def bounce(self):
        self.velocity[0] = -self.velocity[0]
        delta = randint(-2, 2)
        self.velocity[1] += delta
        if self.velocity[1] > 8:
            self.velocity[1] = 8
        elif self.velocity[1] < -8:
            self.velocity[1] = -8

    def reset(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.velocity = [randint(4, 8) * choice([-1, 1]), randint(-8, 8)]
        while self.velocity[1] == 0:
            self.velocity[1] = randint(-8, 8)
