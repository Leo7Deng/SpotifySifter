import requests
import urllib.parse
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session
from app_init import app, db
from models import User, OAuth, Playlist, Track, Skipped, PrevQueue
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
    scope = "user-read-recently-played user-read-playback-state user-read-email user-library-read playlist-modify-public playlist-modify-private user-modify-playback-state playlist-read-private"
    

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
        current_user.user_id = user_info.json()['id']
        current_user.total_played = 0
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
    # return redirect(f'/get_playlists?current_user_id={current_user.id}')
    return redirect(f'http://localhost:3000/PlaylistSelect?current_user_id={current_user.id}')

from models import db, User, Playlist

@app.route("/get_playlists/<current_user_id>")
def get_playlists(current_user_id):
    current_user = User.query.filter_by(id=current_user_id).first()
    access_token = current_user.oauth.access_token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"
    response = requests.get(PLAYLISTS_URL, headers=headers, params={"limit": 50})
    playlists = []
 
    deleted_songs_playlists = Playlist.query.filter(Playlist.delete_playlist != None).all()
    deleted_songs_playlists = [playlist.delete_playlist for playlist in deleted_songs_playlists]

    database_playlists = Playlist.query.filter_by(user_id=current_user_id).all()

    for item in response.json()["items"]:
        # find the select column of database_playlists
        selected = False
        for playlist in database_playlists:
            if playlist.playlist_id == item["id"]:
                if playlist.selected:
                    selected = True
        playlist = {
            "name": item["name"],
            "id": item["id"],
            "owner_id": item["owner"]["id"],
            "image": item["images"][0]["url"]
        }

        if selected:
            playlist["selected"] = True
        else:
            playlist["selected"] = False

        if current_user and playlist["owner_id"] == current_user.user_id and playlist["id"] not in deleted_songs_playlists:
            playlists.append(playlist)

    for playlist in playlists:
        print(playlist["name"])

    return jsonify(playlists)

    # return redirect(f'http://localhost:3000/PlaylistSelect?playlists={playlists}')

@app.route("/manage_playlists/<current_user_id>")
def manage_playlists(current_user_id):
    user = User.query.filter_by(id=current_user_id).first()
    access_token = user.oauth.access_token
    PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(PLAYLISTS_URL, headers=headers, params={"limit": 50})

    deleted_songs_playlists = Playlist.query.filter(Playlist.delete_playlist != None).all()
    deleted_songs_playlists = [playlist.delete_playlist for playlist in deleted_songs_playlists]

    for item in response.json()["items"]:
        playlist_id = item["id"]

        if item["owner"]["id"] == user.user_id and playlist_id not in deleted_songs_playlists:
            playlist_db = Playlist.query.filter_by(user_id=user.id, playlist_id=playlist_id).first()

            if not playlist_db:
                playlist_db = Playlist(
                    user_id=user.id,
                    playlist_id=playlist_id,
                    name=item["name"],
                    currently_playing=False,
                    selected=False,
                    delete_playlist=None
                )
                db.session.add(playlist_db)
                db.session.commit()
    return jsonify({"success": True})

from flask import jsonify

from models import db, User, Playlist
from flask import jsonify

@app.route("/select/<current_user_id>/<playlistId>")
def select(current_user_id, playlistId):
    playlist = Playlist.query.filter_by(user_id=current_user_id, playlist_id=playlistId).first()
    if playlist:
        playlist.selected = True
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})

if __name__ == "__main__":
    app.run(debug=True, port=8888)

