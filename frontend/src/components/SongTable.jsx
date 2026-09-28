import React from "react";
export default function SongTable({ songs = [], onSelect }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Song</th>
            <th>Artist</th>
            <th>Genre</th>
            <th>Popularity</th>
            <th>Cluster</th>
          </tr>
        </thead>

        <tbody>
          {songs.map((song) => (
            <tr
              key={song.track_id}
              onClick={() => onSelect?.(song)}
              className={onSelect ? "clickable" : ""}
            >
              <td>{song.track_name}</td>
              <td>{song.artists}</td>
              <td>{song.track_genre}</td>
              <td>{song.popularity}</td>
              <td>{song.cluster}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
