import pygame

BLACK = (0, 0, 0)
SCREEN_HEIGHT = 500
PADDLE_HEIGHT = 100

class Paddle(pygame.sprite.Sprite):
    
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
 
        pygame.draw.rect(self.image, color, [0, 0, width, height], border_radius=10)
        
        self.rect = self.image.get_rect()
        
    def moveTo(self, y):
        # Move paddle center to y position, clamped inside screen height
        new_y = y - self.rect.height // 2
        if new_y < 0:
            new_y = 0
        elif new_y > SCREEN_HEIGHT - self.rect.height:
            new_y = SCREEN_HEIGHT - self.rect.height
        self.rect.y = new_y
         
    def moveUp(self, pixels):
        self.rect.y -= pixels
        if self.rect.y < 0:
            self.rect.y = 0
          
    def moveDown(self, pixels):
        self.rect.y += pixels
        max_y = SCREEN_HEIGHT - PADDLE_HEIGHT
        if self.rect.y > max_y:
            self.rect.y = max_y
