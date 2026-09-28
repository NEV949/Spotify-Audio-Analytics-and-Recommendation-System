const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {}
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  dashboard: () => request("/dashboard"),
  distributions: () => request("/dashboard/distributions"),

  genres: () => request("/genres"),
  genreStatistics: () => request("/genres/statistics"),
  genreDetail: (genre) =>
    request(`/genres/${encodeURIComponent(genre)}`),

  songs: (params = {}) => {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, value);
      }
    });

    return request(`/songs?${query.toString()}`);
  },

  songDetail: (id) =>
    request(`/songs/${encodeURIComponent(id)}`),

  artists: (query = "") =>
    request(`/artists?query=${encodeURIComponent(query)}`),

  artistDetail: (artist) =>
    request(`/artists/${encodeURIComponent(artist)}`),

  popularity: () => request("/popularity"),

  popularityFeature: (feature) =>
    request(`/popularity/${encodeURIComponent(feature)}`),

  clusters: () => request("/clusters"),

  clusterDetail: (id) =>
    request(`/clusters/${id}`),

  clusterSongs: (id) =>
    request(`/clusters/${id}/songs`),

  moods: () => request("/moods"),
  moodPoints: () => request("/moods/points"),

  moodSongs: (mood) =>
    request(`/moods/${encodeURIComponent(mood)}/songs`),

  correlations: () => request("/correlations"),

  recommend: (id, limit = 10) =>
    request(`/recommend/${encodeURIComponent(id)}?limit=${limit}`),

  health: () => request("/health")
};
