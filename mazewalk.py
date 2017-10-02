import random

SWITCH = 1
DRILL = 0

SWITCH_COLORS = [0, 1, 2, 4]

def build_wall(start, finish, wall_type):
	return (start, finish, wall_type)

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
		self.distance_from_start = None

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

def generate(width, height, x_start, y_start, empty_prob=.5, switch_prob=.2, drill_prob=.3):
	grid = build_grid(width, height)
	start = grid[x_start][y_start][0]
	start.distance_from_start = 0
	mark_switch_visited(start, 0)
	walls = mark_neighbors_visited_and_get_walls(grid[x_start][y_start][0])
	while len(walls) > 0:
		#O(1) randomization scheme
		swap_indx = random.randint(0, len(walls) - 1)
		old_wall = walls[-1]
		idx = random.randint(0, len(walls) - 1)
		walls[-1] = walls[swap_indx]
		walls[swap_indx] = old_wall

		# proposed a new edge between the start and the finish
		start, finish, wall_type = walls.pop()
		
		#TODO do the rest
		if wall_type == DRILL:
			if is_drill_valid(start, finish):
				mark_drill_visited(finish)
				finish.distance_from_start = start.distance_from_start + 1
				walls += mark_neighbors_visited_and_get_walls(finish)
		elif wall_type == SWITCH:
			switch_color = start.color ^ finish.color
			if is_switch_valid(start, finish, switch_color):
				mark_switch_visited(finish, switch_color)
				finish.distance_from_start = start.distance_from_start + 1
				walls += mark_neighbors_visited_and_get_walls(finish)
	return grid

"""
FLOOD FILL AND WALL CODE 
"""
def get_new_walls(node):
	new_walls = []
	for neighbor in node.planar_neighbors:
		if not neighbor.column_taken:
			# add drill move
			new_walls.append(build_wall(node, neighbor, DRILL))
			# add switch moves
			new_walls += [build_wall(node, neighbor.entire_column[neighbor.color ^ switch_color], SWITCH) for switch_color in SWITCH_COLORS]
	return new_walls

def visit_empty_neighbors(node):
	# TODO flood fill empty neighbors and mark visited, return list of all nodes marked visited
	visited_nodes = []
	for neighbor in get_neighbors(node):
		if neighbor.empty and not neighbor.visited:
			neighbor.visited = True
			neighbor.distance_from_start = node.distance_from_start + 1
			visited_nodes.append(neighbor)
			visited_nodes += visit_empty_neighbors(neighbor)
	return visited_nodes

def mark_neighbors_visited_and_get_walls(node):
	new_walls = []
	visited_nodes = []

	visited_nodes.append(node)

	visited_nodes += visit_empty_neighbors(node)

	for new_node in visited_nodes:
		new_walls += get_new_walls(new_node)

	return new_walls


# if we drill out this node will there be a loop
def check_creates_loop(node, switched_node=None, verbose = False):
	if switched_node == None:
		switched_node = node
	visited_in_nodes = set(map(lambda x:(x.x,x.y,x.color), filter(lambda x:x.visited, can_reach_me(switched_node))))
	visited_out_nodes = set(map(lambda x:(x.x,x.y,x.color), filter(lambda x:x.visited, i_can_reach(node))))
	if verbose:
		print node.color
		print "can reach me " + str(visited_in_nodes)
		print "I can reach " + str(visited_out_nodes)
		print "union " + str(visited_in_nodes.union(visited_out_nodes))
	return len(visited_in_nodes) > 0 and len(visited_out_nodes) > 0 and len(visited_in_nodes.union(visited_out_nodes)) > 1

	
"""
--------------\
DRILL CODE ++++	>
--------------/
"""
def is_drill_valid(start, finish):
	# we only drill on a filled column which is not taken
	if start.visited and not finish.column_taken and not finish.color == 0 and not finish.visited:
		# check that it won't create a loop
		# return not (check_creates_loop(finish) or check_drill_creates_unpassables(finish))
		return not check_creates_loop(finish)
	else:
		return False;

def mark_drill_visited(node):
	node.visited = True
	node.empty = True
	for col_neighbor in node.entire_column:
		col_neighbor.column_taken = True


"""
--------------\
SWITCH CODE 
	    o
	   /
	__/__
--------------/
"""

