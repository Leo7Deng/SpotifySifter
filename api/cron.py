import atexit
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, User, OAuth, Playlist

QUEUE_ENDPOINT = "https://api.spotify.com/v1/me/player/queue"
RECENTLY_PLAYED_ENDPOINT = "https://api.spotify.com/v1/me/player/recently-played"
CURRENTLY_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
EMAIL_ENDPOINT = "https://api.spotify.com/v1/me"

def get_response(access_token, endpoint):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(endpoint, headers=headers)

    if not response.ok:
        raise Exception(f'HTTP error! status: {response.status_code}')
    
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

def get_currently_playing_playlist():
    for user in User.query.all():
        user_id = OAuth.query.filter_by(user_id=user.id).first()
        if user_id:
            access_token = user_id.access_token
            print(f"User {user.email} has access token: {access_token}")
        else:
            print(f"No OAuth record found for user {user.email}")
        
        response = get_response(access_token=access_token, endpoint=CURRENTLY_PLAYING_ENDPOINT)
        uri = response["context"]["uri"]
        set_currently_playing(user_id=user.id, playlist_uri=uri)
        


        
        #     user.currently_listening = True
        # else:
        #     user.currently_listening = False
        # db.session.commit()

def run():
    new_playlist = Playlist(
    name="New", 
    playlist_id="spotify:playlist:0S5MFXu9cG5TKLnLuECDBH",  
    user_id=1,  
    currently_playing=False  
)
    db.session.add(new_playlist)
    db.session.commit()

    
    get_currently_playing_playlist()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=get_currently_playing_playlist, args=(), trigger="interval", minutes=5)
    # scheduler.add_job(func=skip_logic, args=(), trigger="interval", seconds=5)
    scheduler.start()
    # blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    # db.session.commit()
    # Shut down the scheduler when exiting the app
    
    atexit.register(lambda: scheduler.shutdown())




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