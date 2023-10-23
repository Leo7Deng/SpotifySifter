import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';

function PlaylistSelect() {
    const [searchParams] = useSearchParams();
    const playlists = searchParams.get("playlists");
    
    console.log(dict)
    return (
        <div>
            <h1>Spotify Sifter</h1>
            <h2>Select a playlist to sift through</h2>
            <p>{dict['name']}</p>
        </div>
    );
}

export default PlaylistSelect;
