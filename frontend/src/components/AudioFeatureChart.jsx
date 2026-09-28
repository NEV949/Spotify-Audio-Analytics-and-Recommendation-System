import React from "react";
export default function AudioFeatureChart({ features = {} }) {
  return (
    <div>
      {Object.entries(features).map(([name, value]) => {
        const numeric = Number(value);
        const width =
          name === "tempo"
            ? Math.min(100, numeric / 2.5)
            : name === "loudness"
            ? Math.min(100, Math.max(0, (numeric + 60) / 1.2))
            : Math.min(100, Math.max(0, numeric * 100));

        return (
          <div className="feature-row" key={name}>
            <div className="feature-label">
              <span>{name}</span>
              <span>{numeric.toFixed(3)}</span>
            </div>
            <div className="feature-bar">
              <div style={{ width: `${width}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
