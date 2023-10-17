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



def setRepeat(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    repeat_data = {
        "state": "context"
    }
    response = requests.put(REPEAT_URL, headers=headers, params=repeat_data)

def create_playlist(access_token, playlist, t, user_id):
    CREATE_PLAYLIST_ENDPOINT = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {access_token}"}
    playlist_data = json.dumps({
        "name": f"{playlist.name} - Deleted Songs",
        "description": f"Deleted songs from {playlist.name}",
        "public": False
    })
    response = requests.post(CREATE_PLAYLIST_ENDPOINT,
                             headers=headers,
                             data=playlist_data).text
    playlist_uri = json.loads(response)['id']
    tracks_data = json.dumps({
        "uris": [t.track_id],
    })
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


def set_currently_playing(user_id, playlist_uri):
    user = User.query.get(user_id)

    if user is None:
        return "User not found"

    playlists = Playlist.query.filter_by(user_id=user.id).all()

    for playlist in playlists:
        if playlist.playlist_id == playlist_uri:
            if playlist.currently_playing == False:
                PrevQueue.query.filter_by(user_id=user_id).delete()
            playlist_id = playlist_uri.split(':')[-1]
            PLAYLIST_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            playlist_data = get_response(access_token=user.oauth.access_token, endpoint=PLAYLIST_URL)
            playlist_data = playlist_data['total']
            if playlist_data < 20:
                playlist.currently_playing = False
                print("Not enough songs in playlist")
                continue
            playlist.currently_playing = True
        else:
            playlist.currently_playing = False

    db.session.commit()
    return "Currently playing updated successfully"

def get_currently_playing(user):
    oauth = OAuth.query.get(user.id)
    access_token = oauth.access_token # pyright: ignore[reportOptionalMemberAccess]
    response = get_response(
        access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT
    )
    return response

def update_currently_playing_playlist(user):
    response = get_currently_playing(user)
    is_playing = False
    playlist_exists = False
    if response:
        uri = response["context"]["uri"]
        playlists = Playlist.query.filter_by(user_id=user.id).all()
        for playlist in playlists:
            if playlist.playlist_id == uri:
                playlist_exists = True
                if playlist.currently_playing == False:
                    PrevQueue.query.filter_by(user_id=user.id).delete()
                playlist_id = uri.split(':')[-1]
                PLAYLIST_URL = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                playlist_data = get_response(access_token=user.oauth.access_token, endpoint=PLAYLIST_URL)
                playlist_data = playlist_data['total']
                if playlist_data < 20:
                    playlist.currently_playing = False
                    print("Not enough songs in playlist")
                else: 
                    playlist.currently_playing = True
                    print("Playing in playlist " + playlist.name)
                    is_playing = True
            else:
                playlist.currently_playing = False
        if not playlist_exists:
            print("Not playing in a registered playlist")
        db.session.commit()
        return is_playing
        
    else:
        if user is None:
            return "User not found"
        playlists = Playlist.query.filter_by(user_id=user.id).all()
        for playlist in playlists:
            playlist.currently_playing = False
        print ("Not currently playing")
    db.session.commit()
    return is_playing



def get_current_queue(user_id):
    oauth = OAuth.query.get(user_id)
    access_token = oauth.access_token # pyright: ignore[reportOptionalMemberAccess]
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


def set_prev_queue(user_id, current_queue):
    prev_queue = PrevQueue.query.filter_by(user_id=user_id).all()
    if prev_queue:
        for i, uri in enumerate(current_queue):
            prev_queue[i].track_id = uri
    else:
        for i, uri in enumerate(current_queue, start=1):
            prev_queue_item = PrevQueue(track_id=uri, queue_index=i, user_id=user_id) # type: ignore
            db.session.add(prev_queue_item)
    db.session.commit()
    print("Prev queue updated successfully")

def delete_tracks_from_playlist(access_token, playlist, change_tracks, user_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    playlist_uri = playlist.playlist_id
    playlist_uri = playlist_uri.split(':')[-1]
    tracks_data = json.dumps({
    "tracks": [{"uri": uri} for uri in change_tracks]
    })
    
    ADD_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
    response = requests.delete(ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data).text

def updateRefreshToken(user):
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
        user.oauth.expires_at = datetime.now().timestamp() + new_token_info["expires_in"]
        db.session.commit()
        print("Refreshed token")

def skip_logic():
    with app.app_context():
        for user in User.query.all():
            updateRefreshToken(user)
            is_playing = update_currently_playing_playlist(user)
            if is_playing:
                access_token=user.oauth.access_token
                current_queue = get_current_queue(user_id=user.id)
                if len(current_queue) < 20:
                    setRepeat(access_token=access_token)
                    current_queue = get_current_queue(user_id=user.id)
                    if len(current_queue) < 20:
                        print("Not enough songs in queue")
                        continue
                playlist = Playlist.query.filter_by(user_id=user.id, currently_playing=True).first()
                prev_queue = PrevQueue.query.filter_by(user_id=user.id).all()
                if prev_queue:
                    played_tracks_60 = [track.track_id for track in prev_queue if track.track_id not in current_queue]
                    played_tracks_60_list = [track for track in played_tracks_60]
                    if current_queue[19] == prev_queue[19-len(played_tracks_60)].track_id and len(played_tracks_60) > 0:
                        print("Skipped to previous")
                        set_prev_queue(user_id=user.id, current_queue=current_queue)
                        continue
                    #code to see if queue shuffled
                    elif current_queue[19-len(played_tracks_60)] != prev_queue[19].track_id and current_queue[18-len(played_tracks_60)] != prev_queue[18].track_id and len(played_tracks_60) > 0:
                        print("Shuffled playlist")
                        set_prev_queue(user_id=user.id, current_queue=current_queue)
                        continue
                    recently_played_data = get_response(
                        access_token=access_token, endpoint=RECENTLY_PLAYED_ENDPOINT
                    )
                    recently_played = [item['track']['uri'] for item in recently_played_data['items']]
                    skipped_tracks_60_list = [track for track in played_tracks_60_list if track not in recently_played]
                    # skipped_tracks_60_list = [track.track_id for track in skipped_tracks_60]
                    skipped_tracks = Skipped.query.filter_by(playlist_id=playlist.playlist_id, user_id=user.id).all()
                    skipped_tracks_now_played = [track.track_id for track in skipped_tracks if track.track_id in recently_played]
                    for track in skipped_tracks_now_played:
                        t = Skipped.query.filter_by(track_id=track).first()
                        if t.skipped_count < 2:
                            db.session.delete(t)
                    skipped_tracks_list = [track.track_id for track in skipped_tracks]
                    print("Skipped: ", skipped_tracks_60_list)

                    change_tracks = []
                    change = False
                    for prev_queue in skipped_tracks_60_list:
                        
                        if prev_queue in skipped_tracks_list:
                            t = Skipped.query.filter_by(track_id=prev_queue).first()
                            t.skipped_count += 1
                            if t.skipped_count == 2:
                                change_tracks.append(t.track_id)
                                change = True
                                if playlist.delete_playlist:
                                    playlist_uri = playlist.delete_playlist
                                    ADD_ITEMS_ENDPOINT = f"https://api.spotify.com/v1/playlists/{playlist_uri}/tracks"
                                    tracks_data = json.dumps({
                                        "uris": [t.track_id],
                                    })
                                    headers = {"Authorization": f"Bearer {access_token}"}
                                    response = requests.post(ADD_ITEMS_ENDPOINT, headers=headers, data=tracks_data).text
                                else:
                                    create_playlist(access_token=access_token, playlist=playlist, t=t, user_id=user.user_id)
                                
                        else:
                            new_skipped = Skipped(
                                playlist_id = playlist.playlist_id, 
                                track_id = prev_queue, 
                                user_id = user.id, 
                                skipped_count = 1)
                            db.session.add(new_skipped
                            )
                        if change:
                            delete_tracks_from_playlist(access_token=access_token, playlist=playlist, change_tracks=change_tracks, user_id=user.user_id)
                    db.session.commit()
                    set_prev_queue(user_id=user.id, current_queue=current_queue)
                else:
                    set_prev_queue(user_id=user.id, current_queue=current_queue)
                #     user.currently_listening = True
                # else:
                #     user.currently_listening = False
                # db.session.commit()


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


# new_playlist = Playlist(
#     name="Test",
#     playlist_id="spotify:playlist:7fip5CI3k2LGT5FAnRy52f",
#     user_id=1,
#     currently_playing=False
# )
#     db.session.add(new_playlist)
#     db.session.commit()


# def header(endpoint):
#     headers = {
#         'Authorization': f'Bearer {access_token}'
#     }
#     queue_response = requests.get(endpoint, headers=headers)

# def skip_logic(queue_data, recently_played_data, user_email):
#     for user in User.query.all():


#     user_data = User.query.filter_by(user_email=user_email).first()


#     queue_data = header(access_token, QUEUE_ENDPOINT)

#     if not user_data:
#   # Create if doesn't exist
#         user_data = User(user_email=user_email)
#         db.session.add(user_data)

#     user_data.prev_queue = track_names
#     user_data.skipped_once = list(set(skipped_tracks_60))
#     user_data.skipped_twice = list(set([track for track in user_data.skipped_once if track in skipped_tracks_60]))

#     #recently_played is the recently played tracks that were not skipped
#     recently_played = [item['track']['name'] for item in recently_played_data['items']]

#     #track_names are all the names in the queue data
#     track_names = [track['name'] for track in queue_data['queue']]
#     currently_playing = queue_data['currently_playing']['name']

#     #add the currently playing track to track_names
#     track_names.append(currently_playing)

#     #played_tracks_60 is the played tracks in the last 60 seconds
#     played_tracks_60 = [track for track in user_data.prev_queue if track not in track_names]

#     #skipped_tracks_60 are the songs found in played_tracks_60 that are not found in recently_played
#     skipped_tracks_60 = [track for track in played_tracks_60 if track not in recently_played]

#     #append songs to skipped_twice if they are found in both skipped_once and skipped_tracks_60
#     user_data.skipped_twice.extend([track for track in user_data.skipped_once if track in skipped_tracks_60])

#     #after skipped_twice is checked, then skipped_once is updated
#     user_data.skipped_once.extend(skipped_tracks_60)

#     #remove duplicates from skipped_once
#     skipped_once = user_data.skipped_once
#     user_data.skipped_once = list(set(skipped_once))

#     #not_skipped_tracks_60 are the songs found in played_tracks_60 that are found in recently_played
#     not_skipped_tracks_60 = [track for track in played_tracks_60 if track in recently_played]

#     #remove songs from skipped_once if they are found in not_skipped_tracks_60
#     user_data.skipped_once = [track for track in user_data.skipped_once if track not in not_skipped_tracks_60]

#     #remove duplicates from skipped_twice
#     skipped_twice = user_data.skipped_twice
#     user_data.skipped_twice = list(set(skipped_twice))

#     print("Currently playing: " + str(currently_playing))
#     # print("Played tracks 60: " + str(played_tracks_60))
#     print("Skipped tracks 60: " + str(skipped_tracks_60))
#     print("Skipped once: " + str(user_data.skipped_once))
#     print("Skipped twice: " + str(user_data.skipped_twice))
#     user_data.prev_queue = track_names

#     # Assign missing_tracks to played_tracks_60
#     return {'added': True}
