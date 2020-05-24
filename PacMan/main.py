import os

import pygame, random, sys
from pygame.locals import *
import math
import glob
import time
import neat
import numpy as np

# Set FPS
FPS = 30

gen = -1

# Window Dimensions
WINDOWWIDTH = 638
WINDOWHEIGHT = 825
WALL_THICKNESS = 10
PLAYER_SIZE = 30
TREAT_SIZE = 10
PLAYER_VEL = 5
ENEMY_VEL = 5
ENEMY_IND = 31
PORTAL1_IND = 32
PORTAL2_IND = 37
WALL_CHECK_OFFSET = 200
# Colors

BLUE = (0, 0, 255, 255)
WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
YELLOW = (255, 255, 0, 255)

# Key Constants
UP = 'up'
DOWN = 'down'
RIGHT = 'right'
LEFT = 'left'
wallList = []
treatList = []
allTreatLists = []

portalList = []
cornerList = []
enemyList = []
playerList = []
cornerPos = []
cornerPosFlat = []
connections = []
prevInputs = []

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

import pprint
from collections import defaultdict


class DNode:
    def __init__(self, value, previous, dist):
        self.prev = previous
        self.dist = dist
        self.val = value

def PerformDjikstra(graph, start, end):
    global cornerList
    DNodeList = []
    queue = []
    visited = []
    result = -1
    for i, _ in enumerate(cornerList):
        DNodeList.append(DNode(i, -1, -1))
    found = False

    currCorner = start

    DNodeList[currCorner].dist = 0
    DNodeList[currCorner].prev = 0

    queue.append(start)
    ind = 0
    while len(queue)-ind is not 0:

        moves = graph._graph[currCorner]
        for move in moves:
            dis1 = DNodeList[move].dist
            if dis1 is -1:
                DNodeList[move].prev = currCorner
                DNodeList[move].dist = DNodeList[currCorner].dist + 1
                # queue.append(move)
            elif DNodeList[currCorner].dist + 1 < dis1:
                DNodeList[move].prev = currCorner
                DNodeList[move].dist = DNodeList[currCorner].dist + 1
            if move not in queue:
                queue.append(move)


        visited.append(currCorner)
        currCorner = queue[ind]
        ind += 1

    path = []
    curr = end
    while curr is not start:
        curr = DNodeList[curr].prev
        path.append(curr)



    return DNodeList[end].dist, path




class Graph(object):
    """ Graph data structure, undirected by default. """

    def __init__(self, connections, directed=False):
        self._graph = defaultdict(set)
        self._directed = directed
        self.add_connections(connections)

    def add_connections(self, connections):
        """ Add connections (list of tuple pairs) to graph """

        for node1, node2 in connections:
            self.add(node1, node2)

    def add(self, node1, node2):
        """ Add connection between node1 and node2 """

        self._graph[node1].add(node2)
        if not self._directed:
            self._graph[node2].add(node1)

    def remove(self, node):
        """ Remove all references to node """

        for n, cxns in self._graph.items():  # python3: items(); python2: iteritems()
            try:
                cxns.remove(node)
            except KeyError:
                pass
        try:
            del self._graph[node]
        except KeyError:
            pass

    def is_connected(self, node1, node2):
        """ Is node1 directly connected to node2 """

        return node1 in self._graph and node2 in self._graph[node1]

    def find_path(self, node1, node2, path=[]):
        """ Find any path between node1 and node2 (may not be shortest) """

        path = path + [node1]
        if node1 == node2:
            return path
        if node1 not in self._graph:
            return None
        for node in self._graph[node1]:
            if node not in path:
                new_path = self.find_path(node, node2, path)
                if new_path:
                    return new_path
        return None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self._graph))


