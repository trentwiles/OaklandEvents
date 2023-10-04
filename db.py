import sqlite3


def create():
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    """
    DOCS

    title: Title of event
    desc: Brief event description
    uniqueID: Event ID in base64
    invitedUsers: JSON string with the people on the guest list, by default {}
    confirmedUsers: JSON string with the people on the confirmed attendance list, by default {}
    humanHappensTime: Time the event takes place (in a human readable form), for example, '10/4 at 6PM'
    createTime: time event was created (in epoch time)
    closed: 0 if still open, 1 if closed/archived
    """
    
    cur.execute(f'''CREATE TABLE IF NOT EXISTS oakland (title TEXT, desc TEXT, uniqueID TEXT, invitedUsers TEXT, confirmedUsers TEXT, humanHappensTime TEXT, createTime INTERGER, closed INTERGER)''')
    conn.commit()
    cur.close()
    conn.close()


def insert(title, desc, uniqueID, invitedUsers, confirmedUsers, humanHappensTime, createTime, closed):
    # sample data:
    # data = [(42349234, "email sent", 1600043)]
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()

    cur.executemany('''INSERT INTO oakland (title, desc, uniqueID, invitedUsers, confirmedUsers, humanHappensTime, createTime, closed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', ([(title, desc, uniqueID, invitedUsers, confirmedUsers, humanHappensTime, createTime, closed)]))
    conn.commit()
    cur.close()
    conn.close()

def selectEventByID(id):
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    items = []
    for x in cur.execute('''SELECT * FROM oakland WHERE uniqueID = ?''', (id,)):
        items.append(x)
    cur.close()
    conn.close()
    return items

def selectAllEvents():
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    items = []
    for x in cur.execute('''SELECT * FROM oakland'''):
        items.append(x)
    cur.close()
    conn.close()
    return items

#'UPDATE your_table SET column_name = ? WHERE id = ?', (new_data, id)

def updateInvited(id, jsonContent):
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    items = []
    cur.execute('''UPDATE oakland SET invitedUsers = ? WHERE uniqueID = ?''', (jsonContent, id,))
    cur.close()
    conn.close()
    return

def updateConfirmed(id, jsonContent):
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    items = []
    cur.execute('''UPDATE oakland SET confirmedUsers = ? WHERE uniqueID = ?''', (jsonContent, id,))
    cur.close()
    conn.close()
    return

def closeOpenEvent(id, oneOrZero):
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    items = []
    cur.execute('''UPDATE oakland SET closed = ? WHERE uniqueID = ?''', (oneOrZero, id,))
    cur.close()
    conn.close()
    return

def deleteAll():
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    sampleTitle = "FBUBBFDJBfewbfwefb"
    cur.execute('''DELETE FROM oakland WHERE title != ?''', (sampleTitle,))
    conn.commit()
    cur.close()
    conn.close()