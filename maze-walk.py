import random

class Node:
	def __init__(self, x, y, color):
		self.planar_neighbors = []
		self.column_neighbors = []

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
				for switch_color in (1, 2, 4):
					new_color = color ^ switch_color
					grid[x][y][color].column_neighbors.append(grid[x][y][new_color])
	return grid

def generate(width, height, x_start, y_start):
	grid = build_grid(width, height)
	walls = make_move_if_valid(grid, None, grid[0][0][0])

	while len(walls) > 0:
		index = random.randint(0, len(walls) - 1)
		wall = walls[index]
		# print("(%d, %d) => (%d, %d)" % (wall[0].x, wall[0].y, wall[1].x, wall[1].y))
		new_walls = make_move_if_valid(grid, wall[0], wall[1])
		walls.extend(new_walls)
		del walls[index]

	return grid

def get_visited_neighbor_count(node):
	visited_neighbors = 0
	for neighbor in node.planar_neighbors:
		if neighbor.visited:
			visited_neighbors += 1
	return visited_neighbors

def get_empty_neighbors(node):
	empty_nodes = []
	neighbors = node.planar_neighbors
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

		# add all new walls for empty_node
		tmp = [(empty_node, x) for x in empty_node.planar_neighbors]
		# print(empty_node.planar_neighbors)
		new_walls.extend(tmp)

		empty_node.visited = True
		empty_node.empty = True
		# marking the column as taken if it's not already
		if not empty_node.is_column_taken:
			for column_node in empty_node.entire_column:
				column_node.is_column_taken = True
		empty_nodes.extend(get_empty_neighbors(empty_node))

		# handling the case where it's a switch
		if empty_node.is_switch:
			# check that it's not visited to avoid a loop
			if not empty_node.switched_node.visited:
				empty_nodes.append(empty_node.switched_node)

	return new_walls

def get_switch_walls(grid, x, y, bitmask):
	new_walls = []
	for color in xrange(8):
		new_walls.append((grid[x][y][color], grid[x][y][color ^ bitmask]))
	return new_walls

def make_move_if_valid(grid, n1, n2):
	new_walls = []
	if n1 is None or n1.color == n2.color:
		# planar move
		if n1 is None or n2.is_column_taken or n2.color == 0:
			# print("Deleting column")
			# checking if it's okay to delete this block on EVERY floor
			# to do this, we need to check that we won't create a loop in the path on every floor
			# a loop would occur if the block we are going to remove had two or more visited neighbors
			ok_to_delete = True
			neighbor_counts = []
			for color in xrange(8):
				node = grid[n2.x][n2.y][color]
				visited_neighbors = get_visited_neighbor_count(node)
				neighbor_counts.append(visited_neighbors)
				if visited_neighbors > 1:
					ok_to_delete = False
					break
			if ok_to_delete:
				# print("Ok to delete")
				

				for color in xrange(8):
					node_to_delete = grid[n2.x][n2.y][color]
					# if the node to delete has a visited neighbor, it is part of the path. therefore, we want to mark it as visited so it will be treated as part of the path
					# if the node to delete is a loner, it is not a part of the path. so we don't mark it visited so it will be included in the path in the future
					node_to_delete.empty = True
					if neighbor_counts[color] > 0 or color == n2.color:
						# print("Deleting color %d" % color)
						new_walls.extend(mark_visited(node_to_delete))

				#TODOs choose to add switch or leave it be
				# maybe this is all we need
				for switch_color in [1, 2, 4]:
					# not sure we want to add EVERY switch wall
					# they're all effectively the same thing: add a switch
					# new_walls.extend(get_switch_walls(grid, n2.x, n2.y, switch_color))
					# instead, just add one for each :
					new_walls.append((n2, grid[n2.x][n2.y][n2.color ^ switch_color]))
		else:
			# turning a wall into a colored block
			if not n2.visited:
				# only care if it's empty or if it won't create a loop
				if n2.empty or get_visited_neighbor_count(n2) < 2:
					# now we're exploring a new node
					new_walls.extend(mark_visited(n2))
					# TODO need to mark is_column_taken to true for every node in column
	else:
		# we want to add a switch
		# this is a whole nother ball game
		if n1.empty and n2.empty and not (n1.is_switch and n2.is_switch):
			print("Trying to add a switch from %d to %d" % (n1.color, n2.color))
		
	return new_walls


grid = generate(20, 20, 0, 0)
for i in xrange(20):
	print([int(grid[i][j][0].visited) for j in xrange(20)])