def makeConnections():
    global connections, cornerList
    connections = []
    for vert, selfCorner in enumerate(cornerList):

        ctr = 0
        i = vert - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == selfCorner.x and corner.y < selfCorner.y:
                offset = selfCorner.y - corner.y
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallVertical(selfCorner.x, selfCorner.y, corner.y):
                        connections.append((vert, i))

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
        i = vert - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == selfCorner.y and corner.x < selfCorner.x:
                offset = corner.x - selfCorner.x
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallHorizontal(corner.y, corner.x, selfCorner.x):
                        connections.append((vert, i))

                    break
            else:
                i -= 1

        ctr = 0
        i = vert + 1
        while i < len(cornerList) and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == selfCorner.x and corner.y > selfCorner.y:
                offset = corner.y - selfCorner.y
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallVertical(selfCorner.x, corner.y, selfCorner.y):

                        connections.append((vert, i))

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
        i = vert + 1
        while i < len(cornerList) and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == selfCorner.y and corner.x > selfCorner.x:
                offset = selfCorner.x - corner.x
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallHorizontal(selfCorner.y, selfCorner.x, corner.x):
                        connections.append((vert, i))
                    break

            else:
                i += 1


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

    def __init__(self, x, y, targetInd, genomeNum, playerColor):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)

        # Set Properties
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.alpha = 255

        self.color = playerColor

        self.image.fill(self.color)
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
        self.posMoves = [0, 0, 0, 0]
        self.posTreats = [0, 0, 0, 0]
        self.posMovesInd = [-1, -1, -1, -1]

    def updateAlpha(self, newAlpha):
        self.alpha = newAlpha

        self.color[3] = newAlpha

        self.image.fill(self.color)

    def calcTreatsAround(self, index):

        # If you add more treats you have to change the start index way for i here

        myTreatList = allTreatLists[self.genomeNum]

        posTreatsInd = [-1, -1, -1, -1]
        posTreats = [-1, -1, -1, -1]
        x = cornerList[index].x
        y = cornerList[index].y

        ctr = 0

        i = index - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            treat = myTreatList[i]
            if treat.x == x and treat.y < y:
                offset = y - treat.y
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallVertical(x, y, treat.y):
                        # self.y = corner.y
                        if not treat.eaten:
                            posTreats[0] = 1
                            posTreatsInd[0] = 1

                        break
            else:
                i -= 1

        # if self.index == PORTAL1_IND:
        #     self.posMoves[1] = 1

        ctr = 0
        i = index - 1
        while i >= 0 and ctr < 15:
            ctr += 1
            treat = myTreatList[i]
            if treat.y == y and treat.x < x:
                offset = treat.x - x
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallHorizontal(treat.y, treat.x, x):
                        # self.x = corner.x
                        if not treat.eaten:
                            posTreats[1] = 1
                            posTreatsInd[1] = 1
                        break

            else:
                i -= 1

        ctr = 0
        i = index + 1
        while i < len(myTreatList) and ctr < 15:
            ctr += 1
            treat = myTreatList[i]
            if treat.x == x and treat.y > y:
                offset = treat.y - y
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallVertical(x, treat.y, y):
                        # self.y = corner.y
                        if not treat.eaten:
                            posTreats[2] = 1
                            posTreatsInd[2] = 1
                        break

            else:
                i += 1

        # if self.index == PORTAL2_IND:
        #     self.posTreats[3] = 1

        ctr = 0
        i = index + 1
        while i < len(myTreatList) and ctr <= 15:
            ctr += 1
            treat = myTreatList[i]
            if treat.y == y and treat.x > x:
                offset = x - treat.x
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallHorizontal(y, x, treat.x):
                        # self.x = corner.x
                        if not treat.eaten:
                            posTreats[3] = 1
                            posTreatsInd[3] = 1
                        break
            else:
                i += 1

        if self.index == index:
            self.posTreats = posTreats
        return posTreats, posTreatsInd

    def calcPosMoves(self, index):

        x = cornerList[index].x
        y = cornerList[index].y
        posMoves = [-1, -1, -1, -1]
        posMovesInd = [-1, -1, -1, -1]
        posTreats = [0, 0, 0, 0]

        ctr = 0
        keepGoing = True
        i = index - 1
        while i >= 0 and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == x and corner.y < y:
                offset = y - corner.y
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallVertical(x, y, corner.y):
                        # self.y = corner.y
                        posMoves[0] = 1
                        posMovesInd[0] = i
                        if not treatList[i].eaten:
                            posTreats[0] = 1

                        break


            else:
                i -= 1

        if index == PORTAL1_IND:
            posMoves[1] = 1
            posMovesInd[1] = PORTAL2_IND
            if not treatList[index].eaten:
                posTreats[1] = 1

        ctr = 0
        i = index - 1
        while i >= 0 and ctr < 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == y and corner.x < x:
                offset = corner.x - x
                if offset > WALL_CHECK_OFFSET:
                    i -= 1
                    continue
                else:

                    if not checkWallHorizontal(corner.y, corner.x, x):
                        # self.x = corner.x
                        posMoves[1] = 1
                        posMovesInd[1] = i
                        if not treatList[i].eaten:
                            posTreats[1] = 1

                        break

            else:
                i -= 1

        ctr = 0
        i = index + 1
        while i < len(cornerList) and ctr < 15:
            ctr += 1
            corner = cornerList[i]
            if corner.x == x and corner.y > y:
                offset = corner.y - y
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallVertical(x, corner.y, y):
                        # self.y = corner.y
                        posMoves[2] = 1
                        posMovesInd[2] = i
                        if not treatList[i].eaten:
                            posTreats[2] = 1

                        break

            else:
                i += 1

        if index == PORTAL2_IND:
            posMoves[3] = 1
            posMovesInd[3] = PORTAL1_IND
            if not treatList[index].eaten:
                posTreats[3] = 1

        ctr = 0
        i = index + 1
        while i < len(cornerList) and ctr <= 15:
            ctr += 1
            corner = cornerList[i]
            if corner.y == y and corner.x > x:
                offset = x - corner.x
                if offset > WALL_CHECK_OFFSET:
                    i += 1
                    continue
                else:

                    if not checkWallHorizontal(y, x, corner.x):
                        # self.x = corner.x
                        posMoves[3] = 1
                        posMovesInd[3] = i
                        if not treatList[i].eaten:
                            posTreats[3] = 1

                        break


            else:
                i += 1

        if self.index == index:
            self.posMoves = posMoves
            self.posMovesInd = posMovesInd

        return posMoves, posMovesInd, posTreats

    def newInputs(self, pressed):
        finding = True

        if pressed[0] == 1:
            i = self.index - 1
            while i >= 0:
                corner = cornerList[i]
                if corner.x == self.x and corner.y < self.y:
                    offset = self.y - corner.y
                    if offset > WALL_CHECK_OFFSET:
                        i -= 1
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
                        i -= 1
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
                        i += 1
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
                        i += 1
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

        myTreatList = allTreatLists[self.genomeNum]
        for treat in myTreatList:
            if treat.x == self.x and treat.y == self.y and not treat.eaten:
                self.score += 1
                treat.eaten = True
                # treatList.remove(treat)
                return 1
        return 0

    def Death(self):

        if pygame.sprite.collide_rect(self, enemyList[self.genomeNum]):
            return True
        else:
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

        self.color = RED
        self.image = pygame.Surface((TREAT_SIZE, TREAT_SIZE))
        self.image.fill(self.color)
        self.rect = Rect(x, y, TREAT_SIZE, TREAT_SIZE)
        self.width = TREAT_SIZE
        self.height = TREAT_SIZE
        self.x = x
        self.y = y
        self.cornerIndex = -1
        self.eaten = False

    def updateColor(self, newColor):
        self.color = newColor
        self.image.fill(self.color)


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
        self.playerAlive = True

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
                    i -= 1
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
                    i -= 1
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
                    i += 1
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
                    i += 1
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


