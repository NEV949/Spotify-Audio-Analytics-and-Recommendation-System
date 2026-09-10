import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import ErrorState from "./ErrorState.jsx";
import LoadingState from "./LoadingState.jsx";

function cellColor(value) {
  const t = (value + 1) / 2;
  const r = Math.round(24 + (29 - 24) * t + (220 - 24) * (1 - t) * 0.35);
  const g = Math.round(24 + 185 * t);
  const b = Math.round(24 + 84 * t);
  return `rgb(${r}, ${g}, ${b})`;
}

export default function Correlations() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.correlations().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!data) return <LoadingState label="Computing Pearson correlations" />;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">Audio feature correlation matrix</h2>
            <p className="text-sm text-spotify-muted">Pearson r across audio features and popularity.</p>
          </div>
          <p className="text-xs text-spotify-muted">Green = positive · Dark = negative</p>
        </div>
        <div className="overflow-x-auto">
          <table className="border-separate border-spacing-1">
            <thead>
              <tr>
                <th />
                {data.features.map((feature) => (
                  <th key={feature} className="px-1 pb-2 text-xs font-medium text-spotify-muted">
                    <span className="inline-block origin-bottom -rotate-45">{feature}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.features.map((rowName, i) => (
                <tr key={rowName}>
                  <th className="pr-3 text-right text-xs font-medium text-spotify-muted">{rowName}</th>
                  {data.matrix[i].map((value, j) => (
                    <td
                      key={`${rowName}-${data.features[j]}`}
                      title={`${rowName} × ${data.features[j]}: ${value}`}
                      className="h-14 w-14 rounded-md text-center text-xs font-semibold text-black"
                      style={{ background: cellColor(value) }}
                    >
                      {value.toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="mb-2 text-lg font-semibold">Features vs popularity</h2>
        <p className="mb-4 text-sm text-spotify-muted">
          Which audio traits move with track popularity in this catalog.
        </p>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.vs_popularity || []} layout="vertical" margin={{ left: 24, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis type="number" domain={[-1, 1]} stroke="#a1a1aa" />
              <YAxis type="category" dataKey="feature" width={120} stroke="#a1a1aa" />
              <Tooltip contentStyle={{ background: "#16161d", border: "1px solid #27272a" }} />
              <Bar dataKey="value" fill="#60a5fa" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="mb-4 text-lg font-semibold">Strongest relationships</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {data.pairs.slice(0, 8).map((pair) => (
            <div key={`${pair.x}-${pair.y}`} className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
              <p className="text-sm">
                {pair.x} <span className="text-spotify-muted">×</span> {pair.y}
              </p>
              <span className={pair.value >= 0 ? "text-spotify-green" : "text-rose-400"}>
                {pair.value > 0 ? "+" : ""}
                {pair.value.toFixed(3)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
