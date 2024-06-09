import json
import requests
import urllib.parse
import os
from flask_cors import CORS
from flask_session import Session
from datetime import datetime
from flask import redirect, request, jsonify, session
from config import app, db
from models import Skipped, User, OAuth, Playlist
from cron import main as cron_run
from flask_cors import cross_origin

Session(app)
CORS(app, supports_credentials=True)

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
if os.environ.get("FLASK_ENV") == "production":
    REDIRECT_URI = "https://api.playlistsifter.com/callback"
else:
    REDIRECT_URI = "http://localhost:8889/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"

def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login")
def login():
    scope = "user-read-recently-played user-read-playback-state user-read-email user-library-read playlist-modify-public playlist-modify-private playlist-read-private user-library-modify user-read-currently-playing"
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
@cross_origin(supports_credentials=True)
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
        liked_songs_playlist.skip_count = 2
        db.session.add(liked_songs_playlist)
        db.session.commit()
        print("Added new user:" + user_info.json()["id"])

    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]
    session["user_id"] = current_user.id

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
    if os.environ.get("FLASK_ENV") != "production":
        cron_run()

    if os.environ.get("FLASK_ENV") == "production":
        redirect_url = "https://playlistsifter.com"
    else:
        redirect_url = "http://localhost:3000"
    return redirect(
        f"{redirect_url}/PlaylistSelect"
    )


@app.route("/get_playlists")
@cross_origin(supports_credentials=True)
def get_playlists():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # get user from user_id using get
    current_user = User.query.get(session["user_id"])

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
        user_id=current_user.id, playlist_id="collection"
    ).first()
    playlists = [
        {
            "name": "Liked Songs",
            "id": "collection",
            "selected": liked_songs_playlist.selected
            if liked_songs_playlist  # if no existing liked songs, set selected to False
            else False,
            "skip_count": liked_songs_playlist.skip_count if liked_songs_playlist else 2,
            "sifted_playlist": liked_songs_playlist.delete_playlist if liked_songs_playlist else None,
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
    database_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    # For each playlist in the response, add it to the database if it doesn't exist
    for item in response.json()["items"]:
        selected = False
        skip_count = 2
        sifted_playlist = ""
        if (
            item["owner"]["id"] == current_user.user_id
            and item["id"] not in deleted_songs_playlists
        ):
            if item["id"] != "collection" and item["id"] not in [
                playlist.playlist_id for playlist in database_playlists
            ]:
                playlist_db = Playlist()
                playlist_db.user_id = current_user.id
                playlist_db.playlist_id = item["id"]
                playlist_db.name = item["name"]
                playlist_db.currently_playing = False
                playlist_db.selected = False
                playlist_db.delete_playlist = None
                playlist_db.skip_count = 2
                db.session.add(playlist_db)
                db.session.commit()
            else:
                for playlist in database_playlists:
                    if playlist.playlist_id == item["id"]:
                        selected = playlist.selected
                        skip_count = playlist.skip_count
                        sifted_playlist = playlist.delete_playlist
                        break
            playlists.append(
                {"name": item["name"], "id": item["id"], "selected": selected, "image": item["images"][0]["url"], "skip_count": skip_count, "sifted_playlist": sifted_playlist}
            )

    # Print only name of playlists
    print([playlist["name"] for playlist in playlists])

    return jsonify(playlists)


@app.route("/get_delete_playlists")
@cross_origin(supports_credentials=True)
def get_delete_playlists():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])

    # Check if user exists
    if current_user is None:
        raise Exception("User not found.")

    # Get playlists that hold the sifted songs from database
    deleted_songs_playlists = Playlist.query.filter(
        Playlist.delete_playlist != None, Playlist.user_id == current_user.id
    ).all()

    # List of playlist ids that hold the sifted songs
    deleted_songs_playlists_uris = [
        playlist.delete_playlist for playlist in deleted_songs_playlists
    ]

    # Return list of playlist ids that hold the sifted songs
    return jsonify(deleted_songs_playlists_uris)


@app.route("/select/<playlist_id>")
@cross_origin(supports_credentials=True)
def select(playlist_id):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    # Get playlist from database
    playlist = Playlist.query.filter_by(
        user_id=current_user.id, playlist_id=playlist_id
    ).first()

    # Check if playlist exists
    if playlist:
        playlist.selected = True
        db.session.commit()
        print(current_user.user_id + "selected playlist " + playlist.name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})


@app.route("/unselect/<playlist_id>")
@cross_origin(supports_credentials=True)
def unselect(playlist_id):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    # Get playlist from database
    playlist = Playlist.query.filter_by(
        user_id=current_user.id, playlist_id=playlist_id
    ).first()

    # Check if playlist exists
    if playlist:
        playlist.selected = False
        db.session.commit()
        print(current_user.user_id + "unselected playlist " + playlist.name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})

@app.route("/currently_playing")
@cross_origin(supports_credentials=True)
def currently_playing():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    access_token = current_user.oauth.access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing", headers=headers
    )
    if response.status_code == 200:
        return jsonify(response.json()["item"]["name"])
    else:
        return jsonify({"success": False})