def MakeTreats(_tileMap, num):
    global treatList, allTreatLists

    allTreatLists = []

    for i in range(num):

        treatList = []
        for y, line in enumerate(_tileMap):
            for x, c in enumerate(line):
                if c == '0' or c == 'T':
                    treatList.append(Treats(x * 12.5, y * 12.5))

        allTreatLists.append(treatList)


def MakeCorners(_tileMap):
    global cornerList, cornerPos, cornerPosFlat
    cornerList = []
    cornerPos = []
    cornerPosFlat = []
    for y, line in enumerate(_tileMap):
        for x, c in enumerate(line):
            if c == 'T':
                cornerList.append(Corner(x * 12.5, y * 12.5))
                cornerPos.append([x * 12.5, y * 12.5])
                cornerPosFlat.append(x * 12.5)
                cornerPosFlat.append(y * 12.5)


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


def DrawWindow(win, players, enemies, maxPlayerInd, numDead, numAlive):
    global gen
    for wall in wallList:
        win.blit(wall.image, (wall.x, wall.y))

    # for corner in cornerList:
    #     win.blit(corner.image, (corner.x, corner.y))
    for portal in portalList:
        portal.Draw(WINDOW)
    for enemy in enemies:
        if enemy.playerAlive:
            enemy.Draw(WINDOW)

    textColor = players[maxPlayerInd].color
    text2 = STAT_FONT.render("PLAYER  " + str(maxPlayerInd), 1, textColor)
    text = STAT_FONT.render("SCORE  " + str(playerList[maxPlayerInd].score), 1, textColor)
    text3 = STAT_FONT.render("DEAD  " + str(numDead), 1, textColor)
    text4 = STAT_FONT.render("ALIVE  " + str(numAlive), 1, textColor)
    genText = STAT_FONT.render("GEN  " + str(gen), 1, textColor)
    WINDOW.blit(text2, (10, 620))
    WINDOW.blit(text, (10, 650))
    WINDOW.blit(genText, (10, 680))
    WINDOW.blit(text3, (200, 620))
    WINDOW.blit(text4, (200, 650))
    # Render player
    players[maxPlayerInd].alpha = 255
    x = 0

    for player in players:
        # if x is not maxPlayerInd:
        win.blit(player.image, (player.x, player.y))
        # x += 1
    # win.blit(players[maxPlayerInd].image, (player.x, player.y))

    for treat in allTreatLists[maxPlayerInd]:
        treat.updateColor(playerList[maxPlayerInd].color)
        if treat.eaten is False:
            win.blit(treat.image, (treat.x, treat.y))

    pygame.display.update()


