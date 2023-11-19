import React, { useState } from 'react';
import './Home.css';

function Home() {
  const [isLoading, setIsLoading] = useState(false);

  const handleLoginClick = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8889/login', {
        method: 'GET',
      });
      if (response.status === 200) {
        const { auth_url } = await response.json();
        console.log(auth_url)
        window.location.href = auth_url;
      } else {
        console.error('Failed to initiate login:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  return (
    <>
      <div className='home'>
        <h1>Spotify Sifter</h1>
        <button className="home-button" onClick={handleLoginClick}>Login with Spotify</button>
      </div>
      {isLoading && <div className="loader"></div>}
    </>
  );
}
  
export default Home;
