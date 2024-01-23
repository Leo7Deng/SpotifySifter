import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useState, useCallback } from "react";
import './PlaylistSelectCheck.css';
import { Link } from 'react-router-dom';
import { useMediaQuery } from 'react-responsive';

function PlaylistSelectCheck() {
    const isMobile = useMediaQuery({ maxWidth: 600 });
    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [selectedPlaylists, setSelectedPlaylists] = useState([]);
    const [unselectedPlaylists, setUnselectedPlaylists] = useState([]);
    const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
    const accessToken = searchParams.get("access_token");
    const currentlyPlayingUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/currently_playing` : `http://localhost:8889/currently_playing`;
    const getPlaylistsUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/get_playlists` : `http://localhost:8889/get_playlists`;
    const selectUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/select/` : `http://localhost:8889/select/`;
    const unselectUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/unselect/` : `http://localhost:8889/unselect/`;
    const [initialChecked, setInitialChecked] = useState({});

    useEffect(() => {
        const selectedCheckboxes = {};
        selectedPlaylists.forEach(playlist => {
            selectedCheckboxes[playlist.id] = true;
        });

        setInitialChecked(selectedCheckboxes);
    }, [selectedPlaylists]);

    const fetchCurrentlyPlaying = useCallback(() => {
        fetch(currentlyPlayingUrl, {
            credentials: 'include',
        })
            .then(response => response.json())
            .then(data => {
                setCurrentlyPlaying(data);
            })
            .catch(error => console.error('Error fetching currently playing track:', error));
    }, [currentlyPlayingUrl]);

    useEffect(() => {
        fetchCurrentlyPlaying();
        const interval = setInterval(fetchCurrentlyPlaying, 10000);

        return () => {
            clearInterval(interval);
        };
    }, [fetchCurrentlyPlaying]);

    useEffect(() => {
        fetch(getPlaylistsUrl, {
            credentials: 'include',
        })
            .then(response => response.json())
            .then(playlists => {
                const likedSongsPlaylist = playlists.find(playlist => playlist.name === "Liked Songs");

                if (likedSongsPlaylist && likedSongsPlaylist.selected) {
                    const selected = playlists.filter(playlist => playlist.selected && playlist.id !== likedSongsPlaylist.id);
                    setSelectedPlaylists([likedSongsPlaylist, ...selected]);
                    setUnselectedPlaylists(playlists.filter(playlist => !playlist.selected));
                } else {
                    const selected = playlists.filter(playlist => playlist.selected);
                    const unselected = playlists.filter(playlist => !playlist.selected && playlist.id !== likedSongsPlaylist.id);
                    setUnselectedPlaylists([likedSongsPlaylist, ...unselected]);
                    setSelectedPlaylists(selected);
                }
            })
            .catch(error => console.error('Error:', error));
    }, [getPlaylistsUrl]);


    function handleCheckboxChange(event, playlistId) {
        const isChecked = event.target.checked;

        setInitialChecked(prevState => ({
            ...prevState,
            [playlistId]: isChecked,
        }));

        if (isChecked) {
            console.log('Checked Playlist ID:', playlistId);
            fetch(selectUrl + current_user_id + '/' + playlistId, {
                credentials: 'include',
            })
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        } else {
            console.log('Unchecked Playlist ID:', playlistId);
            fetch(unselectUrl + current_user_id + '/' + playlistId, {
                credentials: 'include',
            })
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        }
    }


    return (
        <>
            <Link to={`/DeletedSongsPlaylists?current_user_id=${current_user_id}&access_token=${accessToken}`}>
                <div className={`right-arrow ${isMobile ? 'mobile-arrow' : ''}`}>
                    <img src={require('./images/rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🗑️</div>
                </div>
            </Link>
            <Link to={`/Leaderboard?current_user_id=${current_user_id}&access_token=${accessToken}`}>
                <div className={`left-arrow ${isMobile ? 'mobile-arrow' : ''}`}>
                    <img src={require('./images/rightarrow.png')} alt="Left Arrow" width="28" className="arrow-left" />
                    <div className="arrow-emoji-left">🏆</div>
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
                    <img src={require('./images/musicnote.gif')} alt="GIF" width="28" />
                </div>
            )}

            {(selectedPlaylists.length + unselectedPlaylists.length > 0) ? (
                <div className={`large-check-container ${selectedPlaylists.length + unselectedPlaylists.length > 12 && !isMobile ? 'large-playlist' : ''}`}>
                    <div className="playlist-check-container">
                        {selectedPlaylists.map((playlist) => (
                            <div key={playlist.id} className={`playlist-item ${isMobile ? 'mobile-playlist' : ''}`}>
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    checked={initialChecked[playlist.id]}
                                    onChange={(e) => {
                                        setInitialChecked(prevState => ({
                                            ...prevState,
                                            [playlist.id]: !prevState[playlist.id],
                                        }));
                                        handleCheckboxChange(e, playlist.id);
                                    }}
                                />
                                {playlist.name === "Liked Songs" ? (
                                    <div className="trim">
                                        <img
                                            src={require('./images/LikedSongs.png')}
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
                                        title={`Playlist ${playlist.id}`}
                                    ></iframe>
                                )}
                            </div>
                        ))}
                        {unselectedPlaylists.map((playlist) => (
                            <div key={playlist.id} className={`playlist-item ${isMobile ? 'mobile-playlist' : ''}`}>
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    onChange={(e) => handleCheckboxChange(e, playlist.id)}
                                />
                                {playlist.name === "Liked Songs" ? (
                                    <div className="trim">
                                        <img
                                            src={require('./images/LikedSongs.png')}
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
                                        title={`Playlist ${playlist.id}`}
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