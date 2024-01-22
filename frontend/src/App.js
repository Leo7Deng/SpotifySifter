import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"
import DeletedSongsPlaylists from "./DeletedSongsPlaylists";
import Leaderboard from "./Leaderboard";
import PlaylistSelectCheck from "./PlaylistSelectCheck";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/DeletedSongsPlaylists" element={<DeletedSongsPlaylists />} />
        <Route path="/Leaderboard" element={<Leaderboard />} />
        <Route path="/PlaylistSelectCheck" element={<PlaylistSelectCheck />} />
      </Routes>
    </Router>
  );
}

export default App;