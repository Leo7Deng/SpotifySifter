import requests
import urllib.parse
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session
from __init__ import app
# app = Flask(__name__)

# app.app_context().push()
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]

# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)
CORS(app)

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8888/callback"


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"

@app.route("/login")
def login():
    scope = "user-read-recently-played user-read-playback-state user-read-email"
    

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": scope, 
        "redirect_uri": REDIRECT_URI,
        "consent": "prompt",
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return jsonify({"auth_url": auth_url})

@app.route("/callback")
def callback():
    if "error" in request.args:
        return jsonify({"error": request.args["error"]})

    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

    #    session['access_token'] = token_info['access_token']
    #    session['refresh_token'] = token_info['refresh_token']
    #    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()

    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    headers = {
        'Authorization': f'Bearer {token_info["access_token"]}'
    }
    user_info = requests.get(EMAIL_ENDPOINT, headers=headers)
    user_email = user_info.json()['email']
    current_user = User.query.filter_by(email=user_email).first()
    if not current_user:
        from models import db
        current_user = User(email=user_email)
        db.session.add(current_user)
    
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    current_user.access_token = access_token
    current_user.refresh_token = refresh_token

    db.session.add(current_user)
    db.session.commit()
    
    # cron_run()
    return redirect(f'http://localhost:3000/GetCurrentTrack?access_token={token_info["access_token"]}')

@app.route("/refresh_token")
def refresh_token():
    if "refresh_token" not in session:
        return redirect("/login")

    if session["expires_at"] < datetime.now().timestamp():
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

    response = request.post(TOKEN_URL, data=req_body)
    new_token_info = response.json()

    session["access_token"] = new_token_info["access_token"]
    session["expires_at"] = datetime.now().timestamp() + new_token_info["expires_in"]

    return redirect("/playlists")

if __name__ == "__main__":
    from models import User
    from cron import run as cron_run
    app.run(debug=True, port=8888)

