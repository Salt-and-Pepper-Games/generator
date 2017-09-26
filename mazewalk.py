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

# returns a list of the true neighbors (accounting for switches) of a node
def get_neighbors(node):
	neighbors = []
	for neighbor in node.planar_neighbors:
		if neighbor.is_switch:
			neighbors.append(neighbor.switched_node)
		else:
			neighbors.append(neighbor)
	return neighbors

def can_reach_me(node):
	return node.planar_neighbors

def i_can_reach(node):
	return get_neighbors(node)

# if we drill out this node will there be a loop
def check_drill_creates_loop(node):
	visited_in_nodes = set(filter(lambda x:x.visited, can_reach_me(node)))
	visited_out_nodes = set(filter(lambda x:x.visited, i_can_reach(node)))
	return len(in_nodes) > 0 and len(out_nodes) > 0 and len(in_nodes.difference(out_nodes)) > 1

def check_drill_creates_unpassables(node):
	# only check planar neighbors because switch neighbors already have column taken and cannot become un-passable hence no need to resolve them
	filled_planar_neighbors = filter(lambda x:not x.column_taken, node.planar_neighbors)
	for neighbor in filled_planar_neighbors:
		is_black_block = True
		for node_in_column in neighbor.entire_column:
			empty_in_nodes = set(filter(lambda x:x.empty, can_reach_me(neighbors)))
			empty_out_nodes = set(filter(lambda x:x.empty, i_can_reach(neighbors)))
			if not (len(in_nodes) > 0 and len(out_nodes) > 0 and len(in_nodes.difference(out_nodes)) > 1):
				is_black_block = False
				break
		if is_black_block == True:
			return True
	return False

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
		

def is_drill_valid(start, finish):
	# we only drill on a filled column which is not taken
	if start.visited and not finish.column_taken and not finish.visited:
		# check that it won't create a loop
		return not (check_drill_creates_loop(finish) or check_drill_creates_unpassables())
	else:
		return False;

def mark_drill_visited_and_get_walls(node):
	new_walls = []
	visited_nodes = []

	mark_drill_visited(node)
	visited_nodes.append(node)

	visited_nodes += visit_empty_neighbors(node)

	for new_node in visited_nodes:
		new_walls += get_new_walls(new_node)

	return new_walls


def visit_empty_neighbors(node):
	# TODO flood fill empty neighbors and mark visited, return list of all nodes marked visited

def mark_drill_visited(node):
	node.visited = True
	node.empty = True
	for col_neighbor in node.entire_column:
		col_neighbor.column_taken = True

def get_new_walls(node):
