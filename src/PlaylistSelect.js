import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';
import React, { useState, useEffect } from 'react';

function PlaylistSelect() {
    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [playlists, setPlaylists] = useState([]);
    const [hoveredPlaylist, setHoveredPlaylist] = useState(null);

    // Preload iframe contents
    useEffect(() => {
        if (Array.isArray(playlists)) {
            playlists.forEach(playlist => {
                const iframe = document.createElement('iframe');
                iframe.src = `https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`;
                iframe.style.display = 'none';

                iframe.onload = () => {
                    document.body.removeChild(iframe);
                };

                document.body.appendChild(iframe);
            });
        }
    }, [playlists]);

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
                        className="embed"
                        onMouseEnter={() => setHoveredPlaylist(playlist.id)}
                        onMouseLeave={() => setHoveredPlaylist(null)}
                    >
                        <iframe
                            style={{ borderRadius: '12px' }}
                            src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                            width="100%"
                            height="352"
                            frameBorder="0"
                            allowFullScreen=""
                            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                            loading="lazy"
                        ></iframe>
                    </div>
                ))}
            </div>
            {hoveredPlaylist !== null && (
                <div className="large-card">
                    <iframe
                        style={{ borderRadius: '12px' }}
                        src={`https://open.spotify.com/embed/playlist/${hoveredPlaylist}?utm_source=generator`}
                        width="100%"
                        height="352"
                        frameBorder="0"
                        allowFullScreen=""
                        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        loading="lazy"
                    ></iframe>
                </div>
            )}
        </div>
    );
}

export default PlaylistSelect;
