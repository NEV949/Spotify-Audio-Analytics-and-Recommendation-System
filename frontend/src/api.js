const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }
  return response.json();
}

export const api = {
  summary: () => request("/api/analytics/summary"),
  correlations: () => request("/api/analytics/correlations"),
  scatter: (x = "energy", y = "danceability") =>
    request(`/api/analytics/scatter?x=${encodeURIComponent(x)}&y=${encodeURIComponent(y)}`),
  clusters: () => request("/api/clusters"),
  search: (query) => request(`/api/songs/search?query=${encodeURIComponent(query)}`),
  song: (trackId) => request(`/api/songs/${encodeURIComponent(trackId)}`),
  recommend: (trackId, topN = 10) =>
    request("/api/recommend", {
      method: "POST",
      body: JSON.stringify({ track_id: trackId, top_n: topN }),
    }),
};
