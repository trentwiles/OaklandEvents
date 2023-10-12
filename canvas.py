import instructure
import json

api_key = json.loads(open("config.json", "r").read())["canvas"]

# gets all classes by ID
for classID in instructure.getClasses(api_key):
    # then determines if any assingments in each class are due in 7 days
    for x in instructure.getAssignmentsDueSoon(api_key, classID, 7 * 86400):
        # and finally prints the name of it
        print(x["name"])