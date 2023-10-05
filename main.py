from flask import Flask, render_template, session, request, redirect, url_for
import json
import db
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = json.loads(open('config.json').read())["secret_key"]



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
    if 'username' not in session:
        return render_template("index.html")
    api = db.selectAllEvents()
    validEvents = []
    for event in api:
        for user in event[3].split(","):
            if user == session['username']:
                validEvents.append(event)
    return render_template("dash.html", events=validEvents, username=session['username'])

@app.route("/login")
def login():
    redirect_url = url_for("authorize", _external=True)
    return github.authorize_redirect(redirect_url)

@app.route("/authorize")
def authorize():
    token = github.authorize_access_token()
    resp = github.get('user', token=token)
    profile = resp.json()
    session['username'] = profile['login']
    return redirect('/')

@app.route("/logout")
def logout():
    session.pop('username')
    return redirect("/")

if __name__ == '__main__':
    app.run(port=5000)