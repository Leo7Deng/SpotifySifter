import atexit
import base64
import os
import time
import requests
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import threading
from config import app, db
from models import User, OAuth, Playlist, PrevQueue, Skipped, Playlist

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
CURRENTLY_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REPEAT_URL = "https://api.spotify.com/v1/me/player/repeat"

job_lock = threading.Lock()


def set_repeat(headers):
    repeat_data = {"state": "context"}
    requests.put(REPEAT_URL, headers=headers, params=repeat_data)

def create_playlist(playlist, t, user_id, headers):
    CREATE_PLAYLIST_ENDPOINT = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    playlist_data = json.dumps(
        {
            "name": f"{playlist.name}'s Sifted Songs",
            "description": f"Playlist created by Playlist Sifter",
            "public": False,
        }
    )
    response = requests.post(
        CREATE_PLAYLIST_ENDPOINT, headers=headers, data=playlist_data
    ).text
    playlist_uri = json.loads(response)["id"]
    tracks_data = json.dumps(
        {
            "uris": [t.track_id],
        }
    )
    ADD_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
    response = requests.post(ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data).text
    playlist.delete_playlist = playlist_uri
    db.session.commit()


def get_response(access_token, endpoint):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 204 or response.status_code == 503:
        return None
    if not response.ok:
        print("Error in response")
        return None
    return response.json()


def get_currently_playing(user):
    access_token = user.oauth.access_token
    if access_token is None:
        return None
    response = get_response(
        access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT
    )
    return response


def update_currently_playing_playlist(user):
    selected = True
    response = get_currently_playing(user)
    is_playing = False
    if response is None:
        print(user.user_id + " is not playing Spotify")
        return False
    else:
        try:
            uri = response["context"]["uri"]
        except:
            if user is None:
                print("User not found")
            else:
                playlists = Playlist.query.filter_by(user_id=user.id).all()
                for playlist in playlists:
                    playlist.currently_playing = False
                print(user.user_id + " is not playing Spotify")
            return False
        currently_playing_playlist = None
        playlists = Playlist.query.filter_by(user_id=user.id).all()
        for playlist in playlists:
            if playlist.playlist_id == uri:  # if playlist is currently playing
                currently_playing_playlist = playlist
                if playlist.selected == True:  # if playlist is selected
                    is_playing = True
                    if (
                        playlist.currently_playing == False
                    ):  # if playlist was not previously playing
                        PrevQueue.query.filter_by(user_id=user.id).delete()
                    playlist.currently_playing = True
                else:  # if playlist is not selected
                    selected = False
                    playlist.currently_playing = False

            else:  # if playlist is not currently playing
                playlist.currently_playing = False
        db.session.commit()
        if selected == False:  # if playlist is not selected
            print(user.user_id + " is not playing a selected playlist")
            return False
        if currently_playing_playlist is None:  # if playlist is not owned by user
            print(user.user_id + " is not playing in an owned playlist")
            return False
        if is_playing == True:  # if playlist is currently playing
            print(user.user_id + " is playing " + currently_playing_playlist.name)
            return is_playing
    return is_playing


def get_current_queue_uris(user):
    # get current queue
    oauth = user.oauth
    if oauth is None:
        return []
    access_token = oauth.access_token
    response = get_response(access_token=access_token, endpoint=QUEUE_ENDPOINT)
    if response:
        queue = [track["uri"] for track in response["queue"]]
        queue = [response["currently_playing"]["uri"]] + queue
        queue_name = [track["name"] for track in response["queue"]]
        queue_name = [response["currently_playing"]["name"]] + queue_name
        queue_name = queue_name[:-1]
        print(user.user_id + "'s queue: " + str(queue_name))
    else:
        queue = []
    return queue


