from __future__ import absolute_import
import cell

class Food(cell.Cell):
	def __init__(self, x, y):
		self.cellType = 1
		self.color = cell.GREEN
		self.x = x
		self.y= y

class NonFood(cell.Cell):
	def __init__(self, x, y):
		self.cellType = 2
		self.color = cell.BROWN
		self.x = x
		self.y = y