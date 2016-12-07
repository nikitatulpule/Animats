#!/usr/bin/python

#from numpy import *
from __future__ import absolute_import
from __future__ import print_function
import random
from six.moves import range

class State():
    SenseNothing = 0
    SenseFood = 1
    SenseNonFood = 2
    #SenseFoodAndNonFood = 3
    Hungry = True
    NotHungry = False  
    FoodInHand = 4
    AtCache = 5
    AtFoodSource = 6


class Action():
    MoveRandomly = 0
    MoveTowardsFood = 1
    MoveTowardsNonFood = 2
    PickUpFood = 3
    PutDownFood = 4
    DigUpFood = 5
    MoveToCache = 6

class Actions():
    a = {}
    a[(State.SenseNothing)] = [Action.MoveRandomly]
    a[(State.Hungry, State.SenseNothing)] = [Action.MoveRandomly,Action.MoveToCache]
    a[(State.NotHungry, State.SenseNothing)] = [Action.MoveRandomly]
    a[(State.Hungry, State.SenseFood)] = [Action.MoveRandomly,Action.MoveTowardsFood]
    a[(State.NotHungry, State.SenseFood)] = [Action.MoveRandomly,Action.MoveTowardsFood]
    a[(State.NotHungry, State.AtFoodSource)] = [Action.MoveRandomly,Action.PickUpFood]
    a[(State.Hungry, State.AtFoodSource)] = [Action.MoveRandomly,Action.DigUpFood]
    a[(State.AtCache , State.NotHungry, State.FoodInHand)] = [Action.MoveRandomly,Action.PutDownFood]
    a[(State.NotHungry,State.FoodInHand)] = [Action.MoveRandomly,Action.MoveToCache]
    a[(State.AtCache, State.Hungry)] = [Action.MoveRandomly,Action.DigUpFood]
    a[(State.AtCache, State.NotHungry)] = [Action.MoveRandomly]
    
    a[(State.Hungry, State.SenseNonFood)] = [Action.MoveRandomly, Action.MoveTowardsNonFood]
    a[(State.NotHungry, State.SenseNonFood)] = [Action.MoveRandomly, Action.MoveTowardsNonFood]

  
class QLearn():
	
    def __init__(self, actions, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q = {}

        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions
        self.lastAction = None

    def setQ(self, state, action, value):
        self.q[(state,action)] = value

    def getQ(self, state, action):
        return self.q.get((state, action), 0.0)
        # return self.q.get((state, action), 1.0)

#update the Q table depending on the state-action and the reward
    def learnQ(self, state, action, reward, value):
        oldv = self.q.get((state, action), None)
        if oldv is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)

#from the current state, select the most appropriate action for the animat
    def chooseAction(self, state, return_q=False):
        #q = [self.getQ(state, a) for a in self.actions]
        q = [self.getQ(state, a) for a in Actions.a[state]]
        maxQ = max(q)

        if random.random() < self.epsilon:
            minQ = min(q); mag = max(abs(minQ), abs(maxQ))
            #q = [q[i] + random.random() * mag - .5 * mag for i in range(len(self.actions))] # add random values to all the actions, recalculate maxQ
            q = [q[i] + random.random() * mag - .5 * mag for i in range(len(Actions.a[state]))]
            maxQ = max(q)

        count = q.count(maxQ)

        if count > 1:
            #best = [i for i in range(len(self.actions)) if q[i] == maxQ]
            best = [i for i in range(len(Actions.a[state])) if q[i] == maxQ]
            i = random.choice(best)
        else:
            i = q.index(maxQ)

        #action = self.actions[i]
        action = Actions.a[state][i]

        if return_q: # if they want it, give it!
            return action, q

        return action

    def learn(self, state1, action1, reward, state2):
        #maxqnew = max([self.getQ(state2, a) for a in self.actions])
        maxqnew = max([self.getQ(state2, a) for a in Actions.a[state2]])
        self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)
        #self.printQ()

    def printQ(self):
        
        for keys in self.q:
            print (keys,self.q[keys])


