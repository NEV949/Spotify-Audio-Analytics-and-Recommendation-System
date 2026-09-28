import React from "react";
import { useState } from "react";
import { api } from "../api";
import SearchBar from "./SearchBar";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import AudioFeatureChart from "./AudioFeatureChart";

export default function ArtistAnalytics() {
  const [query, setQuery] = useState("");
  const [artists, setArtists] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function search(value) {
    setQuery(value);
    setError(null);

    // Clear everything when search box is empty
    if (!value.trim()) {
      setArtists([]);
      setSelected(null);
      setLoading(false);
      return;
    }

    setLoading(true);

    try {
      const results = await api.artists(value);

      setArtists(results);
      setSelected(null);
    } catch (err) {
      setError(err);
      setArtists([]);
      setSelected(null);
    } finally {
      setLoading(false);
    }
  }

  async function selectArtist(artist) {
    setError(null);
    setLoading(true);

    try {
      const result = await api.artistDetail(artist);

      setSelected(result);
      setArtists([]);

      // Keep the selected artist in the search box
      setQuery(artist);
    } catch (err) {
      setError(err);
      setSelected(null);
    } finally {
      setLoading(false);
    }
  }

  function clearSelection() {
    setQuery("");
    setArtists([]);
    setSelected(null);
    setError(null);
  }

  if (error) {
    return <ErrorState error={error} />;
  }

  return (
    <section>
      <h2>Artist Analytics</h2>

      <SearchBar
        value={query}
        onChange={search}
        placeholder="Search artist..."
      />

      {/* Loading */}
      {loading && !selected && <LoadingState />}

      {/* Artist search results */}
      {!loading && !selected && artists.length > 0 && (
        <div className="artist-results">
          {artists.map((item) => (
            <button
              key={item.artist}
              className="result-button"
              onClick={() => selectArtist(item.artist)}
            >
              <span>
                <strong>{item.artist}</strong>
              </span>

              <span>
                {item.songs} songs
              </span>
            </button>
          ))}
        </div>
      )}

      {/* No search results */}
      {!loading &&
        !selected &&
        query.trim() &&
        artists.length === 0 && (
          <p className="muted">
            No artists found.
          </p>
        )}

      {/* Selected artist analytics */}
      {selected && (
        <div className="grid">

          {/* Artist information */}
          <div className="panel">
            <h3>{selected.artist}</h3>

            <p>
              Songs: <strong>{selected.songs}</strong>
            </p>

            <p>
              Average popularity:{" "}
              <strong>
                {selected.average_popularity}
              </strong>
            </p>

            <h4>Audio Profile</h4>

            <AudioFeatureChart
              features={selected.average_features}
            />

            <button onClick={clearSelection}>
              Back
            </button>
          </div>

          {/* Most popular songs */}
          <div className="panel">
            <h3>Most Popular Songs</h3>

            {selected.top_songs.map((song) => (
              <div
                className="list-row"
                key={song.track_id}
              >
                <span>
                  {song.track_name}
                </span>

                <strong>
                  {song.popularity}
                </strong>
              </div>
            ))}
          </div>

        </div>
      )}
    </section>
  );
}