import { useEffect } from "react";
import { useState } from "react";
import { Link } from 'react-router-dom';
import './SiftedSongs.css';

function SiftedSongs() {
    const [playlists, setPlaylists] = useState([]);
    const getSiftedSongsUrl = process.env.NODE_ENV === 'production' ? 'https://playlistsifter.up.railway.app/get_delete_playlists' : 'http://localhost:8889/get_delete_playlists';

    useEffect(() => {
        fetch(getSiftedSongsUrl)
            .then(response => response.json())
            .then(deleted_songs_playlists_uris => {
                const playlists = deleted_songs_playlists_uris;
                setPlaylists(playlists);
            })
            .catch(error => console.error('Error:', error));
    }, [getSiftedSongsUrl]);

    return (
        <>
            <Link to={"/Leaderboard"}>
                <div className="right-arrow">
                    <img src={require('./images/rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🏆</div>
                </div>
            </Link>
            <Link to={"/PlaylistSelect"}>
                <div className="left-arrow">
                    <img src={require('./images/rightarrow.png')} alt="Left Arrow" width="28" className="arrow-left" />
                    <div className="arrow-emoji-left">🎵</div>
                </div>
            </Link>
            <div className="deleted-title">
                <h4>Browse the playlists your songs got sifted into!</h4>
            </div>
            {playlists.length > 0 ? (
                <div className="deleted-songs-playlists-container">
                    {playlists.map((playlist) => (
                        <iframe src={`https://open.spotify.com/embed/playlist/${playlist}`} width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media" className="deleted-songs-playlist-iframe" title={`Playlist ${playlist}`}></iframe>
                    ))}
                </div>
            ) : (
                <h4 className="no-songs">No songs have been sifted!</h4>
            )}
        </>
    )
}

export default SiftedSongs;
