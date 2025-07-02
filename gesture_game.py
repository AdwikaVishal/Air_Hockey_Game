import pygame
import random
import cv2
from paddle import Paddle
from ball import Ball
from gesture_tracker import HandTracker

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 600
GOAL_TOP = 250
GOAL_BOTTOM = 350
MAX_SCORE = 10
PADDLE_SPEED = 0.3  # lerp speed for smooth paddle movement
BALL_MAX_SPEED = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Fonts & assets
pygame.init()
pygame.mixer.init()
titleFont = pygame.font.Font("assets/Qualy Bold.ttf", 60)
creditsFont = pygame.font.Font("assets/CocoGoose.ttf", 30)

pygame.mixer.music.load("assets/bg music.mp3")
trumpet = pygame.mixer.Sound('assets/trumpet sound effect.wav')

# --- INITIALIZATION ---

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Air Hockey")

# Sprites
paddleA = Paddle(CYAN, 10, 100)
paddleA.rect.x = 20
paddleA.rect.y = 200

paddleB = Paddle(MAGENTA, 10, 100)
paddleB.rect.x = SCREEN_WIDTH - 30
paddleB.rect.y = 200

ball = Ball(WHITE, 10, 10)
ball.rect.x = SCREEN_WIDTH // 2 - 5
ball.rect.y = SCREEN_HEIGHT // 2 - 5

all_sprites = pygame.sprite.Group(paddleA, paddleB, ball)

# Hand Tracker
cap = cv2.VideoCapture(0)
hand_tracker = HandTracker(smoothing=0.3)

clock = pygame.time.Clock()

scoreA, scoreB = 0, 0
paused = False
game_over = False

# For countdown after goal
goal_scored_time = None
GOAL_DELAY_MS = 2000  

# Particle confetti (optional)
particles = []

def particles_generator():
    import random
    particles.append([[random.randint(0, SCREEN_WIDTH), 0], [random.uniform(-1, 1), 2], random.randint(4, 6)])
    for particle in particles[:]:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.05
        particle[1][1] += 0.1
        if particle[2] <= 0:
            particles.remove(particle)
    for particle in particles:
        pygame.draw.circle(screen, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                           (round(particle[0][0]), round(particle[0][1])), round(particle[2]))


