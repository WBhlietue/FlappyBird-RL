import random
import pygame
import Model as M
import math

board = [[0 for x in range(11)] for y in range(11)]

pygame.init()
screen = pygame.display.set_mode((500, 500))
foodPos = [0, 0]
dir = "a"
dqn = M.DQN(11*11+1, 4, fileName="", gamma=0.99, epsilon=1, batch_size=128, train=True, updateFreq=10, saveName="snakeTrain.txt", name="snake")
r = 0
num = 0
def GetBoard(hp):
    b = []
    for i in board:
        for j in i:
            b.append(j)
    b.append(hp)
    return b

class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parts = []
        self.hp = 100
    def Move(self):
        global board
        global r
        state = GetBoard(self.hp)
        preDis = math.sqrt((self.x - foodPos[0])**2 + (self.y - foodPos[1])**2)
        if(len(self.parts) == 0):
            board[self.x][self.y] = 0
        for i in range(len(self.parts)-1, -1, -1):
            self.parts[i].Move(i == len(self.parts)-1)
        a = dqn.ChooseAction(state)
        done = False
        if(a == 0):
            dir = "w"
        elif(a == 1):
            dir = "s"
        elif(a == 2):
            dir = "a"
        elif(a == 3):
            dir = "d"
        if dir == "w":
            self.y -= 1
        elif dir == "s":
            self.y += 1
        elif dir == "a":
            self.x -= 1
        elif dir == "d":
            self.x += 1
        self.hp -= 1
        # print(self.hp)
        if(self.x < 0 or self.x > 10 or self.y < 0 or self.y > 10 or board[self.x][self.y] == 1 or self.hp == 0):
            nextState = GetBoard(self.hp)
            reward = -10
            done= True
            r += reward
            dqn.Remember(state, a, reward, nextState, done)
            GameOver()
            return
        else:
            if(board[self.x][self.y] == 2):
                SpawnFood()
                self.hp  =100
                reward = 10
                self.AddPart()
            else:
                dis = math.sqrt((self.x - foodPos[0])**2 + (self.y - foodPos[1])**2)
                reward = preDis - dis
            board[self.x][self.y] = 3
        nextState = GetBoard(self.hp)
        r += reward
        dqn.Remember(state, a, reward, nextState, done)

    def AddPart(self):
        part = self
        if(len(self.parts) != 0):
            part =  self.parts[-1]
        next = SnakePart(part.x, part.y, part)
        self.parts.append(next)

def GameOver():
    global inGaming
    global num
    global r
    inGaming = False
    num += 1
    file = open("snake.txt", "a")

    file.write(str(num) + "," + str(r) + "," + str(dqn.epsilon) + "\n")
    r = 0
    dqn.Train()
    Restart()
    return

def Restart():
    global snake
    global board
    global foodPos
    global inGaming
    global dir

    dir = "a"
    board = [[0 for x in range(11)] for y in range(11)]
    snake = Snake(5, 5)
    SpawnFood()
    inGaming = True

class SnakePart:

    def __init__(self, x, y, pre):
        self.x = x
        self.y = y
        self.pre = pre
    def Move(self, remove = False):
        if(remove):
            board[self.x][self.y] = 0
        self.x = self.pre.x
        self.y = self.pre.y
        board[self.x][self.y] = 1
    
def SpawnFood():
    global board
    global foodPos
    while True:
        x = random.randint(0, 10)
        y = random.randint(0, 10)
        if board[x][y] == 0:
            foodPos = [x, y]
            board[x][y] = 2
            return

snake = Snake(10, 10)
SpawnFood()
inGaming = True

def ChangeDir(key):
    global dir
    if key == pygame.K_w and dir != "s":
        dir = "a"
    elif key == pygame.K_s and dir != "a":
        dir = "d"
    elif key == pygame.K_a and dir != "s":
        dir = "w"
    elif key == pygame.K_d and dir != "w":
        dir = "s"

def Move():
    snake.Move()
    return

def Render():
    val = 40
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                pygame.draw.rect(screen, (255, 255, 255), (10+j*val, 10+i*val, val, val))
            elif board[i][j] == 1:
                pygame.draw.rect(screen, (0, 0, 255), (10+j*val, 10+i*val, val, val))
            elif board[i][j] == 2:
                pygame.draw.rect(screen, (255, 0, 0), (10+j*val, 10+i*val, val, val))
            elif board[i][j] == 3:
                pygame.draw.rect(screen, (0, 255, 0), (10+j*val, 10+i*val, val, val))
    pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            ChangeDir(event.key)
    if(inGaming):
        Move()
        Render()
    pygame.time.wait(1)
