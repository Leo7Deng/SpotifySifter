import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import NavBar from './NavBar';
import Footer from './Footer';
import Home from "./Home";
import SiftedSongs from "./SiftedSongs";
import Leaderboard from "./Leaderboard";
import PlaylistSelect from "./PlaylistSelect";
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
        <Route path="/SiftedSongs" element={<SiftedSongs />} />
        <Route path="/Leaderboard" element={<Leaderboard />} />
        <Route path="/PlaylistSelect" element={<PlaylistSelect />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
