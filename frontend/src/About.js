import React from 'react';
import './About.css';

function About() {
    return (
        <>
            <div className="about">
                <h1 className="about-title">About</h1>
                <p className='about-text'>Spotify Sifter is a web app that allows you to sort out frequently skipped tracks from your playlists.</p>
                <p className='about-text'>Spotify Sifter was created by Leo Deng.</p>
                <p className='about-text'>Spotify Sifter is a personal project and is not affiliated with Spotify.</p>
                <p className='about-text'>Spotify Sifter is open source. You can find the code on </p>
            </div>
        </>
    );
}

export default About;