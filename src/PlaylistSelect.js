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

    // const handleCheckboxChange = (playlistId) => {
    //     // Toggle the selected status of the playlist
    //     setSelectedPlaylists(prevState => {
    //         if (prevState.includes(playlistId)) {
    //             return prevState.filter(id => id !== playlistId);
    //         } else {
    //             return [...prevState, playlistId];
    //         }
    //     });
    // };

    // const handleSave = () => {
    //     // Send a request to your backend to update the database
    //     fetch('http://localhost:8888/update_database', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //         body: JSON.stringify({ selectedPlaylists })
    //     })
    //     .then(response => {
    //         if (response.ok) {
    //             console.log('Data updated successfully');
    //         } else {
    //             console.error('Error updating data:', response.statusText);
    //         }
    //     })
    //     .catch(error => console.error('Error:', error));
    // };

    return (
        <div>
            <h1>Spotify Sifter</h1>
            <h2>Select a playlist to sift through</h2>
            {Array.isArray(playlists) && playlists.map(playlist => (
                <div key={playlist.id}>
                    <label>
                        <input
                            type="checkbox"
                            // checked={selectedPlaylists.includes(playlist.id)}
                            // onChange={() => handleCheckboxChange(playlist.id)}
                        />
                        <p>{playlist.name}</p>
                    </label>
                </div>
            ))}
        </div>
    );
}

export default PlaylistSelect;
