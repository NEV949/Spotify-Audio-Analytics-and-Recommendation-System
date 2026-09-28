import React from "react";
export default function FilterPanel({
  genre,
  setGenre,
  minPopularity,
  setMinPopularity,
  maxPopularity,
  setMaxPopularity,
  genres
}) {
  return (
    <div className="filters">
      <select value={genre} onChange={(e) => setGenre(e.target.value)}>
        <option value="">All genres</option>
        {genres.map((item) => (
          <option key={item}>{item}</option>
        ))}
      </select>

      <input
        type="number"
        min="0"
        max="100"
        placeholder="Min popularity"
        value={minPopularity}
        onChange={(e) => setMinPopularity(e.target.value)}
      />

      <input
        type="number"
        min="0"
        max="100"
        placeholder="Max popularity"
        value={maxPopularity}
        onChange={(e) => setMaxPopularity(e.target.value)}
      />
    </div>
  );
}
