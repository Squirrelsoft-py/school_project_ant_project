import random
import math
import pygame
from pygame.locals import *
import random
import time

global food_amount, simulate_distance, num_ants, food_value, nsteps, num_nest, max_x, max_y, lifetime, speed, image
food_amount = 100
simulate_distance = 100000
num_ants = 5
food_value = 50
num_antGuards = 10
nsteps = 0
num_nest = 2
max_x = 515
max_y = 515
lifetime = 1000
speed = 5

pygame.init()

clock = pygame.time.Clock()

# Set up the drawing window
screen = pygame.display.set_mode([max_x + 15, max_y + 15])

# Initialize Text
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

sprites = [pygame.image.load("designs/ant.png"), pygame.image.load("designs/ant_nest.png"),
           pygame.image.load("designs/ant_guard.png"), pygame.image.load("designs/food_full.png"),
           pygame.image.load("designs/food_empty.png"), pygame.image.load("designs/background.png"),
           pygame.image.load("designs/rival.png")]

image = sprites[6].copy()

class World(object):
    def __init__(self):
        self.nests = []
        self.food = []

    def create(self):
        """
        World is created and filled with Nests and Ants. Each Nest belongs to one Queen
        """
        # Create Nest
        for i in range(num_nest):
            random_x = random.randint(100, max_x - 100)
            random_y = random.randint(100, max_y - 100)

            MyNest = Nest(random_x, random_y)
            # Append nest to nest list
            MyNest.generatePointsForCircle(100, MyNest.x, MyNest.y)
            self.nests.append(MyNest)
            # print(self.nests)

        # Fill Nest with 5 Ants
        for nest in self.nests:
            for i in range(num_ants):
                MyAnt = Ant(nest)
                nest.add_ant(MyAnt)
            for i in range(num_antGuards):
                MyAntGuard = AntGuard(nest, nest.pointsForCircle)
                nest.add_antGuard(MyAntGuard)
            nest.add_queen(Queen(nest))

        # Add 10 food sources at random locations
        for i in range(food_amount):
            self.food.append(Food(random.randint(15, max_x), random.randint(15, max_y)))

        MyPlayer = Player(100, 100)
        return MyNest, MyPlayer

    def simulate(self, MyNest, MyPlayer):
        while True:

            clock.tick(60)
            pygame.display.set_caption("Ant in Python")
            MyPlayer.walk()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(-1)
            screen.fill((255, 255, 255))
            screen.blit(sprites[5], (0, 0))

            for N in self.nests:
                N.check_foundFood()
                for n in N.ants:
                    n.walk()
                    n.check_food(self.food)
                for n in N.antGuards:
                    n.walk_circle_around_nest()

            for f in self.food:
                if f.amount > 0:
                    screen.blit(sprites[3], (f.x - sprites[3].get_size()[0] / 2, f.y - sprites[3].get_size()[1] / 2))
                else:
                    screen.blit(sprites[4], (f.x - sprites[4].get_size()[0] / 2, f.y - sprites[4].get_size()[1] / 2))
            for n in self.nests:
                screen.blit(sprites[1], (n.x - sprites[1].get_size()[0] / 2, n.y - sprites[1].get_size()[1] / 2))

            for nest in self.nests:
                for a in nest.ants:
                    screen.blit(sprites[0], (a.x - sprites[0].get_size()[0] / 2, a.y - sprites[0].get_size()[1] / 2))
                    if pygame.Rect(MyPlayer.x - sprites[6].get_size()[0] / 2, MyPlayer.y - sprites[6].get_size()[1] / 2, 20, 20).colliderect(pygame.Rect(a.x - sprites[0].get_size()[0] / 2, a.y - sprites[0].get_size()[1] / 2, 20, 20)):
                        nest.ants.pop(nest.ants.index(a))
                        MyPlayer.score += 1
                for ag in nest.antGuards:

                    screen.blit(sprites[2], (ag.x - sprites[2].get_size()[0] / 2, ag.y - sprites[2].get_size()[1] / 2))
                    if pygame.Rect(MyPlayer.x - sprites[6].get_size()[0] / 2, MyPlayer.y - sprites[6].get_size()[1] / 2, 20, 20).colliderect(pygame.Rect(ag.x - sprites[2].get_size()[0] / 2, ag.y - sprites[2].get_size()[1] / 2, 20, 20)):
                        screen.fill((0, 0, 0))
                        text_surface = font.render("U dead! (press r)", False, (200, 0, 0))
                        screen.blit(text_surface, ((max_x + 15) /2, ((max_y + 15) /2) - text_surface.get_size()[1]))
                        pygame.display.update()
                        time.sleep(2)
                        exit()

            screen.blit(image,(MyPlayer.x - image.get_size()[0] / 2, MyPlayer.y - image.get_size()[1] / 2))
            scoreboard = font.render(f"Score: {MyPlayer.score}", False, (0, 0, 0))
            screen.blit(scoreboard, (10,10))

            MyNest.MyQueen.check_populate()

            pygame.display.update()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = speed - 2
        self.score = 0

    def walk(self):
        global image
        # print(self.x, self.y)
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.x - 1*self.speed > 0:
            self.x -= 1 * self.speed
            image = pygame.transform.rotate(sprites[6].copy(), 90)
        if keys[K_RIGHT] and self.x + 1*self.speed < max_x + 15:
            self.x += 1 * self.speed
            image = pygame.transform.rotate(sprites[6].copy(), -90)
        if keys[K_UP] and self.y - 1*self.speed > 0:
            self.y -= 1 * self.speed
            image = pygame.transform.rotate(sprites[6].copy(), 0)
        if keys[K_DOWN] and self.y + 1*self.speed < max_y + 15:
            self.y += 1 * self.speed
            image = pygame.transform.rotate(sprites[6].copy(), 180)


