import numpy as np
from utils import AUDIO_FEATURES, records_to_json

def overview(df):
    return {
        "total_songs": int(len(df)),
        "total_artists": int(df["artists"].nunique()),
        "total_genres": int(df["track_genre"].nunique()),
        "average_popularity": round(float(df["popularity"].mean()), 2),
        "average_features": {
            feature: round(float(df[feature].mean()), 4)
            for feature in AUDIO_FEATURES
        }
    }

def feature_distributions(df, bins=20):
    result = {}
    for feature in AUDIO_FEATURES:
        values = df[feature].dropna()
        counts, edges = np.histogram(values, bins=bins)
        result[feature] = [
            {
                "range": f"{edges[i]:.2f}–{edges[i+1]:.2f}",
                "count": int(counts[i])
            }
            for i in range(len(counts))
        ]
    return result

def genre_statistics(df):
    result = (
        df.groupby("track_genre")
        .agg(
            songs=("track_id", "count"),
            average_popularity=("popularity", "mean"),
            average_energy=("energy", "mean"),
            average_danceability=("danceability", "mean"),
            average_valence=("valence", "mean"),
            average_acousticness=("acousticness", "mean"),
            average_tempo=("tempo", "mean")
        )
        .reset_index()
        .sort_values("average_popularity", ascending=False)
    )
    return records_to_json(result)

def popularity_distribution(df):
    counts, edges = np.histogram(
        df["popularity"].dropna(),
        bins=10,
        range=(0, 100)
    )
    return [
        {
            "range": f"{edges[i]:.0f}–{edges[i+1]:.0f}",
            "count": int(counts[i])
        }
        for i in range(len(counts))
    ]
