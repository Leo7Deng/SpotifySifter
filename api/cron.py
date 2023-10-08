import atexit
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"

def get_user_data(access_token, user_email):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    queue_response = requests.get(QUEUE_ENDPOINT, headers=headers)
    recently_played_response = requests.get(RECENTLY_PLAYED_ENDPOINT, headers=headers)

    if not queue_response.ok:
        raise Exception(f'HTTP error! status: {queue_response.status_code}')
    if not recently_played_response.ok:
        raise Exception(f'HTTP error! status: {recently_played_response.status_code}')
    
    queue_data = queue_response.json()
    recently_played_data = recently_played_response.json()

    change_current_queue(queue_data, recently_played_data, user_email)

def change_current_queue(queue_data, recently_played_data, user_email):
    user_data = UserData.query.filter_by(user_email=user_email).first()

    if not user_data:
  # Create if doesn't exist
        user_data = UserData(user_email=user_email)
        db.session.add(user_data)

    user_data.prev_queue = track_names
    user_data.skipped_once = list(set(skipped_tracks_60)) 
    user_data.skipped_twice = list(set([track for track in user_data.skipped_once if track in skipped_tracks_60]))
    
    #recently_played is the recently played tracks that were not skipped
    recently_played = [item['track']['name'] for item in recently_played_data['items']]

    #track_names are all the names in the queue data
    track_names = [track['name'] for track in queue_data['queue']]
    currently_playing = queue_data['currently_playing']['name']

    #add the currently playing track to track_names
    track_names.append(currently_playing)

    #played_tracks_60 is the played tracks in the last 60 seconds
    played_tracks_60 = [track for track in user_data.prev_queue if track not in track_names]

    #skipped_tracks_60 are the songs found in played_tracks_60 that are not found in recently_played
    skipped_tracks_60 = [track for track in played_tracks_60 if track not in recently_played]

    #append songs to skipped_twice if they are found in both skipped_once and skipped_tracks_60
    user_data.skipped_twice.extend([track for track in user_data.skipped_once if track in skipped_tracks_60])

    #after skipped_twice is checked, then skipped_once is updated
    user_data.skipped_once.extend(skipped_tracks_60)
    
    #remove duplicates from skipped_once
    skipped_once = user_data.skipped_once
    user_data.skipped_once = list(set(skipped_once))

    #not_skipped_tracks_60 are the songs found in played_tracks_60 that are found in recently_played
    not_skipped_tracks_60 = [track for track in played_tracks_60 if track in recently_played]
    
    #remove songs from skipped_once if they are found in not_skipped_tracks_60
    user_data.skipped_once = [track for track in user_data.skipped_once if track not in not_skipped_tracks_60]

    #remove duplicates from skipped_twice
    skipped_twice = user_data.skipped_twice
    user_data.skipped_twice = list(set(skipped_twice))
    
    print("Currently playing: " + str(currently_playing))
    # print("Played tracks 60: " + str(played_tracks_60))
    print("Skipped tracks 60: " + str(skipped_tracks_60))
    print("Skipped once: " + str(user_data.skipped_once))
    print("Skipped twice: " + str(user_data.skipped_twice))
    user_data.prev_queue = track_names

    # Assign missing_tracks to played_tracks_60
    return {'added': True}

def run(access_token):
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_info = requests.get(EMAIL_ENDPOINT, headers=headers)
    user_email = user_info.json()['email']
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=get_user_data, args=(access_token, user_email), trigger="interval", seconds=5)
    scheduler.start()
    db.session.commit()
    # Shut down the scheduler when exiting the app
    
    atexit.register(lambda: scheduler.shutdown())

from app import db, UserData, app