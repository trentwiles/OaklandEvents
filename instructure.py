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
    api = requests.get(BASE_API_URL + "/api/v1/courses/" + str(classID) + "/assignments?access_token=" + apiKey)
    if api.status_code != 200:
        return []
    
    assignmentsDueSoon = []

    for task in api.json():
        if task["due_at"] != None:
            epochTimeDueAt = datetime.fromisoformat(task["due_at"]).timestamp()
            
            # if the due date for the task is sooner (or equal to) the cutoff, it will take not of it
            secondsUntilDue = epochTimeDueAt - round(time.time())
            if secondsUntilDue > 0 and secondsUntilDue <= cutoff:
                assignmentsDueSoon.append(task)
    return assignmentsDueSoon

# view details of assignments due within x days
def getAssignmentsDueWithinDays(apiKey, days):
    tasks = []

    for x in getClasses(apiKey):
        for task in getAssignmentsDueSoon(apiKey, x, days * 86400):
            tasks.append({"name": task["name"], "url": task["html_url"]})

    return tasks