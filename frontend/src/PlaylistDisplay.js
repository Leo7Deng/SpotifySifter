import React, { useState } from 'react';
import './PlaylistDisplay.css';
import gearIcon from './images/gear.svg';

function PlaylistDisplay({ playlist, isChecked }) {
    const [checked, setChecked] = useState(isChecked);
    const inputId = `switch-${playlist.id}`;
    const [isGearChecked, setGearChecked] = useState(false);
    const selectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/select' : 'http://localhost:8889/select';
    const unselectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/unselect' : 'http://localhost:8889/unselect';
    const [isAnimating, setIsAnimating] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    const handleGearClick = () => {
        if (isAnimating) {
            return;
        }
        setIsExpanded(!isExpanded);
        setGearChecked(!isGearChecked);
        setIsAnimating(true);
        setTimeout(() => {
            setIsAnimating(false);
        }, 700);
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
        <div className={`playlist-item ${isExpanded ? 'expanded' : 'collapsed'}`}>
            <div className="playlist-info">
                <div className="info-wrapper">
                    <img
                        className="playlist-image"
                        src={playlist.image ? playlist.image : require('./images/LikedSongs.png')}
                        alt="playlist"
                    />
                    <p className="playlist-name">{playlist.name}</p>
                </div>
                <div className="button-wrapper">
                    <button className={`gear${isGearChecked ? ' rotate' : ''}`} onClick={handleGearClick}>
                        <img className="gear-icon" src={gearIcon} alt="gear" />
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
            {isExpanded && (
                <div className={`expanded-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
                    <p className="expanded-description">blah blah</p>
                </div>
            )}
        </div>
    );
}

export default PlaylistDisplay;
