import atexit
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from app_init import db
from models import User, OAuth, Playlist, PrevQueue, Skipped, Track, Playlist

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
CURRENTLY_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"


def get_response(access_token, endpoint):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)

    if not response.ok:
        raise Exception(f"HTTP error! status: {response.status_code}")

    return response.json()


def set_currently_playing(user_id, playlist_uri):
    user = User.query.get(user_id)

    if user is None:
        return "User not found"

    playlists = Playlist.query.filter_by(user_id=user.id).all()

    for playlist in playlists:
        if playlist.playlist_id == playlist_uri:
            playlist.currently_playing = True
        else:
            playlist.currently_playing = False

    db.session.commit()
    return "Currently playing updated successfully"


def update_currently_playing_playlist():
    for user in User.query.all():
        oauth = OAuth.query.get(user.id)
        access_token = oauth.access_token # pyright: ignore[reportOptionalMemberAccess]
        print(f"User {user.email} has access token: {access_token}")
        response = get_response(
            access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT
        )
        uri = response["context"]["uri"]
        set_currently_playing(user_id=user.id, playlist_uri=uri)


def get_current_queue(user_id):
    oauth = OAuth.query.get(user_id)
    access_token = oauth.access_token # pyright: ignore[reportOptionalMemberAccess]
    response = get_response(access_token=access_token, endpoint=QUEUE_ENDPOINT)
    queue = [track["uri"] for track in response["queue"]]
    print(f"Queue: {queue}")
    return queue


def set_prev_queue(user_id, prev_queue):
    PrevQueue.query.filter_by(user_id=user_id).delete()
    for i, uri in enumerate(prev_queue, start=1):
        prev_queue_item = PrevQueue(track_id=uri, queue_index=i, user_id=user_id) # type: ignore
        db.session.add(prev_queue_item)

    db.session.commit()
    print("Prev queue updated successfully")


def skip_logic():
    for user in User.query.all():
        current_queue = get_current_queue(user_id=user.id)
        playlist = Playlist.query.filter_by(user_id=user.id, currently_playing=True).first()
        prev_queue = PrevQueue.query.filter_by(user_id=user.id).all()
        played_tracks_60 = [track for track in prev_queue if track not in current_queue]
        recently_played_data = get_response(
            access_token=user.oauth.access_token, endpoint=RECENTLY_PLAYED_ENDPOINT
        )
        recently_played = [item['track']['uri'] for item in recently_played_data['items']]
        skipped_tracks_60 = [track for track in played_tracks_60 if track not in recently_played]
        skipped_tracks_60_list = [track.track_id for track in skipped_tracks_60]
        skipped_tracks = Skipped.query.filter_by(playlist_id=playlist.playlist_id, user_id=user.id).all()
        skipped_tracks_list = [track.track_id for track in skipped_tracks]
        for prev_queue in skipped_tracks_60_list:
            breakpoint()
            if prev_queue in skipped_tracks_list:
                t = Skipped.query.filter_by(track_id=prev_queue).first()
                t.skipped_count += 1
            else:
                # breakpoint()
                new_skipped = Skipped(
                    playlist_id = playlist.playlist_id, 
                    track_id = prev_queue, 
                    user_id = user.id, 
                    skipped_count = 1)
                db.session.add(new_skipped
                )

        db.session.commit()
        set_prev_queue(user_id=user.id, prev_queue=current_queue)

        #     user.currently_listening = True
        # else:
        #     user.currently_listening = False
        # db.session.commit()


def run():
    update_currently_playing_playlist()
    skip_logic()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=update_currently_playing_playlist, args=(), trigger="interval", minutes=1
    )
    scheduler.add_job(func=skip_logic, args=(), trigger="interval", minutes=1)
    # scheduler.add_job(func=skip_logic, args=(), trigger="interval", seconds=5)
    scheduler.start()
    # blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    # db.session.commit()
    # Shut down the scheduler when exiting the app

    atexit.register(lambda: scheduler.shutdown())


# new_playlist = Playlist(
#     name="New",
#     playlist_id="spotify:playlist:0qjV67kI6SAZPqE3UscTY0",
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
