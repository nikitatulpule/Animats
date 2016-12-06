'''
This file defines the enviroment of the project -> controls location of the food and non food, creation/destruction of food/non food, randomly spawning a new animat at a new location
'''
from __future__ import absolute_import
from cell import *
from animats import *
from canimats import *
from food import *
from six.moves import range

from random import randint
import threading
import time
import csv
from datetime import datetime

class Environment():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.grids =  [[None for col in range(int(w))] for row in range(int(h))]
        self.initGrids(w, h)
        self.animats = []
	self.canimats = []
        self.foods = []
        self.nonfoods = []
        #we have defined the season -> initially there is plenty of food source(summer/spring),
        #gradually the food sources decreases with time (fall) and finally becomes zero(winter)
        #it is during fall and winter that the animats learn to cache food
        self.seasonFood = [30,40,35,22,20,7,3,4,3,5,7,8,0,0,0]
        self.currentSeason = 0
        self.FoodInCache = {}
        self.curr_time = time.time()
        self.timestamp = str(datetime.now())
        '''self.cachefile = open("Cacheobs.csv",'wt')
        self.digfile = open("Digobs.csv",'wt')
        self.diefile = open("Dieobs.csv",'wt')
        self.cachewriter = csv.writer(self.cachefile)
        self.digwriter = csv.writer(self.digfile)
        self.diewriter = csv.writer(self.diefile)'''

    def initGrids(self, w, h):
        for i in range(int(w)):
            for j in range(int(h)):
                if i == 0 or j ==0 or i == w-1 or j == h-1:
                    self.grids[i][j] = Wall()
                else:
                    self.grids[i][j] = Road()
#randomly spawns an animat at a random location
    def createAnimats(self):
        x = randint(1,self.width)
        y = randint(1,self.height)
        a = Animat(x,y, self)
        self.animats.append(a)

#randomly spawns an animat at a random location
    def createCAnimats(self):
        x = randint(1,self.width)
        y = randint(1,self.height)
        a = CAnimat(x,y, self)
        self.canimats.append(a)
        
#spawns an animat at a random location; it inherits the ai of the dead animat
    def createAdvAnimat(self, advAI):
        x = randint(0,self.width-1)
        y = randint(0,self.height-1)
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
    
#creates food sources at random locations; frequency kept at 5 seconds
    def createFoods(self):
        self.destroyAllFood()
        for i in range(self.seasonFood[self.currentSeason]):
            x = randint(1,self.width-2)
            y = randint(1,self.height-2)
            self.foods.append(Food(x, y))
        self.currentSeason = (self.currentSeason+1)%len(self.seasonFood)
        threading.Timer(5.0, self.createFoods).start()
            
#destoys a food item; when an animat eats it or caches it
    def destroyFood(self,food):
        self.foods.remove(food)
     
    def destroyAllFood(self):
#        self.foods.clear()
	del self.foods[:]

#creates non food at random locations; their locations are kept fixed throughout the experiment
    def createNonFoods(self, num):
        #print (time.perf_counter())
        for i in range(num):
            x = randint(1,self.width-2)
            y = randint(1,self.height-2)
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
                end_time = time.time()
                diefile = open("Dieobs"+self.timestamp+".csv",'a')
                diewriter = csv.writer(diefile)
                diewriter.writerow(("Die ",end_time - self.curr_time, self.currentSeason))
                diefile.flush()
                diefile.close()
                #print("Die ",end_time - self.curr_time, self.currentSeason)
	
	for i in range(len(self.canimats)):
            self.canimats[i].update(self.foods, self.nonfoods)

        for i in range(len(self.canimats)):
            if i >= len(self.canimats):
                break
            if self.canimats[i].energy <= 0:
                #self.animats[i].ai.printQ()
                a = self.canimats[i]
                self.canimats.pop(i)
		#self.createAdvCAnimat(a.ai)
                #print("Die ",end_time - self.curr_time, self.currentSeason)
