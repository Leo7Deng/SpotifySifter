import React from 'react';
import './Home.css';

function Home() {
  const loginUrl = process.env.NODE_ENV === 'production' ? `https://api.spotifysifter.com/login` : 'http://localhost:8889/login';

  const handleLoginClick = async () => {
    try {
      const response = await fetch(loginUrl, {
        method: 'GET',
        // credentials: 'include',
      });
      if (response.status === 200) {
        window.location.href = (await response.json()).auth_url;
      } else {
        console.error('Failed to initiate login:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  return (
    <>
      <div className="home">
        <h1 className="home-title">Spotify Sifter</h1>
        <p className='subtitle'>Select your playlists to sort out frequently skipped tracks</p>
        <button className="home-button" onClick={handleLoginClick}>
          Log in with Spotify
        </button>
      </div>
    </>
  );
}

export default Home;
