// Get the current user ID from the URL
const currentUserId = window.location.search.split('=')[1];

// Make a request to the backend endpoint
fetch(`/get_delete_playlists${currentUserId}`)
    .then(response => response.json())
    .then(data => {
        // Check if the response is not None
        if (data !== null) {
            // Loop through the playlist URIs and display the embedded playlists
            data.forEach(uri => {
                const iframe = document.createElement('iframe');
                iframe.src = `https://open.spotify.com/embed/playlist/${uri}`;
                iframe.width = '300';
                iframe.height = '380';
                document.body.appendChild(iframe);
            });
        } else {
            // Display "no playlists" if the response is None
            const message = document.createElement('p');
            message.textContent = 'No playlists';
            document.body.appendChild(message);
        }
    })
    .catch(error => console.error(error));
