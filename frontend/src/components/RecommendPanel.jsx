import React from "react";
import { useState } from "react";
import { api } from "../api";
import SearchBar from "./SearchBar";
import ErrorState from "./ErrorState";

export default function RecommendPanel() {
  const [query, setQuery] = useState("");
  const [songs, setSongs] = useState([]);
  const [selectedSong, setSelectedSong] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function search(value) {
    setQuery(value);
    setError(null);

    // Clear everything when the search box is empty
    if (!value.trim()) {
      setSongs([]);
      setSelectedSong(null);
      setResult(null);
      return;
    }

    try {
      const results = await api.songs({
        query: value,
        limit: 20
      });

      setSongs(results);
    } catch (err) {
      setError(err);
      setSongs([]);
    }
  }

  async function selectSong(song) {
    // Store selected song
    setSelectedSong(song);

    // Remove search suggestions
    setSongs([]);

    // Remove previous recommendations
    setResult(null);

    // Generate recommendations immediately
    setLoading(true);
    setError(null);

    try {
      const recommendationResult = await api.recommend(
        song.track_id,
        10
      );

      setResult(recommendationResult);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  if (error) {
    return <ErrorState error={error} />;
  }

  return (
    <section>
      <h2>Song Recommendations</h2>

      <p className="muted">
        Audio-feature similarity is the main factor, with cluster
        and popularity similarity used as additional signals.
      </p>

      <SearchBar
        value={query}
        onChange={search}
        placeholder="Search for a song, artist, or genre..."
      />

      {/* Search suggestions */}
      {songs.map((song) => (
        <button
          key={song.track_id}
          className="result-button"
          onClick={() => selectSong(song)}
        >
          <span>
            <strong>{song.track_name}</strong>
            <small>{song.artists}</small>
          </span>

          <span>
            Cluster {song.cluster}
          </span>
        </button>
      ))}

      {selectedSong && (
  <div className="panel">
    <h3>Selected Song</h3>

    <div className="selected-song">
      <div className="selected-song-info">
        <strong className="selected-song-title">
          {selectedSong.track_name}
        </strong>

        <small>
          {selectedSong.artists}
        </small>

        <small>
          {selectedSong.track_genre}
        </small>
      </div>

      <div className="selected-song-cluster">
        Cluster {selectedSong.cluster}
      </div>
    </div>

    {loading && (
      <p className="muted">
        Finding recommendations...
      </p>
    )}
  </div>
)}

      {/* Recommendations */}
      {result && (
        <div className="panel">
          <h3>
            Recommendations for {result.seed.track_name}
          </h3>

          <p>
            Cluster: <strong>{result.cluster}</strong>
          </p>

          {result.recommendations.map((song, index) => (
            <div
              className="recommendation"
              key={song.track_id}
            >
              {/* Rank */}
              <div className="recommendation-rank">
                #{index + 1}
              </div>

              {/* Song information */}
              <div className="recommendation-info">
                <strong className="recommendation-title">
                  {song.track_name}
                </strong>

                <small>
                  {song.artists}
                </small>

                <small>
                  {song.track_genre}
                </small>
              </div>

              {/* Similarity */}
              <div className="recommendation-score">
                <span>Similarity</span>

                <strong>
                  {(song.similarity * 100).toFixed(2)}%
                </strong>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}