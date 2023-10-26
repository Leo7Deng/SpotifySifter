import React, { useState, useEffect } from 'react';
import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';

function PlaylistSelect() {
    const [playlists, setPlaylists] = useState([]);
    const [clickedPlaylist, setClickedPlaylist] = useState(null);
    const [hoveredPlaylist, setHoveredPlaylist] = useState(null);
    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");

    useEffect(() => {
        const handleIframeClick = () => {
            console.log('Iframe clicked');
            const embeds = document.querySelectorAll('.embed');
            embeds.forEach(embed => embed.classList.remove('clicked'));
            const clickedEmbed = document.querySelector(`#embed-${clickedPlaylist}`);
            if (clickedEmbed) {
                clickedEmbed.classList.add('clicked');
            }
        }

        window.addEventListener("blur", () => {
            setTimeout(() => {
                if (document.activeElement.tagName === "IFRAME") {
                    handleIframeClick();
                }
            });
        }, { once: true });

        return () => {
            window.removeEventListener("blur", handleIframeClick);
        }
    }, [clickedPlaylist]);

    const handleCardClick = (playlistId) => {
        console.log('Clicked Playlist ID:', playlistId);
        setClickedPlaylist(prev => prev === playlistId ? null : playlistId);
    }

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
                    >
                        <div className="iframe-container" onClick={() => handleCardClick(playlist.id)}>
                            <iframe
                                id={`embed-${playlist.id}`} 
                                style={{ borderRadius: '12px' }}
                                src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                                width="100%"
                                height="352"
                                frameBorder="0"
                                allowFullScreen=""
                                className="playlist-iframe"
                            ></iframe>
                        </div>
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
                            id={`embed-${playlist.id}`} 
                            style={{ borderRadius: '12px' }}
                            src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                            width="100%"
                            height="352"
                            frameBorder="0"
                            allowFullScreen=""
                        ></iframe>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default PlaylistSelect;
