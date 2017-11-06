import random
import heapq

NODE_TYPES = 3
EMPTY_SWITCH = 2
SWITCH = 1
DRILL = 0

SWITCH_COLORS = [1, 2, 4]
EMPTY_SWITCH_COLOR = 0

def build_wall(start, finish, wall_type):
	return (start, finish, wall_type)

# Refresher for later
# Concepts
#  - Branch History records info about the branch at that time (at that node)
#  - Main branch is sacred this is where the end will go
#	  o TODO entire column of current main leaf (during generation) should be impassable so there is only one way to the exit
#  - Other branches can be fused after generation 
#     o currently for the sake of getting rid of black blocks
#     o TODO use this to also give levels confusing loops
#  - Score child is a heuristic function to determine how to branch
# Major TODO (s)
#  - Potentially integrate branch history with node class (they are kind of the same thing)
#  - Resolving black blocks isn't really there yet should use distance to make sure not creating any major shortcuts

class BranchHistory:
	def __init__(self, node , main = False):
		self.steps_since_last_type = [0,0,0]
		self.distance_from_start = 0
		self.main = False
		# at what point did you branch off of main and how far are you from it?
		self.main_branch_point = 0
		# safe to fuse two branches if they come off from main at the same point

		self.current_leaf = True
		self.children = []
		self.branch_worth = 0
		self.node = node
		
	def branch_from_parent(self, current_node_type, current_node):
		# an attempt at a heuristic
		# memory

		new_history = BranchHistory(current_node)
		for node_type in xrange(NODE_TYPES):
			if node_type is current_node_type:
				new_history.steps_since_last_type[node_type] = 0
			else:
				new_history.steps_since_last_type[node_type] = self.steps_since_last_type[node_type] + 1

		new_history.distance_from_start = self.distance_from_start + 1
		"""if self.main == True and self.current_leaf == True:
			new_history.main = False
			print "main had child with distance " + str(new_history.distance_from_start)"""

		self.current_leaf = False
		new_history.current_leaf = True

		self.children.append(new_history)

		return new_history

	def score_child(self, current_node_type):
		# an example heuristic function
		#score += self.children * 3
		score = 0
		if current_node_type == EMPTY_SWITCH:
			return -2 + random.random() * 2
		if current_node_type == DRILL:
			return -1 + random.random() * 2
		return -100 + random.random() * 2

	def calculate_branch_worth(self):
		# base case
		if len(self.children) == 0:
			visited_col_neighbors = filter(lambda x:x.branch_history is not None, self.node.entire_column)
			self.branch_worth = min(map(lambda x:x.branch_history.distance_from_start, visited_col_neighbors))
			print self.branch_worth
		else:
			self.branch_worth = max(map(lambda child:child.calculate_branch_worth(), self.children))
		return self.branch_worth

	# TODO currently this function returns it's branch as reversed.
	def get_best_branch(self, depth = 0):
		if len(self.children) == 0:
			lst = [self]
		else:
			best_child_score = -10000
			best_child = None
			for child in self.children:
				if child.branch_worth > best_child_score:
					best_child_score = child.branch_worth
					best_child = child
			lst = best_child.get_best_branch(depth + 1)
			lst.append(self)
		return lst  

	# the idea here is to mark branches as offshoots of the main branch so can resolve how to fuse them to avoid black blocks if necessary
	def mark_as_offshoot_of_main(self, branch_point):
		self.main_branch_point = branch_point
		for child in self.children:
			child.mark_as_offshoot_of_main(branch_point)

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
		self.branch_history = None

		self.searched = False

	def is_end_of_level(self):
		for node in self.entire_column:
			if node.branch_history is not None:
				if node.branch_history.current_leaf == True and node.branch_history.main == True:
					return True
		return False

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

def push_walls_to_queue(walls, queue):
	for wall in walls:
		start, finish, wall_type = wall
		score = start.branch_history.score_child(wall_type)
		heapq.heappush(queue, (score, wall))
	return queue

def pop_wall_from_queue(queue):
	return heapq.heappop(queue)

