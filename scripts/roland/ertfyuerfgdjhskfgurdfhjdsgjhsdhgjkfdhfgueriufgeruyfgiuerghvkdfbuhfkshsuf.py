import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы экрана
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пинг-Понг на Python")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Параметры игры
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 15
FPS = 60

# Скорости
PADDLE_SPEED = 7
BALL_SPEED_X = 4
BALL_SPEED_Y = 4

# Создание объектов
# Левая ракетка
left_paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
# Правая ракетка
right_paddle = pygame.Rect(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
# Мяч
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Направление движения
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# Счет
left_score = 0
right_score = 0
font = pygame.font.Font(None, 74)

clock = pygame.time.Clock()

def reset_ball():
    global ball_dx, ball_dy
    ball.x = WIDTH // 2 - BALL_SIZE // 2
    ball.y = HEIGHT // 2 - BALL_SIZE // 2
    ball_dx *= -1  # Меняем направление при голе

# Основной цикл игры
running = True
while running:
    SCREEN.fill(BLACK)

    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Управление ракетками
    keys = pygame.key.get_pressed()
    
    # Левая ракетка (клавиши W и S)
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED

    # Правая ракетка (стрелки Вверх и Вниз)
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED

    # 3. Движение мяча
    ball.x += ball_dx
    ball.y += ball_dy

    # 4. Столкновения с границами (верх/низ)
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1

    # 5. Столкновения с ракетками
    if ball.colliderect(left_paddle):
        ball_dx *= -1
        ball.x = left_paddle.right + 1 # Чтобы мяч не "залип" в ракетке
    
    if ball.colliderect(right_paddle):
        ball_dx *= -1
        ball.x = right_paddle.left - BALL_SIZE - 1

    # 6. Определение голов
    if ball.left <= 0:
        right_score += 1
        reset_ball()
    
    if ball.right >= WIDTH:
        left_score += 1
        reset_ball()

    # 7. Отрисовка объектов
    pygame.draw.rect(SCREEN, WHITE, left_paddle)
    pygame.draw.rect(SCREEN, WHITE, right_paddle)
    pygame.draw.ellipse(SCREEN, WHITE, ball)
    pygame.draw.aaline(SCREEN, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)

    # Отображение счета
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    SCREEN.blit(left_text, (WIDTH // 4, 20))
    SCREEN.blit(right_text, (WIDTH * 3 // 4, 20))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
