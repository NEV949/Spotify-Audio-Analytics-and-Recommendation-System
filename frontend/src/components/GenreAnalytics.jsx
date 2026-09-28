import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";

export default function GenreAnalytics() {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.genreStatistics().then(setData).catch(setError);
  }, []);

  if (error) return <ErrorState error={error} />;
  if (!data.length) return <LoadingState />;

  return (
    <section>
      <h2>Genre Analytics</h2>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Genre</th>
              <th>Songs</th>
              <th>Avg Popularity</th>
              <th>Energy</th>
              <th>Danceability</th>
              <th>Valence</th>
              <th>Acousticness</th>
              <th>Tempo</th>
            </tr>
          </thead>

          <tbody>
            {data.map((row) => (
              <tr key={row.track_genre}>
                <td>{row.track_genre}</td>
                <td>{row.songs}</td>
                <td>{Number(row.average_popularity).toFixed(1)}</td>
                <td>{Number(row.average_energy).toFixed(2)}</td>
                <td>{Number(row.average_danceability).toFixed(2)}</td>
                <td>{Number(row.average_valence).toFixed(2)}</td>
                <td>{Number(row.average_acousticness).toFixed(2)}</td>
                <td>{Number(row.average_tempo).toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
