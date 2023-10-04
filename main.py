from flask import Flask, render_template, session
import json

app = Flask(__name__)
app.secret_key = json.loads(open('config.json').read())["secret_key"]


@app.route('/')
def welcome():
    if 'username' not in session:
        return render_template("index.html")
    return render_template("dash.html")

if __name__ == '__main__':
    app.run(port=5000)