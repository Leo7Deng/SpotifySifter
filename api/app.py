import requests
import urllib.parse
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session
from app_init import app, db
from models import User, OAuth
from cron import run as cron_run

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
    scope = "user-read-recently-played user-read-playback-state user-read-email user-library-read playlist-modify-public playlist-modify-private"
    

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

    req_body = {}
    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

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
        current_user = User()
        current_user.email = user_email
        db.session.add(current_user)
        db.session.commit()

    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]
    
    expires_at = datetime.now().timestamp() + token_info["expires_in"]
    if current_user:
        from models import db, OAuth
        oauth = OAuth.query.filter_by(user_id=current_user.id).first()

        if oauth:
            # Update existing OAuth entry
            oauth.access_token = access_token
            oauth.refresh_token = refresh_token
            oauth.expires_at = expires_at
        else:
            # Create a new OAuth entry
            oauth = OAuth(
                user_id=current_user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
            db.session.add(oauth)

        db.session.commit()
    
    cron_run()
    return redirect(f'http://localhost:3000/PlaylistSelect?current_user={current_user}')

if __name__ == "__main__":
    app.run(debug=True, port=8888)

