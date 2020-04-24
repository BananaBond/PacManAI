import pygame, random, sys
from pygame.locals import *
import math
import glob

# Set FPS
FPS = 30

# Window Dimensions
WINDOWWIDTH = 638
WINDOWHEIGHT = 825
WALL_THICKNESS = 10
PLAYER_SIZE = 30
TREAT_SIZE = 10
PLAYER_VEL = 10
ENEMY_VEL = 5
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

pygame.font.init()
STAT_FONT = pygame.font.SysFont("roboto", 30)

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
WWWWWWWWWW    W T    T      T    T  W    WWWWWWWWWW
W        W    W                     W    W        W
W        W    W                     W    W        W
W        W         WWWW     WWWW         W        W
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

    def __init__(self, x, y):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set Properties
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLUE)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = x
        self.y = y
        self.targetX = x
        self.targetY = y
        self.vx = 0
        self.score = 0
        self.vy = 0
        self.vel = PLAYER_VEL
        self.numKeyPressed = 0
        self.moving = False

    def newInputs(self, pressed):

        if pressed[K_w]:
            for corner in cornerList:
                if corner.x == self.x and corner.y < self.y:
                    offset = self.y - corner.y
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallVertical(self.x, self.y, corner.y):
                            # self.y = corner.y
                            self.smoothMove(corner.x, corner.y, 0)

                            return

        elif pressed[K_a]:
            for corner in cornerList:
                if corner.y == self.y and corner.x < self.x:
                    offset = corner.x - self.x
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallHorizontal(corner.y, corner.x, self.x):
                            # self.x = corner.x
                            self.smoothMove(corner.x, corner.y, 1)

                            return

        elif pressed[K_s]:
            for corner in cornerList:
                if corner.x == self.x and corner.y > self.y:
                    offset = corner.y - self.y
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallVertical(self.x, corner.y, self.y):
                            # self.y = corner.y
                            self.smoothMove(corner.x, corner.y, 2)

                            return

        elif pressed[K_d]:
            for corner in cornerList:
                if corner.y == self.y and corner.x > self.x:
                    offset = self.x - corner.x
                    if offset > WALL_CHECK_OFFSET:

                        continue
                    else:

                        if not checkWallHorizontal(self.y, self.x, corner.x):
                            # self.x = corner.x
                            self.smoothMove(corner.x, corner.y, 3)

                            return

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
            if ((abs(self.x - self.targetX))<=(PLAYER_VEL/2)) and (abs(self.y - self.targetY))<=(PLAYER_VEL/2):
                self.vx = 0
                self.vy = 0
                self.x = self.targetX
                self.y = self.targetY
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


