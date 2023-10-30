import { useEffect } from "react";
import { useState } from "react";
import './Leaderboard.css';

function Leaderboard() {
    const [leaderboard, setLeaderboard] = useState([]); // [ { username: blazing7ice, total_played: 100 }, { username: blazing7ice, total_played: 100 } ]

    useEffect(() => {
        fetch(`http://localhost:8888/leaderboard`)
            .then(response => response.json())
            .then(leaderboard => {
                setLeaderboard(leaderboard);
            })
            .catch(error => console.error('Error:', error));
    }
    , []);
    
    return (
        <>
            <h4>Leaderboard</h4>
            {leaderboard.length > 0 ? (
                <div className="leaderboard-container">
                    {leaderboard.map((user) => (
                        <div className="leaderboard-user">
                            <h5>{user.username}</h5>
                            <h5>{user.total_played}</h5>
                        </div>
                    ))}
                </div>
            ) : (
                <h4 className="no-songs">No songs have been sifted!</h4>
            )}
        </>
    );
}

export default Leaderboard;