import pygame
import random
from paddle import Paddle
from ball import Ball

pygame.init()
pygame.mixer.init()

# Fonts
titleFont = pygame.font.Font("assets/Qualy Bold.ttf", 60)
creditsFont = pygame.font.Font("assets/CocoGoose.ttf", 30)

# SFX
# Add direct file name if its in CWD else add full path
pygame.mixer.music.load("assets/bg music.mp3")
trumpet = pygame.mixer.Sound('assets/trumpet sound effect.wav')

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
CYAN =(0,255,255)
MAGENTA = (255,0,255)
BLUE = (0,0,255)

size = (700, 600)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Air Hockey")
 
# Player paddles
paddleA = Paddle(CYAN, 10, 100)
paddleA.rect.x = 20
paddleA.rect.y = 200
 
paddleB = Paddle(MAGENTA, 10, 100)
paddleB.rect.x = 670
paddleB.rect.y = 200
 
# Ball
ball = Ball(WHITE,10,10)
ball.rect.x = 345
ball.rect.y = 195
 
#This will be a list that will contain all the sprites we intend to use
all_sprites_list = pygame.sprite.Group()
 
all_sprites_list.add(paddleA)
all_sprites_list.add(paddleB)
all_sprites_list.add(ball)
 
carryOn = True
 
clock = pygame.time.Clock()
 
scoreA = 0
scoreB = 0

# Start playing the music
pygame.mixer.music.play()

# --- Functions for Confetti Effect of particles
particles = []
def starting_point():
	" to make a flame like particles [150, 20] # flame, so that all circles with start at the same point"
	return random.randint(0, 700)
 
def particles_generator():
 
    # Every particle starts at a random horizontal position at the top
    particles.append([
    	[starting_point(), 0],
    	[random.randint(0, 20) / 10 - 1, 2],
    	random.randint(4, 6)])
 
    # Every particle  moves... if particles[2] (the radius) is >= than 0 it is removed
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.005 # how fast circles shrinks
        particle[1][1] += 0.10 # circles speed
        if particle[2] <= 0:
            particles.remove(particle)
 
    # draws a circle on the screen of random color, at x y coords and with a ray of particle[2]
    for particle in particles:
        pygame.draw.circle(
        	screen,
        	random_color(),
        	(
        		round(particle[0][0]),
        		round(particle[0][1])),
        		round(particle[2]))
 
while carryOn:

    # --- Main event loop
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            carryOn = False # Flag that we are done so we exit this loop
        elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_x: #Pressing the x Key will quit the game
                    carryOn=False
 
    # --- Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B) 
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        paddleA.moveUp(10)
    if keys[pygame.K_s]:
        paddleA.moveDown(10)
    if keys[pygame.K_UP]:
        paddleB.moveUp(10)
    if keys[pygame.K_DOWN]:
        paddleB.moveDown(10)    
 
    # --- Game logic should go here
    all_sprites_list.update()
    
    # --- Check if the ball is bouncing against any of the 4 walls:
    if ball.rect.x>=690:
        scoreA+=1

        # --- Confetti
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(trumpet)
        for _ in range(150):
            screen.fill(BLACK)
            particles_generator()
            text = titleFont.render("PLAYER 1 SCORES!", 1, WHITE)
            text_rect = text.get_rect(center=(350, 300))
            screen.blit(text, text_rect)
            clock.tick(60)
            pygame.display.flip()
        pygame.mixer.music.unpause()

        particles = []
        ball.velocity = [random.randint(4,8),random.randint(-8,8)]
        ball.rect.x = 345
        ball.rect.y = 195 

    if ball.rect.x<=0:
        scoreB+=1

        # --- Confetti
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(trumpet)
        for _ in range(150):
            screen.fill(BLACK)
            particles_generator()
            text = titleFont.render("PLAYER 2 SCORES!", 1, WHITE)
            text_rect = text.get_rect(center=(350, 300))
            screen.blit(text, text_rect)
            clock.tick(60)
            pygame.display.flip()
        pygame.mixer.music.unpause()

        particles = []
        ball.velocity = [random.randint(4,8),random.randint(-8,8)]
        ball.rect.x = 345
        ball.rect.y = 195 

    if ball.rect.y>490:
        ball.velocity[1] = -ball.velocity[1] #Reverse the ball velocity in the y axis

    if ball.rect.y<0:
        ball.velocity[1] = -ball.velocity[1] #Reverse the ball velocity in the y axis
 
    # --- Detect collisions between the ball and the paddles
    if pygame.sprite.collide_mask(ball, paddleA) or pygame.sprite.collide_mask(ball, paddleB):
        ball.bounce()
    
    # --- Drawing code should go here
    # First, clear the screen to black. 
    screen.fill(BLACK)
    
    pygame.draw.line(screen, WHITE, [349, 0], [349, 500], 5)
    pygame.draw.line(screen, WHITE, [0,500], [700,500], 5)
    text = titleFont.render("AIR HOCKEY", 1, WHITE)
    text_rect = text.get_rect(center=(355, 550))
    screen.blit(text, text_rect)

    all_sprites_list.draw(screen) 
 
    #Display scores:
    text = titleFont.render(str(scoreA), 1, WHITE)
    screen.blit(text, (250,10))
    text = titleFont.render(str(scoreB), 1, WHITE)
    screen.blit(text, (420,10))

    # --- Update the screen
    pygame.display.flip()
     
    # --- Limit to 60 frames per second.
    clock.tick(60)

pygame.quit()
