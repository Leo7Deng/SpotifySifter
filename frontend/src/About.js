import React from 'react';
import './About.css';

function About() {
    return (
        <>
            <div className="about">
                <p className='about-subtitle'>Spotify Sifter is a free service to remove frequently skipped tracks from your playlists.</p>
                <p className='about-text'>A problem many Spotify users face is having bloated playlists. Even good songs will be stuck in the wrong playlists, causing overskipping. To remedy this problem, Spotify Sifter allows users to automatically sift frequently skipped tracks into a "sorted" playlist which they can then review.</p>
                <p className='about-subtitle'>How can I use it?</p>
                <ol className='about-text'>
                    <li>Log in with Spotify on our site.</li>
                    <li>Select the playlists you want to sort.</li>
                    <li>Close Spotify Sifter and start listening to music how you normally would.</li>
                    <li>Periodically check back to see which songs have been sorted.</li>
                </ol>
                <p className='about-subtitle'>How does it work?</p>
                <p className='about-text'>Spotify Sifter listens to a user's activity only when they are listening in a selected playlist. Looking at a user's queued songs periodically, we are able to figure out which songs are skipped. Shuffling and skipping to previous tracks will not disrupt our ability to view skipped tracks.</p>
                <p className='about-subtitle'>My playlist still shows no sifted songs, why?</p>
                <p className='about-text'>Be patient and check back in a week. It takes time for Spotify Sifter to gather enough data to sort out the frequently skipped tracks.</p>
                <p className='about-subtitle'>What should I do if I accidentally skip a song?</p>
                <p className='about-text'>If you accidentally skip a song, don't worry. As long as you dont skip the same song too many times in a row, it will not be sorted out.</p>
                <p className='about-subtitle'>Can I move the sorted songs back into the original playlist?</p>
                <p className='about-text'>Yes, you can move the sorted songs back into the original playlist. This will not affect the sorting process. If you ever want to resort the playlist, you can click the resort button under a playlist's settings.</p>
                <p className='about-subtitle'>What should I do if I deleted one of my sifted playlists?</p>
                <p className='about-text'>If you accidentally delete a playlist that contains the sorted songs and you want it back, you can visit <a href="https://www.spotify.com/us/account/recover-playlists/">spotify.com/us/account/recover-playlists/</a> to restore it.</p>
            </div>
        </>
    );
}

export default About;