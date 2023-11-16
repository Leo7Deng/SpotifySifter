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


    useEffect(() => {
        fetch(`http://localhost:8888/get_playlists/${current_user_id}`)
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
            fetch(`http://localhost:8888/select/${current_user_id}/${playlistId}`)
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        } else {
            console.log('Unchecked Playlist ID:', playlistId);
            fetch(`http://localhost:8888/unselect/${current_user_id}/${playlistId}`)
                .then(response => response.json())
                .then(data => console.log('Manage Playlists Response:', data))
                .catch(error => console.error('Error:', error));
        }
    }



    return (
        <>
            <h4>Select Playlists you want sifted</h4>
            {(selectedPlaylists.length > 0 || unselectedPlaylists.length > 0) ? (
                <div className={`large-check-container ${selectedPlaylists.length + unselectedPlaylists.length > 12 ? 'large-playlist' : ''}`}>
                    <div className="playlist-check-container">
                        {selectedPlaylists.map((playlist) => (
                            <>
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    key={playlist.id}
                                    checked={initialChecked}
                                    onChange={(e) => {
                                        setInitialChecked(!initialChecked);
                                        handleCheckboxChange(e, playlist.id);
                                    }}

                                />
                                <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className="playlist-check-iframe"></iframe>
                            </>
                        ))}
                        {unselectedPlaylists.map((playlist) => (
                            <>
                                <input
                                    className="playlist-checkbox"
                                    type="checkbox"
                                    key={playlist.id}
                                    onChange={(e) => handleCheckboxChange(e, playlist.id)}
                                />
                                <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className="playlist-check-iframe"></iframe>
                            </>
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