def generate(width, height, x_start, y_start, empty_prob=.5, switch_prob=.2, drill_prob=.3):
	grid = build_grid(width, height)
	start = grid[x_start][y_start][0]
	# start the main branch
	start.branch_history = BranchHistory(start)
	mark_switch_visited_and_get_walls(start, 0)
	wall_queue = push_walls_to_queue(mark_neighbors_visited_and_get_walls(start), [])
	#wall_queue = push_walls_to_queue(mark_switch_visited_and_get_walls(start, 0), [])

	while len(wall_queue) > 0:
		# proposed a new edge between the start and the finish
		score, wall = pop_wall_from_queue(wall_queue)
		start, finish, wall_type = wall
		
		#TODO do the rest
		if wall_type == DRILL:
			if is_drill_valid(start, finish):
				mark_drill_visited(finish)
				finish.branch_history = start.branch_history.branch_from_parent(wall_type, finish)
				push_walls_to_queue(mark_neighbors_visited_and_get_walls(finish), wall_queue)
				# DEBUG
				print_grid(grid, width, height)
		elif wall_type == SWITCH or wall_type == EMPTY_SWITCH:
			switch_color = start.color ^ finish.color
			if is_switch_valid(start, finish, switch_color):
				#mark_switch_visited(finish, switch_color)
				finish.branch_history = start.branch_history.branch_from_parent(wall_type, finish)
				push_walls_to_queue(mark_switch_visited_and_get_walls(finish, switch_color), wall_queue)
				push_walls_to_queue(mark_neighbors_visited_and_get_walls(finish), wall_queue)
				# DEBUG
				print_grid(grid, width, height)
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
			new_walls.append(build_wall(node, neighbor.entire_column[neighbor.color ^ EMPTY_SWITCH_COLOR], EMPTY_SWITCH))
	return new_walls

def visit_empty_neighbors(node):
	# TODO flood fill empty neighbors and mark visited, return list of all nodes marked visited
	visited_nodes = []
	for neighbor in get_neighbors(node):
		if neighbor.empty and not neighbor.visited:
			neighbor.visited = True
			# TODO this will either be switch or empty for now treat it as switch but add in empty later
			if neighbor.color == node.color:
				neighbor.branch_history = node.branch_history.branch_from_parent(EMPTY_SWITCH, neighbor)
			else:
				neighbor.branch_history = node.branch_history.branch_from_parent(SWITCH, neighbor)
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
def check_creates_loop(node, switched_node = None):
	if switched_node == None:
		switched_node = node
	visited_in_nodes = set(map(lambda x:(x.x,x.y,x.color), filter(lambda x:x.visited, can_reach_me(switched_node))))
	visited_out_nodes = set(map(lambda x:(x.x,x.y,x.color), filter(lambda x:x.visited, i_can_reach(node))))
	# EXPERIMENTAL stricter conditions (but are they too strict...)
	return len(visited_in_nodes.union(visited_out_nodes)) > 1
	#return len(visited_in_nodes) > 0 and len(visited_out_nodes) > 0 and len(visited_in_nodes.union(visited_out_nodes)) > 1

# will a loop occur with the main branch?
# note this idea should be expanded on later to try to branch as close to the start as possible
# code could also probably be cleaned up to combine with previous function
#
# TODO move the experimental code to the a different function
def check_creates_main_loop(node, switched_node=None):
	if switched_node == None:
		switched_node = node
	visited_in_nodes = set(filter(lambda x:x.visited, can_reach_me(switched_node)))
	visited_out_nodes = set(filter(lambda x:x.visited, i_can_reach(node)))
	union = visited_in_nodes.union(visited_out_nodes)
	does_intersect_main = False
	for node in union:
		if node.branch_history.main == True:
			does_intersect_main = True
			break

	# TODO move the experimental code to a different function
	# START EXPERIMENT
	chosen_branch = None
	for node in union:
		if chosen_branch == None:
			if node.branch_history is not None:
				chosen_branch = node.branch_history.main_branch_point
		elif node.branch_history is not None and node.branch_history.main_branch_point != chosen_branch:
			does_intersect_main = True
			break
	if chosen_branch is not None and not does_intersect_main:
		print "Fused Branch " + str(chosen_branch)
	# END EXPERIMENT

	return len(visited_in_nodes) > 0 and len(visited_out_nodes) > 0 and len(union) > 1 and does_intersect_main

	
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

def mark_switch_visited_and_get_walls(node, switch_color):
	node.visited = True
	new_walls = []
	for col_neighbor in node.entire_column:
		# Do not mark the current node
		col_neighbor.empty = True
		col_neighbor.column_taken = True
		col_neighbor.is_switch = True
		col_neighbor.switched_node = node.entire_column[col_neighbor.color ^ switch_color]
		if col_neighbor == node:
			"""col_neighbor.visited = True
			new_walls += mark_neighbors_visited_and_get_walls(col_neighbor)"""
			col_neighbor.visited = True
			continue
		# mark visited if a neighbor is visited
		for neighbor in can_reach_me(col_neighbor.switched_node):
			# only one neighbor should be visited
			if neighbor.visited:
				# TODO verify that visiting the switched node is correct
				col_neighbor.visited = True
				# in this scenario the neighbor is the parent of col_neighbor
				# TODO mark these as empty switches if they are
				col_neighbor.branch_history = neighbor.branch_history.branch_from_parent(SWITCH, col_neighbor)
				new_walls += mark_neighbors_visited_and_get_walls(col_neighbor)
				break
	return new_walls