@app.route("/new_delete_playlists/<playlist_id>")
@cross_origin(supports_credentials=True)
def new_delete_playlists(playlist_id):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    user = User.query.get(session["user_id"])
    if user is None:
        raise Exception("User not found.")

    access_token = current_user.oauth.access_token
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        GET_PLAYLIST_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        )
        CREATE_PLAYLIST_ENDPOINT = (
            f"https://api.spotify.com/v1/users/{user.user_id}/playlists"
        )

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(GET_PLAYLIST_ENDPOINT, headers=headers).json()
        tracks = response["items"]
        track_ids = []
        for track in tracks:
            track_ids.append(track["track"]["uri"])

        headers = {"Authorization": f"Bearer {access_token}"}
        playlist_data = {
            "name": f"{playlist.name}'s Sifted Songs",
            "description": f"Playlist created by Playlist Sifter",
            "public": False,
        }
        response = requests.post(
            CREATE_PLAYLIST_ENDPOINT, headers=headers, data=playlist_data
        ).text
        playlist_uri = json.loads(response)["id"]
        headers = {"Authorization": f"Bearer {access_token}"}
        tracks_data = {
            "uris": track_ids,
        }
        ADD_ITEMS_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
        )
        response = requests.post(
            ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data
        ).text
        playlist.delete_playlist = playlist_uri
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})

@app.route("/update_playlist_skip_count/<playlist_id>/<new_skip_count>")
@cross_origin(supports_credentials=True)
def update_playlist_skip_count(playlist_id, new_skip_count):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    user = User.query.get(session["user_id"])
    if user is None:
        raise Exception("User not found.")

    playlist = Playlist.query.filter_by(
        user_id=current_user.id, playlist_id=playlist_id
    ).first()

    if playlist:
        playlist.skip_count = int(new_skip_count)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})

# @app.route("/update_playlist_skip_count/<playlist_id>/<new_skip_count>")
# @cross_origin(supports_credentials=True)
# def update_playlist_skip_count(playlist_id, new_skip_count):
#     current_user_id = session.get("user_id")
#     if not current_user_id:
#         return jsonify({"error": "Unauthorized access"})

#     # Get user from database
#     current_user = User.query.get(session["user_id"])
#     if current_user is None:
#         raise Exception("User not found.")

#     user = User.query.get(session["user_id"])
#     if user is None:
#         raise Exception("User not found.")

#     playlist = Playlist.query.filter_by(
#         user_id=current_user.id, playlist_id=playlist_id
#     ).first()
#     access_token = current_user.oauth.access_token

#     if playlist:
#         delete_playlist = playlist.delete_playlist
#         headers = {"Authorization": f"Bearer {access_token}"}
#         skipped_tracks_db = Skipped.query.filter_by(playlist_id=playlist.id, user_id=user.id).all()
#         for skipped_track in skipped_tracks_db:
#             if skipped_track.skipped_count < int(new_skip_count):
#                 PLAYLIST_ADD_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris=spotify%3Atrack%3A{skipped_track.track_id}"
#                 response = requests.delete(PLAYLIST_ADD_ENDPOINT, headers=headers)
#         playlist.skip_count = int(new_skip_count)
#         db.session.commit()
#         return jsonify({"success": True})
#     else:
#         return jsonify({"success": False, "message": "Playlist not found."})


@app.route("/resift_playlist/<playlist_id>")
@cross_origin(supports_credentials=True)
def resift_playlist(playlist_id):
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({"error": "Unauthorized access"})

    # Get user from database
    current_user = User.query.get(session["user_id"])
    if current_user is None:
        raise Exception("User not found.")

    playlist = Playlist.query.get(playlist_id)
    access_token = current_user.oauth.access_token

    if playlist:
        if not playlist.delete_playlist:
            return jsonify({"success": False, "message": "Playlist not sifted."})
        delete_playlist_id = playlist.delete_playlist
        GET_DELETE_PLAYLIST_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{delete_playlist_id}/tracks"
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(GET_DELETE_PLAYLIST_ENDPOINT, headers=headers).json()
        sifted_tracks = response["items"]
        sifted_tracks_id = []
        for track in sifted_tracks:
            sifted_tracks_id.append(track["track"]["id"])

        GET_PLAYLIST_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        )
        response = requests.get(GET_PLAYLIST_ENDPOINT, headers=headers).json()
        tracks = response["items"]
        tracks_id = []
        for track in tracks:
            tracks_id.append(track["track"]["id"])

        skipped_tracks_db = Skipped.query.filter_by(playlist_id=playlist.id).all()
        add_tracks = []
        remove_tracks = []
        for skipped_track in skipped_tracks_db:
            if skipped_track.track_id not in sifted_tracks_id:
                add_tracks.append(skipped_track.track_id)
            if skipped_track.track_id in tracks_id:
                remove_tracks.append(skipped_track.track_id)
        add_tracks_data = {
            "uris": add_tracks,
        }
        remove_tracks_data = {
            "tracks": [
                {"uri": f"spotify:track:{track_id}"} for track_id in remove_tracks
            ],
        }
        ADD_ITEMS_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{delete_playlist_id}/tracks"
        )
        response = requests.post(
            ADD_ITEMS_ENDPOINT, headers=headers, data=add_tracks_data
        ).text
        DELETE_ITEMS_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        )
        response = requests.delete(
            DELETE_ITEMS_ENDPOINT, headers=headers, data=remove_tracks_data
        ).text

        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Playlist not found."})


if __name__ == "__main__":
    app.run(host="localhost", port=8889, debug=False)
