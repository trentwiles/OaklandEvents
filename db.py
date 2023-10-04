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
    """
    
    cur.execute(f'''CREATE TABLE IF NOT EXISTS oakland (title TEXT, desc TEXT, uniqueID TEXT, invitedUsers TEXT, confirmedUsers TEXT, humanHappensTime TEXT, createTime INTERGER)''')
    conn.commit()
    cur.close()
    conn.close()