def reset_ball():
    ball.reset(SCREEN_WIDTH // 2 - 5, SCREEN_HEIGHT // 2 - 5)

def lerp(a, b, f):
    return a + f * (b - a)

def move_paddle_smoothly(paddle, target_y):
    current_y = paddle.rect.y + paddle.rect.height / 2
    new_y = lerp(current_y, target_y, PADDLE_SPEED)
    # Clamp within screen
    new_y = max(paddle.rect.height // 2, min(SCREEN_HEIGHT - paddle.rect.height // 2, new_y))
    paddle.moveTo(new_y)

def draw_text_center(text, font, color, surface, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(SCREEN_WIDTH//2, y))
    surface.blit(rendered, rect)


pygame.mixer.music.play(-1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                running = False
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r and game_over:
                scoreA, scoreB = 0, 0
                game_over = False
                reset_ball()
                pygame.mixer.music.play(-1)
                goal_scored_time = None
                particles.clear()

    ret, frame = cap.read()
    if not ret:
        print("Failed to get camera frame.")
        break

    wrists = hand_tracker.update(frame)
    left_wrist = wrists["Left"]
    right_wrist = wrists["Right"]

    screen.fill(BLACK)

    # Draw goals
    pygame.draw.rect(screen, WHITE, pygame.Rect(0, GOAL_TOP, 5, GOAL_BOTTOM - GOAL_TOP))
    pygame.draw.rect(screen, WHITE, pygame.Rect(SCREEN_WIDTH - 5, GOAL_TOP, 5, GOAL_BOTTOM - GOAL_TOP))

    # Draw middle line and floor
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), 5)
    pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 5)

    # Game paused or over message
    if paused:
        draw_text_center("GAME PAUSED", titleFont, WHITE, screen, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_over:
        winner = "PLAYER 1 WINS!" if scoreA > scoreB else "PLAYER 2 WINS!"
        draw_text_center(winner, titleFont, WHITE, screen, SCREEN_HEIGHT // 2 - 30)
        draw_text_center("Press R to Restart or X to Quit", creditsFont, WHITE, screen, SCREEN_HEIGHT // 2 + 30)
        pygame.display.flip()
        clock.tick(60)
        continue

    # Control paddles by wrist positions smoothly
    frame_height = frame.shape[0]

    if left_wrist is not None:
        target_y = (left_wrist[1] / frame_height) * SCREEN_HEIGHT
        move_paddle_smoothly(paddleA, target_y)

    if right_wrist is not None:
        target_y = (right_wrist[1] / frame_height) * SCREEN_HEIGHT
        move_paddle_smoothly(paddleB, target_y)

    # Wait after a goal before moving ball again
    if goal_scored_time:
        elapsed = pygame.time.get_ticks() - goal_scored_time
        particles_generator()
        draw_text_center("GOAL!", titleFont, WHITE, screen, SCREEN_HEIGHT // 2)
        if elapsed >= GOAL_DELAY_MS:
            goal_scored_time = None
            reset_ball()
    else:
        # Update ball position and handle collisions
        ball.update()

        # Bounce off top and bottom
        if ball.rect.top <= 0 or ball.rect.bottom >= SCREEN_HEIGHT - 100:
            ball.velocity[1] = -ball.velocity[1]

        # Check paddle collisions
        if pygame.sprite.collide_mask(ball, paddleA) or pygame.sprite.collide_mask(ball, paddleB):
            ball.bounce()

        # Check goals
        # Player A scores (ball passes right goal)
        if ball.rect.right >= SCREEN_WIDTH:
            if GOAL_TOP <= ball.rect.centery <= GOAL_BOTTOM:
                scoreA += 1
                pygame.mixer.music.pause()
                trumpet.play()
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                goal_scored_time = pygame.time.get_ticks()
                particles.clear()
                particles_generator()
                # Increase ball speed by 10% capped
                ball.velocity[0] = max(-BALL_MAX_SPEED, min(BALL_MAX_SPEED, ball.velocity[0] * 1.1))
                ball.velocity[1] = max(-BALL_MAX_SPEED, min(BALL_MAX_SPEED, ball.velocity[1] * 1.1))
            else:
                # Bounce off wall outside goal
                ball.rect.right = SCREEN_WIDTH - 1
                ball.velocity[0] = -ball.velocity[0]

        # Player B scores (ball passes left goal)
        if ball.rect.left <= 0:
            if GOAL_TOP <= ball.rect.centery <= GOAL_BOTTOM:
                scoreB += 1
                pygame.mixer.music.pause()
                trumpet.play()
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                goal_scored_time = pygame.time.get_ticks()
                particles.clear()
                particles_generator()
                ball.velocity[0] = max(-BALL_MAX_SPEED, min(BALL_MAX_SPEED, ball.velocity[0] * 1.1))
                ball.velocity[1] = max(-BALL_MAX_SPEED, min(BALL_MAX_SPEED, ball.velocity[1] * 1.1))
            else:
                ball.rect.left = 1
                ball.velocity[0] = -ball.velocity[0]

        # Check game over
        if scoreA >= MAX_SCORE or scoreB >= MAX_SCORE:
            game_over = True
            pygame.mixer.music.stop()

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw scores
    score_text_A = titleFont.render(str(scoreA), True, WHITE)
    score_text_B = titleFont.render(str(scoreB), True, WHITE)
    screen.blit(score_text_A, (SCREEN_WIDTH // 2 - 100, 10))
    screen.blit(score_text_B, (SCREEN_WIDTH // 2 + 60, 10))

    pygame.display.flip()
    clock.tick(100)

cap.release()
pygame.quit()
