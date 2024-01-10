import React, { useState, useEffect } from 'react';
import './Home.css';

function Home() {
  const [fadeOut, setFadeOut] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const loginUrl = process.env.NODE_ENV === 'production' ? '/login' : 'http://localhost:8889/login';

  useEffect(() => {
    if (fadeOut && authUrl) {
      const timer = setTimeout(() => {
        window.location.href = authUrl;
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [fadeOut, authUrl]);

  const handleLoginClick = async () => {
    try {
      setFadeOut(true);
      const response = await fetch(loginUrl, {
        method: 'GET',
      });
      if (response.status === 200) {
        const { auth_url } = await response.json();
        setAuthUrl(auth_url);
      } else {
        console.error('Failed to initiate login:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  return (
    <>
      <div className={`home ${fadeOut ? 'fade-out' : ''}`}>
        <h1>Spotify Sifter</h1>
        <button className="home-button" onClick={handleLoginClick}>
          Login with Spotify
        </button>
      </div>
      <div className="symbol">
        <p className="symbol-music">♫</p>
        <p className="symbol-music-paragraph">Select the playlists you want to be sifted</p>
        <p className="symbol-trash">🗑️</p>
        <p className="symbol-trash-paragraph">Look through your sifted songs</p>
        <p className="symbol-trophy">🏆</p>
        <p className="symbol-trophy-paragraph">See the leaderboard of most played songs</p>
      </div>
      <div className="about">

        <h2 className="about-title">About</h2>
        <p className="about-paragraph">
          Spotify Sifter is a web app that allows you to delete unwanted songs from your Spotify playlists.
          Consecutively skipped songs in selected playlists are automatically deleted and stored in a new playlist.
        </p>
        <h2 className="how-title">How it works</h2>
        <p className="how-paragraph">
          Spotify Sifter uses the Spotify Web API to retrieve your queued songs.
          Comparing the queued songs to the songs you have played all the way through, Spotify Sifter determines which songs to delete.
        </p>
        <h2 className="more-title">More info</h2>
        <p className="more-paragraph">
          Spotify Sifter is open source and available on <a href="https://github.com/Leo7Deng/SpotifySifter">GitHub</a>
        </p>
        
      </div>
    </>
  );
}

export default Home;
