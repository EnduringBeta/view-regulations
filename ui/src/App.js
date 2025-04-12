import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

function Card({ animal }) {
  return (
    <div id="animal-${animal.id}" className="Card">
      <div className="Container">
        <h2>{animal.name}</h2>
        <h3>{animal.type}</h3>
      </div>
    </div>
  );
}

function App() {
  const [animals, setAnimals] = useState([]);

  useEffect(() => {
    fetch("/animals").then((res) => res.json()).then((data) => {
        setAnimals(data);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Web App - Regulations</h1>
        <div className="Animals">
          {animals.map((item, index) =>
            <Card key={index} animal={item} />
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
