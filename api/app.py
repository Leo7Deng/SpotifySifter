import requests
import urllib.parse
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask import redirect, request, jsonify
from api import app, db
from .models import User, OAuth, Playlist
from .cron import run as cron_run

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
if os.environ.get("FLASK_ENV") == "production":
    REDIRECT_URI = "https://spotifysifter.com/callback"
else:
    REDIRECT_URI = "http://localhost:8889/callback" 


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"


@app.route("/login")
def login():
    scope = "user-read-recently-played user-read-playback-state user-read-email user-read-private user-library-read playlist-modify-public playlist-modify-private user-modify-playback-state playlist-read-private user-library-modify user-read-currently-playing user-modify-playback-state"
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
        error_message = request.args["error"]
        print(f"Error in callback: {error_message}")
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
    headers = {"Authorization": f'Bearer {token_info["access_token"]}'}
    user_info = requests.get(EMAIL_ENDPOINT, headers=headers)
    user_email = user_info.json()["email"]
    current_user = User.query.filter_by(email=user_email).first()
    if not current_user:
        current_user = User()
        current_user.email = user_email
        current_user.user_id = user_info.json()["id"]
        current_user.profile_pic = user_info.json()["images"][1]["url"]
        current_user.total_played = 0
        db.session.add(current_user)
        current_user = User.query.filter_by(email=user_email).first()
        liked_songs_playlist = Playlist()
        current_user = User.query.filter_by(email=user_email).first()
        if current_user is None:
            raise Exception("User not found.")
        liked_songs_playlist.user_id = current_user.id
        liked_songs_playlist.playlist_id = "collection"
        liked_songs_playlist.name = "Liked Songs"
        liked_songs_playlist.currently_playing = False
        liked_songs_playlist.selected = False
        liked_songs_playlist.delete_playlist = None
        db.session.add(liked_songs_playlist)
        db.session.commit()
        print("Added new user")

    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    expires_at = datetime.now().timestamp() + token_info["expires_in"]
    if current_user:
        oauth = OAuth.query.filter_by(user_id=current_user.id).first()

        if oauth:
            # Update existing OAuth entry
            oauth.access_token = access_token
            oauth.refresh_token = refresh_token
            oauth.expires_at = expires_at
        else:
            # Create a new OAuth entry
            oauth = OAuth()
            oauth.user_id = current_user.id
            oauth.access_token = access_token
            oauth.refresh_token = refresh_token
            oauth.expires_at = expires_at
            db.session.add(oauth)

        db.session.commit()

    cron_run()
    # return redirect(f'/get_playlists?current_user_id={current_user.id}')
    if os.environ.get("FLASK_ENV") == "production":
        redirect_url = "https://spotifysifter.com"
    else:
        redirect_url = "http://localhost:3000"
    return redirect(
        f"{redirect_url}/PlaylistSelectCheck?current_user_id={current_user.id}&access_token={access_token}"
    )


@app.route("/get_playlists/<current_user_id>")
def get_playlists(current_user_id):
    current_user = User.query.filter_by(id=current_user_id).first()

    # Check if user exists
    if current_user is None:
        raise Exception("User not found.")
    
    # Set headers
    access_token = current_user.oauth.access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get playlists up to 50
    PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"
    response = requests.get(PLAYLISTS_URL, headers=headers, params={"limit": 50})

    # Get liked songs playlist from database
    liked_songs_playlist = Playlist.query.filter_by(
        user_id=current_user_id, playlist_id="collection"
    ).first()
    playlists = [
        {
            "name": "Liked Songs",
            "id": "collection",
            "selected": liked_songs_playlist.selected
            if liked_songs_playlist # if no existing liked songs, set selected to False
            else False,
        }
    ]

    # Get playlists that hold the sifted songs from database
    deleted_songs_playlists = Playlist.query.filter(
        Playlist.delete_playlist != None
    ).all() 

    # List of playlist ids that hold the sifted songs
    deleted_songs_playlists = [
        playlist.delete_playlist for playlist in deleted_songs_playlists
    ]

    # Get playlists from database
    database_playlists = Playlist.query.filter_by(user_id=current_user_id).all()

    # For each playlist in the response, add it to the database if it doesn't exist
    for item in response.json()["items"]:
        selected = False
        if (
            item["owner"]["id"] == current_user.user_id
            and item["id"] not in deleted_songs_playlists
        ):
            if item["id"] != "collection" and item["id"] not in [
                playlist.playlist_id for playlist in database_playlists
            ]:
                playlist_db = Playlist()
                playlist_db.user_id = current_user_id
                playlist_db.playlist_id = item["id"]
                playlist_db.name = item["name"]
                playlist_db.currently_playing = False
                playlist_db.selected = False
                playlist_db.delete_playlist = None
                db.session.add(playlist_db)
                db.session.commit()
            else:
                for playlist in database_playlists:
                    if playlist.playlist_id == item["id"]:
                        selected = playlist.selected
                        break
            playlists.append(
                {"name": item["name"], "id": item["id"], "selected": selected}
            )

    # Print playlists that are in the database or response
    for playlist in playlists:
        print(playlist["name"])

    return jsonify(playlists)

    # return redirect(f'http://localhost:3000/PlaylistSelect?playlists={playlists}')


