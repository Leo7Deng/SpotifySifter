import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useState } from "react";
import './PlaylistSelectCheck.css';

function DeletedSongsCheck() {

    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [selectedPlaylists, setSelectedPlaylists] = useState([]);
    const [unselectedPlaylists, setUnselectedPlaylists] = useState([]);

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
    }, []);

    return (
        <>
            <h4>Select Playlists you want sifted</h4>
            {(selectedPlaylists.length > 0 && unselectedPlaylists.length > 0) ? (
                <div className="playlist-check-container">
                    {selectedPlaylists.map((playlist) => (
                         <>
                            <input 
                                class="playlist-checkbox"
                                type="checkbox"
                                key={playlist.id}></input>
                            <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className = "playlist-check-iframe"></iframe>
                        </>
                    ))}
                    {unselectedPlaylists.map((playlist) => (
                         <>
                            <input 
                                class="playlist-checkbox"
                                type="checkbox"
                                key={playlist.id}></input>
                            <iframe frameBorder="0" src={`https://open.spotify.com/embed/playlist/${playlist.id}?utm_source=generator`} loading="lazy" className = "playlist-check-iframe"></iframe>
                        </>
                    ))}
                </div>
            ) : (
                <h4 className="no-songs">No songs have been sifted!</h4>
            )}
        </>
    )
}

export default DeletedSongsCheck;