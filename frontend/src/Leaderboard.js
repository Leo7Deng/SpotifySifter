import { useEffect, useState } from "react";
import './Leaderboard.css';
import { Link } from 'react-router-dom';

function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState([]);

    const leaderboardUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/leaderboard` : `http://localhost:8889/leaderboard`;

    useEffect(() => {
        fetch(leaderboardUrl, { credentials: 'include' })
            .then(response => response.json())
            .then(leaderboard => {
                setLeaderboard(leaderboard);
                console.log('Leaderboard:', leaderboard);
            })
            .catch(error => console.error('Error:', error));
    }, [leaderboardUrl]);

    return (
        <>
            <Link to={"/PlaylistSelect"}>
                <div className="right-arrow">
                    <img src={require('./images/rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🎵</div>
                </div>
            </Link>
            <Link to={"/SiftedSongs"}>
                <div className="left-arrow">
                    <img src={require('./images/rightarrow.png')} alt="Right Arrow" width="28" className="arrow-left" />
                    <div className="arrow-emoji-left">🗑️</div>
                </div>
            </Link>
            <div className="leaderboard-title">
                <h4 style={{ marginBottom: '0px' }}>Leaderboard</h4>
                <h5 style={{ marginTop: '0px' }}>Total Songs Played</h5>
            </div>
            <div className="leaderboard">
                {leaderboard.map((user, index) => (
                    <div className="leaderboard-user" key={index}>
                        <div className="leaderboard-user-rank">#{index + 1}</div>
                        <div className="leaderboard-user-picture">
                            <iframe className="leaderboard-user-iframe" src={user.profile_pic} frameBorder="0" title={`User ${user.username}`}></iframe>
                        </div>
                        <div className="leaderboard-user-name">{user.username}</div>
                        <div className="leaderboard-user-score">{user.total_played}</div>
                    </div>
                ))}
            </div>
        </>
    );
}

export default Leaderboard;