def set_prev_queue(user_id, current_queue_uris):
    # each user has 20 prev_queue items
    prev_queue = PrevQueue.query.filter_by(user_id=user_id).all()
    if prev_queue:
        for i, uri in enumerate(current_queue_uris):
            prev_queue[i].track_id = uri
    else:
        for i, uri in enumerate(current_queue_uris, start=1):
            prev_queue_item = PrevQueue()
            prev_queue_item.track_id = uri
            prev_queue_item.queue_index = i
            prev_queue_item.user_id = user_id
            db.session.add(prev_queue_item)
    db.session.commit()


def delete_tracks_from_playlist(playlist, change_tracks, headers):
    playlist_uri = playlist.playlist_id
    if playlist_uri == "collection":
        DELETE_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/me/tracks"
        tracks_data = json.dumps({"ids": [uri.split(":")[-1] for uri in change_tracks]})
    else:
        DELETE_ITEMS_ENDPOINT = (
            f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
        )
        tracks_data = json.dumps({"tracks": [{"uri": uri} for uri in change_tracks]})

    response = requests.delete(DELETE_ITEMS_ENDPOINT, headers=headers, data=tracks_data)



def refresh_token(user):
    MAX_RETRIES = 2
    RETRY_DELAY = 20
    if user.oauth.expires_at < datetime.now().timestamp():
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": user.oauth.refresh_token,
            "client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
        }
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        auth_header = f"{os.environ.get('SPOTIFY_CLIENT_ID')}:{client_secret}"
        auth_header = auth_header.encode("ascii")
        auth_header = base64.b64encode(auth_header)
        auth_header = auth_header.decode("ascii")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}",
        }

        for attempt in range(MAX_RETRIES):
            response = requests.post(TOKEN_URL, data=req_body, headers=headers)
            if response.status_code == 400:
                print("User revoked access, deleting user")
                Skipped.query.filter_by(user_id=user.id).delete()
                Playlist.query.filter_by(user_id=user.id).delete()
                PrevQueue.query.filter_by(user_id=user.id).delete()
                OAuth.query.filter_by(user_id=user.id).delete()
                db.session.delete(user)
                db.session.commit()
                return
            try:
                new_token_info = response.json()
                if "access_token" in new_token_info:
                    user.oauth.access_token = new_token_info["access_token"]
                    user.oauth.expires_at = (
                        datetime.now().timestamp() + new_token_info["expires_in"]
                    )
                    db.session.commit()
                    print("Refreshed " + user.user_id + "'s token")
                    print("New Token Info:", new_token_info)
                    return
                else:
                    print("Refresh token not found in response")
                    return
            except json.JSONDecodeError:
                print("Failed to decode JSON. Attempt:", attempt + 1)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
        print("All attempts to refresh token failed")

def skip_logic():
    print("Executing skip_logic()")
    with app.app_context():
        for user in User.query.all():
            skip_logic_user(user)