def check_switch_creates_unpassables(node, switch_color):
	# only check planar neighbors because switch neighbors already have column taken and cannot become un-passable hence no need to resolve them
	"""filled_planar_neighbors = filter(lambda x:not x.column_taken, node.planar_neighbors)
	for neighbor in filled_planar_neighbors:
		for double_neighbor in neighbor.planar_neighbors:
			if double_neighbor.is_switch and double_neighbor is not node:
				return True"""
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
			#print "Attempting to replaced black block @ " + str((x,y))
			for color in xrange(1, 8):
				if not check_creates_loop(grid[x][y][color], None):
					# at this stage BranchHistory and distance_from_start mean nothing but it will still throw an error if we don't have it
					# remove this dependency later
					# but also potentially use it it could mean something if we wanted it to
					grid[x][y][color].branch_history = BranchHistory(None)
					mark_drill_visited(grid[x][y][color])
					mark_neighbors_visited_and_get_walls(grid[x][y][color])
					success = True
					print "replaced black block @ " + str((x,y)) + " with color " + str(color)
					break
			if not success:
				#print "attempting to compromise"
				for color in xrange(1, 8):
					if not check_creates_main_loop(grid[x][y][color], None):
						# once we transform a tree into a graph BranchHistory means nothing but it will still throw an error if we don't have it
						# TODO remove this dependency later
						grid[x][y][color].branch_history = BranchHistory(None)
						mark_drill_visited(grid[x][y][color])
						mark_neighbors_visited_and_get_walls(grid[x][y][color])
						success = True
						print "successfully compromised"
						break
			# If we don't succeed give up for now
			if not success:
				print "failure"
				return None
	return grid

def node_to_char(node):
	empty_count = 0
	empty_color = None
	#colors = [' e ', ' R ', ' G ', ' Y ', ' B ', ' M ', ' C ', ' W ']
	colors = ['e', 'R', 'G', 'Y', 'B', 'M', 'C', 'W']

	"""total_leaf = False
	for col_neighbor in node.entire_column:
		if col_neighbor.branch_history is not None:
			if col_neighbor.branch_history.main:
				total_leaf = True
				break
	if total_leaf:
		colors = ['(e)', '(R)', '(G)', '(Y)', '(B)', '(M)', '(C)', '(W)']"""


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

def stringify_grid(grid, width, height, start=(0, 0), end=None, delimiter = ""):
	if end is None:
		end = (width-1, height-1)
	level_string = ""
	level_string += "%d %d " % (start[0], start[1]) + delimiter
	level_string += "%d %d " % (end[0], end[1]) + delimiter
	level_string += "%d %d " % (width, height) + delimiter
	for j in xrange(height):
		row = ""
		for i in xrange(width):
			if i == end[0] and j == end[1]:
				row += 'e '
			else:
				row += node_to_char(grid[i][j][0]) + ' '
		level_string += row + delimiter
	return level_string

def build_level(width, height, start=(0, 0), min_len = 10):
 	grid = generate(width, height, start[0], start[1])
 	# TODO put all of these complex steps into a simple wrapper method
 	start_node = grid[start[0]][start[1]][0]
	#start_node.branch_history.is_eligable()
	start_node.branch_history.calculate_branch_worth()
	path = start_node.branch_history.get_best_branch()

	"""if len(path) < 10:
		return None

	print len(path)"""

	for branch_history in path:
		branch_history.main = True

	end = (path[0].node.x, path[0].node.y)

	old_string = stringify_grid(grid, width, height, start, end = end, delimiter = "\n")	

	if len(path) < min_len:
		return None

	#grid = eliminate_black_blocks(grid, width, height)
	# fail on failure to remove all black blocks (rare but possible)
	if grid is None:
		return None

	print "LEVEL LENGTH AND SOLUTION"
	print len(path)
	print list(reversed(map(lambda x:(x.node.x, x.node.y, x.node.color), path)))

	print "THE END"
	print map(lambda x:x.branch_history, path[0].node.entire_column)

	print (path[0].node.x, path[0].node.y)
	print old_string

 	return grid, start, end

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

def main():
	width = 3
	height = 3
	lvl = build_level(width, height, min_len = 0)
	if lvl is not None:
		grid, start, end = lvl
		graph_level(grid[start[0]][start[1]][0])
		print_grid(grid, width, height, start, end)
		#break

def graph_level(start_node):
	from graphviz import Digraph
	graph = Digraph(comment='Hawt Level Graph')

	seen_nodes = {}

	current_node = start_node
	graph.node("0", str((start_node.x, start_node.y, start_node.color)))
	seen_nodes[start_node] = "0"

	queue = [current_node]

	next_node_id = 1

	while len(queue) > 0:
		current_node = queue.pop()
		for branch_child in current_node.branch_history.children:
			child = branch_child.node
			if not child in seen_nodes:
				graph.node(str(next_node_id), str((child.x, child.y, child.color)))
				seen_nodes[child] = str(next_node_id)
				queue.append(child)
				next_node_id += 1
			graph.edge(seen_nodes[current_node], seen_nodes[child])

	graph.render('level_graph.gv', view=True)

if __name__ == "__main__":
	main()