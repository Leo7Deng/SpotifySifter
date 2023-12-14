import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useState, useRef } from "react";
import './PlaylistSelectCheck.css';
import { Link } from 'react-router-dom';

function PlaylistSelectCheck() {

    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [selectedPlaylists, setSelectedPlaylists] = useState([]);
    const [unselectedPlaylists, setUnselectedPlaylists] = useState([]);
    const [likedSongs, setLikedSongs] = useState([]);
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
                const likedSongsPlaylist = playlists.find(playlist => playlist.name === "Liked Songs");

                if (likedSongsPlaylist && likedSongsPlaylist.selected) {
                    const selected = playlists.filter(playlist => playlist.selected && playlist.name !== "Liked Songs");
                    setSelectedPlaylists([likedSongsPlaylist, ...selected]);
                } else {
                    const selected = playlists.filter(playlist => playlist.selected && playlist.name !== "Liked Songs");
                    const unselected = playlists.filter(playlist => !playlist.selected && playlist.name !== "Liked Songs");
                    setUnselectedPlaylists([likedSongsPlaylist, ...unselected]);
                    setSelectedPlaylists(selected);
                }
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
            <Link to={`/DeletedSongsPlaylists?current_user_id=${current_user_id}&access_token=${accessToken}`}>
                <div className="right-arrow">
                    <img src={require('./rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🗑️</div>
                </div>
            </Link>
            <Link to={`/Leaderboard?current_user_id=${current_user_id}&access_token=${accessToken}`}>
                <div class="left-arrow">
                    <img src={require('./rightarrow.png')} alt="Left Arrow" width="28" class="arrow-left" />
                    <div class="arrow-emoji-left">🏆</div>
                </div>
            </Link>
            <h4 className="check-title">Select playlists you want sifted</h4>
            {currentlyPlaying !== null && typeof currentlyPlaying === 'object' ? (
                <div className="currently-playing">
                    <h5>Spotify is not currently playing</h5>
                </div>
            ) : (
                <div className="currently-playing">
                    <h5>Currently Playing: {currentlyPlaying}</h5>
                    <img src={require('./musicnote.gif')} alt="GIF" width="28" />
                </div>
            )}

{(selectedPlaylists.length + unselectedPlaylists.length > 0) ? (
            <div className={`large-check-container ${selectedPlaylists.length + unselectedPlaylists.length > 12 ? 'large-playlist' : ''}`}>
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
                            {playlist.name === "Liked Songs" ? (
                                <div className="trim">
                                    <img
                                        src={require('./LikedSongs.png')}
                                        alt="Liked Songs"
                                        className="playlist-check-iframe liked-songs"
                                    />
                                </div>
                            ) : (
                                <iframe
                                    frameBorder="0"
                                    src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                                    loading="lazy"
                                    className="playlist-check-iframe"
                                ></iframe>
                            )}
                        </div>
                    ))}
                    {unselectedPlaylists.map((playlist) => (
                        <div key={playlist.id} className="playlist-item">
                            <input
                                className="playlist-checkbox"
                                type="checkbox"
                                onChange={(e) => handleCheckboxChange(e, playlist.id)}
                            />
                            {playlist.name === "Liked Songs" ? (
                                <div className="trim">
                                    <img
                                        src={require('./LikedSongs.png')}
                                        alt="Liked Songs"
                                        className="playlist-check-iframe liked-songs"
                                    />
                                </div>
                            ) : (
                                <iframe
                                    frameBorder="0"
                                    src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`}
                                    loading="lazy"
                                    className="playlist-check-iframe"
                                ></iframe>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        ) : (
            <h4 className="currently-playing">No playlists!</h4>
        )}
    </>
    )
}

export default PlaylistSelectCheck;
