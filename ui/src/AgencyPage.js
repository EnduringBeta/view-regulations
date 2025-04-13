import React, { useState, useEffect } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import './App.css';

const startYear = 2015;
const loadingText = "Loading...";

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
        <h3>{formatWordCount(regulation.word_count)} words</h3>
        <p>As of {formatDate(regulation.date)}</p>
      </div>
    </div>
  );
}

function YearSelector({ year, currentYear, setYear }) {
  // Generate a list of years for the drop down
  const dropdownYears = Array.from(
    { length: currentYear - startYear + 1 },
    (_, i) => startYear + i
  );

  return (
    <div className="YearSelector">
      <label htmlFor="year-select">Select Year: </label>
      <select
        id="year-select"
        value={year}
        onChange={(e) => setYear(e.target.value)}
      >
        {dropdownYears.map((y) => (
          <option key={y} value={y}>{y}</option>
        ))}
      </select>
    </div>
  );
}

/// Accepts "?year=2022"
/// TODOROSS: check child agencies
function AgencyPage() {
  const { agencyId } = useParams();
  const [searchParams] = useSearchParams();
  const currentYear = new Date().getFullYear();
  const initialYear = searchParams.get("year") || currentYear;
  const [year, setYear] = useState(initialYear);

  //const [loading, setLoading] = useState(true);
  const [agency, setAgency] = useState([]);
  const [regulations, setRegulations] = useState([]);

  useEffect(() => {
    fetch(`/agencies/${agencyId}`).then((res) => res.json()).then((data) => {
      setAgency(data);
    });
  }, [agencyId]);

  useEffect(() => {
    setRegulations([]); // Reset regulations when year changes
    fetch(`/agencies/${agencyId}/regulations/${year}`).then((res) => res.json()).then((data) => {
      setRegulations(data);
    });
  }, [agencyId, year]);

  // Calculate total word count
  const totalWordCount = regulations.reduce((total, regulation) => {
    return total + (regulation.word_count || 0);
  }, 0);

  return (
    <div id={`agency-regulations-${agency.slug}`}>
      <h1>{agency.short_name}</h1>
      <h2>Total words: {totalWordCount === 0 ? loadingText : formatWordCount(totalWordCount)}</h2>
      <YearSelector year={year} currentYear={currentYear} setYear={setYear}></YearSelector>
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

function formatWordCount(count) {
  if (count === null) {
    return "N/A";
  }
  if (count > 1000000000) {
    return `${(count / 1000000000).toFixed(1)}B`;
  } else if (count > 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  } else if (count > 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  } else {
    return count;
  }
}

function formatDate(date) {
  if (!date) return "N/A";

  const d = new Date(date);
  const year = d.getFullYear();
  const month = d.toLocaleString("default", { month: "long" });
  const day = d.getDate();

  return `${month} ${day}, ${year}`;
}

export default AgencyPage;
