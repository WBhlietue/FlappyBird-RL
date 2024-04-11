import pygame
import time
import threading
import random
import Model

# 初始化pygame
pygame.init()

# 设置游戏窗口大小
window_x = 720
window_y = 480

# 定义颜色
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# 初始化游戏窗口
pygame.display.set_caption('贪吃蛇')
game_window = pygame.display.set_mode((window_x, window_y))

# FPS (帧率) 控制器
fps = pygame.time.Clock()

# 蛇的初始位置

score = 0

# 显示得分的函数
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)


# 游戏结束时的函数
def game_over():
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x/2, window_y/4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    Main()

def Train():
    model = Model.DQN()
    pass 


def Main():
    global score
    snake_position = [100, 50]
    # 蛇的初始长度（一条长度为4的蛇）
    snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]]

    # 食物的随机初始位置
    fruit_position = [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]
    fruit_spawn = True

    # 初始方向
    direction = 'RIGHT'
    change_to = direction

    # 初始得分
    score = 0

# 主循环
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_to = 'UP'
                if event.key == pygame.K_DOWN:
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT:
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT:
                    change_to = 'RIGHT'

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'
        
        if direction == 'UP':
            snake_position[1] -= 10
        if direction == 'DOWN':
            snake_position[1] += 10
        if direction == 'LEFT':
            snake_position[0] -= 10
        if direction == 'RIGHT':
            snake_position[0] += 10
        
        # 蛇体增长机制
        snake_body.insert(0, list(snake_position))
        if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
            score += 10
            fruit_spawn = False
        else:
            snake_body.pop()
        
        if not fruit_spawn:
            fruit_position = [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]
        fruit_spawn = True
        
        game_window.fill(black)
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
        
        pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))
        
        # 当蛇撞到墙或自己时游戏结束
        if snake_position[0] < 0 or snake_position[0] > window_x-10:
            game_over()
        if snake_position[1] < 0 or snake_position[1] > window_y-10:
            game_over()
        for block in snake_body[1:]:
            if snake_position[0] == block[0] and snake_position[1] == block[1]:
                game_over()
        
        show_score(1, white, 'times new roman', 20)
        
        pygame.display.update()
        
        fps.tick(25)



t1 = threading.Thread(target=Train)
t1.start()

Main()
