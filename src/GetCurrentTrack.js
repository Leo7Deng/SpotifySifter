const NOW_PLAYING_ENDPOINT = `https://api.spotify.com/v1/me/player/currently-playing`;

function GetCurrentTrack() {
    async function GetNowPlaying() {
        const access_token = new URLSearchParams(window.location.search).get('access_token');
        const response = await fetch(NOW_PLAYING_ENDPOINT, {
            headers: {
                Authorization: `Bearer ${access_token}`,
            },
        });
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        debugger;
        return response.json();
    };
    GetNowPlaying()
    .then(data => {
        // Print the JSON response
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
    return (
        <>
        i like dick
        </>
    )
}

export default GetCurrentTrack;