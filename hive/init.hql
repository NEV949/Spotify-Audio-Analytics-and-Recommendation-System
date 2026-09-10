CREATE DATABASE IF NOT EXISTS spotify;

CREATE EXTERNAL TABLE IF NOT EXISTS spotify.songs_clustered (
  track_id STRING,
  track_name STRING,
  artists STRING,
  album_name STRING,
  track_genre STRING,
  popularity DOUBLE,
  danceability DOUBLE,
  energy DOUBLE,
  loudness DOUBLE,
  acousticness DOUBLE,
  valence DOUBLE,
  tempo DOUBLE,
  speechiness DOUBLE,
  instrumentalness DOUBLE,
  liveness DOUBLE,
  cluster INT
)
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/spotify/processed/songs_clustered';
