import json
import time
import os

def checkCacheAge(username):
    timeNow = round(time.time())
    # returns the "age" of the cached content, -1 if no file found
    try:
        with open("cache/" + username + "-canvas.json", "r") as r:
            return timeNow - json.loads(r.read())["age"]
    except:
        return -1

def cache(username, instructureDataResponse):
    # caches the response from canvas
    # instructureDataResponse must be a response from instructure.getAssignmentsDueWithinDays()
    # for instance:
    # [
    #  {"name": "task name", "url": "https://northeastern.instructure.com/..."},
    #  {"name": "another task name", "url": "https://northeastern.instructure.com/..."}
    # ]

    if os.path.isfile("cache/" + username + "-canvas.json"):
        os.remove("cache/" + username + "-canvas.json")
    
    ts = round(time.time())
    with open("cache/" + username + "-canvas.json", "a") as w:
        w.write(json.dumps({"age": ts, "data": instructureDataResponse}))
    
    return True

# to do... read the data