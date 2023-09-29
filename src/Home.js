import Sdk from "./Sdk";

function Home() {
  const handleLoginClick = async () => {
    try {
      const response = await fetch('http://localhost:8888/login', {
        method: 'GET',
      });
      if (response.status === 200) {
        // Redirect to the Spotify authentication URL if the request was successful.
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
    <div>
      <h1>Spotify</h1>
      <button onClick={handleLoginClick}>Login with Spotify</button>
    </div>
  );
  }
  
  export default Home;
  