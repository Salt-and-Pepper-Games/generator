import random

SWITCH = 1
DRILL = 0

class Node:
	def __init__(self, x, y, color):
		self.planar_neighbors = []

		self.entire_column = []
		# empty is used to render the level at the end
		self.empty = False
		# visited is used to check if a tile is part of the path
		self.visited = False
		self.x = x
		self.y = y
		self.color = color
		self.column_taken = False
		self.is_switch = False
		self.switched_node = None

		self.searched = False

def build_grid(width, height):
	grid = []
	for x in xrange(width):
		col_array = []
		for y in xrange(height):
			color_array = []
			for color in xrange(8):
				color_array.append(Node(x, y, color))
			col_array.append(color_array)
		grid.append(col_array)

	def get_planar_neighbors(x, y):
		neighbors = []
		for (i, j) in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
			if x + i >= 0 and x + i < width and y + j >= 0 and y + j < height and (i == 0 or j == 0):
				neighbors.append((x + i, y + j))
		return neighbors

	for x in xrange(width):
		for y in xrange(height):
			planar_neighbors = get_planar_neighbors(x, y)
			entire_column = [grid[x][y][color] for color in xrange(8)]
			for color in xrange(8):
				grid[x][y][color].entire_column = entire_column
				for neighbor in planar_neighbors:
					grid[x][y][color].planar_neighbors.append(grid[neighbor[0]][neighbor[1]][color])
	return grid

# returns the true neighbors (accounting for switches) of a node
def get_neighbors(node):
	neighbors = []
	for neighbor in node.planar_neighbors:
		if neighbor.is_switch:
			neighbors.append(neighbor.switched_node)
		else:
			neighbors.append(neighbor)
	return neighbors

def generate(width, height, x_start, y_start, empty_prob=.5, switch_prob=.2, drill_prob=.3):
	grid = build_grid(width, height)
	walls = get_potential_neighboring_walls()
	while len(walls) > 0:
		#O(1) randomization scheme
		swap_indx = random.randint(0, len(walls) - 1)
		old_wall = walls[-1]
		idx = random.randint(0, len(walls) - 1)
		walls[-1] = walls[swap_indx]
		walls[swap_indx] = old_wall

		# proposed a new edge between the start and the finish
		start, finish = walls.pop()
		



