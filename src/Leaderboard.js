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
    
    const totalPlayedValues = leaderboard.map(item => item.total_played);
    const maxTotalPlayed = Math.max(...totalPlayedValues);
    const heights = totalPlayedValues.map(value => (value / maxTotalPlayed) * 79);
    
    const [searchParams] = useSearchParams();
    const access_token = searchParams.get("access_token");
    const current_user_id = searchParams.get("current_user_id");

    return (
        <>
            <Link to={`/PlaylistSelectCheck?current_user_id=${current_user_id}&access_token=${access_token}`}>
                <div className="right-arrow">
                    <img src={require('./rightarrow.png')} alt="Right Arrow" width="28" className="arrow"/>
                    <div className="arrow-emoji">🎵</div>
                </div>
            </Link>
            <Link to={`/DeletedSongsPlaylists?current_user_id=${current_user_id}&access_token=${access_token}`}>
                <div class="left-arrow">
                    <img src={require('./rightarrow.png')} alt="Right Arrow" width="28" className="arrow-left"/>
                    <div className="arrow-emoji-left">🗑️</div>
                </div>
            </Link>
            <h4>Leaderboard</h4>
            <div className="leaderboard-line"></div>
            {leaderboard.length > 0 ? (
                <div className="leaderboard-container">
                    {leaderboard.map((item, index) => (
                        <>
                            <div className={`leaderboard-box leaderboard-box-${index+1}`} style={{ height: `${heights[index]}%` }} key={index}></div>
                            <h5 className={`leaderboard-name leaderboard-name-${index+1}`}>{item.username}</h5>
                            <h5 className={`leaderboard-total leaderboard-total-${index+1}`}>{item.total_played}</h5>
                        </>
                    ))}
                </div>
            ) : (
                <h4 className="no-songs">No songs have been sifted!</h4>
            )}
        </>
    );
}

export default Leaderboard;
