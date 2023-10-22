import { useSearchParams } from "react-router-dom";
import './PlaylistSelect.css';

function PlaylistSelect() {
    const [searchParams] = useSearchParams();
    const playlists = searchParams.get("playlists");

    return (
        <div>
            <h1>Spotify Sifter</h1>
            <h2>Select a playlist to sift through</h2>
            <p>{playlists}</p>
        </div>
    );
}

export default PlaylistSelect;
