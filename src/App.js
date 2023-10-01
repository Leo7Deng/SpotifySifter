import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"
import GetCurrentTrack from "./GetCurrentTrack";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/GetCurrentTrack" element={<GetCurrentTrack />} />
      </Routes>
    </Router>
  );
}

export default App;