class Nest(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ants = []
        self.food_store = 0
        self.known_foods = []
        self.silent = True
        self.MyQueen = None
        self.antGuards = []
        self.pointsForCircle = []

    def add_ant(self, ant):
        """ Adds an ant to the nest"""
        self.ants.append(ant)

    def add_queen(self, queen):
        self.MyQueen = queen

    def add_antGuard(self, antGuard):
        self.antGuards.append(antGuard)

    def generatePointsForCircle(self, radius, x, y):
        # The lower this value the higher quality the circle is with more points generated
        stepSize = 0.5

        currentPosition = 0

        while currentPosition < 2 * math.pi:
            self.pointsForCircle.append(
                (round(radius * math.cos(currentPosition) + x), round(radius * math.sin(currentPosition) + y)))
            currentPosition += stepSize

    def check_foundFood(self):
        """
        Checks for each ant of the nest, if they
        have found food and are currently in the Nest
        """
        for A in self.ants:
            # if ant is in nest and carries food
            if ((A.x, A.y) == (self.x, self.y)) and A.food_store > 0:
                if not self.silent: print("FoodLocation is in Nest")

                # Fill Food Store and add Food Source Location
                self.food_store += A.food_store
                if A.foundFood not in self.known_foods:
                    self.known_foods.append(A.foundFood)

                # Remove Food from Ant and set random target food
                A.target_food = random.choice(self.known_foods)
                A.foundFood = False
                A.food_store = 0


class Queen(object):
    def __init__(self, MyNest):
        self.MyNest = MyNest

    def check_populate(self):
        if self.MyNest.food_store >= 5:
            self.MyNest.food_store -= 5
            self.MyNest.add_ant(Ant(self.MyNest))


class Ant(object):
    def __init__(self, MyNest):
        # Current position of Ant
        self.x = MyNest.x
        self.y = MyNest.y

        # Lifetime of Ant
        self.lifetime = lifetime

        # Maximum speed of ant
        self.speed = speed

        # Food store of the ant, e.g. how much food
        # does the ant carry currently
        self.food_store = 0

        # nest of the ant
        self.MyNest = MyNest

        # State of Ants
        self.foundFood = False

        # If not False, self.target_food is a tuple with the food location (x, y)
        self.target_food = False

        # List of all x and y coordinates walked on
        self.xpast = []
        self.ypast = []

        # Maximum number of past steps that are drawn for the ant
        self.nsteps = nsteps
        self.silent = True

    def check_food(self, food):
        """
        Checks if ant has found food
        """
        for f in food:
            if (self.x, self.y) == (f.x, f.y):
                if not self.silent: print("YAY!, I found Food", self.x, self.y)

                # If food is not empty, collect food
                if f.amount >= 1:
                    self.foundFood = self.x, self.y
                    self.food_store += 1
                    f.amount -= 1
                # If food is empty, remove target from Ant
                else:
                    self.target_food = False

    def walk_random(self):
        """ Ant walks in random direction """
        dir_x = random.randint(-1 * self.speed, 1 * self.speed)
        while not self.x + dir_x > 0 or not self.x + dir_x < 500:
            dir_x = random.randint(-1 * self.speed, 1 * self.speed)
        self.x += dir_x

        dir_y = random.randint(-1 * self.speed, 1 * self.speed)
        while not self.y + dir_y > 0 or not self.y + dir_y < 500:
            dir_y = random.randint(-1 * self.speed, 1 * self.speed)
        self.y += dir_y

    def walk_toTarget(self, target):
        """ Ant walks to given Target """
        xdistance = target[0] - self.x
        ydistance = target[1] - self.y

        """
        print(target)

        if target[0] > self.x:
            self.x += (1*self.speed)
        elif target[0] < self.x:
            self.x -= (1*self.speed)

        if target[1] > self.y:
            self.y += (1*self.speed)
        elif target[1] < self.y:
            self.y -= (1*self.speed)

    """
        if xdistance > 0:
            self.x += random.randint(0, 1 * self.speed)
        else:
            self.x += random.randint(-1 * self.speed, 0)

        if ydistance > 0:
            self.y += random.randint(0, 1 * self.speed)
        else:
            self.y += random.randint(-1 * self.speed, 0)

    def walk(self):
        """
        Determines in which direction the ant is going.
        It can go either in a random direction or to a
        given target.
        """
        self.lifetime -= 1

        # If Ant has not foundFood and has no food target: walk in
        # random direction
        if not self.foundFood and not self.target_food:
            self.walk_random()
            if not self.silent: print("Searching for food", self.x, self.y)

        # If Ant carries food, return to nest
        elif self.food_store > 0:
            self.walk_toTarget((self.MyNest.x, self.MyNest.y))
            if not self.silent: print("On my way to nest", self.x, self.y)

        # If Ant carries no food (has an empty food_store), but has target food: go to food
        # Oh my Good, who deleted this part of the Code. It´s crucial
        # for the Ants to go to a known food location

        elif self.food_store == 0 and self.target_food != False:
            self.walk_toTarget((self.target_food[0], self.target_food[1]))

        self.xpast.append(self.x)
        self.ypast.append(self.y)

        # Crop past coordinates to length of self.nsteps
        if len(self.xpast) > self.nsteps: self.xpast = self.xpast[1:]
        if len(self.ypast) > self.nsteps: self.ypast = self.ypast[1:]


class AntGuard(Ant):
    def __init__(self, MyNest, pointsForCircle):
        super().__init__(MyNest)
        self.currentPositionInCicle = []
        self.randomStartPos = 0
        self.randomStartPos = random.randint(0, len(pointsForCircle) - 1)
        self.randomStartX = pointsForCircle[self.randomStartPos][0]
        self.randomStartY = pointsForCircle[self.randomStartPos][1]
        self.currentTargetPosInList = self.randomStartPos
        self.nextTargetPosInList = self.currentTargetPosInList + 1
        self.distanceToNextPoint = 0
        self.pointsForCircle = pointsForCircle

    def walk_circle_around_nest(self):
        super().walk_toTarget(
            [self.pointsForCircle[self.currentTargetPosInList][0],
             self.pointsForCircle[self.currentTargetPosInList][1]])
        if round((((self.pointsForCircle[self.currentTargetPosInList][0] - self.x) ** 2) + (
                (self.pointsForCircle[self.currentTargetPosInList][1] - self.y) ** 2)) ** (0.5)) <= 4:
            self.nextTargetPosInList += 1
            self.currentTargetPosInList += 1
            if self.nextTargetPosInList >= len(self.pointsForCircle):
                self.nextTargetPosInList = 0
            if self.currentTargetPosInList >= len(self.pointsForCircle):
                self.currentTargetPosInList = 0

        self.xpast.append(self.x)
        self.ypast.append(self.y)

        # Crop past coordinates to length of self.nsteps
        if len(self.xpast) > self.nsteps: self.xpast = self.xpast[1:]
        if len(self.ypast) > self.nsteps: self.ypast = self.ypast[1:]


class Food(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.amount = random.randint(1, food_value)


# get_var()
MyWorld = World()
MyNest, MyPlayer = MyWorld.create()
MyWorld.simulate(MyNest, MyPlayer)
pygame.quit()