# Only used in PlaylistSelect.js
@app.route("/manage_playlists/<current_user_id>")
def manage_playlists(current_user_id):
    # Get user from database
    user = User.query.filter_by(id=current_user_id).first()

    # Check if user exists
    if user is None:
        raise Exception("User not found.")
    
    # Set headers
    access_token = user.oauth.access_token
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get playlists up to 50
    PLAYLISTS_URL = "https://api.spotify.com/v1/me/playlists"
    response = requests.get(PLAYLISTS_URL, headers=headers, params={"limit": 50})

    # Get playlists that hold the sifted songs from database
    deleted_songs_playlists = Playlist.query.filter(
        Playlist.delete_playlist != None
    ).all()
    deleted_songs_playlists = [
        playlist.delete_playlist for playlist in deleted_songs_playlists
    ]

    # For each playlist in the response, add it to the database if it doesn't exist
    for item in response.json()["items"]:
        playlist_id = item["id"]

        if (
            item["owner"]["id"] == user.user_id
            and playlist_id not in deleted_songs_playlists
        ):
            playlist_db = Playlist.query.filter_by(
                user_id=user.id, playlist_id=playlist_id
            ).first()
            if not playlist_db:
                playlist_db = Playlist()
                playlist_db.user_id = user.id
                playlist_db.playlist_id = playlist_id
                playlist_db.name = item["name"]
                playlist_db.currently_playing = False
                playlist_db.selected = False
                playlist_db.delete_playlist = None
                db.session.add(playlist_db)
                db.session.commit()

    return jsonify({"success": True})


@app.route("/get_delete_playlists/<current_user_id>")
def get_delete_playlists(current_user_id):
    # Get user from database
    user = User.query.filter_by(id=current_user_id).first()

    # Check if user exists
    if user is None:
        raise Exception("User not found.")
    
    # Get playlists that hold the sifted songs from database
    deleted_songs_playlists = Playlist.query.filter(
        Playlist.delete_playlist != None,
        Playlist.user_id == user.id
    ).all()

    # List of playlist ids that hold the sifted songs
    deleted_songs_playlists_uris = [
        playlist.delete_playlist for playlist in deleted_songs_playlists
    ]

    # Return list of playlist ids that hold the sifted songs
    return jsonify(deleted_songs_playlists_uris)


@app.route("/select/<current_user_id>/<playlistId>")
def select(current_user_id, playlistId):
    # Get playlist from database
    playlist = Playlist.query.filter_by(
        user_id=current_user_id, playlist_id=playlistId
    ).first()

    # Check if playlist exists
    if playlist:
        playlist.selected = True
        db.session.commit()
        print("Selected playlist " + playlist.name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})


@app.route("/unselect/<current_user_id>/<playlistId>")
def unselect(current_user_id, playlistId):
    # Get playlist from database
    playlist = Playlist.query.filter_by(
        user_id=current_user_id, playlist_id=playlistId
    ).first()

    # Check if playlist exists
    if playlist:
        playlist.selected = False
        db.session.commit()
        print("Unselected playlist " + playlist.name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})


@app.route("/leaderboard")
def leaderboard():
    # Get users from database in descending order of total_played
    users = User.query.order_by(User.total_played.desc()).all()

    # Return list of users
    users = [
        {
            "username": user.user_id,
            "total_played": user.total_played,
            "profile_pic": user.profile_pic,
            "id": user.id,
        }
        for user in users
    ]

    # Return top 10 users
    return jsonify(users[:10])


@app.route("/currently_playing/<access_token>")
def currently_playing(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing", headers=headers
    )
    if response.status_code == 200:
        return jsonify(response.json()["item"]["name"])
    else:
        return jsonify({"success": False})


@app.route("/total_played/<current_user_id>/<access_token>")
def total_played(current_user_id: str, access_token: str):
    user = User.query.filter_by(id=current_user_id).first()
    if user is None or user.oauth.access_token != access_token:
        return jsonify({"success": False, "message": "Invalid access token."})
    total_played = user.total_played
    return jsonify(
        {
            "success": True,
            "total_played": total_played,
            "profile_pic": user.profile_pic,
            "username": user.user_id,
        }
    )

if __name__ == "__main__":
    app.run(host="localhost", port=8889, debug=True)