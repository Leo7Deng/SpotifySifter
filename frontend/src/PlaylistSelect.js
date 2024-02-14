import React, { useState, useEffect } from 'react';
import PlaylistDisplay from './PlaylistDisplay';
import './PlaylistSelect.css';

function PlaylistSelect() {
    const [playlists, setPlaylists] = useState([]);
    // const getPlaylistsUrl = process.env.NODE_ENV === 'production' ? `https://api.spotifysifter.com/get_playlists` : 'http://localhost:8889/get_playlists';
    const getPlaylistsUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/get_playlists` : 'http://localhost:8889/get_playlists';
    useEffect(() => {
        fetch(getPlaylistsUrl, {
            // credentials: 'include',
        })
            .then(response => response.json())
            .then(data => {
                console.log('Playlists:', data);
                if (data.error && data.error === "Unauthorized access") {
                    // window.location.href = '/';
                } else {
                    setPlaylists(data);
                }
            })
            .catch(error => {
                console.error('Error fetching playlists:', error);
            });
    }, [getPlaylistsUrl]);

    return (
        <>
            <div className="playlist-container">
                {playlists.map(playlist => (
                    <PlaylistDisplay
                        key={playlist.id}
                        playlist={playlist}
                        isChecked={playlist.selected}
                        playlistSkipCount={playlist.skip_count}
                        siftedPlaylist={playlist.sifted_playlist}
                    />
                ))}
            </div>
        </>
    );
}

export default PlaylistSelect;
