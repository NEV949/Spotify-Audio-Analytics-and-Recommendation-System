import { useState } from "react";
import { api } from "../api";

export default function RecommendPanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [seed, setSeed] = useState(null);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSearch(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const payload = await api.search(query);
      setResults(payload.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function recommendFrom(track) {
    setError("");
    setLoading(true);

    try {
      const payload = await api.recommend(track.track_id);
      setSeed(payload.seed);
      setRecs(payload.recommendations);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <section className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="text-lg font-semibold">Song search</h2>

        <p className="mb-4 text-sm text-spotify-muted">
          Match on track title or artist, then generate neighbors.
        </p>

        <form onSubmit={runSearch} className="mb-5 flex gap-2">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="e.g. Blinding Lights, Drake, lo-fi"
            className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3 outline-none ring-spotify-green focus:ring-2"
          />

          <button
            type="submit"
            className="rounded-xl bg-spotify-green px-5 py-3 font-semibold text-black disabled:opacity-60"
            disabled={loading}
          >
            Search
          </button>
        </form>

        {error && (
          <p className="mb-4 text-sm text-rose-400">
            {error}
          </p>
        )}

        <div className="space-y-2">
          {results.map((track) => (
            <button
              key={track.track_id}
              type="button"
              onClick={() => recommendFrom(track)}
              className="w-full rounded-xl bg-white/5 px-4 py-3 text-left hover:bg-white/10"
            >
              <p className="font-medium">
                {track.track_name}
              </p>

              <p className="text-sm text-spotify-muted">
                {track.artists} · {track.genre} · cluster {track.cluster}
              </p>
            </button>
          ))}

          {!results.length && !loading && (
            <p className="text-sm text-spotify-muted">
              Search for a song to start recommendations.
            </p>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-spotify-card p-5">
        <h2 className="text-lg font-semibold">
          Recommended Songs
        </h2>

        <p className="mb-4 text-sm text-spotify-muted">
          Songs recommended based on audio-feature similarity.
        </p>

        {seed ? (
          <div className="mb-4 rounded-xl border border-spotify-green/40 bg-spotify-green/10 px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-spotify-green">
              Song details
            </p>

            <p className="font-semibold">
              {seed.track_name}
            </p>

            <p className="text-sm text-spotify-muted">
              {seed.artists} · {seed.genre} · cluster {seed.cluster} · popularity{" "}
              {seed.popularity}
            </p>

            {seed.album_name && (
              <p className="text-sm text-spotify-muted">
                Album: {seed.album_name}
              </p>
            )}

            <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
              {Object.entries(seed.features || {}).map(
                ([feature, value]) => (
                  <div
                    key={feature}
                    className="rounded-lg bg-black/30 px-2 py-1"
                  >
                    <dt className="text-spotify-muted">
                      {feature}
                    </dt>

                    <dd className="font-medium">
                      {Number(value).toFixed(3)}
                    </dd>
                  </div>
                )
              )}
            </dl>
          </div>
        ) : (
          <p className="mb-4 text-sm text-spotify-muted">
            Pick a search result to rank the nearest 10 tracks.
          </p>
        )}

        <div className="space-y-2">
          {recs.map((track, index) => (
            <div
              key={track.track_id}
              className="rounded-xl bg-white/5 px-4 py-3"
            >
              <p className="font-medium">
                {index + 1}. {track.track_name}
              </p>

              <p className="text-sm text-spotify-muted">
                {track.artists} · cluster {track.cluster}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
