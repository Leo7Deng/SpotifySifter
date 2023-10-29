import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useState } from "react";
import './DeletedSongsPlaylists.css';

function DeletedSongsPlaylists() {

    const [searchParams] = useSearchParams();
    const current_user_id = searchParams.get("current_user_id");
    const [playlists, setPlaylists] = useState([]);

    useEffect(() => {
        fetch(`http://localhost:8888/get_delete_playlists/${current_user_id}`)
            .then(response => response.json())
            .then(deleted_songs_playlists_uris => {
                const playlists = deleted_songs_playlists_uris;
                setPlaylists(playlists);
            })
            .catch(error => console.error('Error:', error));
    }, []);

    return (
        <>
            <h4>Browse the playlists your songs got sifted into!</h4>
            {playlists.length > 0 ? (
                playlists.map((playlist) => (
                    <div className="deleted-songs-playlists">
                        <iframe src={`https://open.spotify.com/embed/playlist/${playlist}`} width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
                    </div>
                ))
            ) : (
                <h4 className="no-songs">No songs have been sifted!</h4>
            )}
        </>
    )
}

export default DeletedSongsPlaylists;
