import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import ErrorState from "./ErrorState.jsx";
import LoadingState from "./LoadingState.jsx";

function Kpi({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
      <p className="text-xs uppercase tracking-wide text-spotify-muted">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </div>
  );
}

export default function AnalyticsOverview() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.summary().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Loading catalog KPIs" />;

  const { kpis, top_tracks: topTracks, top_artists: topArtists, genres, query_engine: engine } = data;

  return (
    <div className="space-y-8">
      <p className="text-sm text-spotify-muted">
        Query engine:{" "}
        <span className="font-medium text-spotify-green">
          {engine === "hive" ? "Hive SQL" : "in-memory catalog (fast)"}
        </span>
      </p>
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Tracks" value={kpis.tracks.toLocaleString()} />
        <Kpi label="Artists" value={kpis.artists.toLocaleString()} />
        <Kpi label="Genres" value={kpis.genres.toLocaleString()} />
        <Kpi label="Avg popularity" value={kpis.avg_popularity} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-4 text-lg font-semibold">Genre distribution</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={genres} layout="vertical" margin={{ left: 24, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis type="number" stroke="#a1a1aa" />
                <YAxis type="category" dataKey="genre" width={110} stroke="#a1a1aa" />
                <Tooltip
                  contentStyle={{ background: "#16161d", border: "1px solid #27272a" }}
                />
                <Bar dataKey="tracks" fill="#1DB954" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-4 text-lg font-semibold">Top artists by catalog size</h2>
          <div className="space-y-3">
            {topArtists.map((artist) => (
              <div key={artist.artist} className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium">{artist.artist}</p>
                  <p className="text-sm text-spotify-muted">avg popularity {artist.avg_popularity}</p>
                </div>
                <span className="rounded-full bg-white/10 px-3 py-1 text-sm">{artist.tracks} tracks</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="mb-2 text-lg font-semibold">Genre audio profile</h2>
        <p className="mb-4 text-sm text-spotify-muted">
          Average danceability, energy, acousticness, and valence by genre.
        </p>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={genres} margin={{ left: 8, right: 8, bottom: 48 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis dataKey="genre" stroke="#a1a1aa" interval={0} angle={-35} textAnchor="end" height={70} />
              <YAxis stroke="#a1a1aa" domain={[0, 1]} />
              <Tooltip contentStyle={{ background: "#16161d", border: "1px solid #27272a" }} />
              <Legend />
              <Bar dataKey="avg_danceability" name="danceability" fill="#1DB954" />
              <Bar dataKey="avg_energy" name="energy" fill="#60a5fa" />
              <Bar dataKey="avg_acousticness" name="acousticness" fill="#fbbf24" />
              <Bar dataKey="avg_valence" name="valence" fill="#f472b6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="mb-4 text-lg font-semibold">Top tracks by popularity</h2>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-spotify-muted">
              <tr>
                <th className="pb-3 font-medium">Track</th>
                <th className="pb-3 font-medium">Artist</th>
                <th className="pb-3 font-medium">Genre</th>
                <th className="pb-3 font-medium">Cluster</th>
                <th className="pb-3 font-medium">Popularity</th>
              </tr>
            </thead>
            <tbody>
              {topTracks.map((track) => (
                <tr key={track.track_id} className="border-t border-white/5">
                  <td className="py-3">{track.track_name}</td>
                  <td className="py-3 text-spotify-muted">{track.artists}</td>
                  <td className="py-3">{track.genre}</td>
                  <td className="py-3">{track.cluster}</td>
                  <td className="py-3">{track.popularity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
