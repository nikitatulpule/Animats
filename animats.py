'''
This file controls the state-action behavior of the animat
'''
from __future__ import print_function
from __future__ import absolute_import
import cell
import qlearning
import math
import random
import time
import csv
from six.moves import range

actionNum = 7

class Animat(cell.Cell):
    SenseFoodRadius = 10
    MaxEnergy = 1000
    #four directions in which the animat can move
    Speeds = [[0, 1], [1, 0], [0, -1], [-1, 0]]

    def __init__(self, x, y, env):
        self.cellType = 3
        self.color = cell.BLUE
        self.env = env

        self.x = x
        self.y = y
        self.speed = self.Speeds[0]

        self.energy = self.MaxEnergy

        self.ai = qlearning.QLearn(actions = list(range(actionNum)))
        self.lastState = None
        self.lastAction = None
        self.executingAction = False
        
        self.isFoodInHand = False
        self.isAtCache = False
        self.isAtFoodSource = False
        #each animat remembers the cache location when it comes across it
        self.cache = set()
        self.egoCentricMap = [[300,0] , [0,300] , [-300,0] , [0,-300]]
        
#using ego centric map, the animat gets the location of the cache with respect to its own position
#the cache closest to the animat is returned by this function
    def getCacheLocation(self):
        cacheLoc = []
        for x in self.cache:
            for y in self.egoCentricMap:
                if abs(x[0]-self.x)<=y[0] and abs(x[1]-self.y)<=y[1]:
                    cacheLoc.append(x[0])
                    cacheLoc.append(x[1])
                    return cacheLoc
        return cacheLoc

    def move(self):
        nextX = self.x + self.speed[0]
        nextY = self.y + self.speed[1]
        if self.env.grids[nextX][nextY].isWall():
            self.turnBackward()
        self.x = self.x + self.speed[0]
        self.y = self.y + self.speed[1]

    def moveInDirection(self, direction):

        nextX = self.x + self.Speeds[direction][0]
        nextY = self.y + self.Speeds[direction][1]
        if nextX<0:
            nextX = 2
        if nextY < 0:
            nextY = 2
        if nextX >= self.env.width-1:
            nextX = int(self.env.width)-4
        if nextY >= self.env.height-1:
            nextY = int(self.env.height)-4
            
        if self.env.grids[int(nextX)][int(nextY)].isWall():
            direction = (direction + 2) % 4

        self.x += self.Speeds[direction][0]
        self.y += self.Speeds[direction][1]
        self.energy -= 1

    def moveTowardsTarget(self, x, y):
        direction = -1
        minDist = self.calDistance(self.x, self.y, x, y)
        for i in range(4):
            nextX = self.x + self.Speeds[i][0]
            nextY = self.y + self.Speeds[i][1]
            if self.calDistance(nextX, nextY, x, y) < minDist:
                direction = i
                minDist = self.calDistance(self.x, self.y, nextX, nextY)
        if direction >= 0:
            self.moveInDirection(direction)
        if minDist - 0 < 0.001:
            return True
        else:
            return False
        
    def moveTowardsCache(self,x,y):
        direction = -1
        minDist = self.calDistance(self.x, self.y, x, y)
        for i in range(4):
            nextX = self.x + self.Speeds[i][0]
            nextY = self.y + self.Speeds[i][1]
            if self.calDistance(nextX, nextY, x, y) < minDist:
                direction = i
                minDist = self.calDistance(self.x, self.y, nextX, nextY)
        if direction >= 0:
            self.moveInDirection(direction)

        #return True is next position is the target
        if minDist - 0 < 0.001:
            return True
        else:
            return False

    def turnBackward(self):
        if self.speed[0] != 0:
            self.speed[0] *= -1
        elif self.speed[1] != 0:
            self.speed[1] *= -1

