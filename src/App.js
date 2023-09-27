import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./Home"
import Sdk from "./Sdk"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/sdk" element={<Sdk />} />
      </Routes>
    </Router>
  );
}

export default App;