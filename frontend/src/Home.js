import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  const [fadeOut, setFadeOut] = useState(false);
  const [authUrl, setAuthUrl] = useState('');
  const loginUrl = process.env.NODE_ENV === 'production' ? 'https://spotifysifter.up.railway.app/login' : 'http://localhost:8889/login';

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
        credentials: 'include',
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
        <h1 className="home-title">Spotify Sifter</h1>
        <p className='subtitle'>Select your playlists to sort out frequently skipped tracks</p>
        <button className="home-button" onClick={handleLoginClick}>
          Log in with Spotify
        </button>
      </div>
      <hr className='bar'></hr>
      <div className="home-footer">
        <p className="footer-text">Created by Leo Deng</p>
        <p className="footer-text">© 2024 - SpotifySifter.com</p>
        <div className="footer-links">
          <Link className="link" to="/">Home </Link> |
          <Link className="link" to="/about"> About </Link> |
          <Link className="link" to="/contact"> Contact</Link>
        </div>
      </div>
    </>
  );
}

export default Home;
