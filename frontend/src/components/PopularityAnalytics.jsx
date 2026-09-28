import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";

export default function PopularityAnalytics() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.popularity().then(setData).catch(setError);
  }, []);

  if (error) return <ErrorState error={error} />;
  if (!data) return <LoadingState />;

  return (
    <section>
      <h2>Popularity Analysis</h2>

      <div className="stats">
        <Stat label="Minimum" value={data.statistics.min} />
        <Stat label="Maximum" value={data.statistics.max} />
        <Stat label="Mean" value={data.statistics.mean} />
        <Stat label="Median" value={data.statistics.median} />
      </div>

      <div className="panel">
        <h3>Observed Correlation With Popularity</h3>

        {data.relationships.map((item) => (
          <div className="list-row" key={item.feature}>
            <span>{item.feature}</span>
            <strong>{item.correlation}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
