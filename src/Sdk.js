import React, { useEffect, useState } from "react";
import { GetNowPlaying } from "./GetCurrentTrack";

const track = {
    name: "",
    album: {
        images: [
            { url: "" }
        ]
    },
    artists: [
        { name: "" }
 
    ]
}

function Sdk() {
    // const accessToken = new URLSearchParams(window.location.search).get('access_token');
    
    // const [is_paused, setPaused] = useState(false);
    // const [is_active, setActive] = useState(false);
    // const [player, setPlayer] = useState(null);
    // const [current_track, setTrack] = useState(track);

    // useEffect(() => {(async () => {
    //     const script = document.createElement("script");
    //     script.src = "https://sdk.scdn.co/spotify-player.js";
    //     script.async = true;

    //     document.body.appendChild(script);

    //     await new Promise(resolve => {
    //         window.onSpotifyWebPlaybackSDKReady = resolve;
    //     });

    //     /* eslint-disable no-undef */
    //     const player = new Spotify.Player({
    //         /* eslint-enable no-undef */
    //         name: 'Spotify Skipper',
    //         getOAuthToken: cb => { cb(accessToken); },
    //         volume: 0.5
    //     });
    //     setPlayer(player);


    //     player.addListener('ready', ({ device_id }) => {
    //         console.log('Ready with Device ID', device_id);
    //     });

    //     player.addListener('not_ready', ({ device_id }) => {
    //         console.log('Device ID has gone offline', device_id);
    //     });

    //     player.addListener('player_state_changed', (state => {
    //         debugger;
    //         if (!state) {
    //             return;
    //         }

    //         setTrack(state.track_window.current_track);
    //         setPaused(state.paused);

    //         player.getCurrentState().then(state => {
    //             (!state) ? setActive(false) : setActive(true)
    //         });

    //     }));

    //     player.connect();
    // })()}, [accessToken]);


    return (
        <>
            <div className="container">
                <div className="main-wrapper">
                    <h1>Current Track</h1>
                    {/* <img src={current_track.album.images[0].url} className="now-playing__cover" alt="" />

                    <div className="now-playing__side">
                        <div className="now-playing__name">{current_track.name}</div>
                        <div className="now-playing__artist">{current_track.artists[0].name}</div>

                        <button className="btn-spotify" onClick={() => { player.previousTrack() }} >
                            &lt;&lt;
                        </button>

                        <button className="btn-spotify" onClick={() => { player.togglePlay() }} >
                            {is_paused ? "PLAY" : "PAUSE"}
                        </button>

                        <button className="btn-spotify" onClick={() => { player.nextTrack() }} >
                            &gt;&gt;
                        </button>
                    </div> */}
                </div>
            </div>
        </>
    );
}

export default Sdk;