import React, { useState } from 'react';
import './PlaylistDisplay.css';
import gearIcon from './images/gear.svg';

function PlaylistDisplay({ playlist, isChecked, playlistSkipCount, siftedPlaylist }) {
    const [checked, setChecked] = useState(isChecked);
    const inputId = `switch-${playlist.id}`;
    const selectUrl = process.env.NODE_ENV === 'production' ? `${process.env.BACKEND_URL}/select` : 'http://localhost:8889/select';
    const unselectUrl = process.env.NODE_ENV === 'production' ? `${process.env.BACKEND_URL}/unselect` : 'http://localhost:8889/unselect';
    const [isExpanded, setIsExpanded] = useState(false);
    const [skipCount, setSkipCount] = useState(playlistSkipCount);

    const handleChange = (event) => {
        const { value } = event.target;
        if (value === '' || (value.length === 1 && /^[1-9]$/.test(value))) {
            if (value === '') {
                setSkipCount('');
                return;
            }
            const intValue = parseInt(value);
            setSkipCount(intValue);
            if (intValue > 0 && intValue < 10) {
                fetch(`${process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app' : 'http://localhost:8889'}/update_playlist_skip_count/${playlist.id}/${intValue}`, {
                    credentials: 'include',
                })
                    .then(response => response.json())
                    .then(data => console.log('Skip count updated:', data))
                    .catch(error => console.error('Error:', error));
            }
        };
    };

    const handleGearClick = () => {
        setIsExpanded(!isExpanded);
    };


    const handleCheckboxChange = () => {
        const isNowChecked = !checked;
        setChecked(isNowChecked);

        const url = isNowChecked ? selectUrl : unselectUrl;
        const action = isNowChecked ? 'selected' : 'unselected';

        fetch(`${url}/${playlist.id}`, {
            credentials: 'include',
        })
            .then(response => response.json())
            .then(data => console.log(`Item ${action}:`, data))
            .catch(error => console.error('Error:', error));
    };

    return (
        <div className={`playlist-item ${isExpanded ? 'expanded' : ''}`}>
            <div className="info-wrapper">
                <img
                    className="playlist-image"
                    src={playlist.image ? playlist.image : require('./images/LikedSongs.png')}
                    alt="playlist"
                />
                <p className="playlist-name">{playlist.name}</p>
                <div className="button-wrapper">
                    <button className="gear" onClick={handleGearClick}>
                        <img className={`gear-icon${isExpanded ? ' rotated' : ''}`} src={gearIcon} alt="gear" />
                    </button>
                    <div className="checkbox-wrapper-35">
                        <input
                            className="switch"
                            type="checkbox"
                            id={inputId}
                            name={inputId}
                            value="private"
                            checked={checked}
                            onChange={handleCheckboxChange}
                        />
                        <label htmlFor={inputId}>
                            <span className="switch-x-toggletext">
                                <span className="switch-x-unchecked"><span className="switch-x-hiddenlabel">Unchecked: </span>Sift</span>
                                <span className="switch-x-checked"><span className="switch-x-hiddenlabel">Checked: </span>Sifting</span>
                            </span>
                        </label>
                    </div>
                </div>
            </div>
            <div className={`expanded-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
                <p></p>
                <label className="skip-label">
                    Times skipped before sifting
                    <input
                        className="skip-input"
                        type="number"
                        value={skipCount}
                        onChange={handleChange}
                        min="1"
                        max="9"
                    />
                </label>
                {siftedPlaylist === null ?
                    <p className="sifted-playlist">
                        No songs sifted yet
                    </p>
                    :
                    <p className="sifted-playlist">
                        Visit sifted <a href={"https://open.spotify.com/playlist/" + siftedPlaylist} target="_blank" rel="noopener noreferrer">playlist</a>
                    </p>
                }
            </div>
        </div>
    );
}



export default PlaylistDisplay;
