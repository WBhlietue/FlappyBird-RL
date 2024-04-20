import math
import random
import pygame
import sys
# import Training
import numpy as np 
import threading
import time
import logging
import Model as M

objectsList = []

pipes = []



class Vector2:
    def __init__(self, x = 0, y = 0) -> None:
        self.x = x
        self.y = y
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

class GameObject:

    def __init__(self) -> None:
        self.isInit = False
        self.position = Vector2(0, 0)
        self.size = Vector2(100, 100)
        self.color = (255, 255, 255)
        objectsList.append(self)
        self.Awake()

        pass   
    def Awake(self):
        pass
    def Start(self):
        self.isInit = True
        pass
    def Update(self, deltaTime, event):
        pass
    def Destroy(self):
        objectsList.remove(self)
        pass

class Pipe(GameObject):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        pipes.append(self)
        self.localPosition=  Vector2(0, 0)
        pass
    def Start(self):
        self.color = (0, 255, 0)
        self.size = Vector2(50, 500)
        super().Start()

class PipeSet(GameObject):
    def __init__(self):
        super().__init__()
        self.speed = 5.5
    def Start(self):
        self.size = Vector2(0, 0)
        self.color = (255, 255, 0)
        self.pipe1 = Pipe(self)
        self.pipe2 = Pipe(self)
        self.pipe1.Start()
        self.pipe2.Start()
        self.pipe1.localPosition = Vector2(0, 350)
        self.pipe2.localPosition = Vector2(0, -350)
        self.a = -100 + random.random() * 300
        self.SetPosition(800, self.a)
        self.counted = False
        super().Start()
    def SetPosition(self, x, y):
        self.position = Vector2(x, y)
        self.pipe1.position = self.pipe1.localPosition + self.position
        self.pipe2.position = self.pipe2.localPosition + self.position
    def Update(self, deltaTime, event):
        self.SetPosition(self.position.x-self.speed, self.position.y)
        if(self.counted == False and self.position.x < 100):
            AddScore()
            if(len(pipes) > 0):
                pipes.pop(0)
                pipes.pop(0)
            self.counted = True
        
