import requests
from datetime import datetime
import time

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

# cutoff = seconds until a due date for an assignment to be counted
def getAssignmentsDueSoon(apiKey, classID, cutoff):
    api = requests.get(BASE_API_URL + "/api/v1/courses/" + classID + "/assignments?access_token=" + apiKey)
    if api.status_code != 200:
        return []
    
    assignmentsDueSoon = []

    for task in api.json():
        epochTimeDueAt = datetime.fromisoformat(task["due_at"]).timestamp()
        
        # if the due date for the task is sooner (or equal to) the cutoff, it will take not of it
        if (round(time.time()) - epochTimeDueAt) <= cutoff:
            assignmentsDueSoon.append(task)