import pygame
import random
import math

WINDOW_SIZE = (600,600)

zoom = 1.1
difficulty = 0 # min 0, max 4

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption("Shay's Breaker Game")

# 20-ish levels? Player at level 0.
# Every block is 1 level high by 1 level height's wide.
bricks = []
wave = 1
score = 0

keys = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm"
]

for n in range(len(keys)):
    keys[n] = [char for char in keys[n]]

limits = (5000-max(0,min(difficulty,4))*1000,60000)
countdowns = [[random.randrange(limits[0],limits[1]) for col in range(len(keys[row]))] for row in range(len(keys))]
# countdowns = [[limits[0]+(col+row)*1 for col in range(len(keys[row]))] for row in range(len(keys))] # DEBUG LINE

size = (int(30*zoom),int(30*zoom))

def getPos(x, y):
    return [2*zoom+size[0]*x + y*size[0]*2/5,2*zoom+size[1]*y]

def keyboardBounds():
    width, height = 0, getPos(0,len(keys)+1)[1]
    for row in range(len(keys)):
        _w = getPos(len(keys[row])+1, row)[0]
        if _w > width:
            width = _w
    return((0, 0), (width, height))

def getKeyboard():
    ret = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    font = pygame.font.SysFont(None, size[1]-10)
    for y in range(len(keys)):
        for x in range(len(keys[y])):
            pos = getPos(x, y)
            fontPos = [pos[0] + size[0]/4, pos[1]+size[1]/4]
            pygame.draw.rect(ret, (255,255,255), (pos,size), 1)
            img = font.render(keys[y][x], True, (255,255,255))
            ret.blit(img, fontPos)
    return ret
    # Max = 151x44

def getFillLimits():
    ret = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    for y in range(len(countdowns)):
        for x in range(len(countdowns[y])):
            if countdowns[y][x] < limits[0]:
                c = max(countdowns[y][x], 0)
                color = (int(math.floor(255*(limits[0] - c)/limits[0])), int(math.floor(255*(c)/limits[0])), 0)
                pos = getPos(x, y)
                pos = [int(math.floor(pos[0] + size[0]/2)),int(math.floor(pos[1] + size[1]/2))]
                r = int(math.floor(size[0]/2*(limits[0] - c)/limits[0]))
                pygame.draw.circle(ret, color, pos, r)
    return ret


misses = [] # [[character, [targets]], [character, ...
def getMissBoard():
    cap = 15
    spaces = 6
    _buff = 2*zoom
    while len(misses) > cap:
        misses.pop()
    ret = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    bounds = [(keyboardBounds()[1][0], 0), (size[0]*spaces+(spaces-1)*_buff, size[1]*cap+(spaces-1)*_buff)]
    pygame.draw.rect(ret, (255,255,255), bounds, 1)
    if len(misses) == 0:
        return ret

    font = pygame.font.SysFont(None, size[1]-10)
    for i in range(len(misses)):
        x, y = bounds[0][0], (size[1] + _buff) * i
        miss = misses[i]
        char = miss[0]
        targets = miss[1]

        pygame.draw.rect(ret, (255,0,0), ((x,y),size), 1)
        img = font.render(char, True, (255,0,0))
        fontPos = [x + size[0]/4, y+size[1]/4]
        ret.blit(img, fontPos)

        for n in range(min(len(targets), spaces-1)):
            x += size[0] + _buff
            pygame.draw.rect(ret, (255,255,255), ((x,y), size), 1)
            img = font.render(targets[n], True, (255,255,255))
            fontPos = [x + size[0]/4, y+size[1]/4]
            ret.blit(img, fontPos)


    return ret
            


running = True

base = getKeyboard()

lastTick = pygame.time.get_ticks()

while running:
    reduction = pygame.time.get_ticks() - lastTick
    lastTick = pygame.time.get_ticks()
    lowest = limits[1]
    targets = []
    for y in range(len(countdowns)):
        for x in range(len(countdowns[y])):
            countdowns[y][x] -= reduction
            if countdowns[y][x] < limits[0]:
                targets.append(keys[y][x])
            if countdowns[y][x] < lowest:
                lowest = countdowns[y][x]
    
    if lowest > limits[0]:
        reduction = lowest - limits[0]
        for y in range(len(countdowns)):
            for x in range(len(countdowns[y])):
                countdowns[y][x] -= reduction
                if countdowns[y][x] < limits[0]:
                    targets.append(keys[y][x])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # if keystroke is pressed check whether its right or left
        if event.type == pygame.KEYDOWN:
            for row in range(len(keys)):
                for char in range(len(keys[row])):
                    if event.key == ord(keys[row][char]):
                        if countdowns[row][char] < limits[0]:
                            countdowns[row][char] += limits[1]
                        else:
                            misses.insert(0, [keys[row][char], targets])

    temp = pygame.Surface(WINDOW_SIZE)
    temp.fill((0,0,0))

    temp.blit(getFillLimits(), [0,0])
    temp.blit(base, [0,0])
    temp.blit(getMissBoard(), [0,0])

    screen.blit(temp, (0,0))
    pygame.display.update()
    clock.tick(60)