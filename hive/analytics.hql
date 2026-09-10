-- KPI / aggregation queries used by FastAPI. Hive is the SQL analytics layer.

-- kpis
SELECT
  COUNT(*) AS tracks,
  COUNT(DISTINCT artists) AS artists,
  COUNT(DISTINCT track_genre) AS genres,
  COUNT(DISTINCT cluster) AS clusters,
  AVG(popularity) AS avg_popularity,
  AVG(danceability) AS avg_danceability,
  AVG(energy) AS avg_energy,
  AVG(valence) AS avg_valence
FROM spotify.songs_clustered;

-- top_tracks
SELECT track_id, track_name, artists, album_name, track_genre, popularity, cluster,
       danceability, energy, loudness, acousticness, valence, tempo, speechiness, instrumentalness, liveness
FROM spotify.songs_clustered
ORDER BY popularity DESC
LIMIT 10;

-- top_artists
SELECT artists AS artist, COUNT(*) AS tracks, AVG(popularity) AS avg_popularity
FROM spotify.songs_clustered
GROUP BY artists
ORDER BY tracks DESC, avg_popularity DESC
LIMIT 10;

-- genres
SELECT
  track_genre AS genre,
  COUNT(*) AS tracks,
  AVG(popularity) AS avg_popularity,
  AVG(danceability) AS avg_danceability,
  AVG(energy) AS avg_energy,
  AVG(loudness) AS avg_loudness,
  AVG(acousticness) AS avg_acousticness,
  AVG(valence) AS avg_valence,
  AVG(tempo) AS avg_tempo
FROM spotify.songs_clustered
GROUP BY track_genre
ORDER BY tracks DESC
LIMIT 15;
