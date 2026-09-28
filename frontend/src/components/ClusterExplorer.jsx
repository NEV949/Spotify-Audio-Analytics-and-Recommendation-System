import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import AudioFeatureChart from "./AudioFeatureChart";
import SongTable from "./SongTable";

export default function ClusterExplorer() {
  const [clusters, setClusters] = useState([]);
  const [selected, setSelected] = useState(null);
  const [songs, setSongs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.clusters().then(setClusters).catch(setError);
  }, []);

  async function chooseCluster(id) {
    try {
      const [detail, clusterSongs] = await Promise.all([
        api.clusterDetail(id),
        api.clusterSongs(id)
      ]);

      setSelected(detail);
      setSongs(clusterSongs);
    } catch (err) {
      setError(err);
    }
  }

  if (error) return <ErrorState error={error} />;
  if (!clusters.length) return <LoadingState />;

  return (
    <section>
      <h2>K-Means Cluster Explorer</h2>

      <div className="cluster-grid">
        {clusters.map((cluster) => (
          <button
            className="cluster-card"
            key={cluster.cluster}
            onClick={() => chooseCluster(cluster.cluster)}
          >
            <span>Cluster {cluster.cluster}</span>
            <strong>{cluster.songs}</strong>
            <small>songs</small>
          </button>
        ))}
      </div>

      {selected && (
        <>
          <div className="grid">
            <div className="panel">
              <h3>Cluster {selected.cluster}</h3>
              <p>Songs: {selected.songs}</p>
              <p>Average popularity: {selected.average_popularity}</p>

              <AudioFeatureChart features={selected.averages} />
            </div>

            <div className="panel">
              <h3>Dominant Genres</h3>

              {selected.top_genres.map((item) => (
                <div className="list-row" key={item.genre}>
                  <span>{item.genre}</span>
                  <strong>{item.songs}</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <h3>Songs in Cluster</h3>
            <SongTable songs={songs} />
          </div>
        </>
      )}
    </section>
  );
}
