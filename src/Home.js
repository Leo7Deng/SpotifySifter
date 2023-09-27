function Home() {
  const handleLoginClick = async () => {
    try {
      const response = await fetch('http://localhost:8888/login', {
        method: 'GET',
      });
      if (response.status === 200) {
        // Redirect to the Spotify authentication URL if the request was successful.
        const { auth_url } = await response.json();
        window.location.href = auth_url;
      } else {
        console.error('Failed to initiate login:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  return (
    <div>
      <head>
        <title>Spotify Web Playback SDK Quick Start</title>
      </head>
      <body>
        <h1>Spotify Web Playback SDK Quick Start</h1>
        <button onClick={handleLoginClick}>Login with Spotify</button>
      </body>
    </div>
  );
  }
  
  export default Home;
  