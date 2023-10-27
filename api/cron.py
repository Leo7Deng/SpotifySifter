import atexit
import os
import requests
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app_init import db, app
from models import User, OAuth, Playlist, PrevQueue, Skipped, Track, Playlist

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
CURRENTLY_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REPEAT_URL = "https://api.spotify.com/v1/me/player/repeat"


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
    if response.status_code == 204:
        return None
    return response.json()


def get_currently_playing(user):
    oauth = OAuth.query.get(user.id)
    access_token = oauth.access_token
    response = get_response(
        access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT
    )
    return response


def update_currently_playing_playlist(user):
    response = get_currently_playing(user)
    if response is None:
        return False
    is_playing = False
    playlist_selected = False
    try:
        uri = response["context"]["uri"]
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
        playlists = Playlist.query.filter_by(user_id=user.id).all()
        for playlist in playlists:
            if playlist.selected == True:
                playlist_selected = True
                if playlist.currently_playing == False:
                    PrevQueue.query.filter_by(user_id=user.id).delete()
                playlist_id = uri.split(":")[-1]
                PLAYLIST_URL = (
                    f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                )
                playlist_data = get_response(
                    access_token=user.oauth.access_token, endpoint=PLAYLIST_URL
                )
                playlist_data = playlist_data["total"]
                if playlist_data < 20:
                    playlist.currently_playing = False
                    print("Playlist has less than 20 songs")
                else:
                    playlist.currently_playing = True
                    print(playlist.name + " is playing")
                    is_playing = True
            else:
                playlist.currently_playing = False
        if not playlist_selected:
            print("Playing in an unselected playlist")
    db.session.commit()
    return is_playing


def get_current_queue_uris(user_id):
    oauth = OAuth.query.get(user_id)
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
            prev_queue_item = PrevQueue(track_id=uri, queue_index=i, user_id=user_id)
            db.session.add(prev_queue_item)
    db.session.commit()


def delete_tracks_from_playlist(playlist, change_tracks, headers):
    playlist_uri = playlist.playlist_id
    tracks_data = json.dumps({"tracks": [{"uri": uri} for uri in change_tracks]})

    ADD_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
    response = requests.delete(
        ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data
    ).text


def refresh_token(user):
    if user.oauth.expires_at < datetime.now().timestamp():
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": user.oauth.refresh_token,
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET"),
        }
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        user.oauth.access_token = new_token_info["access_token"]
        user.oauth.expires_at = (
            datetime.now().timestamp() + new_token_info["expires_in"]
        )
        db.session.commit()
        print("Refreshed token")


def skip_logic():
    with app.app_context():
        for user in User.query.all():
            skip_logic_user(user)


def skip_logic_user(user):
    refresh_token(user)
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
            new_skipped = Skipped(
                playlist_id=current_playlist.playlist_id,
                track_id=skipped_uri,
                user_id=user.id,
                skipped_count=1,
            )
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
    scheduler.add_job(func=skip_logic, args=(), trigger="interval", seconds=5)
    # scheduler.add_job(func=skip_logic, args=(), trigger="interval", seconds=5)
    scheduler.start()
    # blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    # db.session.commit()
    # Shut down the scheduler when exiting the app

    atexit.register(lambda: scheduler.shutdown())
