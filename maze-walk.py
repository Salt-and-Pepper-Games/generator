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
		self.is_column_taken = False
		self.is_switch = False
		self.switched_node = None

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

def generate(width, height, x_start, y_start):
	grid = build_grid(width, height)
	# print grid[0][0][0].planar_neighbors
	#grid[0][0][0].visited = True
	walls = make_move_if_valid(grid, None, grid[0][0][0], SWITCH)

	while len(walls) > 0:
		index = random.randint(0, len(walls) - 1)
		n1, n2, move_type = walls[index]
		# print("(%d, %d) => (%d, %d)" % (wall[0].x, wall[0].y, wall[1].x, wall[1].y))
		new_walls = make_move_if_valid(grid, n1, n2, move_type)
		walls.extend(new_walls)
		del walls[index]

	replace_black_blocks(grid)
	return grid

def get_visited_neighbor_count(node):
	visited_neighbors = 0
	for neighbor in node.planar_neighbors:
		if neighbor.visited:
			visited_neighbors += 1
	return visited_neighbors

def get_empty_neighbors(node):
	empty_nodes = []
	neighbors = list(node.planar_neighbors)
	if node.is_switch:
		neighbors.append(node.switched_node)
	for neighbor in neighbors:
		if neighbor.empty and not neighbor.visited:
			empty_nodes.append(neighbor)
	return empty_nodes

def get_switch_color(color1, color2):
	# it's just a xor but it's a little confusing so i made a function
	return color1 ^ color2

def mark_visited(node):
	empty_nodes = [node]
	new_walls = []

	while len(empty_nodes) > 0:
		empty_node = empty_nodes.pop()

		#TODO add diagonal connections
		for x in empty_node.planar_neighbors:
			# handling the case where it's a switch
			true_node = x
			if x.is_switch:
				# print("Switching")
				true_node = x.switched_node
				# check that it's not visited to avoid a loop
			if not true_node.visited:
				if true_node.empty:
					empty_nodes.append(true_node)
				if not (empty_node.color == 0 and true_node.color == 0):
					new_walls.append((empty_node, true_node, DRILL))
				for potential_switch_color in [0, 1, 2, 4]:
					#for potential_switch_color in [0]:
					# not sure we want to add EVERY switch wall
					# they're all effectively the same thing: add a switch
					# new_walls.extend(get_switch_walls(grid, n2.x, n2.y, switch_color))
					# instead, just add one for each :
					new_walls.append((empty_node, true_node.entire_column[true_node.color ^ potential_switch_color], SWITCH))
					# pass
		# print(empty_node.planar_neighbors)

		empty_node.visited = True
		empty_node.empty = True
		# marking the column as taken if it's not already
		if not empty_node.is_column_taken:
			for column_node in empty_node.entire_column:
				column_node.is_column_taken = True
		empty_nodes.extend(get_empty_neighbors(empty_node))

	return new_walls

def get_switch_walls(grid, x, y, bitmask):
	new_walls = []
	for color in xrange(8):
		new_walls.append((grid[x][y][color], grid[x][y][color ^ bitmask]))
	return new_walls

def make_move_if_valid(grid, n1, n2, move_type):
	new_walls = []
	# print move_type
	if move_type is SWITCH and not n2.visited and not n2.is_column_taken:
		# print("Deleting column")
		# checking if it's okay to delete this block on EVERY floor
		# to do this, we need to check that we won't create a loop in the path on every floor
		# a loop would occur if the block we are going to remove had two or more visited neighbors
		ok_to_switch = True
		neighbor_counts = []
		switch_color = 0 if n1 is None else get_switch_color(n1.color, n2.color)
		for color in xrange(8):
			node = grid[n2.x][n2.y][color]
			if n1 is None or n1.color == n2.color:
				visited_neighbors = get_visited_neighbor_count(node)
				neighbor_counts.append(visited_neighbors)
				if visited_neighbors > 1:
					ok_to_switch = False
					break
			else:
				visited_neighbor_us = get_visited_neighbor_count(node)
				visited_neighbor_other = get_visited_neighbor_count(node.entire_column[switch_color ^ color])
				neighbor_counts.append(visited_neighbor_us)
				if visited_neighbor_us > 0 and visited_neighbor_other > 0:
					ok_to_switch = False
					break
		if ok_to_switch:
			print (() if n1 is None else (n1.x, n1.y, n1.color)), (n2.x, n2.y, n2.color), switch_color
			# print("Ok to delete")
			for node in n2.entire_column:
				node.is_switch = True
				node.switched_node = node.entire_column[node.color ^ switch_color]
				node.is_column_taken = True
			for color in xrange(8):
				node_to_switch = grid[n2.x][n2.y][color]
				# if the node to delete has a visited neighbor, it is part of the path. therefore, we want to mark it as visited so it will be treated as part of the path
				# if the node to delete is a loner, it is not a part of the path. so we don't mark it visited so it will be included in the path in the future
				node_to_switch.empty = True
				# print color, switch_color, neighbor_counts
				if neighbor_counts[switch_color ^ color] > 0 or color == n2.color:
					# print("Deleting color %d" % color)
					new_walls.extend(mark_visited(node_to_switch))

			#TODO choose to add switch or leave it be
			# maybe this is all we need
		else:
			pass
			# print("not ok to switch")
	elif move_type is DRILL:
		# turning a wall into a colored block
		if not n2.visited and not n2.is_column_taken:
			# only care if it's empty or if it won't create a loop
			if n2.empty or get_visited_neighbor_count(n2) < 2:
				# now we're exploring a new node
				new_walls.extend(mark_visited(n2))
				# TODO need to mark is_column_taken to true for every node in column
				for node in n2.entire_column:
					node.is_column_taken = True
		
	return new_walls

def replace_black_blocks(grid):
	for i in xrange(len(grid)):
		for j in xrange(len(grid[i])):
			if not grid[i][j][0].is_column_taken:
				# it's a black block
				lst = range(8)
				random.shuffle(lst)
				found_color = False
				for color in lst:
					if get_visited_neighbor_count(grid[i][j][color]) < 2:
						# mark_visited(grid[i][j][color])
						grid[i][j][color].empty = True
						found_color = True
						print "Replaced block at %d, %d" % (i, j)
						break
				if not found_color:
					print "Can't replace black block at %d, %d" % (i, j)



def node_to_char(node):
	empty_count = 0
	empty_color = None
	colors = ['e', 'R', 'G', 'Y', 'B', 'M', 'C', 'W']
	for col_neighbor in node.entire_column:
		if col_neighbor.empty:
			empty_count += 1
			empty_color = col_neighbor.color
	if empty_count == 0:
		return '#'
	elif empty_count == 1:
		return colors[empty_color].lower()
	elif empty_count == 8:
		if node.is_switch:
			return colors[get_switch_color(node.color, node.switched_node.color)]
		else:
			return ' '
	else:
		print "Invalid column"
		print [n.empty for n in node.entire_column]

def print_grid(grid, width, height):
	print "%d %d" % (width, height)
	print 0
	for i in xrange(width):
		row = ""
		for j in xrange(height):
			row += node_to_char(grid[i][j][0]) + ' '
		print row

width = 6
height = 6
grid = generate(width, height, 0, 0)
print_grid(grid, width, height)







