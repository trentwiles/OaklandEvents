import db
import json

guestList = json.dumps(["trentwiles"])
#print(guestList)

#db.create()

#db.deleteAll()
print(db.selectAllEvents())
#db.deleteEvent("nWUFANKdbf")
#db.deleteAll()
#print(db.selectEventByID('nWUFANKbf'))
# #db.create()
#db.insert("Small City Night", "Alameda trip for the weekend", "nWUFANKdbf", guestList, "{}", "10/17 @ 3PM", 1696445535, 0)
#print(db.selectEventByID('nWUFANKdbf')[0][3])
# #print(json.loads(db.selectEventByID('nWUFANKbf')[0][3]))

# # x = json.loads()
# # for users in x:
# #     print(x)

# # x = x.append('torvalds')

# # db.updateInvited(x)