#finds the food closest to the animat such that the food lies within the sensing radius of the animat
    def senseFood(self, foods):
        foodToPick = None
        minDist = self.SenseFoodRadius + 1
        for food in foods:
            dist = self.calDistance(self.x, self.y, food.x, food.y)
            if  dist < minDist and dist < self.SenseFoodRadius:
                minDist = dist
                foodToPick = food
        return foodToPick
    
    def flashWallColor(self):
        for x in range(10):
            for i in range(int(self.env.width)):
                for j in range(int(self.env.height)):
                    if i == 0 or j ==0 or i == self.env.width-1 or j == self.env.height-1:
                        self.env.grids[i][j].changeColor(cell.WHITE)

            for i in range(int(self.env.width)):
                for j in range(int(self.env.height)):
                    if i == 0 or j ==0 or i == self.env.width-1 or j == self.env.height-1:
                        self.env.grids[i][j].changeColor(cell.BLACK)


    def isHungry(self):
        if self.energy * 1.0 / self.MaxEnergy < 0.8:
            return True
        else:
            return False

    def eat(self):
        self.energy += self.MaxEnergy * 0.3
        if self.energy > self.MaxEnergy:
            self.energy = self.MaxEnergy

#updates the state of the animat -> selects an action depending on the state of the animat
#reward is given to the animat depending on its state and action
#from the reward, the animat undergoes learning and its behavior is modified
    def update(self, foods, nonfoods):
        #if the animat is already executing some action, let it continue with that action
        if self.executingAction == True:
            self.decodeAndExecuteAction(self.lastAction, foods, nonfoods)
        else:
            #find the current state of the animat
            state = self.calState(foods, nonfoods)
            food = self.senseFood(foods)
            nonfood = self.senseFood(nonfoods)
            reward = 0
            #this module awards rewards to the animat
            '''
            if the animat is hungry and it at the food source, he gets a reward of 100, which will 
            encourage him in the future to come closer to the food source when he gets hungry
            he also gets a reward when he discovers a potential cache location
            this motivates him to discover not only the food sources, but also the cache locations where he can store the food
            the animat is charged a penalty of 20 when he gets to a food source and does not cache it or eat it
            '''
            if food is not None and self.x == food.x and self.y == food.y and self.lastAction != 0:
                if self.isHungry():
                    reward = 100
                elif not self.isHungry() and self.isFoodInHand:
                    reward = 100
                else:
                    reward = -10

            if nonfood is not None and self.x == nonfood.x and self.y == nonfood.y:
                self.cache.add((nonfood.x,nonfood.y))
                if self.lastAction != 0:
                    reward = 200
                    
            if food is None and self.isHungry() and not self.getCacheLocation():
                reward = -20
            
            '''
            once the rewards are granted, the animats undergo Qlearning and changes are updated to the Q table
            '''
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, reward, state)				

            #appropriate action is chosen depending on the state
            self.lastState = self.calState(foods, nonfoods)
            self.lastAction = self.ai.chooseAction(state)
            
            self.decodeAndExecuteAction(self.lastAction, foods, nonfoods)
        
        
    def calDistance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

#caclcuates the current state of the animat eg: hungry/ not hungry/ at cache/ sensing food/ food in hand?
    def calState(self, foods, nonfoods):
        food = self.senseFood(foods)
        nonfood = self.senseFood(nonfoods)
        if food is None and nonfood is None:#sensing nothing
            return self.isHungry(), 0
        elif self.isAtCache and self.isFoodInHand:#at cache and has food in hand -> cache if not hungry else eat
            if(self.isHungry()):
                self.eat()
                return 0
            return 5,False,4
        elif self.isFoodInHand:
            if(self.isHungry()):
                self.eat()
                return 0
            return False,4
        
        elif self.isAtCache:    #at cache -> eat if hungry
            return 5,self.isHungry()
        elif food is not None and nonfood is None:  #sensing food
            return self.isHungry(), 1
        elif food is not None and self.isAtFoodSource: #hungry and at food source -> eat
            self.eat()
            self.env.destroyFood(food)
            return self.isHungry(),6
        else:   #default state -> move randomly
            return 0

