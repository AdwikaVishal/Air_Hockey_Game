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
pygame.mixer.music.load("assets/bg music.mp3")
trumpet = pygame.mixer.Sound('assets/trumpet sound effect.wav')

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)

size = (700, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Air Hockey")

# Paddles
paddleA = Paddle(CYAN, 10, 100)
paddleA.rect.x = 20
paddleA.rect.y = 200

paddleB = Paddle(MAGENTA, 10, 100)
paddleB.rect.x = 670
paddleB.rect.y = 200

# Ball
ball = Ball(WHITE, 10, 10)
ball.rect.x = 345
ball.rect.y = 195

# Sprite Group
all_sprites_list = pygame.sprite.Group()
all_sprites_list.add(paddleA)
all_sprites_list.add(paddleB)
all_sprites_list.add(ball)

# Game Flags
carryOn = True
clock = pygame.time.Clock()
scoreA = 0
scoreB = 0
paused = False
game_over = False

# Confetti
particles = []
def starting_point():
    return random.randint(0, 700)

def particles_generator():
    particles.append([[starting_point(), 0], [random.uniform(-1, 1), 2], random.randint(4, 6)])
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.005
        particle[1][1] += 0.10
        if particle[2] <= 0:
            particles.remove(particle)
    for particle in particles:
        pygame.draw.circle(screen, random_color(), (round(particle[0][0]), round(particle[0][1])), round(particle[2]))

# Reset Game Function
def reset_game():
    global scoreA, scoreB, game_over
    scoreA = 0
    scoreB = 0
    paddleA.rect.y = 200
    paddleB.rect.y = 200
    ball.reset(345, 195)
    game_over = False
    pygame.mixer.music.play(-1)

# Goal settings
goal_top = 250
goal_bottom = 350

# Start music
pygame.mixer.music.play(-1)

while carryOn:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            carryOn = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                carryOn = False
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r and game_over:
                reset_game()

    if not paused and not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: paddleA.moveUp(10)
        if keys[pygame.K_s]: paddleA.moveDown(10)
        if keys[pygame.K_UP]: paddleB.moveUp(10)
        if keys[pygame.K_DOWN]: paddleB.moveDown(10)

        all_sprites_list.update()

        # GOAL: Player A scores if ball enters right goal
        if ball.rect.x >= 690:
            if goal_top <= ball.rect.y <= goal_bottom:
                scoreA += 1
                pygame.mixer.music.pause()
                pygame.mixer.Sound.play(trumpet)
                for _ in range(150):
                    screen.fill(BLACK)
                    particles_generator()
                    text = titleFont.render("PLAYER 1 SCORES!", 1, WHITE)
                    screen.blit(text, text.get_rect(center=(350, 300)))
                    clock.tick(60)
                    pygame.display.flip()
                pygame.mixer.music.unpause()
                particles.clear()
                ball.reset(345, 195)
                ball.velocity[0] = int(ball.velocity[0] * 1.1)
                ball.velocity[1] = int(ball.velocity[1] * 1.1)
                ball.velocity[0] = max(-15, min(15, ball.velocity[0]))
                ball.velocity[1] = max(-15, min(15, ball.velocity[1]))
            else:
                # Bounce if hit side wall outside goal
                ball.rect.x = 689
                ball.velocity[0] = -ball.velocity[0]

        # GOAL: Player B scores if ball enters left goal
        if ball.rect.x <= 0:
            if goal_top <= ball.rect.y <= goal_bottom:
                scoreB += 1
                pygame.mixer.music.pause()
                pygame.mixer.Sound.play(trumpet)
                for _ in range(150):
                    screen.fill(BLACK)
                    particles_generator()
                    text = titleFont.render("PLAYER 2 SCORES!", 1, WHITE)
                    screen.blit(text, text.get_rect(center=(350, 300)))
                    clock.tick(60)
                    pygame.display.flip()
                pygame.mixer.music.unpause()
                particles.clear()
                ball.reset(345, 195)
                ball.velocity[0] = int(ball.velocity[0] * 1.1)
                ball.velocity[1] = int(ball.velocity[1] * 1.1)
                ball.velocity[0] = max(-15, min(15, ball.velocity[0]))
                ball.velocity[1] = max(-15, min(15, ball.velocity[1]))
            else:
                # Bounce if hit side wall outside goal
                ball.rect.x = 1
                ball.velocity[0] = -ball.velocity[0]

        # Bounce from top/bottom
        if ball.rect.y > 490 or ball.rect.y < 0:
            ball.velocity[1] = -ball.velocity[1]

        # Paddle collision
        if pygame.sprite.collide_mask(ball, paddleA) or pygame.sprite.collide_mask(ball, paddleB):
            ball.bounce()

        # Game Over Check
        if scoreA >= 10 or scoreB >= 10:
            game_over = True
            pygame.mixer.music.stop()

    screen.fill(BLACK)

    pygame.draw.rect(screen, WHITE, pygame.Rect(0, goal_top, 5, goal_bottom - goal_top))
    pygame.draw.rect(screen, WHITE, pygame.Rect(695, goal_top, 5, goal_bottom - goal_top))

    pygame.draw.line(screen, WHITE, [349, 0], [349, 500], 5)
    pygame.draw.line(screen, WHITE, [0, 500], [700, 500], 5)

    title_text = titleFont.render("AIR HOCKEY", 1, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(355, 550)))

    all_sprites_list.draw(screen)

    if not game_over:
        score_text_A = titleFont.render(str(scoreA), 1, WHITE)
        screen.blit(score_text_A, (250, 10))
        score_text_B = titleFont.render(str(scoreB), 1, WHITE)
        screen.blit(score_text_B, (420, 10))
    else:
        winner = "PLAYER 1 WINS!" if scoreA >= 10 else "PLAYER 2 WINS!"
        win_text = titleFont.render(winner, 1, WHITE)
        screen.blit(win_text, win_text.get_rect(center=(350, 250)))

        reset_text = creditsFont.render("Press R to Restart or X to Quit", 1, WHITE)
        screen.blit(reset_text, reset_text.get_rect(center=(350, 320)))

    if paused and not game_over:
        pause_text = titleFont.render("GAME PAUSED", 1, WHITE)
        screen.blit(pause_text, pause_text.get_rect(center=(350, 300)))

    pygame.display.flip()
    clock.tick(80)

pygame.quit()
