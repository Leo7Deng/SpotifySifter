import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import NavBar from './NavBar'; 
import Footer from './Footer';
import Home from "./Home";
import DeletedSongsPlaylists from "./DeletedSongsPlaylists";
import Leaderboard from "./Leaderboard";
import PlaylistSelectCheck from "./PlaylistSelectCheck";
import About from "./About";
import Contact from "./Contact";

function App() {
  return (
    <Router>
      <NavBar /> 
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/DeletedSongsPlaylists" element={<DeletedSongsPlaylists />} />
        <Route path="/Leaderboard" element={<Leaderboard />} />
        <Route path="/PlaylistSelectCheck" element={<PlaylistSelectCheck />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
