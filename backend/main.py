"""Spotify clustered-catalog API: analytics, search, and cosine recommendations."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from analytics import (
    clusters_payload,
    correlation_payload,
    recommend_tracks,
    scatter_payload,
    search_tracks,
    song_detail,
    summary_payload,
)
from data_loader import AUDIO_FEATURES, get_store
from hive_client import hive_status


class RecommendRequest(BaseModel):
    track_id: str = Field(..., min_length=1)
    top_n: int = Field(default=10, ge=1, le=50)


def _catalog_or_503():
    try:
        return get_store()
    except Exception as exc:  # noqa: BLE001
        get_store.cache_clear()
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        get_store()
    except Exception:
        get_store.cache_clear()
    yield


app = FastAPI(
    title="Spotify Cluster Analytics API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/api/health")
def health() -> dict:
    try:
        store = get_store()
        return {
            "ok": True,
            "tracks": int(len(store["catalog"])),
            "features": AUDIO_FEATURES,
            "source_columns": store["source_columns"],
            "hive": hive_status(),
        }
    except Exception as exc:  # noqa: BLE001
        get_store.cache_clear()
        return {"ok": False, "error": str(exc)}


@app.get("/api/analytics/summary")
def analytics_summary(engine: str = Query(default="pandas")) -> dict:
    chosen = engine if engine in {"pandas", "hive"} else "pandas"
    return summary_payload(_catalog_or_503()["catalog"], engine=chosen)


@app.get("/api/analytics/correlations")
def analytics_correlations() -> dict:
    return correlation_payload(_catalog_or_503()["catalog"])


@app.get("/api/analytics/scatter")
def analytics_scatter(
    x: str = Query(default="energy"),
    y: str = Query(default="danceability"),
    limit: int = Query(default=800, ge=50, le=4000),
) -> dict:
    try:
        return scatter_payload(_catalog_or_503()["catalog"], x=x, y=y, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/clusters")
def clusters() -> dict:
    return clusters_payload(_catalog_or_503()["catalog"])


@app.get("/api/songs/search")
def songs_search(
    query: str = Query(default="", max_length=200),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict:
    hits = search_tracks(_catalog_or_503()["catalog"], query, limit=limit)
    return {"query": query, "count": len(hits), "results": hits}


@app.get("/api/songs/{track_id}")
def song_by_id(track_id: str) -> dict:
    try:
        return song_detail(_catalog_or_503()["catalog"], track_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Track not found: {exc.args[0]}") from exc


@app.post("/api/recommend")
def recommend(body: RecommendRequest) -> dict:
    store = _catalog_or_503()
    try:
        return recommend_tracks(
            store["catalog"],
            store["unit_matrix"],
            store["id_to_index"],
            body.track_id,
            top_n=body.top_n,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Track not found: {exc.args[0]}") from exc
