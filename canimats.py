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

class CAnimat(cell.Cell):
    SenseFoodRadius = 5
    MaxEnergy = 1000
    #four directions in which the animat can move
    Speeds = [[0, 1], [1, 0], [0, -1], [-1, 0]]

    def __init__(self, x, y, env):
        self.cellType = 3
        self.color = cell.RED
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
            direction = 1
        if nextY < 0:
            direction = 0
        nextX = self.x + self.Speeds[direction][0]
        nextY = self.y + self.Speeds[direction][1]
        if self.env.grids[nextX][nextY].isWall():
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
        #print ("min dist: ", minDist)
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

    def senseFood(self, foods):
        foodToPick = None
        minDist = self.SenseFoodRadius + 1
        for food in foods:
            dist = self.calDistance(self.x, self.y, food.x, food.y)
            if  dist < minDist and dist < self.SenseFoodRadius:
                minDist = dist
                foodToPick = food
        return foodToPick


    def senseSignal(self, signals):
        return False

    def isHungry(self):
        if self.energy * 1.0 / self.MaxEnergy < 0.8:
            return True
        else:
            return False

    def eat(self):
        self.energy += self.MaxEnergy * 0.3
        #print("eating yumm")
        if self.energy > self.MaxEnergy:
            self.energy = self.MaxEnergy
            
 #   def pickup(self):
 #       self.color = cell.BLACK

    def update(self, foods, nonfoods):
        if self.executingAction == True:
            #print("executingAction" + str(self.lastAction))
            self.decodeAndExecuteAction(self.lastAction, foods, nonfoods)
        else:
            #print("not executingAction")
            state = self.calState(foods, nonfoods)
            #print("energy = " + str(self.energy) + " state = " + str(state))
            food = self.senseFood(foods)
            nonfood = self.senseFood(nonfoods)
            reward = 0
            if food is not None and self.x == food.x and self.y == food.y and self.lastAction != 0:
                if self.isHungry():
                    reward = 100
   #             elif not self.isHungry() and self.isFoodInHand:
    #                reward = 100
                else:
                    reward = -10
                #self.eat()
                #self.env.destroyFood(food)
            

            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, reward, state)				

            self.lastState = self.calState(foods, nonfoods)
            self.lastAction = self.ai.chooseAction(state)
            
            #print(self.energy, self.lastState, self.lastAction)

            #self.moveInDirection(self.lastAction)
            self.decodeAndExecuteAction(self.lastAction, foods, nonfoods)
        
        
    def calDistance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def calState(self, foods, nonfoods):
        food = self.senseFood(foods)
        nonfood = self.senseFood(nonfoods)
        if food is None and nonfood is None:
            return self.isHungry(), 0
#        elif self.isFoodInHand:
 #           if(self.isHungry()):
                #print("hungry, food in hand")
  #              self.eat()
                #self.env.destroyFood(food)
   #             return 0
    #        return False,4
        elif food is not None and nonfood is None:
            return self.isHungry(), 1
        elif food is not None and self.isAtFoodSource:
            #print("not hungry, at food source")
            self.eat()
            self.env.destroyFood(food)
            return self.isHungry(),6
        else:
            return 0

    def decodeAndExecuteAction(self, action, foods, nonfoods):
        '''if self.cache:
            print(self.cache)'''
        if action == 0: #move randomly
            self.moveInDirection(random.randrange(0, 4))
            #print("Move randomly")
        elif action == 1:  #move towards food
            #print("Move towards food")
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
                    #self.color = cell.BROWN
                    self.isFoodInHand = True
                    self.isAtFoodSource = True
            else:
                self.moveInDirection(random.randrange(0, 4))
        elif action == 2: #move towards nonfood
            #print("Move towards non food")
            nonfood = self.senseFood(nonfoods)
            if nonfood != None:
                if self.executingAction is False:
                    self.executingAction = True
                if self.moveTowardsTarget(nonfood.x, nonfood.y):
                    self.executingAction = False
            else:
                self.moveInDirection(random.randrange(0, 4))
	else:
                self.moveInDirection(random.randrange(0, 4))
        '''elif action == 3:   #pick up food
            #food = self.senseFood(foods)
            self.color = cell.RED
            #print("brown")
            self.executingAction = True
            self.isFoodInHand = True
            cacheLoc = self.getCacheLocation()
            #print(cacheLoc)
            if cacheLoc :
                #print("Pick up")
                if (self.x,self.y) in self.env.foods:
                    self.env.destroyFood((self.x,self.y))
                while not self.moveTowardsCache(cacheLoc[0],cacheLoc[1]):
                    pass
                self.executingAction = False
                self.isAtCache = True
                self.isAtFoodSource = False
            else:
                self.executingAction = False
                self.color = cell.RED
                self.isFoodInHand = False
            
        elif action == 4:   #put down food
            self.color = cell.RED
            self.isFoodInHand = False
            self.isAtCache = False
            #print("Putting down")
            end_time = time.time()
            #self.env.cachewriter.writerow(("Caching : ", end_time-self.env.curr_time, self.env.currentSeason))
            cachefile = open("Cacheobs"+self.env.timestamp+".csv",'a')
            cachewriter = csv.writer(cachefile)
            cachewriter.writerow(("Caching ",end_time - self.env.curr_time, self.env.currentSeason))
            cachefile.flush()
            cachefile.close()
            #print("Caching : ", end_time-self.env.curr_time, self.env.currentSeason)
            key = (self.x,self.y)
            if key in self.env.FoodInCache:
                self.env.FoodInCache[(self.x,self.y)] = self.env.FoodInCache[(self.x,self.y)] + 1
                self.flashWallColor()
            else:
                self.env.FoodInCache[(self.x,self.y)] = 1
        elif action == 5:
            self.isAtFoodSource = False
            end_time = time.time()
            #self.env.digwriter.writerow(("Digging : ", end_time-self.env.curr_time, self.env.currentSeason))
            digfile = open("Digobs"+self.env.timestamp+".csv",'a')
            digwriter = csv.writer(digfile)
            digwriter.writerow(("Dig ",end_time - self.env.curr_time, self.env.currentSeason))
            digfile.flush()
            digfile.close()
            #print("Digging : ", end_time-self.env.curr_time, self.env.currentSeason)
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
            #print("Move towards cache")
            #self.moveInDirection(random.randrange(0, 4))
            self.executingAction = True
            cacheLoc = self.getCacheLocation()
            #print(cacheLoc)
            if cacheLoc:
                while not self.moveTowardsCache(cacheLoc[0],cacheLoc[1]):
                    pass
                self.executingAction = False
                self.isAtCache = True
            else:
                self.executingAction = False
                self.moveInDirection(random.randrange(0, 4))'''
                
