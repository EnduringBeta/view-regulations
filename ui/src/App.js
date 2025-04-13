import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import logo from './logo.svg';
import './App.css';
import HomePage from './HomePage';
import AgencyPage from './AgencyPage';

function App() {
  return (
    <Router>
      <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Web App - Regulations</h1>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/agencies/:agencyId/regulations" element={<AgencyPage />} />
        </Routes>
      </header>
    </div>
    </Router>
  );
}

export default App;
