import db
import json

guestList = json.dumps(["trentwiles"])
print(guestList)

db.deleteEvent("nWUFANKbf")
print(db.selectEventByID('nWUFANKbf'))
#db.create()
#db.insert("Big City Night", "SF trip for the weekend", "nWUFANKbf", guestList, "{}", "10/7 @ 7PM", 1696445535, 0)
#print(db.selectEventByID('nWUFANKbf')[0][3])
#print(json.loads(db.selectEventByID('nWUFANKbf')[0][3]))

# x = json.loads()
# for users in x:
#     print(x)

# x = x.append('torvalds')

# db.updateInvited(x)