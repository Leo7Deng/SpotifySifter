import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"
import PlaylistSelect from "./PlaylistSelect";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/PlaylistSelect" element={<PlaylistSelect />} />
      </Routes>
    </Router>
  );
}

export default App;