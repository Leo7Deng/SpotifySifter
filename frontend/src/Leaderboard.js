import { useEffect, useState } from "react";
import './Leaderboard.css';
import { useSearchParams } from "react-router-dom";
import { Link } from 'react-router-dom';

function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState([]);
    const [isUserInLeaderboard, setIsUserInLeaderboard] = useState(false);
    const [total_played, setTotalPlayed] = useState(0);
    const [profile_pic, setProfilePic] = useState(null);
    const [username, setUsername] = useState(null);

    const [searchParams] = useSearchParams();
    const access_token = searchParams.get("access_token");
    const current_user_id = searchParams.get("current_user_id");
    const leaderboardUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/leaderboard` : `http://localhost:8889/leaderboard`;
    const totalPlayedUrl = process.env.NODE_ENV === 'production' ? `https://spotifysifter.up.railway.app/total_played/` : `http://localhost:8889/total_played/`;

    useEffect(() => {
        fetch(leaderboardUrl, { credentials: 'include'})
            .then(response => response.json())
            .then(leaderboard => {
                setLeaderboard(leaderboard);
                console.log('Leaderboard:', leaderboard);

                const foundUser = leaderboard.find(user => user.id === Number(current_user_id));
                console.log('Found User:', foundUser);

                if (foundUser) {
                    setIsUserInLeaderboard(true);
                }
            })
            .catch(error => console.error('Error:', error));
    }, [leaderboardUrl]);

    useEffect(() => {
        console.log('Is User In Leaderboard:', isUserInLeaderboard);
        if (!isUserInLeaderboard) {
            console.log('Fetching Total Played');
            fetch(totalPlayedUrl, { credentials: 'include' })
                .then(response => response.json())
                .then(data => {
                    setTotalPlayed(data.total_played);
                    setProfilePic(data.profile_pic);
                    setUsername(data.username);
                })
                .catch(error => console.error('Error:', error));
        }
    }, [isUserInLeaderboard, totalPlayedUrl]);

    return (
        <>
            <Link to={`/PlaylistSelectCheck?current_user_id=${current_user_id}&access_token=${access_token}`}>
                <div className="right-arrow">
                    <img src={require('./images/rightarrow.png')} alt="Right Arrow" width="28" className="arrow" />
                    <div className="arrow-emoji">🎵</div>
                </div>
            </Link>
            <Link to={`/DeletedSongsPlaylists?current_user_id=${current_user_id}&access_token=${access_token}`}>
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

                {!isUserInLeaderboard && (
                    <div className="leaderboard-user">
                        <div className="leaderboard-user-rank">...</div>
                        <div className="leaderboard-user-picture">
                            <iframe className="leaderboard-user-iframe" src={profile_pic} frameBorder="0" title={`Bottom-User ${username}`}></iframe>
                        </div>
                        <div className="leaderboard-user-name">{username}</div>
                        <div className="leaderboard-user-score">{total_played}</div>
                    </div>
                )}
            </div>
        </>
    );
}

export default Leaderboard;
