import db
# import json
# import ast

# guestList = json.dumps(["trentwiles"])

#db.insert("Big City Night: Scooter Race", "To sum it up, we're gonna race around on scooters around the city and play hide and seek", "fiNSkf", "trentwiles", "trentwiles,", "10/7 @7PM Rockridge Bart", 4328923, 0)

# gL = db.selectEventByID("nwiqSA")

# # converts the string into the list
# for x in ast.literal_eval(gL[0][3]):
#     print(x)

# x = ast.literal_eval(gL[0][3]).append("torvalds")

# db.deleteAll()
print(db.selectEventByID("fiNSkf")[0][3].split(","))
print(db.updateInvited("sdf", "nwiqSA"))