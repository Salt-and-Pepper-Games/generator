import sys
import requests
import json
import mazewalk

def main(argv):
	# we will create a config file later for better options
	numLevels = 1000
	packName = argv[1]
	color = argv[2]
	levelSize = 7
	
	pack = {}

	# TODO make this more beautiful / better quality code
	lvl_num = 1
	for i in xrange(numLevels):
		lvl = mazewalk.build_level(levelSize, levelSize)
		if lvl is not None:
			grid, start, end = lvl
			pack["level" + str(lvl_num)] = mazewalk.stringify_grid(grid, levelSize, levelSize, start, end)
			lvl_num += 1
		if lvl_num > 20:
			break

	pack["packInfo"] = {'levelCount' : lvl_num - 1, 'packName' : packName, 'packColor' : color, 'packSize': levelSize}
	pack_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/" + packName + "Pack" + ".json", data=json.dumps(pack))
	print pack_request.text

	packnames_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/packNames/" + packName + ".json", data=json.dumps({packName:packName}))
	print packnames_request.text


if __name__ == "__main__":
	main(sys.argv)