def softmax(arr):
    arr = np.array(arr)

    arr = arr / max(arr)

    arr = np.exp(arr)
    sum = np.sum(arr)

    out = arr / sum

    return out


def eval_genomes(genomes, config):
    nets = []  # Neural nets for all the birds
    ge = []  # The bird neat variable with all the fitness and shit
    global gen, WINDOW, wallList, enemyList, tileMap, treatList, allTreatLists, playerList, prevInputs, connections


    gen += 1
    num = 0
    res = []
    numDead = 0
    numAlive = 0
    pseudoNetInputs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    prevInputs = []
    for _, g in genomes:
        num += 1
        g.fitness = 0
        # For each Genome, create a new network
        res.append(-1)
        prevInputs.append(pseudoNetInputs)
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        ge.append(g)

    clock = pygame.time.Clock()
    pygame.init()
    random.seed()

    allTreatLists = []
    enemyList = []
    playerList = []

    MakeCorners(tileMap)
    MakeWalls(tileMap)
    MakePortals(tileMap)

    MakeTreats(tileMap, num)

    timeCtr = []
    spawnIndex = random.randint(0, len(cornerList) - 1)
    genomeNum = 0
    for g in ge:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        player = Player(cornerList[spawnIndex].x, cornerList[spawnIndex].y, spawnIndex, genomeNum, color)
        genomeNum += 1
        enemy = Enemy(cornerList[31].x, cornerList[31].y, ENEMY_IND, 1)
        enemyList.append(enemy)
        playerList.append(player)
        timeCtr.append(0)

    # enemy1 = Enemy(cornerList[31].x, cornerList[31].y, ENEMY_IND, 1)
    # enemyList.append(enemy1)
    maxPlayer = 0
    Run = True
    makeConnections()
    g = Graph(connections, directed=True)
    mockConnections = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (1, 0), (2, 1), (2, 4), (2, 5), (2, 0), (3, 0), (3, 5), (4, 5), (4, 1), (4, 2), (5, 2), (5, 4), (5, 3)]
    g2 = Graph(mockConnections, directed=True)
    pretty_print = pprint.PrettyPrinter()
    pretty_print.pprint(g2._graph)

    dist, path = PerformDjikstra(g, 0, 23)
    print(dist)
    print(*path)

    while Run:
        if len(playerList) <= 0:
            Run = False
            print("run false")
            break

        # print(str(len(playerList)) + " " + str(Run))

        numAlive = len(playerList)
        mvtInputs = [0, 0, 0, 0]
        WINDOW.fill(WHITE)  # Drawing the window

        for event in pygame.event.get():  # Event handling
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        # Inputs 0-3
        # Enemy

        for x, player in enumerate(playerList):

            enemyList[player.genomeNum].updatePosition(player.x, player.y)

            ge[x].fitness += 0.001
            if player.updateScore():
                ge[x].fitness += 5
                timeCtr[x] = 0
            else:
                timeCtr[x] += 0.1
                # ge[x].fitness -= 0.05
            netInputs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # , 0, 0, 0, 0

            for i in range(4):
                pseudoMoves, pseudoPosMovesInd, posTreats = player.calcPosMoves(player.index)
                ind = pseudoPosMovesInd[i]
                dis = 0
                foundTreat = False
                foundEnemy = False
                while pseudoMoves[i] is 1:
                    dis += 1
                    if not allTreatLists[x][ind].eaten and not foundTreat:
                        netInputs[4 + i] = dis
                        foundTreat = True

                    # if x == maxPlayer:
                    #     print("True " + str(i))
                    if not foundEnemy and enemyList[x].index is ind:
                        netInputs[8 + i] = dis
                        foundEnemy = True
                    netInputs[i] += 1
                    pseudoMoves, pseudoPosMovesInd, posTreats = player.calcPosMoves(ind)
                    ind = pseudoPosMovesInd[i]
                if not foundTreat:
                    netInputs[4 + i] = -1
                if not foundEnemy:
                    netInputs[8 + i] = -1

            player.calcTreatsAround(player.index)

            for i, ip in enumerate(netInputs):
                netInputs[i] *= 100

            netInputs[len(netInputs) - 1] = len(allTreatLists[0]) - player.score

            if player.moving:
                netInputs = prevInputs[x]
            else:
                prevInputs[x] = netInputs

            output = nets[x].activate((*netInputs,))

            out = softmax(output)
            max = np.max(out)
            maxList = [np.argmax(out)]
            maxCtr = 0
            for i in range(out.shape[0]):
                if out[i] == max:
                    maxCtr += 1
                    maxList.append(i)

            # out = output
            #
            # print(len(allTreatLists))

            ctr = 0
            for treat in allTreatLists[x]:
                if not treat.eaten:
                    ctr += 1
            # if x == maxPlayer:
            #     print(timeCtr[x])
            #     print("Player = " + str(x))
            #     print(*netInputs)
            #     print(*out)
            #     print(ctr)
            #     print(ge[x].fitness)
            #     print(" Score = " + str(player.score))
            #     print("Len of eaten treats = " + str(68 - ctr))

            # if max(out) > 0.5:

            if maxCtr is 0:
                res[x] = np.argmax(out)
            else:
                res[x] = random.choice(maxList)
                # if x is maxPlayer:
                # print("More than one")
                # print("res = " + str(res))
            # else:
            #     res[x] = -1

        for x, player in enumerate(playerList):
            if player.score > playerList[maxPlayer].score:
                maxPlayer = x

        # pressed = pygame.key.get_pressed()
        DrawWindow(WINDOW, playerList, enemyList, maxPlayer, numDead, numAlive)

        # if pressed[K_w]:
        #     mvtInputs = [1, 0, 0, 0]
        # elif pressed[K_a]:
        #     mvtInputs = [0, 1, 0, 0]
        # elif pressed[K_s]:
        #     mvtInputs = [0, 0, 1, 0]
        # elif pressed[K_d]:
        #     mvtInputs = [0, 0, 0, 1]

        for x, player in enumerate(playerList):
            if res[x] == 0:
                mvtInputs = [1, 0, 0, 0]
            elif res[x] == 1:
                mvtInputs = [0, 1, 0, 0]
            elif res[x] == 2:
                mvtInputs = [0, 0, 1, 0]
            elif res[x] == 3:
                mvtInputs = [0, 0, 0, 1]
            else:
                mvtInputs = [0, 0, 0, 0]
            player.updatePosition(mvtInputs)
            # enemy1.updatePosition(player.targetX, player.targetY)

            if timeCtr[x] > 60:

                playerList.pop(x)
                if x < maxPlayer:
                    maxPlayer -= 1
                if x == maxPlayer:
                    maxPlayer = 0
                print(len(playerList))
                enemyList[x].playerAlive = False
                ge[x].fitness -= 10
                nets.pop(x)
                ge.pop(x)

                numDead += 1
                continue

            # ge[genomeNum].fitness += 0.1
            if player.Death():
                playerList.pop(x)
                if x < maxPlayer:
                    maxPlayer -= 1
                if x == maxPlayer:
                    maxPlayer = 0
                enemyList[x].playerAlive = False
                ge[x].fitness -= 10
                ge.pop(x)
                nets.pop(x)
                numDead += 1
                continue
        clock.tick(30)


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
