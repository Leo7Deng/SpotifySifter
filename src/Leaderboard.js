import { useEffect, useState } from "react";
import './Leaderboard.css';

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

    return (
        <>
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
