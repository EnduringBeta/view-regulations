import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

function Card({ agency }) {
  return (
    <div id={`agency-${agency.id}`} className="Card">
      <div className="Container">
        <h2>{agency.name}</h2>
        <h3>{agency.type}</h3>
      </div>
    </div>
  );
}

function App() {
  const [agencies, setAgencies] = useState([]);

  useEffect(() => {
    fetch("/agencies").then((res) => res.json()).then((data) => {
        setAgencies(data);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Web App - Regulations</h1>
        <div className="Agencies">
          {agencies.map((item, index) =>
            <Card key={index} agency={item} />
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
