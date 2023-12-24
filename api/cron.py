import atexit
import base64
import os
import requests
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
import atexit
import threading
from api import db, app
from .models import User, OAuth, Playlist, PrevQueue, Skipped, Playlist

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
CURRENTLY_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REPEAT_URL = "https://api.spotify.com/v1/me/player/repeat"

job_lock = threading.Lock()

def set_repeat(access_token, headers):
    repeat_data = {"state": "context"}
    response = requests.put(REPEAT_URL, headers=headers, params=repeat_data)


def create_playlist(access_token, playlist, t, user_id, headers):
    CREATE_PLAYLIST_ENDPOINT = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    playlist_data = json.dumps(
        {
            "name": f"{playlist.name}'s Sifted Songs",
            "description": f"Playlist created by Spotify Sifter",
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
    if not response.ok:
        raise Exception(f"HTTP error! status: {response.status_code}")
    if response.status_code == 204 or response.status_code == 503:
        return None
    return response.json()


def get_currently_playing(user):
    oauth = OAuth.query.get(user.id)
    access_token = None
    if oauth:
        access_token = oauth.access_token
    response = get_response(
        access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT
    )
    return response


def update_currently_playing_playlist(user):
    selected = True
    response = get_currently_playing(user)
    if response is None:
        print("Not currently playing")
        return False
    is_playing = False
    try:
        if response is None:
            raise KeyError
        if response["context"] is None:
            raise KeyError
        uri = response["context"]["uri"]
        uri = uri.split(":")[-1]
    except KeyError:
        if user is None:
            print ("User not found")
        else:
            playlists = Playlist.query.filter_by(user_id=user.id).all()
            for playlist in playlists:
                playlist.currently_playing = False
            print("Not currently playing")
        pass
    else:
        currently_playing_playlist = None
        playlists = Playlist.query.filter_by(user_id=user.id).all()
        for playlist in playlists:
            if playlist.playlist_id == uri:
                currently_playing_playlist = playlist
                if playlist.selected == True:
                    
                    is_playing = True
                    if playlist.currently_playing == False:
                        PrevQueue.query.filter_by(user_id=user.id).delete()
                    playlist.currently_playing = True
                else:
                    selected = False
                    playlist.currently_playing = False
                    
            else:
                playlist.currently_playing = False
        db.session.commit()
        if selected == False:
            print("Playing in an unselected playlist")
            return False
        if currently_playing_playlist is None:
            print("Playing in a playlist not owned by user")
            return False
        if is_playing == True:
            print("Currently playing " + currently_playing_playlist.name)
            return is_playing
    return is_playing

    #         if playlist.selected == True:
    #             playlist_selected = True
    #             if playlist.currently_playing == False:
    #                 PrevQueue.query.filter_by(user_id=user.id).delete()
    #             playlist_id = uri.split(":")[-1]
    #             PLAYLIST_URL = (
    #                 f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    #             )
    #             playlist_data = get_response(
    #                 access_token=user.oauth.access_token, endpoint=PLAYLIST_URL
    #             )
    #             playlist_data = playlist_data["total"]
    #             if playlist_data < 20:
    #                 playlist.currently_playing = False
    #                 print("Playlist has less than 20 songs")
    #             else:
    #                 playlist.currently_playing = True
    #                 print(playlist.name + " is playing")
    #                 is_playing = True
    #         else:
    #             playlist.currently_playing = False
    #     if not playlist_selected:
    #         print("Playing in an unselected playlist")
    # db.session.commit()


def get_current_queue_uris(user_id):
    oauth = OAuth.query.get(user_id)
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
        print(f"Queue: {queue_name}")
        # print(f"Queue: {queue}")
    else:
        queue = []
    return queue


def set_prev_queue(user_id, current_queue_uris):
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
        DELETE_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
        tracks_data = json.dumps({"tracks": [{"uri": uri} for uri in change_tracks]})
    
    response = requests.delete(
        DELETE_ITEMS_ENDPOINT, headers=headers, data=tracks_data
    )
    print(response.status_code)

import requests
def refresh_token(user):
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
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }

        response = requests.post(TOKEN_URL, data=req_body, headers=headers)
        print("Status Code:", response.status_code)
        new_token_info = response.json()
        
        print("New Token Info:", new_token_info)  # Add this line for debugging
        if "access_token" in new_token_info:
            user.oauth.access_token = new_token_info["access_token"]
            user.oauth.expires_at = (
                datetime.now().timestamp() + new_token_info["expires_in"]
            )
            db.session.commit()
            print("Refreshed token")
        else:
            print("Access token not found in response")



def skip_logic():
    with app.app_context():
        for user in User.query.all():
            skip_logic_user(user)


def skip_logic_user(user):
    refresh_token(user)
    acquired = job_lock.acquire(blocking=False)
    if acquired:
        try:
            # Your skip_logic() implementation here
            print("Executing skip_logic()")
        finally:
            # Release the lock after the job finishes
            job_lock.release()
    access_token = user.oauth.access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    is_playing = update_currently_playing_playlist(user=user)
    if not is_playing:
        # print("Not currently playing")
        return

    current_queue_uris = get_current_queue_uris(user_id=user.id)
    if len(current_queue_uris) < 20:
        set_repeat(access_token=access_token, headers=headers)
        current_queue_with_repeat = get_current_queue_uris(user_id=user.id)
        if len(current_queue_with_repeat) < 20:
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

    played_tracks_60_uris = [
        track.track_id
        for track in prev_queue
        if track.track_id not in current_queue_uris
    ]

    user.total_played += len(played_tracks_60_uris)
    if (
        # code to see if skipped to previous
        current_queue_uris[19] == prev_queue[19 - len(played_tracks_60_uris)].track_id
        and
        len(played_tracks_60_uris) > 0
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

    recently_played_uris = [
        item["track"]["uri"] for item in recently_played_response["items"]
    ]

    skipped_tracks_60_uris = [
        track for track in played_tracks_60_uris if track not in recently_played_uris
    ]

    skipped_tracks_history = Skipped.query.filter_by(
        playlist_id=current_playlist.playlist_id, user_id=user.id
    ).all()
    for track in skipped_tracks_history:
        if track.track_id in recently_played_uris:
            db.session.delete(track)

    skipped_tracks_history_uris = [track.track_id for track in skipped_tracks_history]
    # print("Skipped: ", skipped_tracks_60_list)
    print(len(skipped_tracks_60_uris), " songs skipped")

    change_tracks = []
    for skipped_uri in skipped_tracks_60_uris:
        if skipped_uri not in skipped_tracks_history_uris:
            new_skipped = Skipped()
            new_skipped.playlist_id = current_playlist.playlist_id
            new_skipped.track_id = skipped_uri
            new_skipped.user_id = user.id
            new_skipped.skipped_count = 1
            db.session.add(new_skipped)
            continue

        skipped_track = Skipped.query.filter_by(track_id=skipped_uri).first()
        if skipped_track is None:
            raise Exception("Skipped track not found")

        skipped_track.skipped_count += 1
        if skipped_track.skipped_count != 2:
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
                access_token=access_token,
                playlist=current_playlist,
                t=skipped_track,
                user_id=user.user_id,
                headers=headers,
            )
        delete_tracks_from_playlist(
            playlist=current_playlist, change_tracks=change_tracks, headers=headers
        )
    set_prev_queue(user_id=user.id, current_queue_uris=current_queue_uris)
    db.session.commit()


def run():
    skip_logic()
    scheduler = BackgroundScheduler()
    # scheduler.add_job(func=skip_logic, args=(), trigger="interval", minutes=1)
    
    scheduler.add_job(func=skip_logic, args=(), trigger="interval", seconds=5)
    scheduler.start()
    # blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    # db.session.commit()
    # Shut down the scheduler when exiting the app

    atexit.register(lambda: scheduler.shutdown())
