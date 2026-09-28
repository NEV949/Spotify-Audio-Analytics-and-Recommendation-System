from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_loader import get_dataframe, reload_data
import analytics
import song_explorer
import genre_analytics
import artist_analytics
import popularity_analysis
import cluster_analysis
import mood_analysis
import correlation_analysis
import recommender

app = FastAPI(
    title="Spotify Big Data Analytics API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {
        "message": "Spotify Big Data Analytics API",
        "status": "running"
    }

@app.get("/health")
def health():
    try:
        df = get_dataframe()
        return {
            "status": "healthy",
            "rows": int(len(df)),
            "columns": int(len(df.columns))
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc)
        }

@app.post("/reload")
def reload():
    df = reload_data()
    return {"message": "Dataset reloaded", "rows": int(len(df))}

@app.get("/dashboard")
def dashboard():
    return analytics.overview(get_dataframe())

@app.get("/dashboard/distributions")
def distributions():
    return analytics.feature_distributions(get_dataframe())

@app.get("/genres")
def genres():
    return genre_analytics.genre_list(get_dataframe())

@app.get("/genres/statistics")
def genre_statistics():
    return genre_analytics.statistics(get_dataframe())

@app.get("/genres/{genre}")
def genre_detail(genre: str):
    result = genre_analytics.genre_detail(get_dataframe(), genre)
    if result is None:
        raise HTTPException(404, "Genre not found")
    return result

@app.get("/songs")
def songs(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    min_popularity: Optional[int] = Query(None, ge=0, le=100),
    max_popularity: Optional[int] = Query(None, ge=0, le=100),
    cluster: Optional[int] = None,
    sort_by: str = "popularity",
    descending: bool = True,
    limit: int = Query(100, ge=1, le=500)
):
    return song_explorer.search_songs(
        get_dataframe(),
        query,
        genre,
        min_popularity,
        max_popularity,
        cluster,
        sort_by,
        descending,
        limit
    )

@app.get("/songs/{track_id}")
def song_detail(track_id: str):
    result = song_explorer.song_detail(
        get_dataframe(), track_id
    )
    if result is None:
        raise HTTPException(404, "Song not found")
    return result

@app.get("/artists")
def artists(
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    return artist_analytics.search_artists(
        get_dataframe(), query or "", limit
    )

@app.get("/artists/{artist}")
def artist_detail(artist: str):
    result = artist_analytics.artist_detail(
        get_dataframe(), artist
    )
    if result is None:
        raise HTTPException(404, "Artist not found")
    return result

@app.get("/popularity")
def popularity():
    df = get_dataframe()
    return {
        "statistics": popularity_analysis.statistics(df),
        "relationships": popularity_analysis.relationships(df)
    }

@app.get("/popularity/{feature}")
def popularity_feature(feature: str):
    try:
        return popularity_analysis.vs_feature(
            get_dataframe(), feature
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))

@app.get("/clusters")
def clusters():
    return cluster_analysis.summary(get_dataframe())

@app.get("/clusters/{cluster_id}")
def cluster_detail(cluster_id: int):
    result = cluster_analysis.detail(
        get_dataframe(), cluster_id
    )
    if result is None:
        raise HTTPException(404, "Cluster not found")
    return result

@app.get("/clusters/{cluster_id}/songs")
def cluster_songs(
    cluster_id: int,
    limit: int = Query(50, ge=1, le=200)
):
    return cluster_analysis.songs(
        get_dataframe(), cluster_id, limit
    )

@app.get("/moods")
def moods():
    return mood_analysis.distribution(get_dataframe())

@app.get("/moods/points")
def mood_points():
    return mood_analysis.points(get_dataframe())

@app.get("/moods/{mood:path}/songs")
def mood_songs(
    mood: str,
    limit: int = Query(50, ge=1, le=200)
):
    return mood_analysis.songs_by_mood(
        get_dataframe(), mood, limit
    )

@app.get("/correlations")
def correlations():
    return correlation_analysis.matrix(get_dataframe())

@app.get("/recommend/{track_id}")
def recommend(
    track_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    result = recommender.recommend(
        get_dataframe(), track_id, limit
    )
    if result is None:
        raise HTTPException(404, "Song not found")
    return result
