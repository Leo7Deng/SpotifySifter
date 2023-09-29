import React, { useEffect, useState } from "react";
import { WebPlaybackSDK } from "react-spotify-web-playback-sdk";

function Sdk() {
  let player;
  const accessToken = new URLSearchParams(window.location.search).get('access_token');

  useEffect(() => {
    const script = document.createElement('script');
  
    script.src = "https://sdk.scdn.co/spotify-player.js";
    script.async = true;
  
    document.body.appendChild(script);
  
    return () => {
      document.body.removeChild(script);
    }
  }, []);
  
  window.onSpotifyWebPlaybackSDKReady = () => {
    /* eslint-disable no-undef */
    player = new Spotify.Player({
      /* eslint-enable no-undef */
      name: 'Web Playback SDK Quick Start Player',
      getOAuthToken: cb => { debugger;cb(accessToken); }
    });
    player.connect().then(success => {
      debugger;
      if (success) {
        console.log('The Web Playback SDK successfully connected to Spotify!');
      }
    });


  }

  
  return (
    <div>
      <h1>SDK</h1>
    </div>
  );
}

export default Sdk;