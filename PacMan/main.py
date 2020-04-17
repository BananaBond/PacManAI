import pygame, random, sys
from pygame.locals import *
import glob

# Set FPS
FPS = 30

# Window Dimensions
WINDOWWIDTH = 600
WINDOWHEIGHT = 825
WALL_THICKNESS = 10
PLAYER_SIZE = 30
PLAYER_VEL = 10
ENEMY_VEL = 5
# Colors
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Key Constants
UP = 'up'
DOWN = 'down'
RIGHT = 'right'
LEFT = 'left'
wallList = []
tileMap = """
WWWWWWWWWWWWWWWWWWWWWWWW
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
WWWWWW            WWWWWW
W    W            W    W
W    W            W    W
WWWWWW            WWWWWW
W                      W   
W                      W   
WWWWWW            WWWWWW
W    W            W    W
W    W            W    W
WWWWWW            WWWWWW
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
W                      W
WWWWWWWWWWWWWWWWWWWWWWWW"""


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set Properties
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.vel = PLAYER_VEL
        self.numKeyPressed = 0

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

    def updatePosition(self, pressed):

        self.numKeyPressed = 0

        self.input(pressed)
        # Move Player

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


class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = y
        self.vel = ENEMY_VEL
        self.vx = 0
        self.vy = 0

    def move(self, vx, vy):
        pass




class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, w, h):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = Rect(x, y, w, h)

        self.x = x
        self.y = y


def DrawWalls(_tileMap):
    print(len(_tileMap))

    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'W':
                wallList.append(Wall(x * 25, y * 25, 25, 25))


def main():

    global FPSCLOCK, DISPLAYSURF, wallList, enemyList, walls, tileMap
    pygame.init()
    random.seed()

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Lembalo')
    player = Player(WINDOWWIDTH / 2, WINDOWHEIGHT - 100)

    enemyList = [
        Enemy(random.randint(0, WINDOWWIDTH - 30), random.randint(0, WINDOWHEIGHT - 430)),
        Enemy(random.randint(0, WINDOWWIDTH - 30), random.randint(0, WINDOWHEIGHT - 430)),
        Enemy(random.randint(0, WINDOWWIDTH - 30), random.randint(0, WINDOWHEIGHT - 430)),
        Enemy(random.randint(0, WINDOWWIDTH - 30), random.randint(0, WINDOWHEIGHT - 430)),
        Enemy(random.randint(0, WINDOWWIDTH - 30), random.randint(0, WINDOWHEIGHT - 430))
    ]

    tileMap = tileMap.splitlines()
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

    allsprites = pygame.sprite.Group()

    allsprites.add(player)
    allsprites.add(enemyList)
    allsprites.add(wallList)

    DrawWalls(tileMap)
    print(len(wallList))
    while True:

        DISPLAYSURF.fill(WHITE)  # Drawing the window

        for event in pygame.event.get():  # Event handling
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # elif event.type == KEYDOWN:
            #     player.onKeyDown(event)
            # elif event.type == KEYUP:
            #     player.onKeyUp(event)
            #
        pressed = pygame.key.get_pressed()

        # Update player position
        player.updatePosition(pressed)

        # Render enemies and update position
        for enemy in enemyList:
            # enemy.move()
            DISPLAYSURF.blit(enemy.image, (enemy.x, enemy.y))

        # Render walls
        for wall in wallList:
            DISPLAYSURF.blit(wall.image, (wall.x, wall.y))

        # Render player
        DISPLAYSURF.blit(player.image, (player.x, player.y))
        allsprites.update()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()
