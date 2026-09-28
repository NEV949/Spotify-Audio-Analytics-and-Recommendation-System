import React from "react";
import { useEffect, useState } from "react";
import { api } from "../api";
import SearchBar from "./SearchBar";
import FilterPanel from "./FilterPanel";
import SongTable from "./SongTable";
import SongDetails from "./SongDetails";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";

export default function SongExplorer() {
  const [query, setQuery] = useState("");
  const [genre, setGenre] = useState("");
  const [minPopularity, setMinPopularity] = useState("");
  const [maxPopularity, setMaxPopularity] = useState("");
  const [genres, setGenres] = useState([]);
  const [songs, setSongs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.genres().then(setGenres).catch(setError);
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);

      try {
        const result = await api.songs({
          query,
          genre,
          min_popularity: minPopularity,
          max_popularity: maxPopularity,
          limit: 100
        });

        setSongs(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query, genre, minPopularity, maxPopularity]);

  async function selectSong(song) {
    try {
      setSelected(await api.songDetail(song.track_id));
    } catch (err) {
      setError(err);
    }
  }

  if (error) return <ErrorState error={error} />;

  return (
    <section>
      <h2>Song Explorer</h2>

      <SearchBar
        value={query}
        onChange={setQuery}
        placeholder="Search song or artist..."
      />

      <FilterPanel
        genre={genre}
        setGenre={setGenre}
        minPopularity={minPopularity}
        setMinPopularity={setMinPopularity}
        maxPopularity={maxPopularity}
        setMaxPopularity={setMaxPopularity}
        genres={genres}
      />

      {loading ? (
        <LoadingState />
      ) : (
        <SongTable songs={songs} onSelect={selectSong} />
      )}

      {selected && (
        <SongDetails
          song={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </section>
  );
}
