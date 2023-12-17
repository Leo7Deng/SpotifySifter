import React, { useState, useEffect } from 'react';
import './Home.css';

function Home() {
  const [fadeOut, setFadeOut] = useState(false);
  const [authUrl, setAuthUrl] = useState('');

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
      const response = await fetch('http://localhost:8889/login', {
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
    </>
  );
}

export default Home;
