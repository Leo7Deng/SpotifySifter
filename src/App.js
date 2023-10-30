import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"
import PlaylistSelect from "./PlaylistSelect";
import DeletedSongsPlaylists from "./DeletedSongsPlaylists";
import Leaderboard from "./Leaderboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/PlaylistSelect" element={<PlaylistSelect />} />
        <Route path="/DeletedSongsPlaylists" element={<DeletedSongsPlaylists />} />
        <Route path="/Leaderboard" element={<Leaderboard />} />
      </Routes>
    </Router>
  );
}

export default App;