import React, { useState, useEffect } from 'react';
import './PlaylistDisplay.css';
import gearIcon from './images/gear.svg';

function PlaylistDisplay({ playlist, isChecked, skipCount }) {
    const [checked, setChecked] = useState(isChecked);
    const inputId = `switch-${playlist.id}`;
    const selectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/select' : 'http://localhost:8889/select';
    const unselectUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/unselect' : 'http://localhost:8889/unselect';
    const [isExpanded, setIsExpanded] = useState(false);
    const [inputValue, setInputValue] = useState(skipCount);
    const [isButtonEnabled, setIsButtonEnabled] = useState(false);
    // what type is inputValue?
    console.log(inputValue);
    
    const handleSave = (event) => {
        const inputValue = event.target.value;
        if (inputValue !== '') {
            // Assuming you want to perform some action or send data to update skipCount on the server.
            // You can implement the logic here to update skipCount externally.
    
            // After successfully updating, you can set savedSkipCount to the new value
            setInputValue(inputValue);
    
            // Disable the button after saving
            setIsButtonEnabled(false);
        }
    };
    
    

    useEffect(() => {
        // Check if input value differs from skipCount and update button state
        setIsButtonEnabled(inputValue !== skipCount);
    }, [inputValue, skipCount]);

    const handleChange = (event) => {
        const newInputValue = event.target.value;
        setInputValue(newInputValue); // Update input value
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
                    <button className={`gear${isExpanded ? ' rotate' : ''}`} onClick={handleGearClick}>
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
            <div className={`expanded-content ${isExpanded ? 'expanded' : 'collapsed'}`}>
                <p></p>
                <label>
                    Times skipped before sifting: 
                    <input
                        type="number"
                        value={inputValue} 
                        onChange={handleChange}
                        min="1"
                        max="10"
                    />
                </label>
                <button
                    onClick={handleSave}
                    className={`checkmark-button ${isButtonEnabled ? '' : 'disabled-button'}`} // Enable/disable the button
                    disabled={!isButtonEnabled} // Disable based on isButtonEnabled
                >
                    ✓
                </button>
                {inputValue !== null && (
                    <p>Skip count saved: {inputValue}</p>
                )}
            </div>
        </div>
    );
}


export default PlaylistDisplay;
