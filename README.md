# Spotify Sifter
Spotify Sifter is a web application designed to help users filter through extensive playlists by removing songs that are often skipped. Users can select specific playlists for Spotify Sifter to monitor. Upon removal of a song, Spotify Sifter generates a new playlist titled “[Playlist Name]’s Sifted Songs.” While the default configuration removes a song after 2 consecutive skips, users have the flexibility to adjust this threshold to any number they prefer.

**Link to project:** https://spotifysifter.com/

## How It's Made:

**Tech used:** React, Flask, HTML, CSS, JavaScript, Python

The frontend is developed with React. The backend, built with Flask, resides on a subdomain of spotifysifter.com. It is divided into two segments: one manages user interactions on the website, while the other operates as a scheduled task, executing every 3 minutes.

## Skipped Songs Algorithm

Due to Spotify's Web API lacking a direct method for detecting skipped tracks, Spotify Sifter employs a proprietary algorithm to identify skipped songs. Every 3 minutes, a scheduled task (cron) refreshes our database with the user's latest queue of songs via the Spotify Web API. This API allows for tracking of recently played songs, but it only accounts for tracks played in their entirety. By comparing the updated queue with its previous version and integrating the list of recently played tracks, we can deduce which songs were skipped. Additionally, we meticulously account for edge cases, including when songs are added to the queue or when the playlist is shuffled.