class Treats(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((TREAT_SIZE, TREAT_SIZE))
        self.image.fill(YELLOW)
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

    def __init__(self, x, y, ind):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.index = ind
        self.x = x
        self.y = y
        self.vel = ENEMY_VEL
        self.vx = 0
        self.vy = 0
        self.collided = False

    def move(self, targetX, targetY):
        moveDir = -1
        self.collided = False

        if self.index == 1:
            disList = []
            disR = distance(targetX + 10, targetY, self.x, self.y)
            disList.append(disR)
            disL = distance(targetX - 10, targetY, self.x, self.y)
            disList.append(disL)
            disU = distance(targetX, targetY - 10, self.x, self.y)
            disList.append(disU)
            disD = distance(targetX, targetY + 10, self.x, self.y)
            disList.append(disD)
            moveDir = disList.index(max(disList))

        for wall in wallList:
            if pygame.sprite.collide_rect(self, wall):
                self.collided = True
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
        if self.collided:
            tempList = disList
            tempList.remove(disList[moveDir])
            moveDir = tempList.index(max(tempList))

        if moveDir == 0:
            self.vx = self.vel
            self.vy = 0
        elif moveDir == 1:
            self.vx = -self.vel
            self.vy = 0
        elif moveDir == 2:
            self.vx = 0
            self.vy = -self.vel
        elif moveDir == 3:
            self.vx = 0
            self.vy = self.vel

        # Update Position

        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x
        self.rect.y = self.y

    def Draw(self, win):
        win.blit(self.image, (self.x, self.y))


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
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == '0':
                treatList.append(Treats(x * 12.5, y * 12.5))



def MakeCorners(_tileMap):
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'T':
                cornerList.append(Corner(x * 12.5, y * 12.5))


def MakePortals(_tileMap):
    ind = 0
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
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'W':
                wallList.append(Wall(x * 12.5, y * 12.5, 12.5, 12.5))


def DrawWindow(win, player, enemies):
    for wall in wallList:
        win.blit(wall.image, (wall.x, wall.y))
    for treat in treatList:
        win.blit(treat.image, (treat.x, treat.y))
    for corner in cornerList:
        win.blit(corner.image, (corner.x, corner.y))
    for portal in portalList:
        portal.Draw(WINDOW)
    for enemy in enemies:
        enemy.Draw(WINDOW)

    text = STAT_FONT.render("SCORE  " + str(player.score), 1, (255, 0, 0))
    WINDOW.blit(text, (10, 600))
    # Render player
    win.blit(player.image, (player.x, player.y))
    pygame.display.update()


def main():
    global FPSCLOCK, WINDOW, wallList, enemyList, tileMap, treatList
    pygame.init()
    random.seed()

    FPSCLOCK = pygame.time.Clock()

    WINDOW = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Lembalo')

    tileMap = tileMap.splitlines()
    MakeTreats(tileMap)
    MakeCorners(tileMap)
    MakeWalls(tileMap)
    MakePortals(tileMap)
    player = Player(cornerList[10].x, cornerList[10].y)

    enemy1 = Enemy(300, 300, 1)
    enemies = []
    enemies.append(enemy1)

    # wallList = [
    #     # Mid line
    #     # Wall(0,400, 600, WALL_THICKNESS),
    #     Wall(290, 0, WALL_THICKNESS, 100),
    #     Wall(290, 700, WALL_THICKNESS, 100),
    #     # Boundary
    #     Wall(0, 0, WALL_THICKNESS, WINDOWHEIGHT),
    #     Wall(0, 0, WINDOWWIDTH, WALL_THICKNESS),
    #     Wall(WINDOWWIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, WINDOWHEIGHT),
    #     Wall(0, WINDOWHEIGHT - WALL_THICKNESS, WINDOWWIDTH, WALL_THICKNESS),
    #
    #     # Left portal 1
    #     Wall(0, 300, 100, WALL_THICKNESS),
    #     Wall(100, 300, WALL_THICKNESS, 70),
    #     Wall(0, 360, 100, WALL_THICKNESS),
    #
    #     # Left Portal 2
    #     Wall(0, 140 + 300, 100, WALL_THICKNESS),
    #     Wall(100, 140 + 300, WALL_THICKNESS, 70),
    #     Wall(0, 140 + 360, 100, WALL_THICKNESS),
    #
    #     # Right portal 1
    #     Wall(0 + 500, 300, 100, WALL_THICKNESS),
    #     Wall(100 + 400, 300, WALL_THICKNESS, 70),
    #     Wall(0 + 500, 360, 100, WALL_THICKNESS),
    #
    #     # Right Portal 2
    #     Wall(0 + 500, 140 + 300, 100, WALL_THICKNESS),
    #     Wall(100 + 400, 140 + 300, WALL_THICKNESS, 70),
    #     Wall(0 + 500, 140 + 360, 100, WALL_THICKNESS),
    #
    #     # Mid Box
    #     Wall(240, 365, 110, WALL_THICKNESS),
    #     Wall(230, 365, WALL_THICKNESS, 80),
    #     Wall(240, 435, 110, WALL_THICKNESS),
    #     Wall(350, 365, WALL_THICKNESS, 80)
    # ]

    while True:

        WINDOW.fill(WHITE)  # Drawing the window

        for event in pygame.event.get():  # Event handling
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        pressed = pygame.key.get_pressed()
        DrawWindow(WINDOW, player, enemies)
        # Update player position
        # enemy1.move(player.x, player.y)
        player.updatePosition(pressed)
        player.updateScore()

        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()
