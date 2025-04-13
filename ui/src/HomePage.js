import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

import './App.css';

function AgencyCard({ agency, parentAgency }) {
  return (
    <div id={`agency-${agency.slug}`} className="Card">
      <div className="Container">
        <h2>{agency.short_name}</h2>
        <p>
          <Link to={`/agencies/${agency.id}/regulations`} className="App-link">
            {agency.name}
          </Link>
        </p>
        {parentAgency && (
        <h3>Within {parentAgency.short_name}</h3>
        )}
      </div>
    </div>
  );
}

function HomePage() {
  const [agencies, setAgencies] = useState([]);

  useEffect(() => {
    fetch("/agencies").then((res) => res.json()).then((data) => {
        setAgencies(data);
      });
  }, []);

  return (
    <div className="Agencies">
      {agencies.map((item, index) => {
        const parentAgency = agencies.find(
          (agency) => agency.id === item.parent_id
        ) ?? null;

        return (
          <AgencyCard key={index} agency={item} parentAgency={parentAgency} />
        );
      })}
    </div>
  );
}

export default HomePage;
