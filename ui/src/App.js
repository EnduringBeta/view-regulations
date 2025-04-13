import logo from './logo.svg';
import './App.css';

import React, { useState, useEffect } from "react";

function Card({ agency, parentAgency }) {
  return (
    <div id={`agency-${agency.slug}`} className="Card">
      <div className="Container">
        <h2>{agency.short_name}</h2>
        <p>{agency.name}</p>
        {parentAgency && (
        <h3>Within {parentAgency.short_name}</h3>
        )}
        <p>{agency.cfr_references}</p>
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
          {agencies.map((item, index) => {
            const parentAgency = agencies.find(
              (agency) => agency.id === item.parent_id
            ) ?? null;

            return (
              <Card key={index} agency={item} parentAgency={parentAgency} />
            );
          })}
        </div>
      </header>
    </div>
  );
}

export default App;
