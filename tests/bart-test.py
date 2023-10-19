import bart
import json

bartKey = json.loads(open("config.json").read())["bart"]

print(bart.getTrainEstimates(bartKey, "ROCK"))