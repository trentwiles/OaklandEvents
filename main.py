from flask import Flask, render_template, session, request, redirect, url_for, Response, make_response
import json
import db
from authlib.integrations.flask_client import OAuth
import random
import time
import instructure
import canvasCache
import requests

app = Flask(__name__)
app.secret_key = json.loads(open('config.json').read())["secret_key"]
canvasKey = json.loads(open('config.json').read())["canvas"]
CANVAS_DAYS_THRESHOLD = 3
CANVAS_DAYS_THRESHOLD_ENGLISH = "three"
CANVAS_API_KEY = json.loads(open("config.json").read())["canvas"]

def generateRandom(howMany):
    # creates a random string, howMany being how many chars the string should have
    variables = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    final = ""
    for x in range(howMany):
        final += variables[random.randint(0, len(variables) - 1)]
    return final

def jsonResp(input, status):
    # Helper function to create JSON responses for API methods
    return Response(json.dumps(input), content_type="application/json"), status

def parseInvited(raw, username):
    # In the database, users who are invited/confirmed are stored like so:
    # user1,user2,user3
    # So this helper function justinserted from the HTML form into that format, plus adds the username of 
    # the form submitter
    new = raw.split("\n")
    new.append(username)
    return ",".join(new)

def determineIfAnyWorkIsDueNearEvent(eventID, dayThreshold):
    # **Important Note**
    # This method is currently broken as there is nothing entering the epoch time of an event taking place into
    # the database. Until that is fixxed, this is not usable (however, in theory, it does work)

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

        classesInvolved = []

        # go through each class in canvas and get the ID
        for classID in instructure.getClasses(CANVAS_API_KEY):
            # then determines if any assingments in each class are due within the t
            for task in instructure.getAssignmentsDueSoon(CANVAS_API_KEY, classID, threshold):
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
    # if user isn't logged in, return login page
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

    cacheStatus = canvasCache.checkCacheAge(session['username'])
    if cacheStatus != -1 and cacheStatus <= 86400:
        stuffDue = canvasCache.readCache(session['username'])
        cacheHeader = "HIT"
    else:
        stuffDue = instructure.getAssignmentsDueWithinDays(canvasKey, CANVAS_DAYS_THRESHOLD)
        cacheHeader = "MISS"
        canvasCache.cache(session['username'], stuffDue)
        cacheStatus = 0
    howManyDue = len(stuffDue)

    rsp = make_response(render_template("dash.html", events=validEvents, username=session['username'], notInAnyEvents=notInAnyEvents, stuffDue=stuffDue, howManyDue=howManyDue))
    rsp.headers["x-canvas-cache"] = cacheHeader
    rsp.headers["age"] = cacheStatus
    return rsp

@app.route('/details/<id>')
def details(id):
    # if user isn't logged in, return 404/unauthed page
    if 'username' not in session:
        return render_template("404.html")
    api = db.selectEventByID(id)
    # let's assume that only one event will be selected
    # api[0][7] makes sure that only active events are shown
    if session['username'] in api[0][3].split(",") and api[0][7] != 1:
        # .split(",") is used to convert from the database format to python list format
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

@app.route("/bustCanvasCache")
def bustCanvasCache():
    if 'username' not in session:
        return jsonResp({"status": "error", "message": "Please sign in"}, 401)
    canvasCache.cache(session['username'], instructure.getAssignmentsDueWithinDays(CANVAS_API_KEY, CANVAS_DAYS_THRESHOLD))
    return jsonResp({"status": "ok"}, 200)
    
@app.route("/", methods=["POST"])
def homeAPI():
    
    # Transit API
    def bus():
        ac_api = json.loads(open("config.json").read())["actransit"]
        a = requests.get(f"https://api.actransit.org/transit/route/57/trips/?token={ac_api}").json()
        r = requests.get(f"https://api.actransit.org/transit/stops/52277/predictions/?token={ac_api}").json()
        fiveseven = []
        fiveseven_format = []
        nl = []
        nl_format = []
        
        for bus in r:
            print(bus)
            if bus["RouteName"] == "57":
                fiveseven.append(bus)
            if bus["RouteName"] == "NL":
                nl.append(bus)
        
        for bus57 in fiveseven:
            tripID = bus57["TripId"]
            for trips in a:
                if tripID == trips["TripId"]:
                    fiveseven_format.append({"direction": trips["Direction"], "time": bus57["PredictedDeparture"]})

        for busNL in nl:
            tripID = busNL["TripId"]
            for trips in a:
                if tripID == trips["TripId"]:
                    nl_format.append({"direction": trips["Direction"], "time": busNL["PredictedDeparture"]})

        return {"57": fiveseven_format, "NL": nl_format}
    def trainToSF():
        mcar = requests.get("https://bart.trentwil.es/api/v1/getPredictions/MCAR").json()
        rock = requests.get("https://bart.trentwil.es/api/v1/getPredictions/MCAR").json()
        pow = requests.get("https://bart.trentwil.es/api/v1/getPredictions/POWL").json()
        
        # To SF
        # Lines going towards SF are Daly City, Millbrae, SF Airport
        to_sf = []
        to_oak = []

        valid_lines = ["Daly City", "Millbrae", "SF Airport"]
        valid_lines_to_oakland = ["Antioch", "Richmond"]

        for train in mcar["estimates"]:
            if train["lineTerminus"] in valid_lines:
                to_sf.append({"MacArthur": {"lineTerminus": train["lineTerminus"], "estimates": train["estimates"]}})
        for train in rock["estimates"]:
            if train["lineTerminus"] in valid_lines:
                to_sf.append({"Rockridge": {"lineTerminus": train["lineTerminus"], "estimates": train["estimates"]}})

        # From SF
        for train in pow["estimates"]:
            if train["lineTerminus"] in valid_lines_to_oakland:
                to_oak.append({"Powel Street": {"lineTerminus": train["lineTerminus"], "estimates": train["estimates"]}})

        return {"to_sf": to_sf, "to_oak": to_oak}
    

    if request.form.get("mode") == "bus":
        return Response(json.dumps(bus()), content_type="application/json")
    if request.form.get("mode") == "train":
        return Response(json.dumps(trainToSF()), content_type="application/json")
    
    return Response(json.dumps({"error": True, "message": "400 Bad Request"}), content_type="application/json"), 400

if __name__ == '__main__':
    app.run(port=5003, host='0.0.0.0')