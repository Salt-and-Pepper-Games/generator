import sys
import requests
import json
import mazewalk

def main(argv):
	# we will create a config file later for better options
	numLevels = 100
	packName = argv[1]
	color = argv[2]
	levelSize = 6
	
	pack = {}

	for i in xrange(numLevels):
		pack["level" + str(i + 1)] = mazewalk.build_level(levelSize, levelSize)

	pack["packInfo"] = {'levelCount' : numLevels, 'packName' : packName, 'packColor' : color}
	pack_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/" + packName + "Pack" + ".json", data=json.dumps(pack))
	print pack_request.text

	packnames_request = requests.put("https://prism-d2f60.firebaseio.com/levelData/packNames/" + packName + ".json", data=json.dumps({packName:packName}))
	print packnames_request.text


if __name__ == "__main__":
	main(sys.argv)