import React, { useState, useEffect } from 'react';
import './PlaylistDisplay.css';

function PlaylistDisplay({ playlist, isChecked }) {
    const [checked, setChecked] = useState(isChecked);
    const selectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/select' : 'http://localhost:8889/select';
    const unselectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/unselect' : 'http://localhost:8889/unselect';

    useEffect(() => {
        setChecked(isChecked);
    }, [isChecked]);

    const handleCheckboxChange = (event) => {
        const isNowChecked = event.target.checked;
        setChecked(isNowChecked);

        const url = isNowChecked ? selectUrl : unselectUrl;
        fetch(`${url}/${playlist.id}`, {
            credentials: 'include',
            method: 'POST' 
        })
        .then(response => response.json())
        .then(data => console.log('Response:', data))
        .catch(error => console.error('Error:', error));
    };

    return (
        <div className="playlist-item">
            <div className="info-wrapper">
                <img 
                    className="playlist-image" 
                    src={playlist.image ? playlist.image : require('./images/LikedSongs.png')} 
                    alt="playlist"
                />
                <p className="playlist-name">{playlist.name}</p>
            </div>
            <div className="checkbox-wrapper-4">
                <input 
                    className="inp-cbx" 
                    id={`checkbox-${playlist.id}`} 
                    type="checkbox" 
                    checked={checked} 
                    onChange={handleCheckboxChange} 
                />
                <label className="cbx" htmlFor={`checkbox-${playlist.id}`}>
                    <span>
                        <svg width="12px" height="10px">
                            <use xlinkHref="#check-4"></use>
                        </svg>
                    </span>
                </label>
                <svg className="inline-svg">
                    <symbol id="check-4" viewBox="0 0 12 10">
                        <polyline points="1.5 6 4.5 9 10.5 1"></polyline>
                    </symbol>
                </svg>
            </div>
        </div>
    );
}

export default PlaylistDisplay;
