"""KPI, correlation, cluster, search, and cosine-similarity helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from data_loader import AUDIO_FEATURES
from hive_client import (
    GENRES_SQL,
    KPI_SQL,
    TOP_ARTISTS_SQL,
    TOP_TRACKS_SQL,
    ensure_hive_table,
    hive_available,
    hive_query,
)

PERSONA_RULES = (
    ("Instrumental / Ambient", lambda m: m["instrumentalness"] > 0.55),
    ("Acoustic / Intimate", lambda m: m["acousticness"] > 0.55 and m["energy"] < 0.5),
    ("Speech-forward / Hip-Hop", lambda m: m["speechiness"] > 0.18),
    ("Live / Concert", lambda m: m["liveness"] > 0.35),
    ("High-Energy Anthems", lambda m: m["energy"] > 0.7 and m["loudness"] > -8),
    ("Dancefloor / Party", lambda m: m["danceability"] > 0.7 and m["valence"] > 0.55),
    ("Upbeat Pop", lambda m: m["valence"] > 0.65 and m["danceability"] > 0.55),
    ("Melancholic / Moody", lambda m: m["valence"] < 0.4 and m["energy"] < 0.5),
)


def track_payload(row: pd.Series, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    def cell(name: str, default: Any = "") -> Any:
        if name in row.index and pd.notna(row[name]):
            return row[name]
        return default

    payload = {
        "track_id": str(cell("track_id", "")),
        "track_name": str(cell("track_name", "Unknown Track")),
        "artists": str(cell("artists", "Unknown Artist")),
        "album_name": str(cell("album_name", "")),
        "genre": str(cell("genre", cell("track_genre", "unknown"))),
        "popularity": float(cell("popularity", 0) or 0),
        "cluster": int(float(cell("cluster", -1) or -1)),
        "features": {name: float(cell(name, 0) or 0) for name in AUDIO_FEATURES},
    }
    if extra:
        payload.update(extra)
    return payload


def cluster_persona(means: dict[str, float]) -> str:
    for label, rule in PERSONA_RULES:
        if rule(means):
            return label
    return "Balanced Mix"


def minmax_radar(means: pd.Series, global_min: pd.Series, global_max: pd.Series) -> list[dict[str, Any]]:
    radar = []
    for feature in AUDIO_FEATURES:
        span = float(global_max[feature] - global_min[feature]) or 1.0
        scaled = (float(means[feature]) - float(global_min[feature])) / span
        radar.append(
            {
                "feature": feature,
                "raw": float(means[feature]),
                "value": round(float(np.clip(scaled, 0, 1)), 4),
            }
        )
    return radar


def _num(value: Any, digits: int = 4) -> float:
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return 0.0


def _hive_track_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if "genre" not in frame.columns and "track_genre" in frame.columns:
        frame = frame.rename(columns={"track_genre": "genre"})
    rows = []
    for _, row in frame.iterrows():
        rows.append(track_payload(row))
    return rows


def summary_from_hive() -> dict[str, Any]:
    ensure_hive_table()
    kpis_df = hive_query(KPI_SQL)
    row = kpis_df.iloc[0]
    tracks = int(row["tracks"])
    kpis = {
        "tracks": tracks,
        "artists": int(row["artists"]),
        "genres": int(row["genres"]),
        "clusters": int(row["clusters"]),
        "avg_popularity": _num(row["avg_popularity"], 2),
        "avg_danceability": _num(row["avg_danceability"]),
        "avg_energy": _num(row["avg_energy"]),
        "avg_valence": _num(row["avg_valence"]),
    }
    top_tracks = _hive_track_rows(hive_query(TOP_TRACKS_SQL))
    artists_df = hive_query(TOP_ARTISTS_SQL)
    top_artists = [
        {
            "artist": str(item.artist),
            "tracks": int(item.tracks),
            "avg_popularity": _num(item.avg_popularity, 2),
        }
        for item in artists_df.itertuples(index=False)
    ]
    genres_df = hive_query(GENRES_SQL)
    genres = []
    for item in genres_df.itertuples(index=False):
        count = int(item.tracks)
        genres.append(
            {
                "genre": str(item.genre),
                "tracks": count,
                "share": round(count / tracks, 4) if tracks else 0,
                "avg_popularity": _num(item.avg_popularity, 2),
                "avg_danceability": _num(item.avg_danceability),
                "avg_energy": _num(item.avg_energy),
                "avg_loudness": _num(item.avg_loudness, 2),
                "avg_acousticness": _num(item.avg_acousticness),
                "avg_valence": _num(item.avg_valence),
                "avg_tempo": _num(item.avg_tempo, 2),
            }
        )
    return {
        "query_engine": "hive",
        "kpis": kpis,
        "feature_averages": {
            "danceability": kpis["avg_danceability"],
            "energy": kpis["avg_energy"],
            "valence": kpis["avg_valence"],
        },
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "genres": genres,
    }


def summary_payload(catalog: pd.DataFrame, engine: str = "pandas") -> dict[str, Any]:
    if engine == "hive":
        if not hive_available():
            payload = summary_from_catalog(catalog)
            payload["query_engine"] = "pandas"
            payload["hive_error"] = "hiveserver2 is not running"
            return payload
        try:
            return summary_from_hive()
        except Exception as exc:  # noqa: BLE001
            payload = summary_from_catalog(catalog)
            payload["hive_error"] = str(exc)[:400]
            return payload
    return summary_from_catalog(catalog)


def summary_from_catalog(catalog: pd.DataFrame) -> dict[str, Any]:
    n_tracks = int(len(catalog))
    n_artists = int(catalog["artists"].nunique())
    n_genres = int(catalog["genre"].nunique())
    n_clusters = int(catalog["cluster"].nunique())

    top_tracks = (
        catalog.sort_values("popularity", ascending=False)
        .head(10)
        .apply(track_payload, axis=1)
        .tolist()
    )

    artist_stats = (
        catalog.groupby("artists", dropna=False)
        .agg(tracks=("track_id", "count"), avg_popularity=("popularity", "mean"))
        .reset_index()
        .sort_values(["tracks", "avg_popularity"], ascending=False)
        .head(10)
    )
    top_artists = [
        {
            "artist": row.artists,
            "tracks": int(row.tracks),
            "avg_popularity": round(float(row.avg_popularity), 2),
        }
        for row in artist_stats.itertuples(index=False)
    ]

    genre_stats = (
        catalog.groupby("genre", dropna=False)
        .agg(
            tracks=("track_id", "count"),
            avg_popularity=("popularity", "mean"),
            avg_danceability=("danceability", "mean"),
            avg_energy=("energy", "mean"),
            avg_loudness=("loudness", "mean"),
            avg_acousticness=("acousticness", "mean"),
            avg_valence=("valence", "mean"),
            avg_tempo=("tempo", "mean"),
        )
        .reset_index()
        .sort_values("tracks", ascending=False)
        .head(15)
    )
    genres = [
        {
            "genre": row.genre,
            "tracks": int(row.tracks),
            "share": round(int(row.tracks) / n_tracks, 4) if n_tracks else 0,
            "avg_popularity": round(float(row.avg_popularity), 2),
            "avg_danceability": round(float(row.avg_danceability), 4),
            "avg_energy": round(float(row.avg_energy), 4),
            "avg_loudness": round(float(row.avg_loudness), 2),
            "avg_acousticness": round(float(row.avg_acousticness), 4),
            "avg_valence": round(float(row.avg_valence), 4),
            "avg_tempo": round(float(row.avg_tempo), 2),
        }
        for row in genre_stats.itertuples(index=False)
    ]

    feature_avgs = {name: round(float(catalog[name].mean()), 4) for name in AUDIO_FEATURES}

    return {
        "query_engine": "pandas",
        "kpis": {
            "tracks": n_tracks,
            "artists": n_artists,
            "genres": n_genres,
            "clusters": n_clusters,
            "avg_popularity": round(float(catalog["popularity"].mean()), 2),
            "avg_danceability": feature_avgs["danceability"],
            "avg_energy": feature_avgs["energy"],
            "avg_valence": feature_avgs["valence"],
        },
        "feature_averages": feature_avgs,
        "top_tracks": top_tracks,
        "top_artists": top_artists,
        "genres": genres,
    }


def correlation_payload(catalog: pd.DataFrame) -> dict[str, Any]:
    cols = [*AUDIO_FEATURES, "popularity"]
    corr = catalog[cols].corr(method="pearson")
    matrix = [[round(float(corr.loc[row, col]), 4) for col in cols] for row in cols]
    pairs = []
    for i, left in enumerate(cols):
        for j, right in enumerate(cols):
            if i >= j:
                continue
            pairs.append({"x": left, "y": right, "value": round(float(corr.loc[left, right]), 4)})
    pairs.sort(key=lambda item: abs(item["value"]), reverse=True)
    vs_popularity = [
        {"feature": name, "value": round(float(corr.loc[name, "popularity"]), 4)}
        for name in AUDIO_FEATURES
    ]
    vs_popularity.sort(key=lambda item: abs(item["value"]), reverse=True)
    return {
        "features": cols,
        "matrix": matrix,
        "pairs": pairs,
        "vs_popularity": vs_popularity,
    }


def scatter_payload(
    catalog: pd.DataFrame,
    x: str = "energy",
    y: str = "danceability",
    limit: int = 800,
) -> dict[str, Any]:
    allowed = set(AUDIO_FEATURES + ["popularity"])
    if x not in allowed or y not in allowed:
        raise ValueError("x and y must be audio features or popularity")
    sample = catalog.sample(n=min(int(limit), len(catalog)), random_state=42)
    points = [
        {
            "x": float(row[x]),
            "y": float(row[y]),
            "cluster": int(row["cluster"]),
            "track_name": str(row["track_name"]),
            "artists": str(row["artists"]),
            "popularity": float(row["popularity"]),
        }
        for _, row in sample.iterrows()
    ]
    return {"x": x, "y": y, "points": points}


def song_detail(catalog: pd.DataFrame, track_id: str) -> dict[str, Any]:
    hits = catalog.loc[catalog["track_id"].astype(str) == str(track_id)]
    if hits.empty:
        raise KeyError(track_id)
    return track_payload(hits.iloc[0])


def clusters_payload(catalog: pd.DataFrame) -> dict[str, Any]:
    total = max(len(catalog), 1)
    global_min = catalog[AUDIO_FEATURES].min()
    global_max = catalog[AUDIO_FEATURES].max()
    clusters = []

    for cluster_id, group in catalog.groupby("cluster"):
        means = group[AUDIO_FEATURES].mean()
        mean_map = {name: round(float(means[name]), 4) for name in AUDIO_FEATURES}
        top = (
            group.sort_values("popularity", ascending=False)
            .head(5)
            .apply(track_payload, axis=1)
            .tolist()
        )
        clusters.append(
            {
                "id": int(cluster_id),
                "label": cluster_persona(mean_map),
                "size": int(len(group)),
                "share": round(len(group) / total, 4),
                "avg_popularity": round(float(group["popularity"].mean()), 2),
                "means": mean_map,
                "radar": minmax_radar(means, global_min, global_max),
                "top_tracks": top,
                "top_genres": [
                    {"genre": genre, "tracks": int(count)}
                    for genre, count in group["genre"].value_counts().head(5).items()
                ],
            }
        )

    clusters.sort(key=lambda item: item["id"])
    return {"k": len(clusters), "features": AUDIO_FEATURES, "clusters": clusters}


def search_tracks(catalog: pd.DataFrame, query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return (
            catalog.sort_values("popularity", ascending=False)
            .head(limit)
            .apply(track_payload, axis=1)
            .tolist()
        )

    mask = catalog["track_name"].astype(str).str.lower().str.contains(q, na=False) | catalog[
        "artists"
    ].astype(str).str.lower().str.contains(q, na=False)
    hits = catalog.loc[mask].sort_values("popularity", ascending=False).head(limit)
    return hits.apply(track_payload, axis=1).tolist()


def recommend_tracks(
    catalog: pd.DataFrame,
    unit_matrix: np.ndarray,
    id_to_index: dict[str, int],
    track_id: str,
    top_n: int = 10,
) -> dict[str, Any]:
    if track_id not in id_to_index:
        raise KeyError(track_id)

    index = id_to_index[track_id]
    query = unit_matrix[index]
    scores = unit_matrix @ query
    scores[index] = -np.inf
    top_n = max(1, min(int(top_n), len(catalog) - 1))
    neighbor_idx = np.argpartition(-scores, top_n)[:top_n]
    neighbor_idx = neighbor_idx[np.argsort(-scores[neighbor_idx])]

    seed = track_payload(catalog.iloc[index])
    results = []
    for idx in neighbor_idx:
        results.append(
            track_payload(
                catalog.iloc[int(idx)],
                extra={"similarity": round(float(scores[int(idx)]), 4)},
            )
        )
    return {"seed": seed, "recommendations": results}
