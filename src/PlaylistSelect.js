import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';
import React, { useState, useEffect } from 'react';

function PlaylistSelect() {
    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [playlists, setPlaylists] = useState([]);
    const [hoveredPlaylist, setHoveredPlaylist] = useState(null);
    const [clickedPlaylist, setClickedPlaylist] = useState(null);

    const handleCardClick = (playlistId) => {
        setClickedPlaylist(clickedPlaylist === playlistId ? null : playlistId);
    }

    // Preload iframe contents
    

    useEffect(() => {
        fetch(`http://localhost:8888/get_playlists${current_user_id}`)
            .then(response => response.json())
            .then(playlists => setPlaylists(playlists))
            .catch(error => console.error('Error:', error));
    }, [current_user_id]);

    return (
        <div>
            <div className="playlist-container">
                {Array.isArray(playlists) && playlists.map((playlist) => (
                    <div
                        key={playlist.id}
                        className={`embed ${clickedPlaylist === playlist.id ? 'clicked' : ''}`}
                        onMouseEnter={() => setHoveredPlaylist(playlist.id)}
                        onMouseLeave={() => setHoveredPlaylist(null)}
                        onClick={() => handleCardClick(playlist.id)}
                    >
                        <iframe
                            style={{ borderRadius: '12px' }}
                            src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                            width="100%"
                            height="352"
                            frameBorder="0"
                            allowFullScreen=""
                            // allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
                            className="playlist-iframe"
                        ></iframe>
                    </div>
                ))}
            </div>
            <div className="large-card-background"></div>
            <div className="large-card">
                {Array.isArray(playlists) && playlists.map((playlist) => (
                    <div
                        key={playlist.id}
                        className="large-card-embed"
                        style={{ display: hoveredPlaylist === playlist.id ? 'block' : 'none' }}
                    >
                        <div className="overlay" style={{ display: hoveredPlaylist === playlist.id ? 'none' : 'block' }}></div>
                        <iframe
                            style={{ borderRadius: '12px' }}
                            src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                            width="100%"
                            height="352"
                            frameBorder="0"
                            allowFullScreen=""
                            // allow="autoplay; clipboard-write; fullscreen; picture-in-picture"
                        ></iframe>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default PlaylistSelect;
