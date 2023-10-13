from flask import Flask, render_template, session, request, redirect, url_for, Response
import json
import db
from authlib.integrations.flask_client import OAuth
import random
import time
import instructure

app = Flask(__name__)
app.secret_key = json.loads(open('config.json').read())["secret_key"]
canvasKey = json.loads(open('config.json').read())["canvas"]
CANVAS_DAYS_THRESHOLD = 3
CANVAS_DAYS_THRESHOLD_ENGLISH = "three"

def generateRandom(howMany):
    variables = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    final = ""
    for x in range(howMany):
        final += variables[random.randint(0, len(variables) - 1)]
    return final

def jsonResp(input, status):
    return Response(json.dumps(input), status_code=status, content_type="application/json")

def parseInvited(raw, username):
    new = raw.split("\n")
    new.append(username)
    return ",".join(new)

def determineIfAnyWorkIsDueNearEvent(eventID, dayThreshold):
    # How this works:
    # 1. Gets the event time from the database
    # 2. Uses the Canvas API to check if any assignments are due up to 2 days after the event
    # 3. Returns a list of their names (if any)
    dbLookup = db.selectEventByID(eventID)
    try:
        # time when event will happen
        seconds = dbLookup[0][6]
    except:
        raise ValueError("Event doesn't exist or has date has already passed.")
    
    # make sure the event isn't closed and that it already hasn't happened
    secondsUntilItHappens = seconds - round(time.time())
    if (dbLookup[0][7] != 1) and secondsUntilItHappens > 0:
        
        # the "threshold" is the time until the event happens, plus how many days after have been set
        threshold = secondsUntilItHappens + (dayThreshold * 86400)

        canvas_api_key = json.loads(open("config.json").read())["canvas"]

        classesInvolved = []

        # go through each class in canvas and get the ID
        for classID in instructure.getClasses(canvas_api_key):
            # then determines if any assingments in each class are due within the t
            for task in instructure.getAssignmentsDueSoon(canvas_api_key, classID, threshold):
                # and finally adds the details of it to the list
                classesInvolved.append(task)
        
        # now, see if there were any classes
        if len(classesInvolved) != 0:
            htmlReturnString = "<strong>Warning: Work due within " + str(dayThreshold) + " day(s) of event.<strong>Details:<br>"
            for classMetaData in classesInvolved:
                htmlReturnString += "<a href='" + classMetaData["html_url"] + "' target='_blank'>" + classMetaData["name"] + "</a><br>"
        else:
            htmlReturnString = "<p>There is no work due within " + str(dayThreshold) + " day(s) of event.</p>"
        
        return htmlReturnString
    else:
        raise ValueError("Event doesn't exist or has date has already passed.")


oauth = OAuth(app)

github = oauth.register(
    name='github',
    client_id=json.loads(open('config.json').read())["gh_c_id"],
    client_secret=json.loads(open('config.json').read())["gh_s_id"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)   


@app.route('/')
def welcome():
    # if user isn't logged in, return 404/unauthed page
    if 'username' not in session:
        return render_template("index.html")
    
    # by default, we assume that the user has been invited to at least one event
    notInAnyEvents = False

    api = db.selectAllEvents()
    # var to hold the events the user is in
    validEvents = []
    # read through each event...
    for event in api:
        # break down the user invited to the event
        for user in event[3].split(","):
            # if the user is in the event, and the event isn't closed, then add the event to the list
            if user == session['username'] and event[7] != 1:
                validEvents.append(event)
    # the events will be iterated through on the / page
    if len(validEvents) == 0:
        notInAnyEvents = True

    stuffDue = instructure.getAssignmentsDueWithinDays(canvasKey, CANVAS_DAYS_THRESHOLD)
    howManyDue = len(stuffDue)

    return render_template("dash.html", events=validEvents, username=session['username'], notInAnyEvents=notInAnyEvents, stuffDue=stuffDue, howManyDue=howManyDue)

@app.route('/details/<id>')
def details(id):
    # if user isn't logged in, return 404/unauthed page
    if 'username' not in session:
        return render_template("404.html")
    api = db.selectEventByID(id)
    # let's assume that only one event will be selected
    # api[0][7] makes sure that only active events are shown
    if session['username'] in api[0][3].split(",") and api[0][7] != 1:
        numberInvites = len(api[0][3].split(","))
        numberConfirmed = len(api[0][4].split(","))
        attendanceRate = round(numberConfirmed/numberInvites * 100, 1)
        return render_template("event.html", event=api[0], numberInvites=numberInvites, numberConfirmed=numberConfirmed, attendanceRate=attendanceRate)
    return render_template("404.html")

@app.route("/register", methods=["POST"])
def register():
    if 'username' not in session:
        return jsonResp({"success": "false", "message": "Please sign in"}, 401)
    if request.form.get("id") == None:
        return jsonResp({"success": "false", "message": "Please use the id parameter to register for an event"}, 400)
    id = request.form.get("id")

    api = db.selectEventByID(id)

    try:
        print(api[0][0])
    except:
        return jsonResp({"success": "false", "message": "Sorry, this event is invalid"}, 400)

@app.route('/create', methods=["GET"])
def create():
    # if user isn't logged in, return 404/unauthed page
    if 'username' not in session:
        return render_template("404.html")
    return render_template("createEvent.html")

@app.route('/create', methods=["POST"])
def createPOST():
    # again, while it's not likley that the user will have logged out before sending in the form
    # it can't hurt to check again
    if 'username' not in session:
        return render_template("404.html")
    # get inputs and variables
    title = request.form.get("event")
    description = request.form.get("desc")
    whenAndWhere = request.form.get("where")

    # validate
    if title == None or description == None or whenAndWhere == None:
        # make this fancier in the future
        return "Invalid input, you're missing something"

    uniqueID = generateRandom(10)
    timestamp = round(time.time())
    invited = request.form.get("invited")
    created = session['username']

    # once everything has been collected, send it to the database
    db.insert(title, description, uniqueID, parseInvited(invited, session['username']), session['username'], whenAndWhere, timestamp, 0, created)
    return redirect("/?created=true")

@app.route("/login")
def login():
    # send to Github for oauth
    redirect_url = url_for("authorize", _external=True)
    return github.authorize_redirect(redirect_url)

@app.route("/authorize")
def authorize():
    # work with github to log the user in

    # for now, the token doesn't matter
    token = github.authorize_access_token()
    resp = github.get('user', token=token)
    profile = resp.json()

    # set the user in the cookie to the user github gave us
    session['username'] = profile['login']
    return redirect('/')

@app.route("/logout")
def logout():

    # delete the username from the session
    session.pop('username')

    # send back to the homepage (which has the login button)
    return redirect("/")

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')