def is_switch_valid(start, finish, switch_color):
	if start.visited and not finish.column_taken and not finish.visited:
		return not (check_switch_creates_unpassables(finish, switch_color) or check_switch_creates_loop(finish, switch_color))
		#return not (check_switch_creates_loop(finish, switch_color))
	else:
		return False

def mark_switch_visited(node, switch_color):
	node.visited = True
	for col_neighbor in node.entire_column:
		col_neighbor.empty = True
		col_neighbor.column_taken = True
		col_neighbor.is_switch = True
		col_neighbor.switched_node = node.entire_column[col_neighbor.color ^ switch_color]

def check_switch_creates_unpassables(node, switch_color):
	# only check planar neighbors because switch neighbors already have column taken and cannot become un-passable hence no need to resolve them
	filled_planar_neighbors = filter(lambda x:not x.column_taken, node.planar_neighbors)
	for neighbor in filled_planar_neighbors:
		for double_neighbor in neighbor.planar_neighbors:
			if double_neighbor.is_switch:
				return True
	return False

def check_switch_creates_loop(node, switch_color):
	column = node.entire_column
	for color in xrange(len(column)):
		if check_creates_loop(column[color], column[color ^ switch_color]):
			return True
	return False

# Notes on black blocks
# Can always replace UNLESS you can reach the spot with every color and a switch is next to you
# in this case does it matter if we create a loop (there are probably two colors for which it wouldn't make a huge difference)?
# should we prevent this?
def eliminate_black_blocks(grid, width, height):
	for x in xrange(width):
		for y in xrange(height):
			if grid[x][y][0].column_taken:
				continue
			success = False
			print "Attempting to replaced black block @ " + str((x,y))
			for color in xrange(1, 8):
				if not check_creates_loop(grid[x][y][color], None, True):
					mark_drill_visited(grid[x][y][color])
					mark_neighbors_visited_and_get_walls(grid[x][y][color])
					success = True
					print "replaced black block @ " + str((x,y)) + " with color " + str(color)
					break
			if not success:
				print "FUCK"
	return grid

def node_to_char(node):
	empty_count = 0
	empty_color = None
	colors = ['e', 'R', 'G', 'Y', 'B', 'M', 'C', 'W']
	for col_neighbor in node.entire_column:
		if col_neighbor.empty:
			empty_count += 1
			empty_color = col_neighbor.color
	if empty_count == 0:
		# in the future there should not be any unpassable blocks at all
		# but for now just replace them with white blocks
		return '#'
	elif empty_count == 1:
		return colors[empty_color].lower()
	elif empty_count == 8:
		if node.is_switch:
			return colors[node.color ^ node.switched_node.color]
		else:
			return ' '
	else:
		pass
		# print "Invalid column"
		# print [n.empty for n in node.entire_column]

def stringify_grid(grid, width, height, start=(0, 0), end=None):
	if end is None:
		end = (width-1, height-1)
	level_string = ""
	level_string += "%d %d " % (start[0], start[1])
	level_string += "%d %d " % (end[0], end[1])
	level_string += "%d %d " % (width, height)
	for j in xrange(height):
		row = ""
		for i in xrange(width):
			row += node_to_char(grid[i][j][0]) + ' '
		level_string += row
	return level_string

# def build_level(width, height, start=(0, 0)):
# 	grid = generate(width, height, 0, 0)
# 	block, dist = pick_end_block(grid[0][0][0], width, height)
# 	for color in xrange(8):
# 		node = grid[block[0]][block[1]][color]
# 		node.visited = True
# 		node.empty = True
# 		node.is_switch = True
# 		node.switched_node = node
# 	return stringify_grid(grid, width, height, start, end=block)

def print_grid(grid, width, height, start=(0, 0), end=None):
	if end is None:
		end = (width-1, height-1)
	print "%d %d" % (start[0], start[1])
	print "%d %d" % (end[0], end[1])
	print "%d %d" % (width, height)
	for j in xrange(height):
		row = ""
		for i in xrange(width):
			row += node_to_char(grid[i][j][0]) + ' '
		print row

width = 4
height = 4
print "GO/ GO/  GO"
grid = generate(width, height, 0, 0)
print_grid(grid, width, height)
#grid = eliminate_black_blocks(grid, width, height)
#print_grid(grid, width, height)