import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";

export default function Correlations() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.correlations().then(setData).catch(setError);
  }, []);

  if (error) return <ErrorState error={error} />;
  if (!data) return <LoadingState />;

  return (
    <section>
      <h2>Correlation Analysis</h2>

      <p className="muted">
        Values are Pearson correlations. Correlation does not imply causation.
      </p>

      <div className="table-wrap">
        <table className="correlation-table">
          <thead>
            <tr>
              <th></th>
              {data.features.map((feature) => (
                <th key={feature}>{feature}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.matrix.map((row, i) => (
              <tr key={data.features[i]}>
                <th>{data.features[i]}</th>
                {row.map((value, j) => (
                  <td key={j}>{value.toFixed(2)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
