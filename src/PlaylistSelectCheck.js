import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useState, useRef } from "react";
import './PlaylistSelectCheck.css';

function PlaylistSelectCheck() {

    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [selectedPlaylists, setSelectedPlaylists] = useState([]);
    const [unselectedPlaylists, setUnselectedPlaylists] = useState([]);
    const [initialChecked, setInitialChecked] = useState(true);
    const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
    const accessToken = searchParams.get("access_token");

    const fetchCurrentlyPlaying = () => {
        fetch(`http://localhost:8889/currently_playing/${accessToken}`)
            .then(response => response.json())
            .then(data => {
                // Set the currently playing track state
                setCurrentlyPlaying(data);
            })
            .catch(error => console.error('Error fetching currently playing track:', error));
    };

    useEffect(() => {
        // Fetch initially
        fetchCurrentlyPlaying();
        
        // Fetch every 10 seconds (for example)
        const interval = setInterval(fetchCurrentlyPlaying, 10000);

        return () => {
            // Clean up the interval on component unmount
            clearInterval(interval);
        };
    }, []);

    useEffect(() => {
        fetch(`http://localhost:8889/get_playlists/${current_user_id}`)
            .then(response => response.json())
            .then(playlists => {
                const unselected = playlists.filter(playlist => playlist.selected === false);
                const selected = playlists.filter(playlist => playlist.selected === true);
                setSelectedPlaylists(selected);
                setUnselectedPlaylists(unselected);
            })
            .catch(error => console.error('Error:', error));
    }, [current_user_id]);

    function handleCheckboxChange(event, playlistId) {
        const isChecked = event.target.checked;

        if (isChecked) {
            console.log('Checked Playlist ID:', playlistId);
            fetch(`http://localhost:8889/select/${current_user_id}/${playlistId}`)
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        } else {
            console.log('Unchecked Playlist ID:', playlistId);
            fetch(`http://localhost:8889/unselect/${current_user_id}/${playlistId}`)
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        }
    }

    

    return (
        <>
            <h4 className="check-title">Select Playlists you want sifted</h4>
            {currentlyPlaying && (<p>Track: {currentlyPlaying}</p>)}
            {(selectedPlaylists.length > 0 || unselectedPlaylists.length > 0) ? (
                <div className={`large-check-container ${selectedPlaylists.length + unselectedPlaylists.length > 12 ? 'large-playlist' : ''}`}style={{ paddingTop: '50px' }}>
                    <div className="playlist-check-container">
                        {selectedPlaylists.map((playlist) => (
                            <div key={playlist.id} className="playlist-item">
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    checked={initialChecked}
                                    onChange={(e) => {
                                        setInitialChecked(!initialChecked);
                                        handleCheckboxChange(e, playlist.id);
                                    }}

                                />
                                <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className="playlist-check-iframe"></iframe>
                            </div>
                        ))}
                        {unselectedPlaylists.map((playlist) => (
                            <div key={playlist.id} className="playlist-item">
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    onChange={(e) => handleCheckboxChange(e, playlist.id)}
                                />
                                <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className="playlist-check-iframe"></iframe>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <h4 className="no-songs">No playlists!</h4>
            )}
        </>
    )
}

export default PlaylistSelectCheck;
