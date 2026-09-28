from utils import AUDIO_FEATURES, records_to_json

def summary(df):
    result = (
        df.groupby("cluster")
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
        .sort_values("cluster")
    )

    return records_to_json(result)

def detail(df, cluster_id):
    result = df[df["cluster"] == cluster_id]

    if result.empty:
        return None

    genres = (
        result["track_genre"]
        .value_counts()
        .head(10)
        .rename_axis("genre")
        .reset_index(name="songs")
    )

    return {
        "cluster": int(cluster_id),
        "songs": int(len(result)),
        "average_popularity": round(float(result["popularity"].mean()), 2),
        "averages": {
            feature: round(float(result[feature].mean()), 4)
            for feature in AUDIO_FEATURES
        },
        "top_genres": records_to_json(genres)
    }

def songs(df, cluster_id, limit=50):
    result = df[df["cluster"] == cluster_id].head(limit)

    columns = [
        "track_id", "track_name", "artists",
        "track_genre", "popularity", "cluster"
    ]

    return records_to_json(result[columns])
