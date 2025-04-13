import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import './App.css';

function RegulationCard({ regulation }) {
  const referencePieces = [
    regulation.title,
    regulation.subtitle,
    regulation.chapter,
    regulation.subchapter,
    regulation.part,
    regulation.subpart,
  ].filter(item => item !== null);
  const referenceText = referencePieces.join(" ");
  const referenceSlug = referencePieces.join("-").toLowerCase();

  return (
    <div id={`regulation-${referenceSlug}`} className="Card">
      <div className="Container">
        <h2>{referenceText}</h2>
        <p>{regulation.word_count}</p>
        <h3>{regulation.date}</h3>
      </div>
    </div>
  );
}

function AgencyPage() {
  const { agencyId } = useParams();
  const [agency, setAgency] = useState([]);
  const [regulations, setRegulations] = useState([]);

  useEffect(() => {
    fetch(`/agencies/${agencyId}`).then((res) => res.json()).then((data) => {
      setAgency(data);
    });
    fetch(`/agencies/${agencyId}/regulations`).then((res) => res.json()).then((data) => {
      setRegulations(data);
    });
  }, [agencyId]);

  return (
    <div id={`agency-regulations-${agency.slug}`}>
      <h1>{agency.short_name}</h1>
      <div className="Regulations">
        {regulations.map((item, index) => {
          return (
            <RegulationCard key={index} regulation={item} />
          );
        })}
      </div>
    </div>
  );
}

export default AgencyPage;
