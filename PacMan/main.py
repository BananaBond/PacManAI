import pygame, random, sys
from pygame.locals import *

# Set FPS
FPS = 30

# Window Dimensions
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
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
        print(self.numKeyPressed)

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


def main():
    global FPSCLOCK, DISPLAYSURF, wallList, enemyList, walls
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

    wallList = [
        Wall(70, 100, WALL_THICKNESS, 120),
        Wall(100, 100, 120, WALL_THICKNESS)
    ]

    allsprites = pygame.sprite.Group()

    allsprites.add(player)
    allsprites.add(enemyList)
    allsprites.add(wallList)

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
