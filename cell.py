
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0) #border
WHITE = (255, 255, 255) #background
BLUE =  (  0,   0, 255) #animat
GREEN = (  0, 255,   0) #food source
RED =   (255,   0,   0) #cache
YELLOW = (255,255,0)    
BROWN = (92,51,10)  #non food

class Cell():
	Size = 10
	def __init__(self, cellType, color):
		self.cellType = cellType
		self.color = color


	def isWall(self):
		return self.cellType == -1

	def isFood(self):
		return self.cellType == 1

	def isNonFood(self):
		return self.cellType == 2

	def isAnimat(self):
		return self.cellType == 3
    


class Wall(Cell):
    def __init__(self):
        self.cellType = -1
        self.color = BLACK

    def changeColor(self,color):
        self.color = color

class Road(Cell):
	def __init__(self):
		self.cellType = 0
		self.color = WHITE
