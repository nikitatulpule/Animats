from __future__ import absolute_import
from cell import *
from animats import *
from food import *
from six.moves import range

from random import randint
import threading

class Environment():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.grids =  [[None for col in range(int(w))] for row in range(int(h))]
        self.initGrids(w, h)
        self.animats = []
        self.foods = []
        self.nonfoods = []
        self.seasonFood = [30,40,35,22,20,7,3,4,3,5,7,8]
        self.currentSeason = 0

    def initGrids(self, w, h):
        for i in range(int(w)):
            for j in range(int(h)):
                if i == 0 or j ==0 or i == w-1 or j == h-1:
                    self.grids[i][j] = Wall()
                else:
                    self.grids[i][j] = Road()

    def createAnimats(self):
        x = randint(0,self.width)
        y = randint(0,self.height)
        a = Animat(x,y, self)
        self.animats.append(a)
        
    def createAdvAnimat(self, advAI):
        x = randint(0,self.width)
        y = randint(0,self.height)
        a = Animat(x,y, self)
        a.ai = advAI
        self.animats.append(a)

    '''
    def createFoods(self, num):
        for i in range(num):
            x = randint(0,self.width)
            y = randint(0,self.height)
            self.foods.append(Food(x, y))
    '''
    
    def createFoods(self):
        self.destroyAllFood()
        for i in range(self.seasonFood[self.currentSeason]):
            x = randint(0,self.width)
            y = randint(0,self.height)
            self.foods.append(Food(x+1, y+1))
        self.currentSeason = (self.currentSeason+1)%len(self.seasonFood)
        threading.Timer(2.0, self.createFoods).start()
            
    def destroyFood(self,food):
        self.foods.remove(food)
        
    def destroyAllFood(self):
        self.foods.clear()

    def createNonFoods(self, num):
        for i in range(num):
            x = randint(0,self.width)
            y = randint(0,self.height)
            self.nonfoods.append(NonFood(x, y))

    def update(self):
        for i in range(len(self.animats)):
            self.animats[i].update(self.foods, self.nonfoods)

        for i in range(len(self.animats)):
            if i >= len(self.animats):
                break
            if self.animats[i].energy <= 0:
                #self.animats[i].ai.printQ()
                a = self.animats[i]
                self.animats.pop(i)
                self.createAdvAnimat(a.ai)
                print("Die")



