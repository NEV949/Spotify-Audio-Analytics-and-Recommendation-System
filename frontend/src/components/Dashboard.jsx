import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import StatCard from "./StatCard";
import AudioFeatureChart from "./AudioFeatureChart";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.dashboard().then(setData).catch(setError);
  }, []);

  if (error) return <ErrorState error={error} />;
  if (!data) return <LoadingState />;

  return (
    <section>
      <h2>Dataset Overview</h2>

      <div className="stats">
        <StatCard
          label="Songs"
          value={data.total_songs.toLocaleString()}
        />

        <StatCard
          label="Artists"
          value={data.total_artists.toLocaleString()}
        />

        <StatCard
          label="Genres"
          value={data.total_genres.toLocaleString()}
        />

        <StatCard
          label="Average Popularity"
          value={data.average_popularity}
        />
      </div>

      <div className="grid">

        {/* Average Audio Features */}
        <div className="panel">
          <h3>Average Audio Features</h3>

          <AudioFeatureChart
            features={data.average_features}
          />
        </div>


        {/* Processing Pipeline */}
        <div className="panel pipeline-panel">

          <div className="pipeline-header">
            <div>
              <h3>Processing Pipeline</h3>

              <p>
                From raw Spotify data to interactive analytics
              </p>
            </div>

            <span className="pipeline-live">
              ● LIVE PIPELINE
            </span>
          </div>


          <div className="pipeline-diagram">

            {/* Spotify Dataset */}
            <div className="pipeline-node source-node">
              <div className="pipeline-icon">
                ♫
              </div>

              <div>
                <strong>Spotify Dataset</strong>

                <span>
                  {data.total_songs.toLocaleString()} songs
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* PySpark */}
            <div className="pipeline-node">
              <div className="pipeline-icon">
                ⚙
              </div>

              <div>
                <strong>PySpark</strong>

                <span>
                  Data Processing
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* StandardScaler */}
            <div className="pipeline-node">
              <div className="pipeline-icon">
                ↕
              </div>

              <div>
                <strong>StandardScaler</strong>

                <span>
                  Feature Scaling
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* K-Means */}
            <div className="pipeline-node highlight-node">
              <div className="pipeline-icon">
                ◎
              </div>

              <div>
                <strong>K-Means</strong>

                <span>
                  6 Song Clusters
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* Parquet */}
            <div className="pipeline-node">
              <div className="pipeline-icon">
                ▣
              </div>

              <div>
                <strong>Parquet</strong>

                <span>
                  Processed Dataset
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* HDFS */}
            <div className="pipeline-node storage-node">
              <div className="pipeline-icon">
                ⬡
              </div>

              <div>
                <strong>HDFS</strong>

                <span>
                  Distributed Storage
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* FastAPI */}
            <div className="pipeline-node api-node">
              <div className="pipeline-icon">
                ⚡
              </div>

              <div>
                <strong>FastAPI</strong>

                <span>
                  Analytics & Recommendation API
                </span>
              </div>
            </div>


            <div className="pipeline-arrow">
              ↓
            </div>


            {/* React */}
            <div className="pipeline-node frontend-node">
              <div className="pipeline-icon">
                ▤
              </div>

              <div>
                <strong>React Dashboard</strong>

                <span>
                  Interactive Visualization
                </span>
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}