import requests
import json

#
# Code to check Canvas to see how much work is due around the time of an event
#

BASE_API_URL = "https://northeastern.instructure.com"

def authCheck(apiKey):
    return (requests.get(BASE_API_URL + "/api/v1/courses?access_token=" + apiKey).status_code == 200)

def getClasses(apiKey):
    api = requests.get(BASE_API_URL + "/api/v1/courses?access_token=" + apiKey)
    if api.status_code != 200:
        return []
    
    classes = []
    for classID in api.json():
        classes.append(classID["id"])
    
    return classes

def getClassworkByCourseID(apiKey, classID):
    api = requests.get(BASE_API_URL + "/api/v1/courses/" + classID + "/assignments?access_token=" + apiKey)
    if api.status_code != 200:
        return []
    for task in api.json():
        print(task["due_at"])