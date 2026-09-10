import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import ErrorState from "./ErrorState.jsx";
import LoadingState from "./LoadingState.jsx";

const COLORS = ["#1DB954", "#60a5fa", "#f472b6", "#fbbf24", "#a78bfa", "#34d399", "#fb7185", "#38bdf8"];

export default function ClusterExplorer() {
  const [data, setData] = useState(null);
  const [scatter, setScatter] = useState(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(0);

  useEffect(() => {
    Promise.all([api.clusters(), api.scatter("energy", "danceability")])
      .then(([payload, points]) => {
        setData(payload);
        setScatter(points);
        if (payload.clusters?.length) setSelected(payload.clusters[0].id);
      })
      .catch((err) => setError(err.message));
  }, []);

  const cluster = useMemo(
    () => data?.clusters.find((item) => item.id === selected) || data?.clusters[0],
    [data, selected]
  );

  const radarRows = useMemo(() => {
    if (!data) return [];
    const rows = data.features.map((feature) => ({ feature }));
    data.clusters.forEach((item) => {
      item.radar.forEach((point) => {
        const row = rows.find((r) => r.feature === point.feature);
        if (row) row[`c${item.id}`] = point.value;
      });
    });
    return rows;
  }, [data]);

  if (error) return <ErrorState message={error} />;
  if (!data || !cluster) return <LoadingState label="Loading K-Means clusters" />;

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {data.clusters.map((item, index) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setSelected(item.id)}
            className={`rounded-2xl border p-4 text-left transition ${
              selected === item.id
                ? "border-spotify-green bg-spotify-green/10"
                : "border-white/10 bg-spotify-card hover:border-white/20"
            }`}
          >
            <p className="text-xs text-spotify-muted">Cluster {item.id}</p>
            <p className="mt-1 font-semibold" style={{ color: COLORS[index % COLORS.length] }}>
              {item.label}
            </p>
            <p className="mt-2 text-sm text-spotify-muted">
              {item.size.toLocaleString()} tracks · {(item.share * 100).toFixed(1)}%
            </p>
          </button>
        ))}
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-2 text-lg font-semibold">Radar: {cluster.label}</h2>
          <p className="mb-4 text-sm text-spotify-muted">
            Values are min-max scaled per feature so loudness and tempo sit on the same 0–1 ring.
          </p>
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={cluster.radar}>
                <PolarGrid stroke="#3f3f46" />
                <PolarAngleAxis dataKey="feature" tick={{ fill: "#a1a1aa", fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
                <Radar
                  name={cluster.label}
                  dataKey="value"
                  stroke={COLORS[selected % COLORS.length]}
                  fill={COLORS[selected % COLORS.length]}
                  fillOpacity={0.35}
                />
                <Tooltip contentStyle={{ background: "#16161d", border: "1px solid #27272a" }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-2 text-lg font-semibold">All clusters overlay</h2>
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarRows}>
                <PolarGrid stroke="#3f3f46" />
                <PolarAngleAxis dataKey="feature" tick={{ fill: "#a1a1aa", fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
                {data.clusters.map((item, index) => (
                  <Radar
                    key={item.id}
                    name={`C${item.id}`}
                    dataKey={`c${item.id}`}
                    stroke={COLORS[index % COLORS.length]}
                    fill={COLORS[index % COLORS.length]}
                    fillOpacity={selected === item.id ? 0.28 : 0.04}
                    strokeWidth={selected === item.id ? 2.5 : 1}
                  />
                ))}
                <Legend />
                <Tooltip contentStyle={{ background: "#16161d", border: "1px solid #27272a" }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-4 text-lg font-semibold">Centroid means</h2>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(cluster.means).map(([feature, value]) => (
              <div key={feature} className="rounded-xl bg-white/5 px-3 py-2">
                <dt className="text-spotify-muted">{feature}</dt>
                <dd className="font-medium">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-4 text-lg font-semibold">Representative tracks</h2>
          <div className="space-y-3">
            {cluster.top_tracks.map((track) => (
              <div key={track.track_id} className="rounded-xl bg-white/5 px-4 py-3">
                <p className="font-medium">{track.track_name}</p>
                <p className="text-sm text-spotify-muted">
                  {track.artists} · popularity {track.popularity}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {scatter?.points && (
        <section className="rounded-2xl border border-white/10 bg-spotify-card p-5">
          <h2 className="mb-2 text-lg font-semibold">Energy vs danceability</h2>
          <p className="mb-4 text-sm text-spotify-muted">Sample of tracks colored by K-Means cluster.</p>
          <div className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis type="number" dataKey="x" name="energy" stroke="#a1a1aa" domain={[0, 1]} />
                <YAxis type="number" dataKey="y" name="danceability" stroke="#a1a1aa" domain={[0, 1]} />
                <Tooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  contentStyle={{ background: "#16161d", border: "1px solid #27272a" }}
                  formatter={(value, name, props) => [value, name]}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.track_name || ""}
                />
                <Legend />
                {data.clusters.map((item, index) => (
                  <Scatter
                    key={item.id}
                    name={`C${item.id}`}
                    data={scatter.points.filter((p) => p.cluster === item.id)}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}
    </div>
  );
}
