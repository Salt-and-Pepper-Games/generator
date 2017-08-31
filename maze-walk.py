import random

class Node:
	def __init__(self, x, y, color):
		self.planar_neighbors = []
		self.column_neighbors = []
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
		for i in (-1, 1):
			for j in (-1, 1):
					if x + i >= 0 and x + i < width and y + j >= 0 and y + j < height and (i == 0 or j == 0):
						neighbors.append(i, j)
		return neighbors

	for x in xrange(width):
		for y in xrange(height):
			planar_neighbors = get_planar_neighbors(x, y)
			for color in xrange(8):
				for neighbor in planar_neighbors:
					grid[x][y][color].planar_neighbors.append(grid[neighbors[0]][neighbors[1]][color])
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
		new_walls = make_move_if_valid(grid, wall[0], wall[1])
		walls.extend(new_walls)
		del walls[index]

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

def mark_visited(node):
	node.visited = True
	empty_nodes = [node]
	new_walls = []

	while len(empty_nodes) > 0:
		empty_node = empty_nodes.pop()

		# add all new walls for empty_node
		new_walls.extend(map(lambda x:(empty_node, x), empty_node.neighbors))

		empty_node.visited = True
		empty_nodes.extend(get_empty_neighbors(empty_node))


def make_move_if_valid(grid, n1, n2):
	new_walls = []
	if n1 is None or n1.color == n2.color:
		# planar move
		if n1 is None or n2.is_column_taken or n2.color == 0:
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
				#TODOs choose to add switch or leave it be
				for color in xrange(8):
					node_to_delete = grid[n2.x][n2.y][color]
					node_to_delete.empty = True
					# if the node to delete has a visited neighbor, it is part of the path. therefore, we want to mark it as visited so it will be treated as part of the path
					# if the node to delete is a loner, it is not a part of the path. so we don't mark it visited so it will be included in the path in the future
					node_to_delete.visited = neighbor_counts[color] > 0:
					if node_to_delete.visited:
						for neighbor in node_to_delete.planar_neighbors + node_to_delete.column_neighbors:
							new_walls.append((node_to_delete, neighbor))
		else:
			if not n2.visited:
				if n2.empty:
					n2.visited = True




			