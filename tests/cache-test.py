import canvasCache
import json
import instructure

print(canvasCache.checkCacheAge("trentwiles"))

canvasKey = json.loads(open("config.json").read())["canvas"]

canvasCache.cache("trentwiles", instructure.getAssignmentsDueWithinDays(canvasKey, 3))

print(canvasCache.checkCacheAge("trentwiles"))