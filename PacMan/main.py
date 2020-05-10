import os

import pygame, random, sys
from pygame.locals import *
import math
import glob
import time
import neat

# Set FPS
FPS = 30

gen = 0

# Window Dimensions
WINDOWWIDTH = 638
WINDOWHEIGHT = 825
WALL_THICKNESS = 10
PLAYER_SIZE = 30
TREAT_SIZE = 10
PLAYER_VEL = 10
ENEMY_VEL = 5
ENEMY_IND = 31
PORTAL1_IND = 32
PORTAL2_IND = 37
WALL_CHECK_OFFSET = 200
# Colors
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Key Constants
UP = 'up'
DOWN = 'down'
RIGHT = 'right'
LEFT = 'left'
wallList = []
treatList = []
portalList = []
cornerList = []
enemyList = []

pygame.font.init()
STAT_FONT = pygame.font.SysFont("roboto", 30)

WINDOW = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Lembalo')

tileMap = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
W                        W                        W
W T        T         T   W  T         T        T  W
W                        W                        W
W                        W                        W
W    WWWWW    WWWWWW     W     WWWWWW    WWWWW    W
W    W   W                               W   W    W
W    WWWWW T    T    T      T    T    T  WWWWW    W
W                                                 W
W T        T    T                T    T        T  W
W                   WWWWWWWWWWW                   W
W                        W                        W
W    WWWWW    W T    T   W  T    T  W    WWWWW    W
W             W          W          W             W
W T        T  W          W          W T        T  W
W             WWWWW      W      WWWWW             W
W             W                     W             W
WWWWWWWWWW    W T    T   T  T    T  W    WWWWWWWWWW
W        W    W                     W    W        W
W        W    W                     W    W        W
W        W         WWWW  T  WWWW         W        W
WWWWWWWWWW         W           W         WWWWWWWWWW
X                  W           W                  X
XT         T    T  W           W T    T          TX
X                  W           W                  X
X                  W           W                  X
WWWWWWWWWW         W           W         WWWWWWWWWW
W        W         WWWWWWWWWWWWW         W        W
W        W    W                     W    W        W
W        W    W T    T      T    T  W    W        W
WWWWWWWWWW    W                     W    WWWWWWWWWW
W             W                     W             W
W T        T  WWWWW      W      WWWWW T        T  W
W             W          W          W             W
W             W T    T   W  T    T  W             W
W    WWWWW    W          W          W    WWWWW    W
W             W          W          W             W
W T        T    T   WWWWWWWWWWW  T    T        T  W
W                                                 W
W          T    T    T      T    T    T           W
W    WWWWW                               WWWWW    W
W    W   W                               W   W    W
W    WWWWW    WWWWWW     W     WWWWWW    WWWWW    W
W                        W                        W
W T        T         T   W  T         T        T  W
W                        W                        W
W                        W                        W
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"""
tileMap = tileMap.splitlines()


def checkWallVertical(sameX, belowY, aboveY):
    for wall in wallList:
        if belowY > wall.y > aboveY:
            if wall.x == sameX:
                return True
            elif sameX - 12.5 < wall.x < sameX + PLAYER_SIZE:
                return True
    return False


def checkWallHorizontal(sameY, leftX, rightX):
    for wall in wallList:
        if rightX > wall.x > leftX:
            if wall.y == sameY:
                return True
            elif sameY - WALL_THICKNESS < wall.y < sameY + PLAYER_SIZE:
                return True
    return False


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y, targetInd, genomeNum):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set Properties
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLUE)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.genomeNum = genomeNum
        self.x = x
        self.y = y
        self.targetX = x
        self.targetY = y
        self.vx = 0
        self.index = targetInd
        self.targetIndex = targetInd
        self.score = 0
        self.vy = 0
        self.vel = PLAYER_VEL
        self.numKeyPressed = 0
        self.moving = False

    def newInputs(self, pressed):
        finding = True

        if pressed[0] == 1:
            i = self.index - 1
            while i >= 0:
                corner = cornerList[i]
                if corner.x == self.x and corner.y < self.y:
                    offset = self.y - corner.y
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallVertical(self.x, self.y, corner.y):
                            # self.y = corner.y
                            self.targetIndex = cornerList.index(corner)
                            self.smoothMove(corner.x, corner.y, 0)

                            return
                        else:
                            return
                else:
                    i -= 1


        elif pressed[1] == 1:
            if self.index == PORTAL1_IND:
                self.x = cornerList[PORTAL2_IND].x
                self.y = cornerList[PORTAL2_IND].y
                self.index = PORTAL2_IND
                self.targetIndex = PORTAL2_IND
                self.targetX = cornerList[PORTAL2_IND].x
                self.targetY = cornerList[PORTAL2_IND].y
                return

            i = self.index - 1
            while i >= 0:
                corner = cornerList[i]
                if corner.y == self.y and corner.x < self.x:
                    offset = corner.x - self.x
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallHorizontal(corner.y, corner.x, self.x):
                            # self.x = corner.x
                            self.targetIndex = cornerList.index(corner)
                            self.smoothMove(corner.x, corner.y, 1)

                            return
                        else:
                            return
                else:
                    i -= 1

        elif pressed[2] == 1:

            i = self.index + 1
            while i < len(cornerList):
                corner = cornerList[i]
                if corner.x == self.x and corner.y > self.y:
                    offset = corner.y - self.y
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallVertical(self.x, corner.y, self.y):
                            # self.y = corner.y
                            self.targetIndex = cornerList.index(corner)
                            self.smoothMove(corner.x, corner.y, 2)

                            return
                        else:
                            return
                else:
                    i += 1

        elif pressed[3] == 1:
            if self.index == PORTAL2_IND:
                self.x = cornerList[PORTAL1_IND].x
                self.y = cornerList[PORTAL1_IND].y
                self.index = PORTAL1_IND
                self.targetIndex = PORTAL1_IND
                self.targetX = cornerList[PORTAL1_IND].x
                self.targetY = cornerList[PORTAL1_IND].y
                return

            i = self.index + 1
            while i < len(cornerList):
                corner = cornerList[i]
                if corner.y == self.y and corner.x > self.x:
                    offset = self.x - corner.x
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallHorizontal(self.y, self.x, corner.x):
                            # self.x = corner.x
                            self.targetIndex = cornerList.index(corner)
                            self.smoothMove(corner.x, corner.y, 3)

                            return
                        else:
                            return

                else:
                    i += 1

    def smoothMove(self, _targetX, _targetY, _moveDir):
        # moveDir = W A S D = 0 1 2 3
        self.targetY = _targetY
        self.targetX = _targetX
        self.vx = 0
        self.vy = 0
        self.moving = False

        if not self.moving and _moveDir == 0:
            self.moving = True
            self.vy -= self.vel


        elif not self.moving and _moveDir == 1:
            self.moving = True
            self.vx -= self.vel


        elif not self.moving and _moveDir == 2:
            self.moving = True
            self.vy += self.vel


        elif not self.moving and _moveDir == 3:
            self.moving = True
            self.vx += self.vel

        return

    def input(self, pressed):

        for p in pressed:
            if p:
                self.numKeyPressed += 1

        if self.numKeyPressed > 1:
            return
        self.vx = 0
        self.vy = 0
        if pressed[K_LEFT]:
            self.vx = -self.vel

        elif pressed[K_RIGHT]:
            self.vx += self.vel
        elif pressed[K_UP]:
            self.vy -= self.vel
        elif pressed[K_DOWN]:
            self.vy += self.vel

    def updateScore(self):

        for treat in treatList:
            if pygame.sprite.collide_rect(self, treat):
                self.score += 1
                treatList.remove(treat)
                return 1
        return 0

    def Death(self):

        for enemy in enemyList:
            if pygame.sprite.collide_rect(self, enemy):
                self.score -= 1
                return True
        return False

    def updatePosition(self, pressed):

        self.numKeyPressed = 0
        if not self.moving:
            self.newInputs(pressed)
        # self.input(pressed)
        # Move Player
        if self.x < 0:
            self.x = WINDOWWIDTH
        elif self.x > WINDOWWIDTH:
            self.x = 0

        if (self.x is not self.targetX) and self.y is not self.targetY:
            if ((abs(self.x - self.targetX)) <= (PLAYER_VEL / 2)) and (abs(self.y - self.targetY)) <= (PLAYER_VEL / 2):
                self.vx = 0
                self.vy = 0
                self.x = self.targetX
                self.y = self.targetY
                self.index = self.targetIndex
                self.moving = False

        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x
        self.rect.y = self.y

        # Check for Collisions
        for wall in wallList:
            if pygame.sprite.collide_rect(self, wall):

                if self.vx > 0:
                    self.x = wall.rect.left - self.width

                elif self.vx < 0:
                    self.x = wall.rect.right
                elif self.vy > 0:
                    self.y = wall.rect.top - self.height

                elif self.vy < 0:
                    self.y = wall.rect.bottom

                self.vx = 0
                self.vy = 0


def nLargest(targetList, n):
    max = targetList[0]
    ind = 0
    for i, t in enumerate(targetList):
        if t > max:
            max = t
            ind = i


class Treats(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((TREAT_SIZE, TREAT_SIZE))
        self.image.fill(RED)
        self.rect = Rect(x, y, TREAT_SIZE, TREAT_SIZE)
        self.width = TREAT_SIZE
        self.height = TREAT_SIZE
        self.x = x
        self.y = y
        self.eaten = False


class Portal():

    def __init__(self, x, y, w, h):
        self.image = pygame.Surface((w, h))
        self.image.fill(RED)
        self.rect = Rect(x, y, w, h)

        self.x = x
        self.y = y

    def Draw(self, win):
        win.blit(self.image, (self.x, self.y))


class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, ind, type):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.index = ind
        self.type = type
        self.targetX = x
        self.targetY = y
        self.targetIndex = ind
        self.posMoves = [-1, -1, -1, -1]
        self.x = x
        self.y = y
        self.moving = False
        self.vel = ENEMY_VEL
        self.vx = 0
        self.vy = 0

    def updatePosition(self, _targetX, _targetY):

        if not self.moving:
            self.move(_targetX, _targetY)
        # self.input(pressed)
        # Move Player
        if self.x < 0:
            self.x = WINDOWWIDTH
        elif self.x > WINDOWWIDTH:
            self.x = 0

        if (self.x is not self.targetX) and self.y is not self.targetY:
            if ((abs(self.x - self.targetX)) <= (PLAYER_VEL / 2)) and (abs(self.y - self.targetY)) <= (PLAYER_VEL / 2):
                self.vx = 0
                self.vy = 0
                self.x = self.targetX
                self.y = self.targetY
                self.index = self.targetIndex
                self.moving = False

        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, targetX, targetY):
        _moveCorner = -1
        self.targetX = targetX
        self.targetY = targetY
        if self.x == targetX and self.y == targetY:
            return

        disList = [math.inf, math.inf, math.inf, math.inf]

        self.updatePosMoves()

        for i, potentialCorner in enumerate(self.posMoves):
            if potentialCorner is not -1:
                disList[i] = distance(targetX, targetY, cornerList[potentialCorner].x, cornerList[potentialCorner].y)

        i = disList.index(min(disList))
        _moveCorner = self.posMoves[i]
        self.targetX = cornerList[_moveCorner].x
        self.targetY = cornerList[_moveCorner].y
        self.smoothMove(self.targetX, self.targetY, i)

        self.targetIndex = _moveCorner

    def Draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def updatePosMoves(self):

        self.posMoves = [-1, -1, -1, -1]
        ctr = 0
        i = self.index - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == self.x and corner.y < self.y:
                offset = self.y - corner.y
                if offset > WALL_CHECK_OFFSET:

                    continue
                else:

                    if not checkWallVertical(self.x, self.y, corner.y):

                        self.posMoves[0] = cornerList.index(corner)

                    else:
                        self.posMoves[0] = -1
                    break

            else:
                i -= 1

            #
            # if self.index == PORTAL1_IND:
            #     self.x = cornerList[PORTAL2_IND].x
            #     self.y = cornerList[PORTAL2_IND].y
            #     self.index = PORTAL2_IND
            #     self.targetIndex = PORTAL2_IND
            #     self.targetX = cornerList[PORTAL2_IND].x
            #     self.targetY = cornerList[PORTAL2_IND].y
            #     return True
        ctr = 0
        i = self.index - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == self.y and corner.x < self.x:
                offset = corner.x - self.x
                if offset > WALL_CHECK_OFFSET:

                    continue
                else:

                    if not checkWallHorizontal(corner.y, corner.x, self.x):

                        self.posMoves[1] = cornerList.index(corner)

                    else:
                        self.posMoves[0] = -1

                    break
            else:
                i -= 1
        ctr = 0
        i = self.index + 1
        while i < len(cornerList) and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == self.x and corner.y > self.y:
                offset = corner.y - self.y
                if offset > WALL_CHECK_OFFSET:

                    continue
                else:

                    if not checkWallVertical(self.x, corner.y, self.y):

                        self.posMoves[2] = cornerList.index(corner)

                    else:
                        self.posMoves[2] = -1

                    break
            else:
                i += 1

        # if self.index == PORTAL2_IND:
        #     self.x = cornerList[PORTAL1_IND].x
        #     self.y = cornerList[PORTAL1_IND].y
        #     self.index = PORTAL1_IND
        #     self.targetIndex = PORTAL1_IND
        #     self.targetX = cornerList[PORTAL1_IND].x
        #     self.targetY = cornerList[PORTAL1_IND].y
        #     return True
        ctr = 0
        i = self.index + 1
        while i < len(cornerList) and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == self.y and corner.x > self.x:
                offset = self.x - corner.x
                if offset > WALL_CHECK_OFFSET:

                    continue
                else:

                    if not checkWallHorizontal(self.y, self.x, corner.x):

                        self.posMoves[3] = cornerList.index(corner)

                    else:
                        self.posMoves[3] = -1

                    break

            else:
                i += 1

    def smoothMove(self, _targetX, _targetY, _moveDir):
        # moveDir = W A S D = 0 1 2 3
        self.targetY = _targetY
        self.targetX = _targetX
        self.vx = 0
        self.vy = 0
        self.moving = False

        if not self.moving and _moveDir == 0:
            self.moving = True
            self.vy -= self.vel


        elif not self.moving and _moveDir == 1:
            self.moving = True
            self.vx -= self.vel


        elif not self.moving and _moveDir == 2:
            self.moving = True
            self.vy += self.vel


        elif not self.moving and _moveDir == 3:
            self.moving = True
            self.vx += self.vel

        return


class Corner():
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((TREAT_SIZE, TREAT_SIZE))
        self.image.fill(YELLOW)
        self.rect = Rect(x, y, TREAT_SIZE, TREAT_SIZE)
        self.width = TREAT_SIZE
        self.height = TREAT_SIZE
        self.x = x
        self.y = y
        self.playerOnCorner = False


class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, w, h):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = Rect(x, y, w, h)

        self.x = x
        self.y = y


def distance(x1, y1, x2, y2):
    res = (x1 - x2) ** 2 + (y1 - y2) ** 2
    res = math.sqrt(res)
    return res


def MakeTreats(_tileMap):
    global treatList
    treatList = []
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == '0' or c == 'T':
                treatList.append(Treats(x * 12.5, y * 12.5))


def MakeCorners(_tileMap):
    global cornerList
    cornerList = []
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'T':
                cornerList.append(Corner(x * 12.5, y * 12.5))


def MakePortals(_tileMap):
    ind = 0
    global portalList
    portalList = []
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'X':
                if x < 300:
                    ind = 0
                    portalList.append(Portal(x * 12.5, y * 12.5, 12.5, 12.5))
                else:
                    ind = 1
                    portalList.append(Portal(x * 12.5, y * 12.5, 12.5, 12.5))


def MakeWalls(_tileMap):
    global wallList
    wallList = []
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'W':
                wallList.append(Wall(x * 12.5, y * 12.5, 12.5, 12.5))


def DrawWindow(win, player, enemies):
    global gen
    for wall in wallList:
        win.blit(wall.image, (wall.x, wall.y))
    for treat in treatList:
        win.blit(treat.image, (treat.x, treat.y))
    # for corner in cornerList:
    #     win.blit(corner.image, (corner.x, corner.y))
    for portal in portalList:
        portal.Draw(WINDOW)
    for enemy in enemies:
        enemy.Draw(WINDOW)

    text = STAT_FONT.render("SCORE  " + str(player.score), 1, (255, 0, 0))
    genText = STAT_FONT.render("GEN  " + str(gen), 1, (255, 0, 0))
    WINDOW.blit(text, (10, 700))
    WINDOW.blit(genText, (10, 750))
    # Render player
    win.blit(player.image, (player.x, player.y))
    pygame.display.update()






def eval_genomes(genomes, config):

    nets = []  # Neural nets for all the birds
    ge = []  # The bird neat variable with all the fitness and shit
    global gen
    gen += 1
    for _, g in genomes:

        g.fitness = 0
        # For each Genome, create a new network
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ge.append(g)

    for _, g in genomes:
        gameFunction(0, nets, ge)



def gameFunction(genomeNum, nets, ge):
    lastScoreTime = time.time()
    global FPSCLOCK, WINDOW, wallList, enemyList, tileMap, treatList
    pygame.init()
    random.seed()

    fitness = 0

    FPSCLOCK = pygame.time.Clock()


    # pxarray = pygame.PixelArray(screensurf)
    # print(pxarray)

    enemyList = []
    MakeTreats(tileMap)
    MakeCorners(tileMap)
    MakeWalls(tileMap)
    MakePortals(tileMap)

    spawnIndex = random.randint(0, len(cornerList))
    player = Player(cornerList[spawnIndex].x, cornerList[spawnIndex].y, spawnIndex, genomeNum)

    enemy1 = Enemy(cornerList[31].x, cornerList[31].y, ENEMY_IND, 1)
    enemyList.append(enemy1)

    while True:
        mvtInputs = [0, 0, 0, 0]
        WINDOW.fill(WHITE)  # Drawing the window

        for event in pygame.event.get():  # Event handling
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        screensurf = pygame.display.get_surface()
        pixelArray = pygame.surfarray.pixels2d(screensurf)

        output = nets[genomeNum].activate((player.x, player.y, enemy1.x, enemy1.y, *pixelArray))
        del pixelArray

        res = output.index(max(output))

        pressed = pygame.key.get_pressed()
        DrawWindow(WINDOW, player, enemyList)





        # if pressed[K_w]:
        #     mvtInputs = [1, 0, 0, 0]
        # elif pressed[K_a]:
        #     mvtInputs = [0, 1, 0, 0]
        # elif pressed[K_s]:
        #     mvtInputs = [0, 0, 1, 0]
        # elif pressed[K_d]:
        #     mvtInputs = [0, 0, 0, 1]

        if res == 0:
            mvtInputs = [1, 0, 0, 0]
        elif res == 1:
            mvtInputs = [0, 1, 0, 0]
        elif res == 2:
            mvtInputs = [0, 0, 1, 0]
        elif res == 3:
            mvtInputs = [0, 0, 0, 1]
        else:
            mvtInputs = [0, 0, 0, 0]

        player.updatePosition(mvtInputs)
        enemy1.updatePosition(player.targetX, player.targetY)
        if player.updateScore():
            ge[genomeNum].fitness += 5
            lastScoreTime = time.time()
        else:
            if time.time() - lastScoreTime > 60:
                ge[genomeNum].fitness -= 10
                ge.pop(genomeNum)
                nets.pop(genomeNum)
                return

        ge[genomeNum].fitness += 0.1
        if player.Death():
            ge[genomeNum].fitness -= 10
            ge.pop(genomeNum)
            nets.pop(genomeNum)
            return

        FPSCLOCK.tick(FPS)



def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