def skip_logic_user(user):
    refresh_token(user)

    if os.environ.get("FLASK_ENV") != "production":
        acquired = job_lock.acquire(blocking=False)
        if acquired:
            job_lock.release()


    access_token = user.oauth.access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    is_playing = update_currently_playing_playlist(user=user)
    if not is_playing:
        return

    # check if user has premium
    requests.get(EMAIL_ENDPOINT, headers=headers)
    if not requests.get(EMAIL_ENDPOINT, headers=headers).json()["product"] == "premium":
        print(user.user_id + " does not have premium")
        return

    # wont work if queue is less than 20 songs
    current_queue_uris = get_current_queue_uris(user=user)
    if len(current_queue_uris) < 20:
        print("Queue has less than 20 songs")
        return

    current_playlist = Playlist.query.filter_by(
        user_id=user.id, currently_playing=True
    ).first()
    if current_playlist is None:
        raise Exception("No playlist currently playing")

    prev_queue = PrevQueue.query.filter_by(user_id=user.id).all()
    if not prev_queue:
        set_prev_queue(user_id=user.id, current_queue_uris=current_queue_uris)
        return

    # tracks played in the last 60 seconds including skipped
    played_tracks_60_uris = [
        track.track_id
        for track in prev_queue
        if track.track_id not in current_queue_uris
    ]

    user.total_played += len(played_tracks_60_uris)
    if (
        # code to see if skipped to previous
        current_queue_uris[19] == prev_queue[19 - len(played_tracks_60_uris)].track_id
        and len(played_tracks_60_uris) > 0
    ):
        print("Skipped to previous")
        set_prev_queue(user_id=user.id, current_queue_uris=current_queue_uris)
        return
    elif (
        # code to see if queue shuffled
        current_queue_uris[19 - len(played_tracks_60_uris)] != prev_queue[19].track_id
        and current_queue_uris[18 - len(played_tracks_60_uris)]
        != prev_queue[18].track_id
        and len(played_tracks_60_uris) > 0
    ):
        print("Shuffled playlist")
        set_prev_queue(user_id=user.id, current_queue_uris=current_queue_uris)
        return

    recently_played_response = get_response(
        access_token=access_token, endpoint=RECENTLY_PLAYED_ENDPOINT
    )
    if recently_played_response is None:
        print("No recently played tracks found")
        return

    # tracks played in the last 60 seconds excluding skipped
    recently_played_uris = [
        item["track"]["uri"] for item in recently_played_response["items"]
    ]

    # tracks skipped in the last 60 seconds
    skipped_tracks_60_uris = [
        track for track in played_tracks_60_uris if track not in recently_played_uris
    ]

    skipped_tracks_history = Skipped.query.filter_by(
        playlist_id=current_playlist.id, user_id=user.id
    ).all()
    for track in skipped_tracks_history:
        if track.track_id in recently_played_uris:
            db.session.delete(track)

    skipped_tracks_history_uris = [track.track_id for track in skipped_tracks_history]

    # remove skipped tracks from history if they are played
    for track in recently_played_uris:
        if track in skipped_tracks_history_uris:
            delete_track = Skipped.query.filter_by(
                playlist_id=current_playlist.id, user_id=user.id, track_id=track
            ).first()
            if delete_track is not None:
                db.session.delete(delete_track)
                print("Succesfully deleted " + track + " from skipped history")
            print(track + " is not found in database")
            

    print(skipped_tracks_history_uris)
    print(recently_played_uris)
    print(user.user_id + " skipped " + str(len(skipped_tracks_60_uris)) + " songs")

    # tracks that will be removed from playlist
    change_tracks = []
    for skipped_uri in skipped_tracks_60_uris:
        if skipped_uri not in skipped_tracks_history_uris:
            new_skipped = Skipped()
            new_skipped.playlist_id = current_playlist.id
            new_skipped.track_id = skipped_uri
            new_skipped.user_id = user.id
            new_skipped.skipped_count = 1
            db.session.add(new_skipped)
        
        skipped_track = Skipped.query.filter_by(track_id=skipped_uri).first()
        if skipped_track is None:
            raise Exception("Skipped track not found")

        skipped_track.skipped_count += 1
        if skipped_track.skipped_count < current_playlist.skip_count:
            continue

        change_tracks.append(skipped_track.track_id)
        if current_playlist.delete_playlist:
            playlist_uri = current_playlist.delete_playlist
            if playlist_uri == "collection":
                ADD_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/me/tracks"
            else:
                ADD_ITEMS_ENDPOINT = (
                    f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
                )
            tracks_data = json.dumps(
                {
                    "uris": [skipped_track.track_id],
                }
            )
            requests.post(ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data).text
        else:
            create_playlist(
                playlist=current_playlist,
                t=skipped_track,
                user_id=user.user_id,
                headers=headers,
            )
        delete_tracks_from_playlist(
            playlist=current_playlist, change_tracks=change_tracks, headers=headers
        )
        print("Created new playlist")
    set_prev_queue(user_id=user.id, current_queue_uris=current_queue_uris)
    db.session.commit()


def main():
    skip_logic()
    if os.environ.get("FLASK_ENV") != "production":
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=skip_logic, trigger="interval", seconds=5)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    main()
