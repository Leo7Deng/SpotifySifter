import React from 'react';
import './About.css';

function About() {
    return (
        <>
            <div className="about">
                <p className='about-subtitle'>Spotify Sifter is a free service to remove frequently skipped tracks from your playlists.</p>
                <p className='about-text'>A problem many Spotifer users face is having bloated playlists. Even good songs will be stuck in the wrong playlists, causing overskipping. To remedy this problem, Spotify Sifter allows users to automatically sift frequently skipped tracks into a "sorted" playlist which they can then review.</p>
                <p className='about-subtitle'>How can I use it?</p>
                <ol className='about-text'>
                    <li>Log in with Spotify on our site.</li>
                    <li>Select the playlists you want to sort.</li>
                    <li>Close Spotify Sifter and start listening to music how you normally would.</li>
                    <li>Periodically check back to see which songs have been sorted.</li>
                </ol>
                <p className='about-subtitle'>How does it work?</p>
                <p className='about-text'>Spotify Sifter listens to a user's activity only when they are listening in a selected playlist. Looking at a user's queued songs periodically, we are able to figure out which songs are skipped. Shuffling and skipping to previous tracks will not disrupt our ability to view skipped tracks.</p>
            </div>
        </>
    );
}

export default About;