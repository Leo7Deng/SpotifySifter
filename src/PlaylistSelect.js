import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';
import React, { useState, useEffect } from 'react';

function PlaylistSelect() {
    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");

    const [playlists, setPlaylists] = useState({});

    useEffect(() => {
        fetch(`http://localhost:8888/get_playlists${current_user_id}`)
            .then(response => response.json())
            .then(playlists => setPlaylists(playlists))
            .catch(error => console.error('Error:', error));
    }, [current_user_id]);


    return (
        <div>
            <h1>Spotify Sifter</h1>
            <h2>Select a playlist to sift through</h2>
            <ul>
            {playlists.map((playlist, index) => (
                <li key={index}>{playlist.name}</li>
            ))}
        </ul>
        </div>
    );
}

export default PlaylistSelect;
