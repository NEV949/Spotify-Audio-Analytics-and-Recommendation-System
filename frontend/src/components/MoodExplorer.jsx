import React from "react";

import { useEffect, useState } from "react";
import { api } from "../api";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import SongTable from "./SongTable";

const moods = [
  "Happy / Energetic",
  "Intense / Melancholic",
  "Calm / Positive",
  "Sad / Calm"
];

export default function MoodExplorer() {
  const [points, setPoints] = useState([]);
  const [songs, setSongs] = useState([]);
  const [selectedMood, setSelectedMood] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    api.moodPoints().then(setPoints).catch(setError);
  }, []);

  async function chooseMood(mood) {
    setSelectedMood(mood);

    try {
      setSongs(await api.moodSongs(mood));
    } catch (err) {
      setError(err);
    }
  }

  if (error) return <ErrorState error={error} />;
  if (!points.length) return <LoadingState />;

  return (
    <section>
      <h2>Mood Explorer</h2>
      <p className="muted">
        Mood regions are derived from energy and valence.
      </p>

      <div className="mood-buttons">
        {moods.map((mood) => (
          <button
            key={mood}
            className={selectedMood === mood ? "active" : ""}
            onClick={() => chooseMood(mood)}
          >
            {mood}
          </button>
        ))}
      </div>

      <div className="mood-map">
        {points.map((point, index) => (
          <span
            className="mood-dot"
            key={index}
            title={`${point.track_name} — ${point.artists}`}
            style={{
              left: `${point.valence * 100}%`,
              bottom: `${point.energy * 100}%`
            }}
          />
        ))}

        <span className="axis x">Valence →</span>
        <span className="axis y">Energy ↑</span>
      </div>

      {selectedMood && (
        <div className="panel">
          <h3>{selectedMood}</h3>
          <SongTable songs={songs} />
        </div>
      )}
    </section>
  );
}
