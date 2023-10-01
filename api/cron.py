import time
import atexit
import os
import data
import requests

from apscheduler.schedulers.background import BackgroundScheduler

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"

def change_current_queue(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(QUEUE_ENDPOINT, headers=headers)

    if not response.ok:
        raise Exception(f'HTTP error! status: {response.status_code}')

    queue_data = response.json()
    # print(queue_data)
    track_names = [track['name'] for track in queue_data['queue']]
    
    data.data['current_queue'] = track_names
    return {'added': True}

def run(access_token):
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=change_current_queue, args=(access_token,), trigger="interval", seconds=5)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())