#performs the action returned by the qlearning
    def decodeAndExecuteAction(self, action, foods, nonfoods):
        if action == 0: #move randomly
            self.moveInDirection(random.randrange(0, 4))
            
        elif action == 1:  #move towards food
            food = self.senseFood(foods)
            if food != None:
                if self.executingAction is False:
                    self.executingAction = True
                while not self.moveTowardsTarget(food.x, food.y):
                    pass
                self.executingAction = False
                if self.isHungry(): #animat was hungry and now is at food source ->eat food
                    self.eat()
                    self.env.destroyFood(food)
                else:           #animat is not hungry and is at food source -> pick up food
                    self.isFoodInHand = True
                    self.isAtFoodSource = True
            else:
                self.moveInDirection(random.randrange(0, 4))
                
        elif action == 2: #move towards nonfood
            nonfood = self.senseFood(nonfoods)
            if nonfood != None:
                if self.executingAction is False:
                    self.executingAction = True
                if self.moveTowardsTarget(nonfood.x, nonfood.y):
                    self.executingAction = False
            else:
                self.moveInDirection(random.randrange(0, 4))
                
        elif action == 3:   #pick up food
            self.color = cell.RED
            self.executingAction = True
            self.isFoodInHand = True
            cacheLoc = self.getCacheLocation()
            if cacheLoc :
                if (self.x,self.y) in self.env.foods:
                    self.env.destroyFood((self.x,self.y))
                while not self.moveTowardsCache(cacheLoc[0],cacheLoc[1]):
                    pass
                self.executingAction = False
                self.isAtCache = True
                self.isAtFoodSource = False
            else:
                self.executingAction = False
                self.color = cell.BLUE
                self.isFoodInHand = False
            
        elif action == 4:   #put down food = caching 
            self.color = cell.BLUE
            self.isFoodInHand = False
            self.isAtCache = False
            #output written in .csv file for observation of animat behavior
            '''end_time = time.time()
            cachefile = open("Cacheobs"+self.env.timestamp+".csv",'a')
            cachewriter = csv.writer(cachefile)
            cachewriter.writerow(("Caching ",end_time - self.env.curr_time, self.env.currentSeason))
            cachefile.flush()
            cachefile.close()'''
            key = (self.x,self.y)
            if key in self.env.FoodInCache:
                self.env.FoodInCache[(self.x,self.y)] = self.env.FoodInCache[(self.x,self.y)] + 1
                self.flashWallColor()
            else:
                self.env.FoodInCache[(self.x,self.y)] = 1
                
        elif action == 5:   #dig up food and eat it
            self.isAtFoodSource = False
            #output written in .csv file for observation of animat behavior
            '''end_time = time.time()
            digfile = open("Digobs"+self.env.timestamp+".csv",'a')
            digwriter = csv.writer(digfile)
            digwriter.writerow(("Dig ",end_time - self.env.curr_time, self.env.currentSeason))
            digfile.flush()
            digfile.close()'''
            key = (self.x,self.y)
            if key in self.env.FoodInCache:
                self.eat()
                self.flashWallColor()
                self.env.FoodInCache[key] -= 1
                if self.env.FoodInCache[key] == 0:
                    del self.env.FoodInCache[key]
            else:
                self.executingAction = False
                self.moveInDirection(random.randrange(0, 4))
            
        elif action == 6:   #move towards cache
            self.executingAction = True
            cacheLoc = self.getCacheLocation()
            if cacheLoc:
                while not self.moveTowardsCache(cacheLoc[0],cacheLoc[1]):
                    pass
                self.executingAction = False
                self.isAtCache = True
            else:
                self.executingAction = False
                self.moveInDirection(random.randrange(0, 4))