class Player(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self.upSpeed = 10
        self.downSpeed = 10
        self.count = 0
        self.tar = 0.2
        self.isUp = False
        self.preDis = -1
    def Start(self):
        self.position = Vector2(100, 200)
        self.color = (255, 0, 0)
        self.size = Vector2(50, 50)
        super().Start()
        pass
    def Update(self, deltaTime, event):
        self.isUp = forceUp
        if(self.position.y < 0):
            self.position.y = 0
        if(self.isUp):
            self.position.y -= self.upSpeed
        else:
            self.position.y += self.downSpeed
        
        for i in pipes:
            # if(i.position.x-i.size.x/2 - self.size.x/2 < self.position.x and i.position.x-i.size.x/2 - self.size.x/2 > self.position.x and i.position.y-i.size.y/2 - self.size.y/2 < self.position.x and i.position.y+i.size.y/2 + self.size.y/2 > self.position.y):
            center = (i.position.x + i.size.x/2, i.position.y + i.size.y/2)
            thisCenter = (self.position.x+self.size.x/2, self.position.y + self.size.y/2)
            x1 = center[0] - i.size.x/2 - self.size.x/2 < thisCenter[0]
            x2 = center[0] + i.size.x/2 + self.size.x/2 > thisCenter[0]
            y1 = center[1] + i.size.y/2 + self.size.y/2 > thisCenter[1]
            y2 = center[1] - i.size.y/2 - self.size.y/2 < thisCenter[1]
            if( x1 and x2 and y1 and y2):
                Fail()  
        if(self.position.y >= 600):
            Fail()
        pass
    def CalculateReward(self):
        global playerPos
        global lineColor
        global targetPos
        add = 0
        x =pipes[0].position.x+pipes[0].size.x/2
        y = (pipes[0].position.y + pipes[1].position.y)/2
        thisCenter = (self.position.x+self.size.x/2, self.position.y + self.size.y/2)
        y += pipes[0].size.y/2
        playerPos = (thisCenter[0], thisCenter[1])
        dis = math.sqrt((thisCenter[0] - x)*(thisCenter[0] - x) + (thisCenter[1] - y)*(thisCenter[1] - y))
        if(targetPos[0] < x):
            self.preDis = dis
            add = 10
        targetPos = (x, y)
        if(self.preDis < 0):
            self.preDis = dis
            return 0
        # reward = 0

        reward  = (self.preDis - dis)/10
        if reward < 0:
            lineColor = (255, 0, 0)
        else :
            lineColor = (0, 0, 255)
        if(self.preDis > dis):
            self.preDis = dis
        # self.preDis = dis
        return reward + add
        
        

    
class PipeSpawn(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.target = 1.5
        self.size = Vector2(0, 0)
    def Start(self):
        return super().Start()
    def Update(self, deltaTime, event):
        self.count += deltaTime
        if(self.count >= self.target):
            self.count = 0
            PipeSet().Start()


random.seed(1000)
def AddScore():
    global score
    score += 1

def Restart():
    global score 
    global gaming 
    global objectsList
    global pipes
    global maxScore
    random.seed(1000)
    if(maxScore < score):
        maxScore = score
    score = 0
    gaming = True
    objectsList.clear()
    pipes.clear()
    Init()
    for i in objectsList:
        if(i.isInit):
            pass
        else:
            i.Start()


score = 0
maxScore = 0
gaming = True
pygame.init()
window_size = (800, 600)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Flappy Bird")
window.fill((255, 255, 255))
clock = pygame.time.Clock()
fps = 30
forceUp = False
timeInterval = 1 / fps
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
player = None
lineColor = (0, 0, 0)
def Init():
    global player
    spawn = PipeSpawn()
    player = Player()
    pipe = PipeSet()
    pipe.Start()
    pipe.SetPosition(pipe.position.x- 2*(pipe.speed * spawn.target * fps), pipe.position.y)
    pipe = PipeSet()
    pipe.Start()
    pipe.SetPosition(pipe.position.x- (pipe.speed * spawn.target * fps), pipe.position.y)
    pipe = PipeSet()

    pass
def Fail():
    global gaming
    pipes.clear()
    gaming = False
    
  
Init()
for i in objectsList:
    if(i.isInit):
        pass
    else:
        i.Start()
def Render():
    window.fill((255, 200, 255))
    for i in objectsList:
        pygame.draw.rect(window, i.color, (i.position.x, i.position.y, i.size.x, i.size.y))
    pygame.draw.line(window, lineColor, playerPos, targetPos)


def GetDatas():
    global player
    global pipes
    playerPos = player.position
    pipe1 = pipes[0].position
    pipe2 = pipes[1].position
    pipe3 = pipes[2].position
    pipe4 = pipes[3].position
    value = 300
    return [ playerPos.x/value,
             playerPos.y/value, 
             pipe1.x/value, 
             pipe1.y/value, 
             pipe2.x/value, 
             pipe2.y/value, 
             pipe3.x/value, 
             pipe3.y/value, 
             pipe4.x/value, 
             pipe4.y/value]


modelEnd = False
modelUpdating = False

def Model():
    global forceUp
    global modelUpdating
    
    dqn = M.DQN(10, 2, fileName="", gamma=0.99, epsilon=1, batch_size=128, train=True, updateFreq=10)
    for i in range(100000):
        while( len(pipes) < 4):
            time.sleep(0.1)
        state = GetDatas()
        r = 0
        while(gaming):
            if modelEnd:
                return
            ac = dqn.ChooseAction(state)
            if (ac == 1):
                forceUp = True
            else:
                forceUp = False
            time.sleep(0.1)
            if(not gaming):
                dqn.Remember(state, ac, -10, nextState, gaming)
                break

            nextState = GetDatas()
            reward = 0
            if(gaming == False):
                reward = -100
            else:
                reward = player.CalculateReward()
                reward *= (score+1)
                # reward = score
            r += reward
            dqn.Remember(state, ac, reward, nextState, gaming)
            state = nextState
        dqn.Train()
        WriteReward(i, r, dqn.epsilon)
        Restart()
            

file = open("./reward.txt", "w")
file.write("")
file.close()

def WriteReward(num, reward, e):
    num = str(num)
    file = open("./reward.txt", "a")
    file.write(num + ", " + str(reward) + ", " + str(e) + ", " + str(score) +"\n")
    file.close()

playerPos = (0, 0)
targetPos = (0, 0)


thread = threading.Thread(target=Model)
thread.start()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            modelEnd = True
            pygame.quit()
            sys.exit()
        if(event.type == pygame.KEYDOWN):
            if(event.key == pygame.K_SPACE):
                forceUp = True
        if(event.type == pygame.KEYUP):
            if(event.key == pygame.K_SPACE):
                forceUp = False
        
    if gaming:
        for i in objectsList:
            if(i.isInit):
                i.Update(timeInterval, events)
    Render()
    
    # pygame.display.flip()
    text_surface = my_font.render(str(score) + " / " + str(maxScore), False, (0, 0, 0))
    window.blit(text_surface, (0,0))
    if(gaming == False):
        text_surface = my_font.render('You Fail', False, (0, 0, 0))
        window.blit(text_surface, (300,300))
        pygame.display.update()
        # pygame.time.wait(100)
        # while(modelUpdating): 
        #     pygame.time.wait(10)
        # Restart()
    pygame.display.update()
    clock.tick(fps)


