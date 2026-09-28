import React from "react";
import AudioFeatureChart from "./AudioFeatureChart";

export default function SongDetails({ song, onClose }) {
  const features = {
    danceability: song.danceability,
    energy: song.energy,
    loudness: song.loudness,
    acousticness: song.acousticness,
    valence: song.valence,
    tempo: song.tempo,
    speechiness: song.speechiness,
    instrumentalness: song.instrumentalness,
    liveness: song.liveness
  };

  return (
    <div className="panel">
      <div className="detail-header">
        <div>
          <h3>{song.track_name}</h3>
          <p>{song.artists} • {song.album_name}</p>
        </div>
        <button onClick={onClose}>Close</button>
      </div>

      <div className="stats">
        <Stat label="Popularity" value={song.popularity} />
        <Stat label="Genre" value={song.track_genre} />
        <Stat label="Cluster" value={song.cluster} />
      </div>

      <h4>Audio Features</h4>
      <AudioFeatureChart features={features} />
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="mini-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
