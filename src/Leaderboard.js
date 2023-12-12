import { useEffect, useState } from "react";
import './Leaderboard.css';
import { useSearchParams } from "react-router-dom";
import { Link } from 'react-router-dom';

function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState([]);

    useEffect(() => {
        fetch(`http://localhost:8889/leaderboard`)
            .then(response => response.json())
            .then(leaderboard => {
                setLeaderboard(leaderboard);
            })
            .catch(error => console.error('Error:', error));
    }, []);

    const [searchParams] = useSearchParams();
    const access_token = searchParams.get("access_token");
    const current_user_id = searchParams.get("current_user_id");

    return (
        <>
            <Link to={`/PlaylistSelectCheck?current_user_id=${current_user_id}&access_token=${access_token}`}>
                <div className="right-arrow">
                    <img src={require('./rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🎵</div>
                </div>
            </Link>
            <Link to={`/DeletedSongsPlaylists?current_user_id=${current_user_id}&access_token=${access_token}`}>
                <div class="left-arrow">
                    <img src={require('./rightarrow.png')} alt="Right Arrow" width="28" className="arrow-left" />
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
                            <iframe className="leaderboard-user-iframe" src={user.profile_pic} frameBorder="0"></iframe>
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
