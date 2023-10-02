import time
import atexit
import os
import data
import requests

from apscheduler.schedulers.background import BackgroundScheduler

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"

def change_current_queue(access_token):
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

    #recently_played is the recently played tracks that were not skipped
    data.data['recently_played'] = [track['name'] for track in recently_played_data['items']]

    #track_names are all the names in the queue data
    track_names = [track['name'] for track in queue_data['queue']]
    currently_playing = queue_data['currently_playing']['name']

    #add the currently playing track to track_names
    track_names.append(currently_playing)
    data.data['prev_queue'] = data.data['current_queue']
    data.data['current_queue'] = track_names

    #played_tracks_60 is the played tracks in the last 60 seconds
    data.data['played_tracks_60'] = [track for track in data.data['prev_queue'] if track not in data.data['current_queue']]
    print('update')

    #skipped_tracks_60 are the songs found in played_tracks_60 that are not found in recently_played
    data.data['skipped_tracks_60'] = [track for track in data.data['played_tracks_60'] if track not in data.data['recently_played']]

    #not_skipped_tracks_60 are the songs found in played_tracks_60 that are found in recently_played
    data.data['not_skipped_tracks_60'] = [track for track in data.data['played_tracks_60'] if track in data.data['recently_played']]

    # Assign missing_tracks to played_tracks_60
    return {'added': True}

def run(access_token):
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=change_current_queue, args=(access_token,), trigger="interval", seconds=5)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())