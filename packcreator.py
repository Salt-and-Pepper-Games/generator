import sys
import requests
import json
import mazewalk
import random

def main(argv):
	# we will create a config file later for better options
	maxTries = 10000
	packName = argv[1]
	color = argv[2]
	levelSize = int(argv[3])
	num_levels = int(argv[4])
	min_complexity = int(argv[5])
	
	pack = {}

	# TODO make this more beautiful / better quality code
	lvl_num = 1
	for i in xrange(maxTries):
		start = (random.randint(0, levelSize - 1), random.randint(0, levelSize - 1))
		#start = (0, 0)
		lvl = mazewalk.build_level(levelSize, levelSize, start, min_complexity)
		if lvl is not None:
			grid, start, end = lvl
			pack["level" + str(lvl_num)] = mazewalk.stringify_grid(grid, levelSize, levelSize, start, end)
			lvl_num += 1
		if lvl_num > num_levels:
			break

	pack["packInfo"] = {'levelCount' : lvl_num - 1, 'packName' : packName, 'packColor' : color, 'packSize': levelSize}
	pack_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/" + packName + "Pack" + ".json", data=json.dumps(pack))
	print pack_request.text

	packnames_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/packNames/" + packName + ".json", data=json.dumps({packName:packName}))
	print packnames_request.text


if __name__ == "__main__":
	main(sys.argv)